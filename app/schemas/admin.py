from __future__ import annotations

from typing import Any, Dict, List, Optional

try:  # Pydantic v2
    from pydantic import BaseModel, ConfigDict, Field
except ImportError:  # pragma: no cover - fallback to v1
    from pydantic import BaseModel, Field  # type: ignore
    ConfigDict = None  # type: ignore


class _ORMModel(BaseModel):
    """Shared configuration to support both Pydantic v1 and v2."""

    if ConfigDict:
        model_config = ConfigDict(from_attributes=True)  # type: ignore[misc]
    else:  # pragma: no branch

        class Config:
            orm_mode = True


class EquipmentItemCreate(BaseModel):
    name: str
    slot: str = "misc"
    rarity: str = "common"
    cosmetic: bool = False
    description: Optional[str] = None
    icon: Optional[str] = None


class EquipmentItemPublic(_ORMModel):
    id: int
    name: str
    slot: str
    rarity: str
    cosmetic: bool
    description: Optional[str]
    icon: Optional[str]


class EquipmentItemUpdate(BaseModel):
    name: Optional[str] = None
    slot: Optional[str] = None
    rarity: Optional[str] = None
    cosmetic: Optional[bool] = None
    description: Optional[str] = None
    icon: Optional[str] = None


class PlantTypeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    growth_seconds: int = Field(default=600, ge=1)
    xp_reward: int = Field(default=15, ge=0)
    energy_cost: int = Field(default=2, ge=0)
    seed_cost: int = Field(default=0, ge=0)
    sell_price: int = Field(default=0, ge=0)
    unlock_level: int = Field(default=1, ge=1)
    unlock_farming_level: int = Field(default=1, ge=1)
    icon: Optional[str] = None


class PlantTypePublic(_ORMModel):
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


class PlantTypeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    growth_seconds: Optional[int] = Field(default=None, ge=1)
    xp_reward: Optional[int] = Field(default=None, ge=0)
    energy_cost: Optional[int] = Field(default=None, ge=0)
    seed_cost: Optional[int] = Field(default=None, ge=0)
    sell_price: Optional[int] = Field(default=None, ge=0)
    unlock_level: Optional[int] = Field(default=None, ge=1)
    unlock_farming_level: Optional[int] = Field(default=None, ge=1)
    icon: Optional[str] = None


class QuestChoiceCreate(BaseModel):
    id: str
    label: str
    next_node_id: Optional[str] = None
    reward_xp: int = Field(default=0, ge=0)
    reward_item_id: Optional[int] = None


class QuestNodeCreate(BaseModel):
    id: str
    title: str
    body: str
    is_start: bool = False
    is_final: bool = False
    choices: List[QuestChoiceCreate] = Field(default_factory=list)


class QuestCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    is_repeatable: bool = False
    nodes: List[QuestNodeCreate] = Field(default_factory=list)


class QuestUpdateRequest(QuestCreateRequest):
    """Full replacement payload for updating existing quests."""


class QuestChoicePublic(_ORMModel):
    id: str
    node_id: str
    label: str
    next_node_id: Optional[str]
    reward_xp: int
    reward_item_id: Optional[int]


class QuestNodePublic(_ORMModel):
    id: str
    quest_id: int
    title: str
    body: str
    is_start: bool
    is_final: bool
    choices: List[QuestChoicePublic]


class QuestPublic(_ORMModel):
    id: int
    title: str
    description: Optional[str]
    is_repeatable: bool
    nodes: List[QuestNodePublic]


AdminResponse = Dict[str, Any]


__all__ = [
    "EquipmentItemCreate",
    "EquipmentItemPublic",
    "EquipmentItemUpdate",
    "PlantTypeCreate",
    "PlantTypePublic",
    "PlantTypeUpdate",
    "QuestChoiceCreate",
    "QuestNodeCreate",
    "QuestCreateRequest",
    "QuestUpdateRequest",
    "QuestChoicePublic",
    "QuestNodePublic",
    "QuestPublic",
    "AdminResponse",
]
