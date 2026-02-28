"""
API endpoints for Economic Evaluation (Module 12).
"""

from fastapi import APIRouter, HTTPException

from app.schemas.economics import (
    CapexInput,
    CapexOutput,
    UtilityInput,
    OpexInput,
    EconomicEvaluationInput,
)
from app.services.modules.economics import (
    calculate_capex,
    calculate_utility_demand,
    calculate_opex,
    get_cepci,
)

router = APIRouter()


@router.post("/capex", response_model=CapexOutput)
def estimate_capex(input_data: CapexInput):
    """
    Estimate total capital cost (CAPEX) for a list of equipment.

    Uses cost correlations, CEPCI escalation, material/pressure factors,
    and Lang/module installation factors.
    """
    try:
        result = calculate_capex(input_data.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CAPEX calculation error: {e}")
    return result


@router.post("/utilities")
def estimate_utilities(input_data: UtilityInput):
    """
    Calculate utility demands (steam, CW, IA, electricity) and annual costs.
    """
    try:
        result = calculate_utility_demand(input_data.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Utility calculation error: {e}")
    return result


@router.post("/opex")
def estimate_opex(input_data: OpexInput):
    """
    Estimate annual operating cost (OPEX) breakdown.
    """
    try:
        result = calculate_opex(input_data.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OPEX calculation error: {e}")
    return result


@router.get("/cepci/{year}")
def get_cepci_index(year: int):
    """Return CEPCI index for a given year (2000-2026+)."""
    if year < 1990 or year > 2050:
        raise HTTPException(status_code=422, detail="Year must be between 1990 and 2050")
    index = get_cepci(year)
    return {"year": year, "cepci_index": round(index, 1)}


@router.post("/evaluate")
def full_evaluation(input_data: EconomicEvaluationInput):
    """
    Full economic evaluation: CAPEX + utility demand + OPEX + NPV analysis.
    """
    try:
        # Step 1: CAPEX
        capex_result = calculate_capex(input_data.capex.model_dump())

        # Step 2: Utilities (if provided)
        utility_result = None
        annual_utility_cost = 0.0
        if input_data.utility:
            utility_result = calculate_utility_demand(input_data.utility.model_dump())
            annual_utility_cost = utility_result.get("annual_utility_cost_usd", 0)
            capex_result["utility_demand_summary"] = utility_result

        # Step 3: OPEX (if provided or derive from CAPEX)
        opex_data = input_data.opex.model_dump() if input_data.opex else {
            "annual_utility_cost_usd": annual_utility_cost,
            "total_installed_cost_usd": capex_result["cost_summary"]["total_installed_cost_usd"],
        }
        opex_data["annual_utility_cost_usd"] = annual_utility_cost
        opex_data["total_installed_cost_usd"] = capex_result["cost_summary"]["total_installed_cost_usd"]
        opex_result = calculate_opex(opex_data)

        # Step 4: NPV analysis
        total_capex = capex_result["cost_summary"]["location_adjusted_usd"]
        annual_opex = opex_result["annual_opex"]["total_annual_opex_usd"]
        annual_revenue = input_data.annual_revenue_usd
        discount_rate = input_data.discount_rate
        lifetime = input_data.project_lifetime_years

        annual_cash_flow = annual_revenue - annual_opex
        npv = -total_capex
        for year in range(1, lifetime + 1):
            npv += annual_cash_flow / (1 + discount_rate)**year

        # Payback period (simple)
        if annual_cash_flow > 0:
            payback = total_capex / annual_cash_flow
        else:
            payback = float("inf")

        # Internal Rate of Return (approximate via bisection)
        irr = _calculate_irr(total_capex, annual_cash_flow, lifetime)

        return {
            "capex": capex_result,
            "opex": opex_result,
            "npv_analysis": {
                "discount_rate": discount_rate,
                "project_lifetime_years": lifetime,
                "annual_revenue_usd": annual_revenue,
                "annual_cash_flow_usd": round(annual_cash_flow, 0),
                "npv_usd": round(npv, 0),
                "simple_payback_years": round(payback, 1) if payback != float("inf") else None,
                "irr_percent": round(irr * 100, 1) if irr else None,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation error: {e}")


def _calculate_irr(capex: float, annual_cf: float, years: int) -> float | None:
    """Approximate IRR via bisection method."""
    if annual_cf <= 0:
        return None

    low, high = -0.5, 2.0
    for _ in range(100):
        mid = (low + high) / 2
        npv = -capex + sum(annual_cf / (1 + mid)**y for y in range(1, years + 1))
        if abs(npv) < 1.0:
            return mid
        if npv > 0:
            low = mid
        else:
            high = mid
    return (low + high) / 2
