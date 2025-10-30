from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_session
from app.db.models.player import Player
from app.services.progression_service import ProgressionService


router = APIRouter(prefix="/player", tags=["progression"])


@router.get("/{player_id}/progression")
def get_progression(player_id: int, session: Session = Depends(get_session)) -> dict:
    player = session.get(Player, player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    xp_to_next = ProgressionService.xp_to_next_level(player)
    milestone = ProgressionService.build_milestone(player)

    return {
        "level": player.level,
        "xp": player.xp,
        "xp_to_next_level": xp_to_next,
        "milestone": milestone,
    }
