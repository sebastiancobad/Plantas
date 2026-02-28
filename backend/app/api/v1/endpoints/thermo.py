"""
API endpoints for Thermodynamic Property calculations.
"""

from fastapi import APIRouter, HTTPException

from app.schemas.thermo import (
    ThermoPropertyRequest,
    ThermoPropertyResponse,
    ComponentListResponse,
)
from app.services.components.database import get_component, list_components
from app.services.thermo.properties import MixturePropertyCalculator

router = APIRouter()


@router.post("/properties", response_model=ThermoPropertyResponse)
def calculate_properties(request: ThermoPropertyRequest):
    """
    Calculate thermodynamic and transport properties for a mixture
    at specified T, P, and composition.
    """
    try:
        components = [get_component(c.name) for c in request.components]
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    z = [c.mole_fraction for c in request.components]
    total = sum(z)
    if abs(total - 1.0) > 0.01:
        raise HTTPException(status_code=422, detail=f"Mole fractions sum to {total}, expected 1.0")

    calc = MixturePropertyCalculator(components, eos_model=request.eos_model)

    try:
        props = calc.properties(
            T=request.temperature_K,
            P=request.pressure_Pa,
            z=z,
            phase=request.phase,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {e}")

    return ThermoPropertyResponse(
        temperature_K=props.temperature,
        pressure_Pa=props.pressure,
        density_kg_m3=round(props.density, 4),
        molar_density_mol_m3=round(props.molar_density, 4),
        viscosity_Pa_s=props.viscosity,
        thermal_conductivity_W_mK=props.thermal_conductivity,
        heat_capacity_cp_J_molK=round(props.heat_capacity_cp, 4),
        compressibility_Z=round(props.compressibility, 6),
        molecular_weight_g_mol=round(props.molecular_weight, 3),
        phase=props.phase,
        enthalpy_departure_J_mol=round(props.enthalpy, 4),
    )


@router.get("/components", response_model=ComponentListResponse)
def get_available_components():
    """List all chemical components available in the database."""
    comps = list_components()
    return ComponentListResponse(components=comps, count=len(comps))
