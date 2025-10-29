from __future__ import annotations

from sqlalchemy import select

from app.db.base import SessionLocal
from app.db.models.inventory import InventoryItemCatalog
from app.db.models.quest import Quest, QuestChoice, QuestNode


def seed() -> None:
    """Populate the database with a minimal quest storyline and catalog items."""
    session = SessionLocal()
    try:
        item = session.execute(
            select(InventoryItemCatalog).where(InventoryItemCatalog.name == "Кинджал Мандрівника")
        ).scalar_one_or_none()
        if item is None:
            item = InventoryItemCatalog(
                name="Кинджал Мандрівника",
                rarity="rare",
                cosmetic=False,
                description="Колекційний клинок, що нагадує про перші пригоди.",
            )
            session.add(item)
            session.flush()

        start_node = session.execute(
            select(QuestNode).where(QuestNode.id == "village_square")
        ).scalar_one_or_none()
        if start_node is None:
            quest = Quest(
                title="Сигнали з Таверни",
                description="Герой прибуває до села, де потрібна допомога.",
                is_repeatable=False,
            )

            node_start = QuestNode(
                id="village_square",
                quest=quest,
                title="Площа Села",
                body="Селяни зібралися навколо тебе у пошуках захисту.",
                is_start=True,
                is_final=False,
            )
            node_after_help = QuestNode(
                id="after_help",
                quest=quest,
                title="Нові Друзі",
                body="Ти допоміг селянам і відчуваєш тепло їхньої вдячності.",
                is_start=False,
                is_final=True,
            )

            choice_help = QuestChoice(
                id="help_villagers",
                node=node_start,
                label="Допомогти селянам",
                next_node_id="after_help",
                reward_xp=25,
                reward_item_id=item.id,
            )
            choice_rest = QuestChoice(
                id="keep_moving",
                node=node_start,
                label="Продовжити шлях",
                next_node_id="after_help",
                reward_xp=10,
                reward_item_id=None,
            )

            session.add_all([quest, node_start, node_after_help, choice_help, choice_rest])

        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    seed()
