from __future__ import annotations

from fastapi.testclient import TestClient

from app.db.models.player import Player


def _create_player(session_factory, player_id: int = 7000) -> int:
    session = session_factory()
    player = Player(
        id=player_id,
        username="Newcomer",
        level=1,
        xp=0,
        energy=20,
        max_energy=20,
        gold=50,
    )
    session.add(player)
    session.commit()
    session.close()
    return player_id


def test_onboarding_state_initial(client: TestClient, session_factory) -> None:
    player_id = _create_player(session_factory, 9100)

    response = client.get(f"/player/{player_id}/onboarding")
    assert response.status_code == 200

    payload = response.json()
    assert payload["player_id"] == player_id
    assert payload["completed"] is False
    assert payload["steps"], "steps should be provided"
    assert payload["starter_seed_charges"] >= 1
    assert payload["current_node"] is not None


def test_onboarding_can_be_completed(client: TestClient, session_factory) -> None:
    player_id = _create_player(session_factory, 9101)

    # touch state to ensure quest seeded
    client.get(f"/player/{player_id}/onboarding")

    response = client.post(f"/player/{player_id}/onboarding/complete")
    assert response.status_code == 200

    payload = response.json()
    assert payload["completed"] is True
    assert payload["current_node"] is None

    # Ensure subsequent fetch remains completed
    follow_up = client.get(f"/player/{player_id}/onboarding")
    assert follow_up.status_code == 200
    assert follow_up.json()["completed"] is True
