from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

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
                "rarity": catalog_item.rarity if catalog_item else "common",
                "cosmetic": catalog_item.cosmetic if catalog_item else False,
                "is_equipped": item.is_equipped,
            }
        )

    return inventory_public
