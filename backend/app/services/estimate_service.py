from fastapi import HTTPException

from app.engines.tile_math import mixed_tile_count, tile_count
from app.repositories import history, rooms, settings_repo, tiles


def run_estimate(room_id: int, tile_id: int, waste_pct: float | None, save: bool, note: str):
    room = rooms.get_room(room_id)
    if not room:
        raise HTTPException(404, "room not found")
    tile = tiles.get_tile(tile_id)
    if not tile:
        raise HTTPException(404, "tile not found")
    if room.get("data_quality") == "dirty":
        raise HTTPException(422, "room marked dirty; fix dimensions before estimate")

    waste = float(waste_pct) if waste_pct is not None else settings_repo.get_waste_pct()
    calc = tile_count(room["length"], room["width"], tile["tile_l"], tile["tile_w"], waste)

    run_id = None
    if save:
        payload = {**calc, "room_id": room_id, "tile_id": tile_id}
        run_id = history.insert_run(room_id, tile_id, waste, payload, note)

    return {
        "room_id": room_id,
        "tile_id": tile_id,
        "room": room,
        "tile": tile,
        "run_id": run_id,
        **calc,
    }


def run_mixed_estimate(
    room_id: int,
    tile_id: int,
    aux_tile_id: int,
    main_ratio_pct: float,
    waste_pct: float | None,
    save: bool,
    note: str,
):
    """Dual-tile mixed paving: main tile covers main_ratio_pct% of the floor,
    the aux tile covers the rest; each slice goes through the area method with
    the same waste. Saving appends exactly one run carrying both tile ids."""
    room = rooms.get_room(room_id)
    if not room:
        raise HTTPException(404, "room not found")
    tile = tiles.get_tile(tile_id)
    if not tile:
        raise HTTPException(404, "tile not found")
    aux_tile = tiles.get_tile(aux_tile_id)
    if not aux_tile:
        raise HTTPException(404, "aux tile not found")
    if room.get("data_quality") == "dirty":
        raise HTTPException(422, "room marked dirty; fix dimensions before estimate")

    ratio = float(main_ratio_pct)
    if not 0.0 < ratio <= 100.0:
        raise HTTPException(422, "main_ratio_pct out of range (0, 100]")
    if tile_id == aux_tile_id and ratio != 100.0:
        raise HTTPException(422, "same tile for both paths requires main_ratio_pct = 100")

    waste = float(waste_pct) if waste_pct is not None else settings_repo.get_waste_pct()
    calc = mixed_tile_count(
        room["length"],
        room["width"],
        tile["tile_l"],
        tile["tile_w"],
        aux_tile["tile_l"],
        aux_tile["tile_w"],
        ratio,
        waste,
    )

    run_id = None
    if save:
        payload = {
            **calc,
            "room_id": room_id,
            "tile_id": tile_id,
            "aux_tile_id": aux_tile_id,
        }
        run_id = history.insert_run(room_id, tile_id, waste, payload, note)

    return {
        "room_id": room_id,
        "tile_id": tile_id,
        "aux_tile_id": aux_tile_id,
        "room": room,
        "tile": tile,
        "aux_tile": aux_tile,
        "run_id": run_id,
        **calc,
    }
