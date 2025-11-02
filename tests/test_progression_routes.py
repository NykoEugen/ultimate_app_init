from __future__ import annotations

from fastapi.testclient import TestClient

from app.db.models.player import Player


def test_get_progression_returns_summary(client: TestClient, session_factory):
    session = session_factory()
    player = Player(id=51, username="Leveller", level=3, xp=40, energy=15, max_energy=20, gold=10)
    session.add(player)
    session.commit()
    player_id = player.id
    session.close()

    response = client.get(f"/player/{player_id}/progression")
    assert response.status_code == 200
    payload = response.json()

    assert payload["level"] == 3
    assert payload["xp"] == 40
    assert payload["xp_to_next_level"] >= 0
    assert payload["milestone"]["label"] == "До титулу 'Голос Ночі'"
    assert payload["milestone"]["target"] == 5
