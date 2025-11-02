from __future__ import annotations

from typing import Dict, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.constants.onboarding import (
    ONBOARDING_CHOICE_INTRO_NEXT,
    ONBOARDING_CHOICE_MECHANICS_FINISH,
    ONBOARDING_NODE_FINISH,
    ONBOARDING_NODE_INTRO,
    ONBOARDING_NODE_MECHANICS,
    ONBOARDING_QUEST_ID,
)
from app.db.models.quest import Quest, QuestChoice, QuestNode, QuestProgress
from app.db.models.player import Player
from app.schemas.onboarding import OnboardingState
from app.schemas.quest import QuestNodePublic
from app.services.farm_service import FarmService
from app.services.quest_engine import QuestEngine
from app.utils.exceptions import QuestNotConfigured


ONBOARDING_STEPS: List[Dict[str, str]] = [
    {
        "title": "Вітаємо у тихому куточку",
        "body": "Твоя ферма вже чекає на перші посадки. Витрачай енергію, щоб вирощувати врожай та відкривати все більше ділянок.",
    },
    {
        "title": "Енергія та насіння",
        "body": "Енергія відновлюється з часом, а подарункове насіння дозволяє почати без витрат. Пізніше купуй насіння за золото або отримуй у винагородах.",
    },
    {
        "title": "Квести та прогрес",
        "body": "Виконуй квести, щоб отримувати досвід, золото та особливі предмети. Початковий квест навчить базовим механікам ферми.",
    },
]


class OnboardingService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def ensure_onboarding_content(self) -> None:
        quest = self._session.get(Quest, ONBOARDING_QUEST_ID)
        if quest is None:
            quest = Quest(
                id=ONBOARDING_QUEST_ID,
                title="Перші кроки фермера",
                description="Познайомтесь із фермою та її базовими механіками",
                is_repeatable=False,
            )
            self._session.add(quest)
            self._session.flush()

        nodes_map = {node.id: node for node in quest.nodes}

        intro_node = nodes_map.get(ONBOARDING_NODE_INTRO)
        if intro_node is None:
            intro_node = QuestNode(
                id=ONBOARDING_NODE_INTRO,
                quest_id=quest.id,
                title="Вітаємо на фермі",
                body="Тут ти зможеш вирощувати фантазійні рослини, заробляти досвід та відкривати нові можливості.",
                is_start=True,
                is_final=False,
            )
            self._session.add(intro_node)
        else:
            intro_node.is_start = True
            intro_node.is_final = False

        mechanics_node = nodes_map.get(ONBOARDING_NODE_MECHANICS)
        if mechanics_node is None:
            mechanics_node = QuestNode(
                id=ONBOARDING_NODE_MECHANICS,
                quest_id=quest.id,
                title="Як усе працює",
                body="Посадка витрачає енергію, але врожай повертає золото та досвід. Не забувай про подарункове насіння – воно дає можливість почати без витрат!",
                is_start=False,
                is_final=False,
            )
            self._session.add(mechanics_node)
        else:
            mechanics_node.is_start = False
            mechanics_node.is_final = False

        finish_node = nodes_map.get(ONBOARDING_NODE_FINISH)
        if finish_node is None:
            finish_node = QuestNode(
                id=ONBOARDING_NODE_FINISH,
                quest_id=quest.id,
                title="Готово до пригод",
                body="Ти готовий вирушити у свою першу фермерську подорож. Перевір квестову панель, щоб продовжити.",
                is_start=False,
                is_final=True,
            )
            self._session.add(finish_node)
        else:
            finish_node.is_start = False
            finish_node.is_final = True

        existing_choices = {
            choice.id: choice for choice in self._session.execute(
                select(QuestChoice).where(QuestChoice.id.in_([ONBOARDING_CHOICE_INTRO_NEXT, ONBOARDING_CHOICE_MECHANICS_FINISH]))
            ).scalars()
        }

        if ONBOARDING_CHOICE_INTRO_NEXT not in existing_choices:
            self._session.add(
                QuestChoice(
                    id=ONBOARDING_CHOICE_INTRO_NEXT,
                    node_id=ONBOARDING_NODE_INTRO,
                    label="Розповісти більше",
                    next_node_id=ONBOARDING_NODE_MECHANICS,
                    reward_xp=15,
                )
            )
        else:
            choice = existing_choices[ONBOARDING_CHOICE_INTRO_NEXT]
            choice.node_id = ONBOARDING_NODE_INTRO
            choice.label = "Розповісти більше"
            choice.next_node_id = ONBOARDING_NODE_MECHANICS
            choice.reward_xp = 15

        if ONBOARDING_CHOICE_MECHANICS_FINISH not in existing_choices:
            self._session.add(
                QuestChoice(
                    id=ONBOARDING_CHOICE_MECHANICS_FINISH,
                    node_id=ONBOARDING_NODE_MECHANICS,
                    label="Я готовий",
                    next_node_id=ONBOARDING_NODE_FINISH,
                    reward_xp=40,
                )
            )
        else:
            choice = existing_choices[ONBOARDING_CHOICE_MECHANICS_FINISH]
            choice.node_id = ONBOARDING_NODE_MECHANICS
            choice.label = "Я готовий"
            choice.next_node_id = ONBOARDING_NODE_FINISH
            choice.reward_xp = 40

        self._session.flush()

    def _ensure_progress(self, player_id: int) -> QuestNodePublic:
        quest_engine = QuestEngine(self._session)
        return quest_engine.get_current_node(player_id)

    def get_state(self, player_id: int) -> OnboardingState:
        player = self._session.get(Player, player_id)
        if player is None:
            raise QuestNotConfigured(f"Player {player_id} does not exist")

        self.ensure_onboarding_content()

        farm_state = FarmService(self._session).get_farm_state(player_id)

        quest_node: QuestNodePublic | None = None
        if not player.onboarding_completed:
            quest_node = self._ensure_progress(player_id)

        return OnboardingState(
            player_id=player_id,
            completed=player.onboarding_completed,
            steps=ONBOARDING_STEPS,
            current_node=quest_node,
            starter_seed_charges=farm_state.stats.starter_seed_charges,
        )

    def mark_completed(self, player_id: int) -> OnboardingState:
        player = self._session.get(Player, player_id)
        if player is None:
            raise QuestNotConfigured(f"Player {player_id} does not exist")

        self.ensure_onboarding_content()

        player.onboarding_completed = True
        self._session.add(player)

        # Ensure quest progress exists so the quest card is ready on dashboard
        progress = self._session.get(QuestProgress, player_id)
        if progress is None:
            self._ensure_progress(player_id)

        self._session.flush()
        return self.get_state(player_id)
