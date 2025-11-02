from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from app.db.models.inventory import InventoryItem, InventoryItemCatalog
from app.db.models.player import Player
from app.utils.exceptions import InventoryItemNotFound


@dataclass
class GrantedItem:
    item_id: int
    catalog_item_id: int
    name: str


class InventoryService:
    """Handles inventory mutations for players."""

    def __init__(self, session: Session):
        self._session = session

    def grant_catalog_item(self, player: Player, catalog_item_id: int, *, auto_flush: bool = True) -> GrantedItem:
        catalog_item = self._session.get(InventoryItemCatalog, catalog_item_id)
        if catalog_item is None:
            raise InventoryItemNotFound(f"Catalog item {catalog_item_id} does not exist")

        inventory_item = InventoryItem(owner_id=player.id, catalog_item_id=catalog_item.id)
        self._session.add(inventory_item)

        if auto_flush:
            self._session.flush()

        return GrantedItem(
            item_id=inventory_item.id,
            catalog_item_id=catalog_item.id,
            name=catalog_item.name,
        )


async def build_inventory_public(session: AsyncSession, player_id: int) -> List[Dict[str, Any]]:
    """Return a public representation of player's inventory suitable for the UI."""
    stmt = (
        select(InventoryItem)
        .where(InventoryItem.owner_id == player_id)
        .options(selectinload(InventoryItem.catalog_item))
    )
    result = await session.execute(stmt)
    items = result.scalars().all()

    inventory_public: List[Dict[str, Any]] = []
    for item in items:
        catalog_item = item.catalog_item
        inventory_public.append(
            {
                "id": item.id,
                "name": catalog_item.name if catalog_item else "Невідомий предмет",
                "slot": catalog_item.slot if catalog_item else "misc",
                "rarity": catalog_item.rarity if catalog_item else "common",
                "cosmetic": catalog_item.cosmetic if catalog_item else False,
                "is_equipped": item.is_equipped,
                "icon": catalog_item.icon if catalog_item else None,
                "description": catalog_item.description if catalog_item else None,
            }
        )

    return inventory_public


async def equip_inventory_item(session: AsyncSession, player_id: int, item_id: int) -> Optional[InventoryItem]:
    """Equip the specified inventory item, unequipping others in the same slot."""
    stmt = (
        select(InventoryItem)
        .where(InventoryItem.id == item_id, InventoryItem.owner_id == player_id)
        .options(selectinload(InventoryItem.catalog_item))
    )
    result = await session.execute(stmt)
    item = result.scalars().first()
    if item is None:
        return None

    slot = item.catalog_item.slot if item.catalog_item else None

    if slot:
        other_items_stmt = (
            select(InventoryItem)
            .join(InventoryItem.catalog_item)
            .where(
                InventoryItem.owner_id == player_id,
                InventoryItem.id != item.id,
                InventoryItemCatalog.slot == slot,
            )
        )
        others_result = await session.execute(other_items_stmt)
        for other in others_result.scalars().all():
            other.is_equipped = False

    item.is_equipped = True
    await session.flush()
    await session.refresh(item)
    return item


async def unequip_inventory_item(session: AsyncSession, player_id: int, item_id: int) -> Optional[InventoryItem]:
    """Unequip the specified inventory item for the player."""
    stmt = (
        select(InventoryItem)
        .where(InventoryItem.id == item_id, InventoryItem.owner_id == player_id)
        .options(selectinload(InventoryItem.catalog_item))
    )
    result = await session.execute(stmt)
    item = result.scalars().first()
    if item is None:
        return None

    item.is_equipped = False
    await session.flush()
    await session.refresh(item)
    return item
