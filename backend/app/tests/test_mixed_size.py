import pytest

from app.engines.tile_math import tile_count
from app.modules.mixed_size import mixed_count


def test_split_areas_and_counts():
    # 27 m² room, 60% 主砖 600x600 / 40% 辅砖 800x800, 损耗 8%
    r = mixed_count(6.0, 4.5, 0.6, 0.6, 0.8, 0.8, 60.0, 8.0)
    assert r["area_m2"] == 27.0
    assert r["main_ratio"] == 60.0
    assert r["main"]["area_m2"] == 16.2
    assert r["main"]["raw_count"] == 45
    assert r["main"]["order_count"] == 49
    assert r["aux"]["area_m2"] == 10.8
    assert r["aux"]["raw_count"] == 17
    assert r["aux"]["order_count"] == 19
    assert r["total_count"] == 49 + 19


def test_leg_areas_sum_to_room_area():
    r = mixed_count(6.0, 4.5, 0.6, 0.6, 0.8, 0.8, 33.3, 8.0)
    assert r["main"]["area_m2"] + r["aux"]["area_m2"] == pytest.approx(27.0, abs=1e-3)


def test_ratio_100_ignores_aux_and_matches_single_tile():
    r = mixed_count(6.0, 4.5, 0.6, 0.6, 0.8, 0.8, 100.0, 8.0)
    single = tile_count(6.0, 4.5, 0.6, 0.6, 8.0)
    assert r["aux"] is None
    assert r["main"]["area_m2"] == single["area_m2"]
    assert r["main"]["raw_count"] == single["raw_count"] == 75
    assert r["main"]["order_count"] == single["order_count"] == 81
    assert r["total_count"] == single["order_count"]


def test_ratio_100_same_tile_dims_still_matches_single():
    r = mixed_count(8.0, 1.2, 0.8, 0.8, 0.8, 0.8, 100.0, 8.0)
    single = tile_count(8.0, 1.2, 0.8, 0.8, 8.0)
    assert r["total_count"] == single["order_count"] == 17


@pytest.mark.parametrize("ratio", [-5.0, 0.0, 100.5, 150.0])
def test_ratio_out_of_range_raises(ratio):
    with pytest.raises(ValueError):
        mixed_count(6.0, 4.5, 0.6, 0.6, 0.8, 0.8, ratio, 8.0)


def test_zero_area_tile_raises():
    with pytest.raises(ValueError):
        mixed_count(6.0, 4.5, 0.0, 0.6, 0.8, 0.8, 60.0, 8.0)
