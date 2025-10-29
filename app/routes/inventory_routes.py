from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.inventory import InventoryEquipRequest
from app.services.inventory_service import build_inventory_public, equip_inventory_item


router = APIRouter(prefix="/player/{player_id}/inventory", tags=["inventory"])


@router.get("")
async def get_inventory(player_id: int, db: AsyncSession = Depends(get_db)):
    """Return full inventory for the given player."""
    return await build_inventory_public(db, player_id)


@router.post("/equip")
async def equip_item(
    player_id: int,
    payload: InventoryEquipRequest,
    db: AsyncSession = Depends(get_db),
):
    """Equip the specified item and return updated inventory state."""
    item = await equip_inventory_item(db, player_id, payload.item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found for this player")

    await db.commit()
    inventory = await build_inventory_public(db, player_id)
    return {
        "status": "equipped",
        "equipped_item_id": item.id,
        "inventory": inventory,
    }
