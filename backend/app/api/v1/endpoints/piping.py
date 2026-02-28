"""API endpoints for Pipe Sizing & Hydraulics (Module 1)."""

from fastapi import APIRouter, HTTPException
from app.services.modules.piping import size_pipe, PIPE_SCHEDULES, PIPE_ROUGHNESS

router = APIRouter()


@router.post("/size")
def pipe_sizing(input_data: dict):
    """Size a pipe or check pressure drop for a given configuration."""
    try:
        return size_pipe(input_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipe sizing error: {e}")


@router.get("/schedules")
def get_pipe_schedules():
    """List available NPS sizes and schedules."""
    return {"schedules": {str(k): v for k, v in PIPE_SCHEDULES.items()}}


@router.get("/roughness")
def get_roughness_values():
    """List standard pipe roughness values by material."""
    return {"roughness_mm": PIPE_ROUGHNESS}
