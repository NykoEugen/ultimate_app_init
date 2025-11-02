from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class PlantTypePublic(BaseModel):
    id: int
    name: str
    description: Optional[str]
    growth_seconds: int
    xp_reward: int
    energy_cost: int
    seed_cost: int
    sell_price: int
    unlock_level: int
    unlock_farming_level: int
    icon: Optional[str]
    is_unlocked: bool

    class Config:
        from_attributes = True


class PlantedCropPublic(BaseModel):
    id: int
    plant_type: PlantTypePublic
    planted_at: datetime
    ready_at: datetime
    state: str

    class Config:
        from_attributes = True


class FarmPlotPublic(BaseModel):
    id: int
    slot_index: int
    unlocked: bool
    unlock_cost: int
    unlock_level_requirement: int
    unlock_farming_level_requirement: int
    crop: Optional[PlantedCropPublic]

    class Config:
        from_attributes = True


class FarmingToolPublic(BaseModel):
    level: int
    name: str
    bonus_percent: int


class FarmingStatsPublic(BaseModel):
    level: int
    xp: int
    xp_to_next_level: int
    energy: int
    max_energy: int
    tool: FarmingToolPublic
    starter_seed_charges: int


class FarmState(BaseModel):
    player_id: int
    stats: FarmingStatsPublic
    plots: List[FarmPlotPublic]
    available_plants: List[PlantTypePublic]
    wallet_gold: int


class PlantCropRequest(BaseModel):
    plot_id: int
    plant_type_id: int


class HarvestCropRequest(BaseModel):
    plot_id: int


class RefillFarmEnergyRequest(BaseModel):
    amount: int


class FarmActionResponse(BaseModel):
    state: FarmState
    message: str
