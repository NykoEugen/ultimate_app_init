from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.inventory import InventoryEquipRequest, InventoryUnequipRequest
from app.services.inventory_service import (
    build_inventory_public,
    equip_inventory_item,
    unequip_inventory_item,
)
from app.auth.dependencies import require_player_access


router = APIRouter(prefix="/player/{player_id}/inventory", tags=["inventory"])


@router.get("")
async def get_inventory(
    player_id: int,
    db: AsyncSession = Depends(get_db),
    _user=Depends(require_player_access),
):
    """Return full inventory for the given player."""
    return await build_inventory_public(db, player_id)


@router.post("/equip")
async def equip_item(
    player_id: int,
    payload: InventoryEquipRequest,
    db: AsyncSession = Depends(get_db),
    _user=Depends(require_player_access),
):
    """Equip the specified item and return updated inventory state."""
    item = await equip_inventory_item(db, player_id, payload.item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found for this player")

    await db.commit()
    inventory_state = await build_inventory_public(db, player_id)
    return {
        "status": "equipped",
        "equipped_item_id": item.id,
        "inventory": inventory_state["items"],
        "base_stats": inventory_state["base_stats"],
    }


@router.post("/unequip")
async def unequip_item(
    player_id: int,
    payload: InventoryUnequipRequest,
    db: AsyncSession = Depends(get_db),
    _user=Depends(require_player_access),
):
    """Unequip the specified item and return updated inventory state."""
    item = await unequip_inventory_item(db, player_id, payload.item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found for this player")

    await db.commit()
    inventory_state = await build_inventory_public(db, player_id)
    return {
        "status": "unequipped",
        "unequipped_item_id": item.id,
        "inventory": inventory_state["items"],
        "base_stats": inventory_state["base_stats"],
    }
