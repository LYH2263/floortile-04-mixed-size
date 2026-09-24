from fastapi import HTTPException

from app.engines.tile_math import tile_count
from app.modules.mixed_size import mixed_count
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
    main_tile_id: int,
    aux_tile_id: int | None,
    main_ratio: float,
    waste_pct: float | None,
    save: bool,
    note: str,
):
    """双砖混铺：一次请求给主砖、辅砖与主砖面积占比，分路计算后合计。

    校验失败（占比越界、占比非整百但两砖相同等）直接抛错，不会写入历史。
    """
    room = rooms.get_room(room_id)
    if not room:
        raise HTTPException(404, "room not found")
    if room.get("data_quality") == "dirty":
        raise HTTPException(422, "room marked dirty; fix dimensions before estimate")
    main_tile = tiles.get_tile(main_tile_id)
    if not main_tile:
        raise HTTPException(404, "main tile not found")

    try:
        ratio = float(main_ratio)
    except (TypeError, ValueError):
        raise HTTPException(422, "main_ratio must be a number")
    if not 0.0 < ratio <= 100.0:
        raise HTTPException(422, "main_ratio out of range: expect 0 < ratio <= 100")

    aux_tile = None
    if ratio < 100.0:
        if aux_tile_id is None:
            raise HTTPException(422, "aux_tile_id required when main_ratio < 100")
        aux_tile = tiles.get_tile(aux_tile_id)
        if not aux_tile:
            raise HTTPException(404, "aux tile not found")
        if aux_tile["id"] == main_tile["id"]:
            raise HTTPException(422, "main and aux tiles must differ unless main_ratio is 100")

    for t in (main_tile, aux_tile):
        if t is not None and float(t["tile_l"]) * float(t["tile_w"]) <= 0:
            raise HTTPException(422, f"tile {t['id']} has invalid dimensions")

    waste = float(waste_pct) if waste_pct is not None else settings_repo.get_waste_pct()
    try:
        calc = mixed_count(
            room["length"],
            room["width"],
            main_tile["tile_l"],
            main_tile["tile_w"],
            aux_tile["tile_l"] if aux_tile else 0.0,
            aux_tile["tile_w"] if aux_tile else 0.0,
            ratio,
            waste,
        )
    except ValueError as e:
        raise HTTPException(422, str(e))

    calc["main"] = {**calc["main"], "tile_id": main_tile["id"], "tile_name": main_tile["name"]}
    if calc["aux"] is not None:
        calc["aux"] = {**calc["aux"], "tile_id": aux_tile["id"], "tile_name": aux_tile["name"]}

    payload = {
        "kind": "mixed",
        "room_id": room_id,
        "tile_id": main_tile["id"],
        "aux_tile_id": aux_tile["id"] if aux_tile else None,
        **calc,
    }

    run_id = None
    if save:
        run_id = history.insert_run(room_id, main_tile["id"], waste, payload, note)

    return {**payload, "room": room, "run_id": run_id}
