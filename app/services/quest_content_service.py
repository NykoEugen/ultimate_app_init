from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.content.fallen_crown import (
    FALLEN_CROWN_START_NODE_ID,
    fallen_crown_blueprint,
)
from app.constants.onboarding import ONBOARDING_QUEST_ID
from app.db.models.player import Player
from app.db.models.quest import QuestNode, QuestProgress
from app.services.quest_content_builder import QuestContentBuilder, QuestSpec
from app.utils.exceptions import QuestNotConfigured


class QuestContentService:
    """High-level orchestration for seeding narrative quest content."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._builder = QuestContentBuilder(session)

    def ensure_fallen_crown_saga(self) -> None:
        """Ensure the Saga of the Fallen Crown quests exist and are up to date."""
        quest_specs = fallen_crown_blueprint()
        self._sync_specs(quest_specs)
        self._migrate_players_to_saga()

    def ensure_fallen_crown_start_node(self) -> QuestNode:
        """Ensure saga exists and return the first playable node."""
        self.ensure_fallen_crown_saga()
        node = self._session.get(QuestNode, FALLEN_CROWN_START_NODE_ID)
        if node is None:
            raise QuestNotConfigured("Fallen Crown quest content is not configured correctly.")
        return node

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _sync_specs(self, specs: list[QuestSpec]) -> None:
        for spec in specs:
            self._builder.sync_quest(spec)
        self._session.flush()

    def _migrate_players_to_saga(self) -> None:
        saga_node = self._session.get(QuestNode, FALLEN_CROWN_START_NODE_ID)
        if saga_node is None:
            raise QuestNotConfigured("Fallen Crown start node is missing")

        stmt = (
            select(QuestProgress)
            .join(Player, Player.id == QuestProgress.player_id)
            .where(Player.onboarding_completed.is_(True))
            .where(QuestProgress.quest_id == ONBOARDING_QUEST_ID)
        )
        progresses = self._session.execute(stmt).scalars().all()

        for progress in progresses:
            progress.quest_id = saga_node.quest_id
            progress.current_node_id = saga_node.id

        players_stmt = (
            select(Player)
            .where(Player.onboarding_completed.is_(True))
            .where(Player.id.notin_(select(QuestProgress.player_id)))
        )
        players_without_progress = self._session.execute(players_stmt).scalars().all()
        for player in players_without_progress:
            progress = QuestProgress(
                player_id=player.id,
                quest_id=saga_node.quest_id,
                current_node_id=saga_node.id,
            )
            self._session.add(progress)

        self._session.flush()
