from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, cast

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.schemas.quest import QuestNodePublic
from app.services.inventory_service import build_inventory_public
from app.services.player_service import create_player_if_not_exists
from app.services.progression_service import DAILY_REWARD_COOLDOWN, ProgressionService
from app.services.quest_engine import QuestEngine
from app.utils.exceptions import QuestNotConfigured

DAILY_PREVIEW_REWARD = {"energy": 5, "xp": 15}


async def build_dashboard(db: AsyncSession, player_id: int) -> Dict[str, Any]:
    """Aggregate data from multiple services for the dashboard UI."""
    player = await create_player_if_not_exists(db, player_id)

    xp_to_next_level = ProgressionService.xp_required_for_next_level(player.level)

    now = datetime.now(timezone.utc)
    progression_service = ProgressionService(cast(Session, None))  # type: ignore[arg-type]
    can_claim_daily = progression_service.can_claim_daily(player, now)

    cooldown_seconds_left = 0
    if not can_claim_daily and player.last_daily_claim_at is not None:
        last_claim = player.last_daily_claim_at
        if last_claim.tzinfo is None:
            last_claim = last_claim.replace(tzinfo=timezone.utc)
        cooldown_ends = last_claim + DAILY_REWARD_COOLDOWN
        cooldown_seconds_left = max(0, int((cooldown_ends - now).total_seconds()))

    quest_node = await _load_current_quest_node(db, player_id)
    quest_data = _format_quest_node(quest_node)

    inventory_public = await build_inventory_public(db, player_id)
    inventory_preview = _build_inventory_preview(inventory_public)

    return {
        "player": {
            "id": player.id,
            "username": player.username,
            "level": player.level,
            "xp": player.xp,
            "xp_to_next_level": xp_to_next_level,
            "energy": player.energy,
            "max_energy": player.max_energy,
        },
        "daily": {
            "can_claim": can_claim_daily,
            "cooldown_seconds_left": cooldown_seconds_left,
            "preview_reward": DAILY_PREVIEW_REWARD,
        },
        "quest": quest_data,
        "inventory": inventory_public,
        "inventory_preview": inventory_preview,
        "milestone": {
            "label": "До титулу 'Голос Ночі'",
            "current": player.level,
            "target": player.level + 2,
        },
    }


async def _load_current_quest_node(db: AsyncSession, player_id: int) -> Optional[QuestNodePublic]:
    def _sync_fetch(session: Session) -> Optional[QuestNodePublic]:
        engine = QuestEngine(session)
        try:
            node = engine.get_current_node_public(player_id)
        except QuestNotConfigured:
            return None
        session.flush()
        return node

    return await db.run_sync(_sync_fetch)


def _format_quest_node(node: Optional[QuestNodePublic]) -> Dict[str, Any]:
    if node is None:
        quest_dict = {
            "node_id": None,
            "title": "Мандрівка ще попереду",
            "body": "Розділ пригод готується. Повернись пізніше, щоб розпочати квест!",
            "is_final": False,
            "choices": [],
        }
        return quest_dict

    quest_dict: Dict[str, Any] = node.model_dump()
    formatted_choices: List[Dict[str, Any]] = []
    for choice in quest_dict.get("choices", []):
        formatted_choice = dict(choice)
        formatted_choice["reward_preview"] = {
            "xp": formatted_choice.get("reward_xp"),
            "item_name": formatted_choice.get("reward_item_name"),
        }
        formatted_choices.append(formatted_choice)
    quest_dict["choices"] = formatted_choices
    return quest_dict


def _build_inventory_preview(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not items:
        return []
    sorted_items = sorted(
        items,
        key=lambda entry: (
            not entry.get("is_equipped", False),
            entry.get("slot") or "",
            entry.get("name") or "",
        ),
    )
    return sorted_items[:4]
