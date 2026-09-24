import pytest
from fastapi import HTTPException

from app import seed
from app.repositories import history, settings_repo
from app.services import estimate_service

seed.init_db()

# 种子数据：房间1 客餐厅 6.0x4.5；砖1 600x600、砖2 800x800；默认损耗 8%


def runs_count() -> int:
    return len(history.list_runs(1000))


def test_preview_returns_split_and_does_not_save():
    before = runs_count()
    r = estimate_service.run_mixed_estimate(1, 1, 2, 60.0, None, False, "")
    assert r["run_id"] is None
    assert r["kind"] == "mixed"
    assert r["main"]["order_count"] == 49
    assert r["aux"]["order_count"] == 19
    assert r["total_count"] == 68
    assert runs_count() == before


def test_save_appends_exactly_one_run_with_both_tiles_ratio_and_split():
    before = runs_count()
    r = estimate_service.run_mixed_estimate(1, 1, 2, 60.0, None, True, "混铺下单")
    assert runs_count() == before + 1

    row = history.get_run(r["run_id"])
    assert row["room_id"] == 1
    assert row["tile_id"] == 1  # 主砖落在既有 tile_id 列
    res = row["result"]
    assert res["kind"] == "mixed"
    assert res["tile_id"] == 1
    assert res["aux_tile_id"] == 2
    assert res["main_ratio"] == 60.0
    assert res["main"]["order_count"] == 49
    assert res["aux"]["order_count"] == 19
    assert res["total_count"] == 68


def test_ratio_100_ignores_aux_and_matches_single_tile_result():
    mixed = estimate_service.run_mixed_estimate(1, 1, None, 100.0, None, False, "")
    single = estimate_service.run_estimate(1, 1, None, False, "")
    assert mixed["aux"] is None
    assert mixed["main"]["raw_count"] == single["raw_count"]
    assert mixed["main"]["order_count"] == single["order_count"]
    assert mixed["total_count"] == single["order_count"]


def test_ratio_100_with_same_tile_still_ok():
    r = estimate_service.run_mixed_estimate(1, 1, 1, 100.0, None, False, "")
    single = estimate_service.run_estimate(1, 1, None, False, "")
    assert r["total_count"] == single["order_count"]


@pytest.mark.parametrize("ratio", [-5.0, 0.0, 100.5, 150.0])
def test_ratio_out_of_range_fails_and_history_untouched(ratio):
    before = runs_count()
    with pytest.raises(HTTPException) as exc:
        estimate_service.run_mixed_estimate(1, 1, 2, ratio, None, True, "")
    assert exc.value.status_code == 422
    assert runs_count() == before


def test_same_tiles_with_ratio_not_100_fails_and_history_untouched():
    before = runs_count()
    with pytest.raises(HTTPException) as exc:
        estimate_service.run_mixed_estimate(1, 1, 1, 50.0, None, True, "")
    assert exc.value.status_code == 422
    assert runs_count() == before


def test_ratio_below_100_without_aux_fails_and_history_untouched():
    before = runs_count()
    with pytest.raises(HTTPException) as exc:
        estimate_service.run_mixed_estimate(1, 1, None, 60.0, None, True, "")
    assert exc.value.status_code == 422
    assert runs_count() == before


def test_unknown_aux_tile_fails_and_history_untouched():
    before = runs_count()
    with pytest.raises(HTTPException) as exc:
        estimate_service.run_mixed_estimate(1, 1, 999, 60.0, None, True, "")
    assert exc.value.status_code == 404
    assert runs_count() == before


def test_saved_split_not_recomputed_after_default_waste_change():
    r = estimate_service.run_mixed_estimate(1, 1, 2, 60.0, None, True, "快照")
    run_id = r["run_id"]
    saved_waste = r["waste_pct"]
    saved_main = r["main"]["order_count"]
    saved_aux = r["aux"]["order_count"]
    saved_total = r["total_count"]

    old = settings_repo.get_waste_pct()
    try:
        settings_repo.set_waste_pct(old + 7.0)
        # 默认损耗确实变了：新预览按新默认值
        fresh = estimate_service.run_mixed_estimate(1, 1, 2, 60.0, None, False, "")
        assert fresh["waste_pct"] == old + 7.0
        assert fresh["total_count"] != saved_total

        # 已保存的混铺分路保持快照，不重算
        row = history.get_run(run_id)
        assert row["waste_pct"] == saved_waste
        assert row["result"]["waste_pct"] == saved_waste
        assert row["result"]["main"]["order_count"] == saved_main
        assert row["result"]["aux"]["order_count"] == saved_aux
        assert row["result"]["total_count"] == saved_total
    finally:
        settings_repo.set_waste_pct(old)
