from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Sequence

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from app.db.models.quest import Quest, QuestChoice, QuestNode


@dataclass(frozen=True, slots=True)
class QuestChoiceSpec:
    """Declarative definition of a quest choice within a quest node."""

    id: str
    label: str
    reward_xp: int = 0
    next_node_id: Optional[str] = None
    reward_item_id: Optional[int] = None


@dataclass(frozen=True, slots=True)
class QuestNodeSpec:
    """Declarative definition of a quest node."""

    id: str
    title: str
    body: str
    choices: Sequence[QuestChoiceSpec] = field(default_factory=tuple)
    is_start: bool = False
    is_final: bool = False


@dataclass(frozen=True, slots=True)
class QuestSpec:
    """Declarative definition of a quest with its nodes and choices."""

    id: Optional[int]
    title: str
    description: str
    nodes: Sequence[QuestNodeSpec]
    is_repeatable: bool = False


class QuestContentBuilder:
    """Utility responsible for idempotent quest content synchronisation."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def sync_quest(self, spec: QuestSpec) -> Quest:
        """Create or update quest content so that it matches ``spec``."""

        quest = self._load_or_create_quest(spec)
        self._sync_nodes(quest, spec.nodes)

        quest.title = spec.title
        quest.description = spec.description
        quest.is_repeatable = spec.is_repeatable

        self._session.flush()
        return quest

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_or_create_quest(self, spec: QuestSpec) -> Quest:
        quest: Optional[Quest] = None
        if spec.id is not None:
            quest = self._session.get(Quest, spec.id)

        if quest is None:
            stmt = (
                select(Quest)
                .where(Quest.title == spec.title)
                .options(selectinload(Quest.nodes).selectinload(QuestNode.choices))
            )
            quest = self._session.execute(stmt).scalars().first()

        if quest is None:
            quest = Quest(
                id=spec.id,
                title=spec.title,
                description=spec.description,
                is_repeatable=spec.is_repeatable,
            )
            self._session.add(quest)
            self._session.flush()
        return quest

    def _sync_nodes(self, quest: Quest, nodes_spec: Sequence[QuestNodeSpec]) -> None:
        existing_nodes = {
            node.id: node
            for node in self._session.execute(
                select(QuestNode)
                .where(QuestNode.quest_id == quest.id)
                .options(selectinload(QuestNode.choices))
            ).scalars()
        }

        desired_node_ids = {node_spec.id for node_spec in nodes_spec}
        nodes_to_remove = [node for node_id, node in existing_nodes.items() if node_id not in desired_node_ids]

        for node in nodes_to_remove:
            self._session.execute(delete(QuestChoice).where(QuestChoice.node_id == node.id))
            self._session.delete(node)

        for node_spec in nodes_spec:
            node = existing_nodes.get(node_spec.id)
            if node is None:
                node = QuestNode(
                    id=node_spec.id,
                    quest_id=quest.id,
                    title=node_spec.title,
                    body=node_spec.body,
                    is_start=node_spec.is_start,
                    is_final=node_spec.is_final,
                )
                self._session.add(node)
                self._session.flush()
            else:
                node.title = node_spec.title
                node.body = node_spec.body
                node.is_start = node_spec.is_start
                node.is_final = node_spec.is_final

            self._sync_choices(node, node_spec.choices)

    def _sync_choices(self, node: QuestNode, choices_spec: Sequence[QuestChoiceSpec]) -> None:
        existing_choices = {
            choice.id: choice
            for choice in self._session.execute(
                select(QuestChoice).where(QuestChoice.node_id == node.id)
            ).scalars()
        }

        desired_choice_ids = {choice_spec.id for choice_spec in choices_spec}
        choices_to_remove = [choice for choice_id, choice in existing_choices.items() if choice_id not in desired_choice_ids]
        for choice in choices_to_remove:
            self._session.delete(choice)

        for choice_spec in choices_spec:
            choice = existing_choices.get(choice_spec.id)
            if choice is None:
                choice = QuestChoice(
                    id=choice_spec.id,
                    node_id=node.id,
                    label=choice_spec.label,
                    next_node_id=choice_spec.next_node_id,
                    reward_xp=choice_spec.reward_xp,
                    reward_item_id=choice_spec.reward_item_id,
                )
                self._session.add(choice)
            else:
                choice.label = choice_spec.label
                choice.next_node_id = choice_spec.next_node_id
                choice.reward_xp = choice_spec.reward_xp
                choice.reward_item_id = choice_spec.reward_item_id

        self._session.flush()
