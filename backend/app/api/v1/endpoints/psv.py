"""API endpoints for Safety Relief Valve Sizing (Module 8)."""

from fastapi import APIRouter, HTTPException
from app.services.modules.psv import size_psv, API_ORIFICES

router = APIRouter()


@router.post("/size")
def size_relief_valve(input_data: dict):
    """Size a PSV/PRV for a given overpressure scenario."""
    try:
        return size_psv(input_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PSV sizing error: {e}")


@router.get("/orifices")
def get_orifice_sizes():
    """List API 526 standard orifice designations and areas."""
    return {"orifices": {k: {"area_in2": v, "area_mm2": round(v * 645.16, 1)}
                         for k, v in API_ORIFICES.items()}}
