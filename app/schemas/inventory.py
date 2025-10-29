from __future__ import annotations

from pydantic import BaseModel


class InventoryEquipRequest(BaseModel):
    item_id: int
