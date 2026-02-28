"""API endpoints for Phase Separator Sizing (Module 4)."""

from fastapi import APIRouter, HTTPException
from app.services.modules.separators import size_separator

router = APIRouter()


@router.post("/design")
def design_separator(input_data: dict):
    """Size a 2-phase or 3-phase separator (horizontal/vertical)."""
    try:
        return size_separator(input_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Separator sizing error: {e}")
