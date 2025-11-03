from __future__ import annotations

from app.content.fallen_crown import FALLEN_CROWN_ACT_I_ID, FALLEN_CROWN_START_NODE_ID
from app.constants.onboarding import ONBOARDING_QUEST_ID
from app.db.models.inventory import InventoryItemCatalog
from app.db.models.player import Player
from app.db.models.quest import Quest, QuestChoice, QuestNode, QuestProgress
from app.services.quest_engine import QuestEngine


def _setup_quest_graph(session):
    quest = Quest(id=1, title="Пригоди у селі", description="Початок мандрівки")
    node_start = QuestNode(
        id="village_square",
        quest=quest,
        title="Площа Села",
        body="Перед тобою зібралися мешканці у відчаї.",
        is_start=True,
        is_final=False,
    )
    node_after = QuestNode(
        id="after_help",
        quest=quest,
        title="Надія у їхніх очах",
        body="Селяни дякують тобі за допомогу.",
        is_start=False,
        is_final=True,
    )

    catalog_item = InventoryItemCatalog(
        id=1,
        name="Кинджал Мандрівника",
        slot="weapon",
        rarity="rare",
        cosmetic=False,
        icon="dagger_traveler",
    )

    choice = QuestChoice(
        id="help_villagers",
        node=node_start,
        label="Допомогти селянам",
        next_node_id="after_help",
        reward_xp=25,
        reward_item_id=catalog_item.id,
    )

    session.add_all([quest, node_start, node_after, catalog_item, choice])


def test_apply_choice_returns_rewards_and_next_node(db_session):
    player = Player(id=10, username="Hero", level=1, xp=90, energy=10, max_energy=20, gold=0)
    db_session.add(player)
    _setup_quest_graph(db_session)
    db_session.commit()

    engine = QuestEngine(db_session)

    # initialise progress
    current_node = engine.get_current_node(player.id)
    assert current_node.node_id == "village_square"

    result_node, rewards = engine.apply_choice(player.id, "help_villagers")

    assert result_node.node_id == "after_help"
    assert rewards.xp_gained == 25
    assert rewards.level_up is True
    assert rewards.granted_item is not None
    assert rewards.granted_item.name == "Кинджал Мандрівника"
    assert "Ти зробив вибір" in rewards.message

    progress = db_session.query(QuestProgress).filter_by(player_id=player.id).first()
    assert progress is not None
    assert progress.current_node_id == "after_help"


def _setup_onboarding_quest(session):
    quest = Quest(
        id=ONBOARDING_QUEST_ID,
        title="Пробудження фермера",
        description="Навчальний квест",
        is_repeatable=False,
    )
    intro_node = QuestNode(
        id="onboarding_test_intro",
        quest=quest,
        title="Початок",
        body="Перший крок.",
        is_start=True,
        is_final=False,
    )
    finish_node = QuestNode(
        id="onboarding_test_finish",
        quest=quest,
        title="Завершення",
        body="Готовий до пригод.",
        is_start=False,
        is_final=True,
    )
    finish_choice = QuestChoice(
        id="onboarding_test_finish_choice",
        node=intro_node,
        label="Завершити навчання",
        next_node_id="onboarding_test_finish",
        reward_xp=10,
    )
    session.add_all([quest, intro_node, finish_node, finish_choice])


def test_onboarding_completion_advances_to_fallen_crown(db_session):
    player = Player(
        id=25,
        username="Learner",
        level=1,
        xp=0,
        energy=10,
        max_energy=20,
        gold=0,
        onboarding_completed=False,
    )
    db_session.add(player)
    _setup_onboarding_quest(db_session)
    db_session.commit()

    engine = QuestEngine(db_session)

    current_node = engine.get_current_node(player.id)
    assert current_node.node_id == "onboarding_test_intro"

    next_node, _ = engine.apply_choice(player.id, "onboarding_test_finish_choice")
    assert next_node.node_id == FALLEN_CROWN_START_NODE_ID

    progress = db_session.get(QuestProgress, player.id)
    assert progress is not None
    assert progress.current_node_id == FALLEN_CROWN_START_NODE_ID
    assert progress.quest_id == FALLEN_CROWN_ACT_I_ID

    updated_player = db_session.get(Player, player.id)
    assert updated_player is not None
    assert updated_player.onboarding_completed is True
