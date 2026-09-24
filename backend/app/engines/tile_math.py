"""Floor tile order count: area method + optional grid layout preview."""

from app.engines.helpers import ceil_units


def tile_count(
    room_l: float,
    room_w: float,
    tile_l: float,
    tile_w: float,
    waste_pct: float,
) -> dict:
    """
    raw_count: ceil(room_area / tile_piece_area)
    order_count: ceil(raw * (1 + waste_pct/100))
    """
    area = float(room_l) * float(room_w)
    piece = float(tile_l) * float(tile_w)
    if piece <= 0 or area < 0:
        raise ValueError("invalid dimensions")
    raw = ceil_units(area / piece)
    with_waste = ceil_units(raw * (1 + float(waste_pct) / 100.0))
    layout = layout_preview(room_l, room_w, tile_l, tile_w)
    return {
        "area_m2": round(area, 3),
        "piece_m2": round(piece, 4),
        "raw_count": raw,
        "waste_pct": float(waste_pct),
        "order_count": with_waste,
        "layout": layout,
    }


def layout_preview(room_l: float, room_w: float, tile_l: float, tile_w: float) -> dict:
    """Grid count if tiles are laid on a full rectangular lattice (may exceed area method)."""
    cols = ceil_units(float(room_l) / float(tile_l))
    rows = ceil_units(float(room_w) / float(tile_w))
    grid_count = cols * rows
    return {
        "cols": cols,
        "rows": rows,
        "grid_count": grid_count,
    }


def _area_path_count(area: float, piece: float, waste_pct: float) -> tuple[int, int]:
    """Area-method counts for one slice of floor: raw pieces, then with waste."""
    raw = ceil_units(float(area) / float(piece))
    return raw, ceil_units(raw * (1 + float(waste_pct) / 100.0))


def mixed_tile_count(
    room_l: float,
    room_w: float,
    main_tile_l: float,
    main_tile_w: float,
    aux_tile_l: float,
    aux_tile_w: float,
    main_ratio_pct: float,
    waste_pct: float,
) -> dict:
    """
    Dual-tile mixed paving: split the room area by main_ratio_pct, then run the
    same area method + waste as tile_count on each slice independently.

    main_ratio_pct must be in (0, 100]. At exactly 100 the aux tile is ignored
    and the main path reproduces tile_count(room_l, room_w, main...) exactly.
    """
    ratio = float(main_ratio_pct)
    if not 0.0 < ratio <= 100.0:
        raise ValueError("main_ratio_pct out of range")
    area = float(room_l) * float(room_w)
    if area < 0:
        raise ValueError("invalid dimensions")
    main_piece = float(main_tile_l) * float(main_tile_w)
    if main_piece <= 0:
        raise ValueError("invalid dimensions")

    main_area = area * (ratio / 100.0)
    aux_area = area - main_area
    main_raw, main_order = _area_path_count(main_area, main_piece, waste_pct)

    full_main = ratio == 100.0
    aux_piece = float(aux_tile_l) * float(aux_tile_w)
    if full_main:
        # Aux tile ignored: do not touch its dimensions (may be a placeholder).
        aux_raw, aux_order = 0, 0
    else:
        if aux_piece <= 0:
            raise ValueError("invalid dimensions")
        aux_raw, aux_order = _area_path_count(aux_area, aux_piece, waste_pct)

    return {
        "mode": "mixed",
        "area_m2": round(area, 3),
        "main_ratio_pct": ratio,
        "waste_pct": float(waste_pct),
        "main_path": {
            "ratio_pct": ratio,
            "area_m2": round(main_area, 3),
            "piece_m2": round(main_piece, 4),
            "raw_count": main_raw,
            "order_count": main_order,
        },
        "aux_path": {
            "ratio_pct": round(100.0 - ratio, 6),
            "area_m2": round(aux_area, 3),
            "piece_m2": None if full_main else round(aux_piece, 4),
            "raw_count": aux_raw,
            "order_count": aux_order,
        },
        "raw_count": main_raw + aux_raw,
        "order_count": main_order + aux_order,
    }
