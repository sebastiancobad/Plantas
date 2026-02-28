"""API endpoints for Advanced Process Control (Module 10)."""

from fastapi import APIRouter, HTTPException
from app.services.modules.apc import tune_pid_loop, get_control_strategy, CONTROL_STRATEGIES

router = APIRouter()


@router.post("/tune-pid")
def tune_pid(input_data: dict):
    """Calculate PID tuning parameters from FOPDT process model."""
    try:
        return tune_pid_loop(input_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PID tuning error: {e}")


@router.post("/strategy")
def control_strategy(input_data: dict):
    """Get recommended control strategy for a unit operation."""
    try:
        return get_control_strategy(input_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/unit-types")
def list_unit_types():
    """List all unit operation types with available control strategies."""
    return {"unit_types": list(CONTROL_STRATEGIES.keys())}
