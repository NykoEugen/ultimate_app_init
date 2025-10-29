from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_session
from app.schemas.quest import QuestChoiceRequest, QuestChoiceResponse, QuestNodePublic
from app.services.quest_engine import QuestEngine
from app.utils.exceptions import (
    QuestChoiceInvalid,
    QuestNodeNotFound,
    QuestNotConfigured,
)


router = APIRouter(prefix="/player/{player_id}/quest", tags=["quest"])


@router.get("/current", response_model=QuestNodePublic)
def get_current_quest_node(player_id: int, session: Session = Depends(get_session)) -> QuestNodePublic:
    engine = QuestEngine(session)
    try:
        node = engine.get_current_node(player_id)
    except QuestNotConfigured as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    session.commit()
    return node


@router.post("/choose", response_model=QuestChoiceResponse)
def apply_quest_choice(
    player_id: int,
    payload: QuestChoiceRequest,
    session: Session = Depends(get_session),
) -> QuestChoiceResponse:
    engine = QuestEngine(session)
    try:
        result_node, rewards = engine.apply_choice(player_id, payload.choice_id)
    except QuestChoiceInvalid as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except (QuestNodeNotFound, QuestNotConfigured) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    session.commit()

    return QuestChoiceResponse(
        result_node=result_node,
        gained_xp=rewards.xp_gained,
        gained_item=rewards.granted_item.name if rewards.granted_item else None,
    )
