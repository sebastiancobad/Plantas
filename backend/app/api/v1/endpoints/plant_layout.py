"""API endpoints for Plant Layout & Location (Module 3)."""

from fastapi import APIRouter, HTTPException
from app.services.modules.plant_layout import generate_layout, get_spacing, EQUIPMENT_TYPES

router = APIRouter()


@router.post("/generate")
def generate_plant_layout(input_data: dict):
    """Generate plant layout with spacing analysis and plot plan estimate."""
    try:
        return generate_layout(input_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Layout generation error: {e}")


@router.get("/spacing/{type_a}/{type_b}")
def get_equipment_spacing(type_a: str, type_b: str):
    """Get minimum spacing between two equipment types."""
    return {
        "type_a": type_a, "type_b": type_b,
        "minimum_distance_m": get_spacing(type_a, type_b),
    }


@router.get("/equipment-types")
def list_equipment_types():
    """List all equipment types available for layout."""
    return {"equipment_types": EQUIPMENT_TYPES}
