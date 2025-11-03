from __future__ import annotations

import logging
from typing import List, Set

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.quest_content_service import QuestContentService
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
from app.auth.dependencies import require_admin
from app.db.models.quest import QuestNode, QuestChoice

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])

logger = logging.getLogger(__name__)


async def _ensure_fallen_crown(db: AsyncSession) -> None:
    def _sync(session):
        QuestContentService(session).ensure_fallen_crown_saga()

    await db.run_sync(_sync)


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


async def _validate_quest_payload(
    payload: QuestCreateRequest,
    db: AsyncSession,
    *,
    current_quest_id: int | None = None,
) -> None:
    if not payload.nodes:
        raise HTTPException(status_code=400, detail="Квест має містити принаймні один вузол.")

    node_ids = [node.id for node in payload.nodes]
    duplicate_node_ids = [node_id for node_id in set(node_ids) if node_ids.count(node_id) > 1]
    if duplicate_node_ids:
        logger.warning("Duplicate quest node IDs detected: %s", duplicate_node_ids)
        raise HTTPException(
            status_code=400,
            detail=f"ID вузлів мають бути унікальними. Дублікати: {', '.join(duplicate_node_ids)}.",
        )

    start_nodes = [node for node in payload.nodes if node.is_start]
    if len(start_nodes) != 1:
        raise HTTPException(status_code=400, detail="Має бути рівно один стартовий вузол.")

    if not any(node.is_final for node in payload.nodes):
        raise HTTPException(status_code=400, detail="Має бути хоча б один фінальний вузол.")

    node_id_set: Set[str] = set(node_ids)
    for node in payload.nodes:
        choice_ids = [choice.id for choice in node.choices]
        duplicate_choice_ids = [choice_id for choice_id in set(choice_ids) if choice_ids.count(choice_id) > 1]
        if duplicate_choice_ids:
            logger.warning("Duplicate choice IDs in node %s: %s", node.id, duplicate_choice_ids)
            raise HTTPException(
                status_code=400,
                detail=f"ID варіантів вибору мають бути унікальними у вузлі {node.id}. "
                f"Дублікати: {', '.join(duplicate_choice_ids)}.",
            )

        for choice in node.choices:
            if not choice.next_node_id:
                continue
            if choice.next_node_id in node_id_set:
                continue

            result = await db.execute(select(QuestNode.id).where(QuestNode.id == choice.next_node_id))
            node_exists = result.scalar_one_or_none()
            if node_exists is None:
                await _ensure_fallen_crown(db)
                result = await db.execute(select(QuestNode.id).where(QuestNode.id == choice.next_node_id))
                node_exists = result.scalar_one_or_none()
            if node_exists is None:
                logger.warning(
                    "Choice %s references missing node %s (quest payload title=%s)",
                    choice.id,
                    choice.next_node_id,
                    payload.title,
                )
                raise HTTPException(
                    status_code=400,
                    detail=f"Варіант {choice.id} посилається на неіснуючий вузол {choice.next_node_id}.",
                )

    # Check for global collisions with other quests
    all_choice_ids = {choice.id for node in payload.nodes for choice in node.choices}
    if all_choice_ids:
        stmt = (
            select(QuestChoice.id, QuestNode.quest_id)
            .join(QuestNode, QuestNode.id == QuestChoice.node_id)
            .where(QuestChoice.id.in_(all_choice_ids))
        )
        if current_quest_id is not None:
            stmt = stmt.where(QuestNode.quest_id != current_quest_id)
        conflicts = await db.execute(stmt)
        conflict_rows = conflicts.all()
        if conflict_rows:
            conflict_ids = [row.id for row in conflict_rows]
            logger.warning(
                "Quest payload has choice ID collisions with existing quests: ids=%s, current_quest_id=%s",
                conflict_ids,
                current_quest_id,
            )
            raise HTTPException(
                status_code=400,
                detail=(
                    "ID варіантів мають бути унікальними між усіма квестами. "
                    f"Конфліктні ID: {', '.join(conflict_ids)}."
                ),
            )


@router.get("/quests", response_model=List[QuestPublic])
async def get_quests(db: AsyncSession = Depends(get_db)):
    await _ensure_fallen_crown(db)
    return await list_quests(db)


@router.post("/quests", response_model=QuestPublic, status_code=status.HTTP_201_CREATED)
async def add_quest(
    payload: QuestCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    await _ensure_fallen_crown(db)
    await _validate_quest_payload(payload, db, current_quest_id=None)
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
    await _ensure_fallen_crown(db)
    await _validate_quest_payload(payload, db, current_quest_id=quest_id)
    try:
        quest = await update_quest(db, quest_id, payload)
        if quest is None:
            raise HTTPException(status_code=404, detail="Квест не знайдено.")
        await db.commit()
        return quest
    except IntegrityError as exc:
        await db.rollback()
        logger.exception("Failed to update quest %s due to integrity error", quest_id)
        raise HTTPException(status_code=400, detail="Не вдалося оновити квест. Перевірте унікальність ID вузлів або виборів.") from exc
