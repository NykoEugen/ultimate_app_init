from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.db.models.player import Player
from app.services.progression_service import DAILY_REWARD_COOLDOWN, DAILY_REWARD_ENERGY, DAILY_REWARD_XP


def _create_player(session, *, energy: int = 10) -> Player:
    player = Player(
        id=1,
        username="tester",
        level=1,
        xp=0,
        energy=energy,
        max_energy=20,
        gold=0,
    )
    session.add(player)
    session.commit()
    session.refresh(player)
    return player


def test_claim_daily_reward_success(client: TestClient, session_factory):
    session = session_factory()
    _create_player(session, energy=10)
    session.close()

    response = client.post("/player/1/claim-daily-reward")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "claimed"
    assert payload["gained"]["xp"] == DAILY_REWARD_XP
    assert payload["gained"]["energy"] == DAILY_REWARD_ENERGY
    assert payload["gained"]["level_up"] is False
    assert "message" in payload


def test_claim_daily_reward_cooldown(client: TestClient, session_factory):
    session = session_factory()
    player = _create_player(session, energy=20)
    player.last_daily_claim_at = datetime.now(timezone.utc) - timedelta(hours=1)
    session.add(player)
    session.commit()
    session.close()

    response = client.post("/player/1/claim-daily-reward")
    assert response.status_code == 200
    payload = response.json()

    assert payload["status"] == "cooldown"
    assert payload["retry_after_seconds"] <= int(DAILY_REWARD_COOLDOWN.total_seconds())
    assert payload["retry_after_seconds"] > 0
    assert "message" in payload
