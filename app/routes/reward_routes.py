from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_session
from app.db.models.player import Player
from app.services.progression_service import DAILY_REWARD_COOLDOWN, ProgressionService
from app.utils.exceptions import DailyRewardUnavailable


router = APIRouter(prefix="/player", tags=["reward"])


@router.post("/{player_id}/claim-daily-reward")
def claim_daily_reward(player_id: int, session: Session = Depends(get_session)) -> Dict[str, object]:
    player = session.get(Player, player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    now = datetime.now(timezone.utc)
    progression = ProgressionService(session)

    try:
        reward = progression.claim_daily(player, now=now)
    except DailyRewardUnavailable:
        retry_after_seconds = _calculate_retry_after(player, now)
        session.rollback()
        return {
            "status": "cooldown",
            "retry_after_seconds": retry_after_seconds,
            "message": "Ти вже відпочивав нещодавно. Спробуй пізніше.",
        }

    session.commit()

    return {
        "status": "claimed",
        "gained": {
            "energy": reward.energy_gained,
            "xp": reward.xp_gained,
            "level_up": reward.levels_gained > 0,
        },
        "message": "Ти відпочив біля вогнища і відчуваєш прилив сил.",
    }


def _calculate_retry_after(player: Player, now: datetime) -> int:
    last_claim = player.last_daily_claim_at
    if last_claim is None:
        return 0
    if last_claim.tzinfo is None:
        last_claim = last_claim.replace(tzinfo=timezone.utc)
    cooldown_end = last_claim + DAILY_REWARD_COOLDOWN
    return max(0, int((cooldown_end - now).total_seconds()))
