from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class InventoryItemPublic(BaseModel):
    id: int
    name: str
    rarity: str
    cosmetic: bool
    is_equipped: bool

class PlayerProfile(BaseModel):
    player_id: int
    username: Optional[str]

    level: int
    xp: int
    energy: int
    max_energy: int

    last_daily_claim_at: Optional[datetime]

    inventory: List[InventoryItemPublic]

    class Config:
        from_attributes = True
