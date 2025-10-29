from __future__ import annotations
from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_session
from app.schemas.quest import QuestChoiceRequest, QuestNodePublic
from app.services.quest_engine import QuestEngine
from app.utils.exceptions import (
    QuestChoiceInvalid,
    QuestNodeNotFound,
    QuestNotConfigured,
)


router = APIRouter(prefix="/player/{player_id}/quest", tags=["quest"])


@router.get("/current")
def get_current_quest_node(player_id: int, session: Session = Depends(get_session)) -> Dict[str, Any]:
    engine = QuestEngine(session)
    try:
        node = engine.get_current_node(player_id)
    except QuestNotConfigured as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    session.commit()

    return {"node": _serialize_node(node)}


@router.post("/choose")
def apply_quest_choice(
    player_id: int,
    payload: QuestChoiceRequest,
    session: Session = Depends(get_session),
) -> Dict[str, Any]:
    engine = QuestEngine(session)
    try:
        result_node, rewards = engine.apply_choice(player_id, payload.choice_id)
    except QuestChoiceInvalid as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except (QuestNodeNotFound, QuestNotConfigured) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    session.commit()

    return {
        "result": {
            "node": _serialize_node(result_node),
            "rewards": {
                "gained_xp": rewards.xp_gained,
                "gained_item_name": rewards.granted_item.name if rewards.granted_item else None,
                "level_up": rewards.level_up,
            },
            "message": rewards.message,
        }
    }


def _serialize_node(node: QuestNodePublic) -> Dict[str, Any]:
    node_data = node.model_dump()
    choices = node_data.get("choices") or []
    formatted_choices = []
    for choice in choices:
        formatted_choices.append(
            {
                "choice_id": choice["choice_id"],
                "label": choice["label"],
                "reward_preview": {
                    "xp": choice.get("reward_xp"),
                    "item_name": choice.get("reward_item_name"),
                },
            }
        )
    node_data["choices"] = formatted_choices
    return node_data
