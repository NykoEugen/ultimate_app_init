from __future__ import annotations

from fastapi.testclient import TestClient

from app.db.models.inventory import InventoryItem, InventoryItemCatalog
from app.db.models.player import Player


def _seed_player_with_inventory(session) -> tuple[Player, list[InventoryItem]]:
    player = Player(id=77, username="Styler", level=5, xp=20, energy=15, max_energy=20, gold=100)

    cloak = InventoryItemCatalog(
        name="Плащ Мандрівника",
        slot="cloak",
        rarity="rare",
        cosmetic=True,
        description="Додає загадковості силуету.",
        icon="cloak_traveler_rare",
    )
    headpiece = InventoryItemCatalog(
        name="Маска Сутінків",
        slot="head",
        rarity="epic",
        cosmetic=True,
        description="Приховує обличчя у півтіні.",
        icon="mask_dusk_epic",
    )
    other_cloak = InventoryItemCatalog(
        name="Пелерина Довіри",
        slot="cloak",
        rarity="common",
        cosmetic=True,
        description="Легка пелерина на кожен день.",
        icon="cloak_trust_common",
    )

    session.add_all([player, cloak, headpiece, other_cloak])
    session.flush()

    items = [
        InventoryItem(owner_id=player.id, catalog_item_id=cloak.id, is_equipped=True),
        InventoryItem(owner_id=player.id, catalog_item_id=headpiece.id, is_equipped=False),
        InventoryItem(owner_id=player.id, catalog_item_id=other_cloak.id, is_equipped=False),
    ]
    session.add_all(items)
    session.commit()
    return player, items


def test_get_inventory_returns_public_data(client: TestClient, session_factory):
    session = session_factory()
    player, items = _seed_player_with_inventory(session)
    item_description = items[0].catalog_item.description
    player_id = player.id
    session.close()

    response = client.get(f"/player/{player_id}/inventory")
    assert response.status_code == 200

    payload = response.json()
    assert isinstance(payload, dict)
    assert "items" in payload
    assert "base_stats" in payload
    assert len(payload["items"]) == 3
    cloak = next(item for item in payload["items"] if item["slot"] == "cloak" and item["is_equipped"])
    assert cloak["name"] == "Плащ Мандрівника"
    assert cloak["icon"] == "cloak_traveler_rare"
    assert cloak["description"] == item_description


def test_equip_inventory_item_switches_items(client: TestClient, session_factory):
    session = session_factory()
    player, items = _seed_player_with_inventory(session)
    target_item_id = items[2].id  # other cloak
    player_id = player.id
    session.close()

    response = client.post(
        f"/player/{player_id}/inventory/equip",
        json={"item_id": target_item_id},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "equipped"
    assert payload["equipped_item_id"] == target_item_id

    equipped_items = [item for item in payload["inventory"] if item["slot"] == "cloak" and item["is_equipped"]]
    assert len(equipped_items) == 1
    assert equipped_items[0]["id"] == target_item_id


def test_unequip_inventory_item_moves_to_bag(client: TestClient, session_factory):
    session = session_factory()
    player, items = _seed_player_with_inventory(session)
    equipped_item_id = items[0].id
    player_id = player.id
    session.close()

    response = client.post(
        f"/player/{player_id}/inventory/unequip",
        json={"item_id": equipped_item_id},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "unequipped"
    assert payload["unequipped_item_id"] == equipped_item_id

    equipped_items = [item for item in payload["inventory"] if item["slot"] == "cloak" and item["is_equipped"]]
    assert len(equipped_items) == 0
