from __future__ import annotations

from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import get_session
from app.db.models.user import SessionToken, UserAccount


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> UserAccount:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Потрібна авторизація.")

    token_value = credentials.credentials
    stmt = select(SessionToken).where(SessionToken.token == token_value)
    token = session.execute(stmt).scalars().first()
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недійсний токен.")

    if token.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Токен протерміновано.")

    user = token.user
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Користувача не знайдено.")
    return user


def require_admin(user: UserAccount = Depends(get_current_user)) -> UserAccount:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ дозволено лише адміністраторам.")
    return user


def require_player_access(
    player_id: int | None = None,
    user: UserAccount = Depends(get_current_user),
) -> UserAccount:
    if user.is_admin or player_id is None:
        return user
    if user.player_id != player_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостатньо прав доступу до героя.")
    return user
