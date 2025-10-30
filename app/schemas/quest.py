from pydantic import AliasChoices, BaseModel, ConfigDict, Field
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


class QuestChoiceRequest(BaseModel):
    choice_id: str = Field(validation_alias=AliasChoices("choice_id", "choiceId"))

    model_config = ConfigDict(populate_by_name=True)


class QuestChoiceResponse(BaseModel):
    result_node: QuestNodePublic
    gained_xp: int
    gained_item: Optional[str] = None
