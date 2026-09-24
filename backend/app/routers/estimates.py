from fastapi import APIRouter, Query

from app.schemas.estimate import EstimateRequest, MixedEstimateRequest
from app.services import estimate_service

router = APIRouter(tags=["estimates"])


@router.get("/estimate")
def estimate_get(
    room_id: int = Query(...),
    tile_id: int = Query(...),
    waste_pct: float | None = None,
    save: bool = False,
):
    return estimate_service.run_estimate(room_id, tile_id, waste_pct, save, "")


@router.post("/estimate")
def estimate_post(body: EstimateRequest):
    return estimate_service.run_estimate(
        body.room_id, body.tile_id, body.waste_pct, body.save, body.note
    )


@router.get("/estimate/mixed")
def estimate_mixed_get(
    room_id: int = Query(...),
    tile_id: int = Query(...),
    aux_tile_id: int = Query(...),
    main_ratio_pct: float = Query(...),
    waste_pct: float | None = None,
    save: bool = False,
):
    return estimate_service.run_mixed_estimate(
        room_id, tile_id, aux_tile_id, main_ratio_pct, waste_pct, save, ""
    )


@router.post("/estimate/mixed")
def estimate_mixed_post(body: MixedEstimateRequest):
    return estimate_service.run_mixed_estimate(
        body.room_id,
        body.tile_id,
        body.aux_tile_id,
        body.main_ratio_pct,
        body.waste_pct,
        body.save,
        body.note,
    )
