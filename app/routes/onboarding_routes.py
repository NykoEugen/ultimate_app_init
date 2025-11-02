from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_session
from app.schemas.onboarding import OnboardingState
from app.services.onboarding_service import OnboardingService
from app.utils.exceptions import QuestNotConfigured


router = APIRouter(prefix="/player/{player_id}/onboarding", tags=["onboarding"])


@router.get("", response_model=OnboardingState)
def get_onboarding_state(player_id: int, session: Session = Depends(get_session)) -> OnboardingState:
    service = OnboardingService(session)
    try:
        return service.get_state(player_id)
    except QuestNotConfigured as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/complete", response_model=OnboardingState)
def complete_onboarding(player_id: int, session: Session = Depends(get_session)) -> OnboardingState:
    service = OnboardingService(session)
    try:
        return service.mark_completed(player_id)
    except QuestNotConfigured as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=400, detail=str(exc)) from exc
