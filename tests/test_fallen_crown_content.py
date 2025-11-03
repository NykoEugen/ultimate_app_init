from __future__ import annotations

from sqlalchemy import select

from app.content.fallen_crown import (
    FALLEN_CROWN_ACT_I_ID,
    FALLEN_CROWN_ACT_II_ID,
    FALLEN_CROWN_ACT_III_ID,
    FALLEN_CROWN_ACT_IV_ID,
    FALLEN_CROWN_ACT_V_ID,
    FALLEN_CROWN_START_NODE_ID,
    fallen_crown_blueprint,
)
from app.constants.onboarding import ONBOARDING_NODE_FINISH, ONBOARDING_QUEST_ID
from app.db.models.player import Player
from app.db.models.quest import Quest, QuestChoice, QuestNode, QuestProgress
from app.services.quest_content_service import QuestContentService


def test_fallen_crown_blueprint_structure():
    specs = fallen_crown_blueprint()
    assert len(specs) == 5

    expected_ids = [
        FALLEN_CROWN_ACT_I_ID,
        FALLEN_CROWN_ACT_II_ID,
        FALLEN_CROWN_ACT_III_ID,
        FALLEN_CROWN_ACT_IV_ID,
        FALLEN_CROWN_ACT_V_ID,
    ]
    for spec, quest_id in zip(specs, expected_ids):
        assert spec.id == quest_id
        assert len(spec.nodes) == 10
        assert spec.nodes[0].is_start is True
        assert spec.nodes[-1].is_final is True
        for node in spec.nodes:
            assert node.id.startswith("fallen_crown_a")
            for choice in node.choices:
                assert choice.label
                assert choice.reward_xp >= 30


def test_fallen_crown_content_service_is_idempotent(db_session):
    specs = fallen_crown_blueprint()
    expected_nodes = sum(len(spec.nodes) for spec in specs)
    expected_choices = sum(len(node.choices) for spec in specs for node in spec.nodes)

    service = QuestContentService(db_session)
    service.ensure_fallen_crown_saga()
    db_session.commit()

    first_snapshot = _snapshot_counts(db_session)
    assert first_snapshot[0] == len(specs)
    assert first_snapshot[1] == expected_nodes
    assert first_snapshot[2] == expected_choices

    service.ensure_fallen_crown_saga()
    db_session.commit()

    second_snapshot = _snapshot_counts(db_session)
    assert first_snapshot == second_snapshot


def test_migration_moves_completed_onboarding_players(db_session):
    player = Player(
        id=77,
        username="Archivist",
        level=5,
        xp=150,
        energy=30,
        max_energy=30,
        gold=100,
        onboarding_completed=True,
    )
    progress = QuestProgress(
        player_id=player.id,
        quest_id=ONBOARDING_QUEST_ID,
        current_node_id=ONBOARDING_NODE_FINISH,
    )
    db_session.add_all([player, progress])
    db_session.commit()

    service = QuestContentService(db_session)
    service.ensure_fallen_crown_saga()
    db_session.commit()

    updated_progress = db_session.get(QuestProgress, player.id)
    assert updated_progress is not None
    assert updated_progress.quest_id == FALLEN_CROWN_ACT_I_ID
    assert updated_progress.current_node_id == FALLEN_CROWN_START_NODE_ID


def _snapshot_counts(session):
    quest_ids = [
        FALLEN_CROWN_ACT_I_ID,
        FALLEN_CROWN_ACT_II_ID,
        FALLEN_CROWN_ACT_III_ID,
        FALLEN_CROWN_ACT_IV_ID,
        FALLEN_CROWN_ACT_V_ID,
    ]

    quests = session.execute(
        select(Quest).where(Quest.id.in_(quest_ids))
    ).scalars().unique().all()

    nodes = session.execute(
        select(QuestNode).where(QuestNode.quest_id.in_(quest_ids))
    ).scalars().unique().all()

    choices = session.execute(
        select(QuestChoice).where(QuestChoice.node_id.like("fallen_crown%"))
    ).scalars().unique().all()

    quests_count = len(quests)
    nodes_count = len(nodes)
    choices_count = len(choices)

    return quests_count, nodes_count, choices_count
