import pytest
from fastapi.testclient import TestClient

from app.engines.tile_math import mixed_tile_count, tile_count
from app.main import app
from app.repositories import history, settings_repo

client = TestClient(app)


def run_count() -> int:
    return len(history.list_runs(1000))


# --- engine ---------------------------------------------------------------


def test_ratio_100_matches_single_tile_same_room_same_waste():
    """占比 100 且忽略辅砖时，主路须等于现有单砖同房同损耗结果。"""
    for waste in (0.0, 8.0, 12.5):
        mixed = mixed_tile_count(6.0, 4.5, 0.6, 0.6, 0.0, 0.0, 100.0, waste)
        single = tile_count(6.0, 4.5, 0.6, 0.6, waste)
        assert mixed["main_path"]["raw_count"] == single["raw_count"]
        assert mixed["main_path"]["order_count"] == single["order_count"]
        assert mixed["aux_path"]["raw_count"] == 0
        assert mixed["aux_path"]["order_count"] == 0
        assert mixed["order_count"] == single["order_count"]


def test_ratio_100_ignores_dirty_aux_dimensions():
    # Aux tile with zero-area dimensions must not break a 100% main run.
    mixed = mixed_tile_count(8.0, 1.2, 0.8, 0.8, 0.0, 0.6, 100.0, 8.0)
    assert mixed["main_path"]["order_count"] == 17
    assert mixed["aux_path"]["order_count"] == 0


def test_split_known_values():
    mixed = mixed_tile_count(6.0, 4.5, 0.6, 0.6, 0.8, 0.8, 60.0, 8.0)
    assert mixed["mode"] == "mixed"
    assert mixed["area_m2"] == 27.0
    assert mixed["main_path"]["area_m2"] == 16.2
    assert mixed["aux_path"]["area_m2"] == 10.8
    assert mixed["main_path"]["raw_count"] == 45
    assert mixed["main_path"]["order_count"] == 49
    assert mixed["aux_path"]["raw_count"] == 17
    assert mixed["aux_path"]["order_count"] == 19
    assert mixed["order_count"] == 68
    assert (
        mixed["main_path"]["area_m2"] + mixed["aux_path"]["area_m2"]
        == mixed["area_m2"]
    )
    assert (
        mixed["main_path"]["order_count"] + mixed["aux_path"]["order_count"]
        == mixed["order_count"]
    )


@pytest.mark.parametrize("bad", [0.0, -5.0, 100.5, 101.0, 200.0])
def test_ratio_out_of_bounds_raises(bad):
    with pytest.raises(ValueError):
        mixed_tile_count(6.0, 4.5, 0.6, 0.6, 0.8, 0.8, bad, 8.0)


# --- API / service --------------------------------------------------------

MIXED_BODY = {
    "room_id": 1,
    "tile_id": 1,
    "aux_tile_id": 2,
    "main_ratio_pct": 60.0,
    "save": False,
    "note": "",
}


def test_preview_does_not_add_history_row():
    before = run_count()
    r = client.get(
        "/api/estimate/mixed",
        params={
            "room_id": 1,
            "tile_id": 1,
            "aux_tile_id": 2,
            "main_ratio_pct": 60.0,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["run_id"] is None
    assert body["main_path"]["order_count"] == 49
    assert body["aux_path"]["order_count"] == 19
    assert body["order_count"] == 68
    assert run_count() == before


def test_save_appends_exactly_one_run_with_both_tiles_and_split():
    before = run_count()
    r = client.post("/api/estimate/mixed", json={**MIXED_BODY, "save": True})
    assert r.status_code == 200
    body = r.json()
    assert body["run_id"] is not None
    assert run_count() == before + 1

    run = client.get(f"/api/runs/{body['run_id']}").json()
    assert run["tile_id"] == 1
    res = run["result"]
    assert res["mode"] == "mixed"
    assert res["tile_id"] == 1
    assert res["aux_tile_id"] == 2
    assert res["main_ratio_pct"] == 60.0
    assert res["main_path"]["order_count"] == 49
    assert res["aux_path"]["order_count"] == 19
    assert res["order_count"] == 68
    assert run["waste_pct"] == 8.0  # seeded default snapshot


@pytest.mark.parametrize("bad", [0.0, -1.0, 100.5, 150.0])
def test_ratio_out_of_bounds_fails_without_history(bad):
    before = run_count()
    r = client.post(
        "/api/estimate/mixed", json={**MIXED_BODY, "main_ratio_pct": bad}
    )
    assert r.status_code == 422
    assert run_count() == before


def test_same_tile_with_non_100_ratio_fails_without_history():
    before = run_count()
    r = client.post(
        "/api/estimate/mixed",
        json={**MIXED_BODY, "aux_tile_id": 1, "main_ratio_pct": 50.0, "save": True},
    )
    assert r.status_code == 422
    assert run_count() == before


def test_same_tile_with_ratio_100_is_allowed():
    before = run_count()
    r = client.post(
        "/api/estimate/mixed",
        json={**MIXED_BODY, "aux_tile_id": 1, "main_ratio_pct": 100.0, "save": True},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["order_count"] == 81  # same as single-tile estimate
    assert body["aux_path"]["order_count"] == 0
    assert run_count() == before + 1


def test_missing_room_or_tile_404():
    assert (
        client.post("/api/estimate/mixed", json={**MIXED_BODY, "room_id": 999}).status_code
        == 404
    )
    assert (
        client.post("/api/estimate/mixed", json={**MIXED_BODY, "tile_id": 999}).status_code
        == 404
    )
    assert (
        client.post(
            "/api/estimate/mixed", json={**MIXED_BODY, "aux_tile_id": 999}
        ).status_code
        == 404
    )


def test_dirty_room_rejected():
    before = run_count()
    r = client.post("/api/estimate/mixed", json={**MIXED_BODY, "room_id": 3})
    assert r.status_code == 422
    assert run_count() == before


def test_changing_default_waste_does_not_recompute_saved_run():
    r = client.post("/api/estimate/mixed", json={**MIXED_BODY, "save": True})
    run_id = r.json()["run_id"]
    saved = client.get(f"/api/runs/{run_id}").json()
    assert saved["waste_pct"] == 8.0
    assert saved["result"]["order_count"] == 68

    try:
        settings_repo.set_waste_pct(15.0)
        # New previews pick up the new default...
        fresh = client.get(
            "/api/estimate/mixed",
            params={
                "room_id": 1,
                "tile_id": 1,
                "aux_tile_id": 2,
                "main_ratio_pct": 60.0,
            },
        ).json()
        assert fresh["waste_pct"] == 15.0
        assert fresh["order_count"] != 68
        # ...but the saved run is frozen at its snapshot.
        again = client.get(f"/api/runs/{run_id}").json()
        assert again["waste_pct"] == 8.0
        assert again["result"]["main_path"]["order_count"] == 49
        assert again["result"]["aux_path"]["order_count"] == 19
        assert again["result"]["order_count"] == 68
    finally:
        settings_repo.set_waste_pct(8.0)
