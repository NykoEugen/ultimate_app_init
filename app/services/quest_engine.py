from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models.inventory import InventoryItemCatalog
from app.db.models.player import Player
from app.db.models.quest import QuestChoice, QuestNode, QuestProgress
from app.schemas.quest import QuestChoicePublic, QuestNodePublic
from app.services.inventory_service import GrantedItem, InventoryService
from app.services.progression_service import ProgressionService
from app.utils.exceptions import (
    QuestChoiceInvalid,
    QuestNodeNotFound,
    QuestNotConfigured,
)


@dataclass
class AppliedRewards:
    xp_gained: int
    levels_gained: int
    new_level: int
    xp_into_current_level: int
    xp_needed_for_next_level: int
    granted_item: Optional[GrantedItem]
    level_up: bool
    message: str


class QuestEngine:
    """Core quest progression logic: node traversal, choice handling and rewards."""

    def __init__(
        self,
        session: Session,
        *,
        progression_service: Optional[ProgressionService] = None,
        inventory_service: Optional[InventoryService] = None,
    ) -> None:
        self._session = session
        self._progression = progression_service or ProgressionService(session)
        self._inventory = inventory_service or InventoryService(session)

    def get_current_node(self, player_id: int) -> QuestNodePublic:
        player = self._session.get(Player, player_id)
        if player is None:
            raise QuestNotConfigured(f"Player {player_id} does not exist")

        progress = self._session.get(QuestProgress, player_id)

        if progress is None:
            node = self._get_default_start_node()
            if node is None:
                raise QuestNotConfigured("No quest start node configured")
            progress = QuestProgress(
                player_id=player.id,
                quest_id=node.quest_id,
                current_node_id=node.id,
            )
            self._session.add(progress)
            self._session.flush()
        else:
            node = self._load_node(progress.current_node_id)

        return self._to_public_node(node)

    def apply_choice(self, player_id: int, choice_id: str) -> Tuple[QuestNodePublic, AppliedRewards]:
        player = self._session.get(Player, player_id)
        if player is None:
            raise QuestChoiceInvalid(f"Player {player_id} does not exist")

        progress = self._session.get(QuestProgress, player_id)
        if progress is None:
            raise QuestChoiceInvalid("Quest progress is not initialised for this player")

        choice = self._load_choice(choice_id)
        if choice is None:
            raise QuestChoiceInvalid(f"Choice {choice_id} does not exist")

        if choice.node_id != progress.current_node_id:
            raise QuestChoiceInvalid("Choice does not belong to the current quest node")

        xp_result = self._progression.give_xp(player, choice.reward_xp)

        granted_item: Optional[GrantedItem] = None
        if choice.reward_item_id:
            granted_item = self._inventory.grant_catalog_item(player, choice.reward_item_id)

        next_node: QuestNode
        if choice.next_node_id:
            next_node = self._load_node(choice.next_node_id)
            progress.current_node_id = next_node.id
            progress.quest_id = next_node.quest_id
        else:
            next_node = self._load_node(progress.current_node_id)

        self._session.add_all([progress, player])
        self._session.flush()

        level_up = xp_result.levels_gained > 0
        reward_message = getattr(choice, "result_message", None)
        if not reward_message:
            reward_message = f"Ти зробив вибір: {choice.label}."

        rewards = AppliedRewards(
            xp_gained=choice.reward_xp,
            levels_gained=xp_result.levels_gained,
            new_level=xp_result.new_level,
            xp_into_current_level=xp_result.xp_into_current_level,
            xp_needed_for_next_level=xp_result.xp_needed_for_next_level,
            granted_item=granted_item,
            level_up=level_up,
            message=reward_message,
        )

        return self._to_public_node(next_node), rewards

    def get_current_node_public(self, player_id: int) -> QuestNodePublic:
        """Public helper mirroring get_current_node for read-only access."""
        return self.get_current_node(player_id)

    def _get_default_start_node(self) -> Optional[QuestNode]:
        stmt = (
            select(QuestNode)
            .where(QuestNode.is_start.is_(True))
            .options(selectinload(QuestNode.choices))
            .order_by(QuestNode.quest_id)
            .limit(1)
        )
        result = self._session.execute(stmt)
        return result.scalars().first()

    def _load_node(self, node_id: str) -> QuestNode:
        stmt = (
            select(QuestNode)
            .where(QuestNode.id == node_id)
            .options(selectinload(QuestNode.choices))
        )
        node = self._session.execute(stmt).scalars().first()
        if node is None:
            raise QuestNodeNotFound(f"Quest node {node_id} does not exist")
        return node

    def _load_choice(self, choice_id: str) -> Optional[QuestChoice]:
        stmt = select(QuestChoice).where(QuestChoice.id == choice_id)
        return self._session.execute(stmt).scalars().first()

    def _to_public_node(self, node: QuestNode) -> QuestNodePublic:
        reward_item_names = self._fetch_reward_item_names(node)

        choices_public = [
            QuestChoicePublic(
                choice_id=choice.id,
                label=choice.label,
                reward_xp=choice.reward_xp,
                reward_item_name=reward_item_names.get(choice.reward_item_id),
            )
            for choice in node.choices
        ]

        return QuestNodePublic(
            node_id=node.id,
            title=node.title,
            body=node.body,
            is_final=node.is_final,
            choices=choices_public,
        )

    def _fetch_reward_item_names(self, node: QuestNode) -> dict[int, str]:
        reward_ids = {choice.reward_item_id for choice in node.choices if choice.reward_item_id}
        if not reward_ids:
            return {}

        stmt = (
            select(InventoryItemCatalog.id, InventoryItemCatalog.name)
            .where(InventoryItemCatalog.id.in_(reward_ids))
        )
        result = self._session.execute(stmt)
        return {row.id: row.name for row in result}
