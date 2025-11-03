from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.schemas.player import PlayerProfile


class HeroRegistrationRequest(BaseModel):
    login: str = Field(..., min_length=3, max_length=128)
    password: str = Field(..., min_length=6, max_length=256)
    hero_name: str = Field(..., min_length=1, max_length=64)


class LoginRequest(BaseModel):
    login: str = Field(..., min_length=3, max_length=128)
    password: str = Field(..., min_length=1, max_length=256)


class AuthenticatedUser(BaseModel):
    id: int
    login: str
    is_admin: bool
    player_id: Optional[int] = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user: AuthenticatedUser
    player: Optional[PlayerProfile] = None
