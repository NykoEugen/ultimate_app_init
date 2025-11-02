from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.base import get_session
from app.db.models.inventory import InventoryItem
from app.db.models.player import Player
from app.db.models.wallet import Wallet
from app.schemas.player import (
    InventoryItemPublic,
    PlayerCreateRequest,
    PlayerProfile,
)
from app.services.farm_service import FarmService
from app.services.onboarding_service import OnboardingService


router = APIRouter(prefix="/player", tags=["player"])


@router.get("/{player_id}/profile", response_model=PlayerProfile)
def get_player_profile(player_id: int, session: Session = Depends(get_session)) -> PlayerProfile:
    player = _load_player(session, player_id)
    return _build_player_profile(player)


@router.post("/", response_model=PlayerProfile, status_code=201)
def create_player(
    payload: PlayerCreateRequest,
    response: Response,
    session: Session = Depends(get_session),
) -> PlayerProfile:
    player = session.get(Player, payload.player_id)
    if player is not None:
        if player.wallet is None:
            wallet = Wallet(player_id=player.id, gold=player.gold)
            session.add(wallet)
            session.commit()
            session.refresh(player)
        FarmService(session).get_farm_state(player.id)
        OnboardingService(session).ensure_onboarding_content()
        response.status_code = 200
        return _build_player_profile(player)

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
    return _build_player_profile(player)


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


def _build_player_profile(player: Player) -> PlayerProfile:
    inventory_public = [
        InventoryItemPublic(
            id=item.id,
            name=item.catalog_item.name if item.catalog_item else "Невідомий предмет",
            slot=item.catalog_item.slot if item.catalog_item else "misc",
            rarity=item.catalog_item.rarity if item.catalog_item else "common",
            cosmetic=item.catalog_item.cosmetic if item.catalog_item else False,
            is_equipped=item.is_equipped,
            icon=item.catalog_item.icon if item.catalog_item else None,
            description=item.catalog_item.description if item.catalog_item else None,
        )
        for item in (player.inventory_items or [])
    ]

    wallet_gold = player.wallet.gold if player.wallet else getattr(player, "gold", 0)

    return PlayerProfile(
        player_id=player.id,
        username=player.username,
        level=player.level,
        xp=player.xp,
        energy=player.energy,
        max_energy=player.max_energy,
        gold=wallet_gold,
        last_daily_claim_at=player.last_daily_claim_at,
        inventory=inventory_public,
    )
