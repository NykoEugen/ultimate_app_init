from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.dashboard_service import build_dashboard


router = APIRouter(prefix="/player", tags=["dashboard"])


@router.get("/{player_id}/dashboard")
async def get_dashboard(player_id: int, db: AsyncSession = Depends(get_db)):
    """
    Повертає агрегований стан для головного екрану користувача.
    """
    data = await build_dashboard(db, player_id)
    return data
