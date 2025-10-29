from pydantic import BaseModel
from typing import List, Optional

class QuestChoicePublic(BaseModel):
    choice_id: str
    label: str
    reward_xp: int
    reward_item_name: Optional[str] = None

class QuestNodePublic(BaseModel):
    node_id: str
    title: str
    body: str
    is_final: bool
    choices: List[QuestChoicePublic]
