from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import get_session
from app.db.models.player import Player
from app.db.models.user import SessionToken, UserAccount
from app.db.models.wallet import Wallet
from app.schemas.auth import AuthResponse, AuthenticatedUser, HeroRegistrationRequest, LoginRequest
from app.services.farm_service import FarmService
from app.services.onboarding_service import OnboardingService
from app.services.player_profile import build_player_profile
from app.services.quest_content_service import QuestContentService
from app.utils.security import (
    create_access_token,
    create_password_digest,
    token_expiry,
    verify_password,
)


router = APIRouter(prefix="/auth", tags=["auth"])


def _normalize_login(raw: str) -> str:
    normalized = raw.strip().lower()
    if not normalized:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Логін не може бути порожнім.")
    return normalized


def _build_auth_response(token_value: str, user: UserAccount) -> AuthResponse:
    profile = None
    player = user.player
    if player is not None:
        profile = build_player_profile(player)

    return AuthResponse(
        access_token=token_value,
        user=AuthenticatedUser(
            id=user.id,
            login=user.login,
            is_admin=user.is_admin,
            player_id=user.player_id,
        ),
        player=profile,
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register_hero(payload: HeroRegistrationRequest, session: Session = Depends(get_session)) -> AuthResponse:
    login = _normalize_login(payload.login)

    existing = session.execute(select(UserAccount).where(UserAccount.login == login)).scalars().first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Такий логін уже існує.")

    hero_name = payload.hero_name.strip()
    if not hero_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Назва героя обов'язкова.")

    salt, digest = create_password_digest(payload.password)

    player = Player(
        username=hero_name,
        level=1,
        xp=0,
        energy=20,
        max_energy=20,
        gold=0,
    )
    session.add(player)
    session.flush()

    wallet = Wallet(player_id=player.id, gold=player.gold)
    session.add(wallet)
    session.flush()

    FarmService(session).get_farm_state(player.id)
    onboarding_service = OnboardingService(session)
    onboarding_service.ensure_onboarding_content()
    QuestContentService(session).ensure_fallen_crown_saga()

    user = UserAccount(
        login=login,
        password_hash=digest,
        password_salt=salt,
        is_admin=False,
        player_id=player.id,
    )
    session.add(user)
    session.flush()

    token_value = create_access_token()
    token = SessionToken(
        token=token_value,
        user_id=user.id,
        expires_at=token_expiry(),
    )
    session.add(token)
    session.flush()

    session.refresh(user)
    session.refresh(player)

    return _build_auth_response(token_value, user)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, session: Session = Depends(get_session)) -> AuthResponse:
    login_value = _normalize_login(payload.login)

    user = session.execute(select(UserAccount).where(UserAccount.login == login_value)).scalars().first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невірний логін або пароль.")

    if not verify_password(payload.password, user.password_salt, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Невірний логін або пароль.")

    token_value = create_access_token()
    session.add(
        SessionToken(
            token=token_value,
            user_id=user.id,
            expires_at=token_expiry(),
        )
    )
    session.flush()
    session.refresh(user)
    if user.player is not None:
        session.refresh(user.player)
    return _build_auth_response(token_value, user)
