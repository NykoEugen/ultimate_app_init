from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.base import get_session
from app.db.models.inventory import InventoryItem
from app.db.models.player import Player
from app.schemas.player import (
    DailyRewardClaimResponse,
    InventoryItemPublic,
    PlayerProfile,
)
from app.services.progression_service import ProgressionService
from app.utils.exceptions import DailyRewardUnavailable


router = APIRouter(prefix="/player", tags=["player"])


@router.get("/{player_id}/profile", response_model=PlayerProfile)
def get_player_profile(player_id: int, session: Session = Depends(get_session)) -> PlayerProfile:
    player = _load_player(session, player_id)
    return _build_player_profile(player)


@router.post("/{player_id}/claim-daily-reward", response_model=DailyRewardClaimResponse)
def claim_daily_reward(player_id: int, session: Session = Depends(get_session)) -> DailyRewardClaimResponse:
    player = _load_player(session, player_id)

    progression = ProgressionService(session)
    try:
        reward = progression.claim_daily(player)
    except DailyRewardUnavailable as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    session.flush()

    profile = _build_player_profile(player)

    reward_parts = []
    if reward.energy_gained:
        reward_parts.append(f"+{reward.energy_gained} енергії")
    if reward.gold_gained:
        reward_parts.append(f"+{reward.gold_gained} золота")
    if reward.xp_gained:
        reward_parts.append(f"+{reward.xp_gained} XP")

    details = ", ".join(reward_parts) if reward_parts else "жодних бонусів"
    message = f"Ти відпочив біля вогнища і відчуваєш сили ({details})."

    session.commit()

    return DailyRewardClaimResponse(profile=profile, message=message)


def _load_player(session: Session, player_id: int) -> Player:
    stmt = (
        select(Player)
        .where(Player.id == player_id)
        .options(
            selectinload(Player.inventory_items).selectinload(InventoryItem.catalog_item),
            selectinload(Player.quest_progress),
        )
    )
    player = session.execute(stmt).scalars().first()
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


def _build_player_profile(player: Player) -> PlayerProfile:
    inventory_public = [
        InventoryItemPublic(
            id=item.id,
            name=item.catalog_item.name if item.catalog_item else "Невідомий предмет",
            rarity=item.catalog_item.rarity if item.catalog_item else "common",
            cosmetic=item.catalog_item.cosmetic if item.catalog_item else False,
            is_equipped=item.is_equipped,
        )
        for item in (player.inventory_items or [])
    ]

    return PlayerProfile(
        player_id=player.id,
        username=player.username,
        level=player.level,
        xp=player.xp,
        energy=player.energy,
        max_energy=player.max_energy,
        gold=getattr(player, "gold", 0),
        last_daily_claim_at=player.last_daily_claim_at,
        inventory=inventory_public,
    )
