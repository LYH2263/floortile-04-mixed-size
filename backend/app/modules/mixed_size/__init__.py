"""双砖混铺：按主砖面积占比切分房间面积，两路各自走面积法与损耗。"""

from app.engines.tile_math import area_count


def mixed_count(
    room_l: float,
    room_w: float,
    main_tile_l: float,
    main_tile_w: float,
    aux_tile_l: float,
    aux_tile_w: float,
    main_ratio: float,
    waste_pct: float,
) -> dict:
    """
    main_ratio: 主砖面积占比，取值 (0, 100]。
    占比 100 时忽略辅砖，主路结果与同房同损耗的单砖面积法完全一致。
    两路分别按面积法向上取整后再乘 (1+损耗%) 取整；total_count 为两路订货片数之和。
    """
    ratio = float(main_ratio)
    if not 0.0 < ratio <= 100.0:
        raise ValueError("main ratio out of range")
    area = float(room_l) * float(room_w)
    if area < 0:
        raise ValueError("invalid dimensions")

    if ratio >= 100.0:
        main_area, aux_area = area, None
    else:
        main_area = area * ratio / 100.0
        aux_area = area - main_area

    main = area_count(main_area, main_tile_l, main_tile_w, waste_pct)
    aux = area_count(aux_area, aux_tile_l, aux_tile_w, waste_pct) if aux_area is not None else None

    return {
        "area_m2": round(area, 3),
        "main_ratio": ratio,
        "waste_pct": float(waste_pct),
        "main": main,
        "aux": aux,
        "total_count": main["order_count"] + (aux["order_count"] if aux else 0),
    }
