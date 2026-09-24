from pydantic import BaseModel, Field


class EstimateRequest(BaseModel):
    room_id: int
    tile_id: int
    waste_pct: float | None = None
    save: bool = False
    note: str = ""


class MixedEstimateRequest(BaseModel):
    room_id: int
    main_tile_id: int
    aux_tile_id: int | None = None
    main_ratio: float = Field(..., description="主砖面积占比，取值 (0, 100]")
    waste_pct: float | None = None
    save: bool = False
    note: str = ""


class EstimateResponse(BaseModel):
    room_id: int
    tile_id: int
    room_name: str
    tile_name: str
    area_m2: float
    piece_m2: float
    raw_count: int
    waste_pct: float
    order_count: int
    layout: dict
    run_id: int | None = None
