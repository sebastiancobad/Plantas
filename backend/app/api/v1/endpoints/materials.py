"""API endpoints for Material Selection & Metallurgy (Module 2)."""

from fastapi import APIRouter, HTTPException
from app.services.modules.materials import (
    select_material, co2_corrosion_rate, h2s_sour_service_check, MATERIALS
)

router = APIRouter()


@router.post("/select")
def material_selection(input_data: dict):
    """Select optimal material based on process conditions."""
    try:
        return select_material(input_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Material selection error: {e}")


@router.post("/corrosion/co2")
def co2_corrosion(input_data: dict):
    """Calculate CO₂ (sweet) corrosion rate via de Waard-Milliams."""
    try:
        return co2_corrosion_rate(
            T_C=input_data.get("temperature_C", 60),
            co2_partial_bar=input_data.get("co2_partial_pressure_bar", 2.0),
            pH=input_data.get("pH", 4.0),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/corrosion/h2s")
def h2s_sour_check(input_data: dict):
    """Screen material for H₂S sour service per NACE MR0175."""
    try:
        return h2s_sour_service_check(
            h2s_partial_bar=input_data.get("h2s_partial_pressure_bar", 0.05),
            pH=input_data.get("pH", 4.0),
            T_C=input_data.get("temperature_C", 60),
            material_key=input_data.get("material_key", "carbon_steel_A106B"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/database")
def list_materials():
    """List all available materials with properties."""
    return {"materials": MATERIALS}
