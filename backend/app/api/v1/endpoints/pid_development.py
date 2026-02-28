"""API endpoints for P&ID Development (Module 11)."""

from fastapi import APIRouter, HTTPException
from app.services.modules.pid_development import (
    generate_pid_data, ISA_FIRST_LETTER, ISA_SUCCEEDING_LETTERS, ISA_SYMBOLS
)

router = APIRouter()


@router.post("/generate")
def generate_pid(input_data: dict):
    """Generate P&ID drawing data model (JSON for frontend rendering)."""
    try:
        return generate_pid_data(input_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"P&ID generation error: {e}")


@router.get("/isa-symbols")
def get_isa_symbols():
    """List ISA 5.1 instrument symbols and letter codes."""
    return {
        "first_letters": ISA_FIRST_LETTER,
        "succeeding_letters": ISA_SUCCEEDING_LETTERS,
        "symbol_types": ISA_SYMBOLS,
    }
