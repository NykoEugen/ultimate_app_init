from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.base import get_session
from app.db.models.inventory import InventoryItem
from app.db.models.player import Player
from app.db.models.wallet import Wallet
from app.schemas.player import PlayerCreateRequest, PlayerProfile
from app.services.farm_service import FarmService
from app.services.onboarding_service import OnboardingService
from app.services.quest_content_service import QuestContentService
from app.services.player_profile import build_player_profile
from app.auth.dependencies import get_current_user, require_player_access


router = APIRouter(prefix="/player", tags=["player"])


@router.get("/{player_id}/profile", response_model=PlayerProfile)
def get_player_profile(
    player_id: int,
    session: Session = Depends(get_session),
    _user=Depends(require_player_access),
) -> PlayerProfile:
    QuestContentService(session).ensure_fallen_crown_saga()
    player = _load_player(session, player_id)
    return build_player_profile(player)


@router.post("/", response_model=PlayerProfile, status_code=201)
def create_player(
    payload: PlayerCreateRequest,
    response: Response,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
) -> PlayerProfile:
    if not current_user.is_admin and current_user.player_id != payload.player_id:
        raise HTTPException(status_code=403, detail="Недостатньо прав для створення або оновлення героя.")
    player = session.get(Player, payload.player_id)
    if player is not None:
        if player.wallet is None:
            wallet = Wallet(player_id=player.id, gold=player.gold)
            session.add(wallet)
            session.commit()
        session.refresh(player)
        FarmService(session).get_farm_state(player.id)
        OnboardingService(session).ensure_onboarding_content()
        QuestContentService(session).ensure_fallen_crown_saga()
        response.status_code = 200
        return build_player_profile(player)

    player = Player(
        id=payload.player_id,
        username=payload.username,
        level=1,
        xp=0,
        energy=20,
        max_energy=20,
        gold=0,
    )
    session.add(player)
    session.commit()
    session.refresh(player)

    wallet = Wallet(player_id=player.id, gold=player.gold)
    session.add(wallet)
    session.commit()
    session.refresh(player)
    FarmService(session).get_farm_state(player.id)
    OnboardingService(session).ensure_onboarding_content()
    QuestContentService(session).ensure_fallen_crown_saga()
    return build_player_profile(player)


def _load_player(session: Session, player_id: int) -> Player:
    stmt = (
        select(Player)
        .where(Player.id == player_id)
        .options(
            selectinload(Player.inventory_items).selectinload(InventoryItem.catalog_item),
            selectinload(Player.quest_progress),
            selectinload(Player.wallet),
        )
    )
    player = session.execute(stmt).scalars().first()
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")
    return player
