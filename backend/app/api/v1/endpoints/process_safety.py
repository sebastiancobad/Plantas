"""API endpoints for Process Safety & Industrial Hygiene (Module 9)."""

from fastapi import APIRouter, HTTPException
from app.services.modules.process_safety import (
    calculate_dow_fei, generate_hazop, inherently_safer_design_checklist, CASE_STUDIES
)

router = APIRouter()


@router.post("/dow-fei")
def dow_fire_explosion_index(input_data: dict):
    """Calculate Dow Fire & Explosion Index for a process unit."""
    try:
        return calculate_dow_fei(input_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"F&EI calculation error: {e}")


@router.post("/hazop")
def generate_hazop_worksheet(input_data: dict):
    """Generate a HAZOP worksheet template for a process node."""
    try:
        return generate_hazop(input_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/isd-checklist")
def get_isd_checklist():
    """Get Inherently Safer Design checklist (Kletz principles)."""
    return inherently_safer_design_checklist({})


@router.get("/case-studies")
def get_case_studies():
    """Get historical process safety case studies."""
    return {"case_studies": CASE_STUDIES}


@router.get("/case-studies/{case_id}")
def get_case_study(case_id: str):
    """Get a specific case study by ID."""
    study = CASE_STUDIES.get(case_id)
    if not study:
        raise HTTPException(status_code=404, detail=f"Case study '{case_id}' not found")
    return study
