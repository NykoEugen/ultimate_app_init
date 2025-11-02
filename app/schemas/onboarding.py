from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel

from app.schemas.quest import QuestNodePublic


class OnboardingStep(BaseModel):
    title: str
    body: str


class OnboardingState(BaseModel):
    player_id: int
    completed: bool
    steps: List[OnboardingStep]
    starter_seed_charges: int
    current_node: Optional[QuestNodePublic] = None
