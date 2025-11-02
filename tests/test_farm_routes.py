from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.db.models.farm import FarmPlot, PlayerFarmingStats
from app.db.models.player import Player


def _create_player(session_factory, player_id: int = 707) -> int:
    session = session_factory()
    player = Player(
        id=player_id,
        username="Farmer",
        level=5,
        xp=0,
        energy=20,
        max_energy=20,
        gold=2000,
    )
    session.add(player)
    session.commit()
    session.close()
    return player_id


def test_get_farm_state_initialises_defaults(client: TestClient, session_factory) -> None:
    player_id = _create_player(session_factory, player_id=900)

    response = client.get(f"/farm/{player_id}")
    assert response.status_code == 200
    payload = response.json()

    assert payload["player_id"] == player_id
    assert payload["stats"]["level"] == 1
    assert payload["stats"]["energy"] == 30
    assert payload["wallet_gold"] == 2000
    assert payload["stats"]["starter_seed_charges"] == 1
    assert len(payload["available_plants"]) >= 1
    first_plant = payload["available_plants"][0]
    assert first_plant["is_unlocked"] is True

    plots = payload["plots"]
    assert len(plots) == 8
    unlocked = [plot for plot in plots if plot["unlocked"]]
    assert len(unlocked) == 3


def test_plant_and_harvest_cycle(client: TestClient, session_factory) -> None:
    player_id = _create_player(session_factory, player_id=901)

    state = client.get(f"/farm/{player_id}").json()
    plot_id = next(plot["id"] for plot in state["plots"] if plot["unlocked"])
    plant_id = state["available_plants"][0]["id"]

    plant_resp = client.post(f"/farm/{player_id}/plant", json={"plot_id": plot_id, "plant_type_id": plant_id})
    assert plant_resp.status_code == 200
    plant_payload = plant_resp.json()
    planted_plot = next(plot for plot in plant_payload["state"]["plots"] if plot["id"] == plot_id)
    assert planted_plot["crop"] is not None
    assert plant_payload["state"]["wallet_gold"] == 2000
    assert plant_payload["state"]["stats"]["starter_seed_charges"] == 1

    session = session_factory()
    plot = session.get(FarmPlot, plot_id)
    crop = plot.crop
    crop.ready_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    session.add(crop)
    session.commit()
    session.close()

    harvest_resp = client.post(f"/farm/{player_id}/harvest", json={"plot_id": plot_id})
    assert harvest_resp.status_code == 200
    harvest_payload = harvest_resp.json()
    harvested_plot = next(plot for plot in harvest_payload["state"]["plots"] if plot["id"] == plot_id)
    assert harvested_plot["crop"] is None
    assert harvest_payload["state"]["stats"]["xp"] > 0
    assert harvest_payload["state"]["stats"]["level"] >= 1
    assert harvest_payload["state"]["stats"]["energy"] <= 30
    assert harvest_payload["state"]["wallet_gold"] == 2000 + harvest_payload["state"]["available_plants"][0]["sell_price"]
    assert harvest_payload["state"]["stats"]["starter_seed_charges"] == 1


def test_energy_passive_regeneration(client: TestClient, session_factory) -> None:
    player_id = _create_player(session_factory, player_id=902)

    # Ensure farm structures exist
    client.get(f"/farm/{player_id}")

    session = session_factory()
    stats = session.get(PlayerFarmingStats, player_id)
    stats.energy = 5
    stats.max_energy = 30
    stats.last_energy_refill_at = datetime.now(timezone.utc) - timedelta(minutes=55)
    session.add(stats)
    session.commit()
    session.close()

    refreshed = client.get(f"/farm/{player_id}")
    assert refreshed.status_code == 200
    payload = refreshed.json()

    expected_regen = min(30, 5 + (55 * 60) // 600)
    assert payload["stats"]["energy"] == expected_regen
    assert payload["wallet_gold"] == 2000
    assert payload["stats"]["starter_seed_charges"] == 1
