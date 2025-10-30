from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.db.base import SessionLocal
from app.db.models.inventory import InventoryItemCatalog
from app.db.models.shop import ShopOffer
from app.db.models.quest import Quest, QuestChoice, QuestNode


def seed() -> None:
    """Populate the database with a minimal quest storyline and catalog items."""
    session = SessionLocal()
    try:
        catalog_seed = [
            {
                "name": "Плащ Мандрівника",
                "slot": "cloak",
                "rarity": "rare",
                "cosmetic": True,
                "description": "Легкий плащ, що захищає від вітру і надає впевненості.",
                "icon": "cloak_traveler_rare",
            },
            {
                "name": "Кинджал Мандрівника",
                "slot": "weapon",
                "rarity": "rare",
                "cosmetic": False,
                "description": "Колекційний клинок, що нагадує про перші пригоди.",
                "icon": "dagger_traveler",
            },
            {
                "name": "Маска Сутінків",
                "slot": "head",
                "rarity": "epic",
                "cosmetic": True,
                "description": "Тонка маска, що приховує обличчя у тіні.",
                "icon": "mask_dusk_epic",
            },
            {
                "name": "Поножі Рейнджера",
                "slot": "legs",
                "rarity": "common",
                "cosmetic": False,
                "description": "Зручні шкіряні штани з додатковими ременями.",
                "icon": "legs_ranger_common",
            },
            {
                "name": "Сапоги Тиші",
                "slot": "feet",
                "rarity": "rare",
                "cosmetic": False,
                "description": "Дозволяють рухатися безшумно навіть по гальці.",
                "icon": "boots_silence_rare",
            },
            {
                "name": "Перо Астролога",
                "slot": "accessory",
                "rarity": "seasonal",
                "cosmetic": True,
                "description": "Прикраса для волосся, що світиться нічним небом.",
                "icon": "accessory_astrologist",
            },
            {
                "name": "Наплічники Сторожа",
                "slot": "shoulders",
                "rarity": "common",
                "cosmetic": False,
                "description": "Прості, але надійні сталеві наплічники.",
                "icon": "shoulders_guard_common",
            },
            {
                "name": "Рукавиці Іскри",
                "slot": "hands",
                "rarity": "epic",
                "cosmetic": False,
                "description": "Зберігають тепло і підсилюють точність удару.",
                "icon": "gloves_spark_epic",
            },
            {
                "name": "Сяйливий Обруч",
                "slot": "head",
                "rarity": "seasonal",
                "cosmetic": True,
                "description": "Святковий обруч для зимових фестивалів.",
                "icon": "crown_glimmer_seasonal",
            },
            {
                "name": "Плаский Рюкзак Слідопита",
                "slot": "back",
                "rarity": "common",
                "cosmetic": False,
                "description": "Компактний рюкзак із безліччю прихованих кишень.",
                "icon": "backpack_pathfinder",
            },
        ]

        items_by_name: dict[str, InventoryItemCatalog] = {}
        for payload in catalog_seed:
            existing = session.execute(
                select(InventoryItemCatalog).where(InventoryItemCatalog.name == payload["name"])
            ).scalar_one_or_none()
            if existing is None:
                existing = InventoryItemCatalog(**payload)
                session.add(existing)
                session.flush()
            items_by_name[payload["name"]] = existing

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

            dagger_item = items_by_name["Кинджал Мандрівника"]

            choice_help = QuestChoice(
                id="help_villagers",
                node=node_start,
                label="Допомогти селянам",
                next_node_id="after_help",
                reward_xp=25,
                reward_item_id=dagger_item.id,
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

        now = datetime.now(timezone.utc)

        offers_payload = [
            {
                "catalog_name": "Плащ Мандрівника",
                "price_gold": 80,
                "expires_at": now + timedelta(days=1),
                "is_limited": True,
            },
            {
                "catalog_name": "Маска Сутінків",
                "price_gold": 120,
                "expires_at": now + timedelta(days=2),
                "is_limited": False,
            },
            {
                "catalog_name": "Рукавиці Іскри",
                "price_gold": 150,
                "expires_at": None,
                "is_limited": True,
            },
        ]

        for payload in offers_payload:
            item = items_by_name.get(payload["catalog_name"])
            if not item:
                continue
            existing_offer = session.execute(
                select(ShopOffer).where(ShopOffer.catalog_item_id == item.id)
            ).scalar_one_or_none()
            if existing_offer is None:
                offer = ShopOffer(
                    catalog_item_id=item.id,
                    price_gold=payload["price_gold"],
                    expires_at=payload["expires_at"],
                    is_limited=payload["is_limited"],
                )
                session.add(offer)

        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    seed()
