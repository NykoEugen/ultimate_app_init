from __future__ import annotations

from pydantic import BaseModel


class InventoryEquipRequest(BaseModel):
    item_id: int


class InventoryUnequipRequest(BaseModel):
    item_id: int
