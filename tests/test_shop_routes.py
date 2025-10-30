from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.db.models.inventory import InventoryItem, InventoryItemCatalog
from app.db.models.player import Player
from app.db.models.shop import ShopOffer
from app.db.models.wallet import Wallet


def _create_offer(session, *, price: int = 80) -> tuple[Player, ShopOffer]:
    player = Player(id=301, username="Shopper", level=2, xp=40, energy=15, max_energy=20, gold=price)
    wallet = Wallet(player_id=player.id, gold=price)

    item = InventoryItemCatalog(
        name="Порожистий Плащ Ночі",
        slot="cloak",
        rarity="epic",
        cosmetic=True,
        description="Плащ, що сяє місячним світлом.",
        icon="cloak_void_epic",
    )

    session.add_all([player, wallet, item])
    session.flush()

    offer = ShopOffer(
        catalog_item_id=item.id,
        price_gold=price,
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        is_limited=True,
    )
    session.add(offer)
    session.commit()
    session.refresh(player)
    session.refresh(offer)
    return player, offer


def test_shop_list_returns_offers(client: TestClient, session_factory):
    session = session_factory()
    player, offer = _create_offer(session)
    session.close()

    response = client.get(f"/player/{player.id}/shop")
    assert response.status_code == 200

    payload = response.json()
    assert payload["wallet"]["gold"] == offer.price_gold
    assert payload["offers"]
    first_offer = payload["offers"][0]
    assert first_offer["offer_id"] == offer.id
    assert first_offer["price_gold"] == offer.price_gold
    assert first_offer["item_name"] == "Порожистий Плащ Ночі"


def test_shop_buy_deducts_wallet_and_grants_item(client: TestClient, session_factory):
    session = session_factory()
    player, offer = _create_offer(session, price=60)
    session.close()

    response = client.post(
        f"/player/{player.id}/shop/buy",
        json={"offer_id": offer.id},
    )
    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] == "purchased"
    assert payload["wallet"]["gold"] == 0
    granted_id = payload["granted"]["inventory_item_id"]

    check_session = session_factory()
    inventory_item = check_session.get(InventoryItem, granted_id)
    assert inventory_item is not None
    assert inventory_item.owner_id == player.id
    check_session.close()
