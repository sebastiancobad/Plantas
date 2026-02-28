"""
Pydantic schemas for the Thermodynamic Property Engine.
"""

from pydantic import BaseModel, Field


class ComponentInput(BaseModel):
    name: str
    mole_fraction: float = Field(..., ge=0, le=1)


class ThermoPropertyRequest(BaseModel):
    """Request fluid properties at given T, P, composition."""
    components: list[ComponentInput] = Field(..., min_length=1)
    temperature_K: float = Field(..., gt=0, description="Temperature in Kelvin")
    pressure_Pa: float = Field(..., gt=0, description="Pressure in Pascals")
    eos_model: str = Field(default="PR", pattern="^(PR|SRK)$")
    phase: str = Field(default="auto", pattern="^(auto|vapor|liquid)$")


class ThermoPropertyResponse(BaseModel):
    temperature_K: float
    pressure_Pa: float
    density_kg_m3: float
    molar_density_mol_m3: float
    viscosity_Pa_s: float
    thermal_conductivity_W_mK: float
    heat_capacity_cp_J_molK: float
    compressibility_Z: float
    molecular_weight_g_mol: float
    phase: str
    enthalpy_departure_J_mol: float


class FlashRequest(BaseModel):
    """Request VLE flash calculation."""
    components: list[ComponentInput] = Field(..., min_length=2)
    temperature_K: float = Field(..., gt=0)
    pressure_Pa: float = Field(..., gt=0)
    eos_model: str = Field(default="PR", pattern="^(PR|SRK)$")


class ComponentListResponse(BaseModel):
    components: list[str]
    count: int
