from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.farm import PlantType
from app.db.models.inventory import InventoryItemCatalog
from app.db.models.quest import Quest, QuestChoice, QuestNode
from app.schemas.admin import (
    EquipmentItemCreate,
    EquipmentItemUpdate,
    PlantTypeCreate,
    PlantTypeUpdate,
    QuestCreateRequest,
    QuestUpdateRequest,
)


def _model_dump(model, *, exclude_unset: bool = False) -> dict:
    if hasattr(model, "model_dump"):
        return model.model_dump(exclude_unset=exclude_unset)
    return model.dict(exclude_unset=exclude_unset)


async def list_equipment_items(session: AsyncSession) -> List[InventoryItemCatalog]:
    statement = select(InventoryItemCatalog).order_by(InventoryItemCatalog.id)
    result = await session.execute(statement)
    return list(result.scalars().all())


async def create_equipment_item(
    session: AsyncSession,
    payload: EquipmentItemCreate,
) -> InventoryItemCatalog:
    item = InventoryItemCatalog(**_model_dump(payload))
    session.add(item)
    await session.flush()
    await session.refresh(item)
    return item


async def update_equipment_item(
    session: AsyncSession,
    item_id: int,
    payload: EquipmentItemUpdate,
) -> InventoryItemCatalog | None:
    item = await session.get(InventoryItemCatalog, item_id)
    if item is None:
        return None

    data = _model_dump(payload, exclude_unset=True)
    for field, value in data.items():
        setattr(item, field, value)

    await session.flush()
    await session.refresh(item)
    return item


async def list_plants(session: AsyncSession) -> List[PlantType]:
    statement = select(PlantType).order_by(PlantType.id)
    result = await session.execute(statement)
    return list(result.scalars().all())


async def create_plant_type(
    session: AsyncSession,
    payload: PlantTypeCreate,
) -> PlantType:
    plant = PlantType(**_model_dump(payload))
    session.add(plant)
    await session.flush()
    await session.refresh(plant)
    return plant


async def update_plant_type(
    session: AsyncSession,
    plant_id: int,
    payload: PlantTypeUpdate,
) -> PlantType | None:
    plant = await session.get(PlantType, plant_id)
    if plant is None:
        return None

    data = _model_dump(payload, exclude_unset=True)
    for field, value in data.items():
        setattr(plant, field, value)

    await session.flush()
    await session.refresh(plant)
    return plant


async def list_quests(session: AsyncSession) -> List[Quest]:
    statement = (
        select(Quest)
        .options(selectinload(Quest.nodes).selectinload(QuestNode.choices))
        .order_by(Quest.id)
    )
    result = await session.execute(statement)
    quests = result.scalars().unique().all()
    return list(quests)


async def create_quest(
    session: AsyncSession,
    payload: QuestCreateRequest,
) -> Quest:
    quest = Quest(
        **{
            "title": payload.title,
            "description": payload.description,
            "is_repeatable": payload.is_repeatable,
        }
    )
    session.add(quest)
    await session.flush()

    node_payload_map: Dict[str, Tuple[QuestNode, Iterable]] = {}
    for node_data in payload.nodes:
        node = QuestNode(
            id=node_data.id,
            quest_id=quest.id,
            title=node_data.title,
            body=node_data.body,
            is_start=node_data.is_start,
            is_final=node_data.is_final,
        )
        session.add(node)
        node_payload_map[node.id] = (node, node_data.choices)

    await session.flush()

    for node_id, (node, choices_data) in node_payload_map.items():
        for choice_data in choices_data:
            choice = QuestChoice(
                id=choice_data.id,
                node_id=node.id,
                label=choice_data.label,
                next_node_id=choice_data.next_node_id,
                reward_xp=choice_data.reward_xp,
                reward_item_id=choice_data.reward_item_id,
            )
            session.add(choice)

    await session.flush()

    query = (
        select(Quest)
        .options(selectinload(Quest.nodes).selectinload(QuestNode.choices))
        .where(Quest.id == quest.id)
    )
    result = await session.execute(query)
    created = result.scalar_one()
    return created


async def update_quest(
    session: AsyncSession,
    quest_id: int,
    payload: QuestUpdateRequest,
) -> Quest | None:
    query = (
        select(Quest)
        .options(selectinload(Quest.nodes).selectinload(QuestNode.choices))
        .where(Quest.id == quest_id)
    )
    result = await session.execute(query)
    quest = result.scalars().unique().one_or_none()
    if quest is None:
        return None

    quest.title = payload.title
    quest.description = payload.description
    quest.is_repeatable = payload.is_repeatable

    # Remove existing nodes and choices before inserting the new structure.
    await session.execute(
        delete(QuestChoice).where(
            QuestChoice.node_id.in_(select(QuestNode.id).where(QuestNode.quest_id == quest_id))
        )
    )
    await session.execute(delete(QuestNode).where(QuestNode.quest_id == quest_id))
    await session.flush()

    node_payload_map: Dict[str, Tuple[QuestNode, Iterable]] = {}
    for node_data in payload.nodes:
        node = QuestNode(
            id=node_data.id,
            quest_id=quest.id,
            title=node_data.title,
            body=node_data.body,
            is_start=node_data.is_start,
            is_final=node_data.is_final,
        )
        session.add(node)
        node_payload_map[node.id] = (node, node_data.choices)

    await session.flush()

    for node_id, (node, choices_data) in node_payload_map.items():
        for choice_data in choices_data:
            choice = QuestChoice(
                id=choice_data.id,
                node_id=node.id,
                label=choice_data.label,
                next_node_id=choice_data.next_node_id,
                reward_xp=choice_data.reward_xp,
                reward_item_id=choice_data.reward_item_id,
            )
            session.add(choice)

    await session.flush()

    refreshed = await session.execute(query)
    return refreshed.scalars().unique().one()
