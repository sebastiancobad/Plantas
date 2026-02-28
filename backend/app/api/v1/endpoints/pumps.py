"""API endpoints for Pump Selection & Sizing (Module 5)."""

from fastapi import APIRouter, HTTPException
from app.services.modules.pumps import size_pump

router = APIRouter()


@router.post("/design")
def design_pump(input_data: dict):
    """Size a pump: system curve, NPSH, type selection, power calculation."""
    try:
        return size_pump(input_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pump sizing error: {e}")
