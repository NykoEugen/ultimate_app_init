from __future__ import annotations

import pytest

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
    assert data["milestone"]["current"] == data["player"]["level"]
    assert data["milestone"]["target"] == data["player"]["level"] + 2
