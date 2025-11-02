from __future__ import annotations

from typing import List, Set

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.admin import (
    EquipmentItemCreate,
    EquipmentItemPublic,
    EquipmentItemUpdate,
    PlantTypeCreate,
    PlantTypePublic,
    PlantTypeUpdate,
    QuestCreateRequest,
    QuestPublic,
    QuestUpdateRequest,
)
from app.services.admin_service import (
    create_equipment_item,
    create_plant_type,
    create_quest,
    list_equipment_items,
    list_plants,
    list_quests,
    update_equipment_item,
    update_plant_type,
    update_quest,
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/equipment", response_model=List[EquipmentItemPublic])
async def get_equipment_catalog(db: AsyncSession = Depends(get_db)):
    return await list_equipment_items(db)


@router.post(
    "/equipment",
    response_model=EquipmentItemPublic,
    status_code=status.HTTP_201_CREATED,
)
async def add_equipment_item(
    payload: EquipmentItemCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        item = await create_equipment_item(db, payload)
        await db.commit()
        return item
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Не вдалося створити предмет еквіпу. Перевірте унікальність назви або ідентифікатора.") from exc


@router.put("/equipment/{item_id}", response_model=EquipmentItemPublic)
async def edit_equipment_item(
    item_id: int,
    payload: EquipmentItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        item = await update_equipment_item(db, item_id, payload)
        if item is None:
            raise HTTPException(status_code=404, detail="Предмет не знайдено.")
        await db.commit()
        return item
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Не вдалося оновити предмет. Перевірте унікальність назви або ідентифікатора.") from exc


@router.get("/plants", response_model=List[PlantTypePublic])
async def get_plants(db: AsyncSession = Depends(get_db)):
    return await list_plants(db)


@router.post(
    "/plants",
    response_model=PlantTypePublic,
    status_code=status.HTTP_201_CREATED,
)
async def add_plant(
    payload: PlantTypeCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        plant = await create_plant_type(db, payload)
        await db.commit()
        return plant
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Не вдалося створити рослину. Ім'я має бути унікальним.") from exc


@router.put("/plants/{plant_id}", response_model=PlantTypePublic)
async def edit_plant(
    plant_id: int,
    payload: PlantTypeUpdate,
    db: AsyncSession = Depends(get_db),
):
    try:
        plant = await update_plant_type(db, plant_id, payload)
        if plant is None:
            raise HTTPException(status_code=404, detail="Рослину не знайдено.")
        await db.commit()
        return plant
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Не вдалося оновити рослину. Ім'я має бути унікальним.") from exc


def _validate_quest_payload(payload: QuestCreateRequest) -> None:
    if not payload.nodes:
        raise HTTPException(status_code=400, detail="Квест має містити принаймні один вузол.")

    node_ids = [node.id for node in payload.nodes]
    if len(node_ids) != len(set(node_ids)):
        raise HTTPException(status_code=400, detail="ID вузлів мають бути унікальними.")

    start_nodes = [node for node in payload.nodes if node.is_start]
    if len(start_nodes) != 1:
        raise HTTPException(status_code=400, detail="Має бути рівно один стартовий вузол.")

    if not any(node.is_final for node in payload.nodes):
        raise HTTPException(status_code=400, detail="Має бути хоча б один фінальний вузол.")

    node_id_set: Set[str] = set(node_ids)
    for node in payload.nodes:
        choice_ids = [choice.id for choice in node.choices]
        if len(choice_ids) != len(set(choice_ids)):
            raise HTTPException(status_code=400, detail=f"ID варіантів вибору мають бути унікальними у вузлі {node.id}.")

        for choice in node.choices:
            if choice.next_node_id and choice.next_node_id not in node_id_set:
                raise HTTPException(
                    status_code=400,
                    detail=f"Варіант {choice.id} посилається на неіснуючий вузол {choice.next_node_id}.",
                )


@router.get("/quests", response_model=List[QuestPublic])
async def get_quests(db: AsyncSession = Depends(get_db)):
    return await list_quests(db)


@router.post("/quests", response_model=QuestPublic, status_code=status.HTTP_201_CREATED)
async def add_quest(
    payload: QuestCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    _validate_quest_payload(payload)
    try:
        quest = await create_quest(db, payload)
        await db.commit()
        return quest
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Не вдалося створити квест. Перевірте унікальність ID.") from exc


@router.put("/quests/{quest_id}", response_model=QuestPublic)
async def edit_quest(
    quest_id: int,
    payload: QuestUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    _validate_quest_payload(payload)
    try:
        quest = await update_quest(db, quest_id, payload)
        if quest is None:
            raise HTTPException(status_code=404, detail="Квест не знайдено.")
        await db.commit()
        return quest
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Не вдалося оновити квест. Перевірте унікальність ID вузлів або виборів.") from exc
