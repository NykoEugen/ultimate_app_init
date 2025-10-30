from __future__ import annotations

import pytest

from sqlalchemy import select

from app.db.models.activity import PlayerActivityLog
from app.services.dashboard_service import build_dashboard


@pytest.mark.asyncio
async def test_dashboard_returns_defaults_without_quest(async_session):
    player_id = 42

    data = await build_dashboard(async_session, player_id)

    assert data["player"]["id"] == player_id
    assert data["daily"]["can_claim"] is True
    assert data["daily"]["preview_reward"] == {"energy": 5, "xp": 15}
    assert data["quest"]["choices"] == []
    assert data["quest"]["title"] == "Мандрівка ще попереду"
    assert data["inventory_preview"] == []
    assert data["milestone"]["label"] == "До титулу 'Голос Ночі'"
    assert data["milestone"]["target"] == 5
    assert data["pending_actions"] == {
        "you_have_unspent_points": True,
        "you_can_equip_new_item": False,
    }

    log_result = await async_session.execute(select(PlayerActivityLog))
    logs = log_result.scalars().all()
    assert len(logs) == 1
    assert logs[0].player_id == player_id
    assert logs[0].activity_type == "dashboard_view"
