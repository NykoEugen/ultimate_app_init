from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class PlayerCreateRequest(BaseModel):
    player_id: int
    username: Optional[str] = None


class InventoryItemPublic(BaseModel):
    id: int
    name: str
    slot: str
    rarity: str
    cosmetic: bool
    is_equipped: bool
    icon: Optional[str] = None
    description: Optional[str] = None

class PlayerProfile(BaseModel):
    player_id: int
    username: Optional[str]

    level: int
    xp: int
    energy: int
    max_energy: int
    gold: int

    last_daily_claim_at: Optional[datetime]

    inventory: List[InventoryItemPublic]

    class Config:
        from_attributes = True


class DailyRewardClaimResponse(BaseModel):
    profile: PlayerProfile
    message: str
