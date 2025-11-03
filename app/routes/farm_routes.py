from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.base import get_session
from app.schemas.farm import (
    FarmActionResponse,
    FarmState,
    HarvestCropRequest,
    PlantCropRequest,
    RefillFarmEnergyRequest,
)
from app.services.farm_service import FarmService
from app.utils.exceptions import GameLogicError
from app.auth.dependencies import require_player_access


router = APIRouter(prefix="/farm", tags=["farm"])


@router.get("/{player_id}", response_model=FarmState)
def get_farm_state(
    player_id: int,
    session: Session = Depends(get_session),
    _user=Depends(require_player_access),
) -> FarmState:
    service = FarmService(session)
    state = service.get_farm_state(player_id)
    public = service.build_public_state(state)
    return FarmState(**public)


@router.post("/{player_id}/plant", response_model=FarmActionResponse)
def plant_crop(
    player_id: int,
    payload: PlantCropRequest,
    session: Session = Depends(get_session),
    _user=Depends(require_player_access),
) -> FarmActionResponse:
    service = FarmService(session)
    try:
        state, message = service.plant_crop(player_id, payload.plot_id, payload.plant_type_id)
    except GameLogicError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    public = service.build_public_state(state)
    return FarmActionResponse(state=FarmState(**public), message=message)


@router.post("/{player_id}/harvest", response_model=FarmActionResponse)
def harvest_crop(
    player_id: int,
    payload: HarvestCropRequest,
    session: Session = Depends(get_session),
    _user=Depends(require_player_access),
) -> FarmActionResponse:
    service = FarmService(session)
    try:
        state, message = service.harvest_crop(player_id, payload.plot_id)
    except GameLogicError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    public = service.build_public_state(state)
    return FarmActionResponse(state=FarmState(**public), message=message)


@router.post("/{player_id}/plots/{plot_id}/unlock", response_model=FarmActionResponse)
def unlock_plot(
    player_id: int,
    plot_id: int,
    session: Session = Depends(get_session),
    _user=Depends(require_player_access),
) -> FarmActionResponse:
    service = FarmService(session)
    try:
        state, message = service.unlock_plot(player_id, plot_id)
    except GameLogicError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    public = service.build_public_state(state)
    return FarmActionResponse(state=FarmState(**public), message=message)


@router.post("/{player_id}/tool/upgrade", response_model=FarmActionResponse)
def upgrade_tool(
    player_id: int,
    session: Session = Depends(get_session),
    _user=Depends(require_player_access),
) -> FarmActionResponse:
    service = FarmService(session)
    try:
        state, message = service.upgrade_tool(player_id)
    except GameLogicError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    public = service.build_public_state(state)
    return FarmActionResponse(state=FarmState(**public), message=message)


@router.post("/{player_id}/energy/refill", response_model=FarmActionResponse)
def refill_farm_energy(
    player_id: int,
    payload: RefillFarmEnergyRequest,
    session: Session = Depends(get_session),
    _user=Depends(require_player_access),
) -> FarmActionResponse:
    service = FarmService(session)
    try:
        state, message = service.refill_energy(player_id, payload.amount)
    except GameLogicError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    public = service.build_public_state(state)
    return FarmActionResponse(state=FarmState(**public), message=message)
