from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

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
