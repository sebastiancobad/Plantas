"""API endpoints for Distillation Column Design (Module 7)."""

from fastapi import APIRouter, HTTPException
from app.services.modules.distillation import design_distillation_column, TRAY_TYPES, PACKING_TYPES

router = APIRouter()


@router.post("/design")
def design_column(input_data: dict):
    """Design a distillation column using FUG shortcut method."""
    try:
        return design_distillation_column(input_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Distillation design error: {e}")


@router.get("/tray-types")
def get_tray_types():
    """List available tray types with characteristics."""
    return {"tray_types": TRAY_TYPES}


@router.get("/packing-types")
def get_packing_types():
    """List available packing types with HETP and capacity data."""
    return {"packing_types": PACKING_TYPES}
