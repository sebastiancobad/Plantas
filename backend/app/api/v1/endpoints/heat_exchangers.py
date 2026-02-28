"""
API endpoints for Heat Exchanger Design (Module 6).
"""

from fastapi import APIRouter, HTTPException

from app.schemas.heat_exchanger import (
    HeatExchangerDesignInput,
    HeatExchangerDesignOutput,
)
from app.services.modules.heat_exchanger import design_heat_exchanger

router = APIRouter()


TEMA_TYPES = {
    "AES": "Split ring floating head — general purpose refinery service",
    "AEU": "U-tube bundle — thermal expansion tolerance",
    "AEM": "Fixed tubesheet — low-cost, single material",
    "AEP": "Outside packed floating head",
    "AET": "Pull-through floating head — easy maintenance",
    "BEM": "Bonnet cover, fixed tubesheet — compact",
    "BES": "Bonnet cover, split ring floating head",
    "BEU": "Bonnet cover, U-tube",
    "AKT": "Kettle reboiler — thermosiphon service",
    "AJW": "Reflux condenser — vertical",
}


@router.post("/design", response_model=HeatExchangerDesignOutput)
def design(input_data: HeatExchangerDesignInput):
    """
    Design a shell & tube heat exchanger.

    Accepts process conditions and mechanical constraints,
    returns complete thermal, hydraulic, and mechanical design
    with standards compliance checks.
    """
    try:
        result = design_heat_exchanger(input_data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Component not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {e}")

    return result


@router.get("/tema-types")
def get_tema_types():
    """List available TEMA shell/head type combinations with descriptions."""
    return {"tema_types": TEMA_TYPES}
