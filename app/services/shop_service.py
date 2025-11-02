from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Tuple

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.inventory import InventoryItem, InventoryItemCatalog
from app.db.models.player import Player
from app.db.models.shop import ShopOffer
from app.db.models.wallet import Wallet
from app.services.player_service import create_player_if_not_exists
from app.utils.exceptions import InsufficientFunds, ShopOfferUnavailable


async def ensure_wallet(session: AsyncSession, player: Player) -> Wallet:
    wallet = await session.get(Wallet, player.id)
    if wallet is None:
        wallet = Wallet(player_id=player.id, gold=player.gold)
        session.add(wallet)
        await session.flush()
    return wallet


async def list_shop_offers(session: AsyncSession, player_id: int) -> Tuple[Wallet, List[Dict[str, object]]]:
    player = await create_player_if_not_exists(session, player_id)
    wallet = await ensure_wallet(session, player)

    now = datetime.now(timezone.utc)

    offers_stmt = (
        select(ShopOffer)
        .options(selectinload(ShopOffer.catalog_item))
        .where(or_(ShopOffer.expires_at.is_(None), ShopOffer.expires_at > now))
        .order_by(ShopOffer.id)
    )
    offers_result = await session.execute(offers_stmt)
    offers = offers_result.scalars().all()

    owned_stmt = select(InventoryItem.catalog_item_id).where(InventoryItem.owner_id == player_id)
    owned_result = await session.execute(owned_stmt)
    owned_item_ids = {row[0] for row in owned_result.all()}

    offers_public: List[Dict[str, object]] = []
    for offer in offers:
        catalog_item: InventoryItemCatalog = offer.catalog_item
        offers_public.append(
            {
                "offer_id": offer.id,
                "item_name": catalog_item.name if catalog_item else "Невідомий предмет",
                "rarity": catalog_item.rarity if catalog_item else "common",
                "price_gold": offer.price_gold,
                "expires_at": offer.expires_at.isoformat() if offer.expires_at else None,
                "owned": catalog_item.id in owned_item_ids if catalog_item else False,
                "is_limited": offer.is_limited,
                "slot": catalog_item.slot if catalog_item else "misc",
                "cosmetic": catalog_item.cosmetic if catalog_item else False,
                "description": catalog_item.description if catalog_item else None,
                "icon": catalog_item.icon if catalog_item else None,
            }
        )

    return wallet, offers_public


async def buy_offer(session: AsyncSession, player_id: int, offer_id: int) -> Tuple[Wallet, Dict[str, object]]:
    player = await create_player_if_not_exists(session, player_id)
    wallet = await ensure_wallet(session, player)

    offer = await session.get(ShopOffer, offer_id, options=(selectinload(ShopOffer.catalog_item),))
    if offer is None:
        raise ShopOfferUnavailable("Offer not found")

    now = datetime.now(timezone.utc)
    expires_at = offer.expires_at
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at and expires_at <= now:
        raise ShopOfferUnavailable("Offer has expired")

    if wallet.gold < offer.price_gold:
        raise InsufficientFunds(available=wallet.gold, required=offer.price_gold)

    owned_stmt = select(InventoryItem).where(
        InventoryItem.owner_id == player_id,
        InventoryItem.catalog_item_id == offer.catalog_item_id,
    )
    owned_result = await session.execute(owned_stmt)
    already_owned = owned_result.scalars().first()
    if offer.is_limited and already_owned:
        raise ShopOfferUnavailable("Offer already purchased")

    wallet.gold -= offer.price_gold
    player.gold = wallet.gold

    new_item = InventoryItem(owner_id=player.id, catalog_item_id=offer.catalog_item_id, is_equipped=False)
    session.add(new_item)
    await session.flush()
    await session.refresh(new_item)

    await session.flush()

    granted = {
        "inventory_item_id": new_item.id if new_item else already_owned.id,
        "catalog_item_id": offer.catalog_item_id,
    }
    return wallet, granted
