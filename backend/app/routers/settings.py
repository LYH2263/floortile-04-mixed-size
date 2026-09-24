from fastapi import APIRouter
from pydantic import BaseModel

from app.repositories import settings_repo

router = APIRouter(tags=["settings"])


class WasteUpdate(BaseModel):
    waste_pct: float


@router.get("/settings")
def get_settings():
    return settings_repo.get_all()


@router.put("/settings/waste")
def put_waste(body: WasteUpdate):
    """Update the system default waste. Already-saved runs keep their stored
    snapshot and are never recomputed."""
    settings_repo.set_waste_pct(body.waste_pct)
    return settings_repo.get_all()
