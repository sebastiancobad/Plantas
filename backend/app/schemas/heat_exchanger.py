"""
Pydantic schemas for Heat Exchanger Design (Module 6).

These schemas define the exact JSON contract between the frontend
and the HX calculation engine — input validation, serialization,
and documentation are all derived from these models.
"""

from pydantic import BaseModel, Field, model_validator


# ── Value + Unit Pattern (used throughout ChemScale) ────────────────

class ValueUnit(BaseModel):
    """A physical quantity with its unit for safe I/O conversion."""
    value: float
    unit: str


# ── Input Schemas ───────────────────────────────────────────────────

class ComponentFraction(BaseModel):
    name: str = Field(..., description="Component name (must exist in database)")
    mole_fraction: float = Field(..., ge=0, le=1)


class FluidSide(BaseModel):
    fluid_name: str = Field(..., description="Human-readable label for the fluid")
    components: list[ComponentFraction] = Field(..., min_length=1)
    mass_flow_rate: ValueUnit
    inlet_temperature: ValueUnit
    outlet_temperature: ValueUnit
    inlet_pressure: ValueUnit
    fouling_resistance: ValueUnit = Field(
        default=ValueUnit(value=0.0, unit="m2*K/W"),
        description="Fouling factor per TEMA Table RCB-2.32"
    )
    placement: str = Field(..., pattern="^(shell|tube)$")

    @model_validator(mode="after")
    def check_fractions_sum(self):
        total = sum(c.mole_fraction for c in self.components)
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Mole fractions must sum to 1.0 (got {total:.4f})")
        return self


class MechanicalConstraints(BaseModel):
    max_shell_diameter: ValueUnit = Field(default=ValueUnit(value=1524, unit="mm"))
    tube_od: ValueUnit = Field(default=ValueUnit(value=19.05, unit="mm"))
    tube_bwg: int = Field(default=14, description="Birmingham Wire Gauge for tube wall thickness")
    tube_length: ValueUnit = Field(default=ValueUnit(value=6096, unit="mm"))
    tube_pitch_ratio: float = Field(default=1.25, ge=1.15, le=2.0)
    tube_layout_angle: int = Field(default=30, description="30, 45, 60, or 90 degrees")
    baffle_cut_percent: float = Field(default=25, ge=15, le=45)
    tube_material: str = Field(default="carbon_steel")
    shell_material: str = Field(default="carbon_steel")
    design_pressure: ValueUnit = Field(default=ValueUnit(value=10.0, unit="barg"))
    design_temperature: ValueUnit = Field(default=ValueUnit(value=200, unit="degC"))


class HXDesignOptions(BaseModel):
    correlation_method: str = Field(
        default="kern",
        pattern="^(kern|bell_delaware)$",
        description="Heat transfer correlation method"
    )
    include_vibration_check: bool = False
    include_pressure_drop: bool = True


class HeatExchangerDesignInput(BaseModel):
    """Top-level input for a heat exchanger design calculation."""
    calculation_mode: str = Field(default="design", pattern="^(design|rating)$")
    exchanger_type: str = Field(default="shell_and_tube")
    tema_type: str = Field(default="AES", description="TEMA designation (e.g., AES, BEM, AEU)")

    hot_side: FluidSide
    cold_side: FluidSide
    mechanical_constraints: MechanicalConstraints = Field(default_factory=MechanicalConstraints)
    options: HXDesignOptions = Field(default_factory=HXDesignOptions)


# ── Output Schemas ──────────────────────────────────────────────────

class ThermalResults(BaseModel):
    duty: ValueUnit
    lmtd: ValueUnit
    correction_factor_ft: float
    effective_mtd: ValueUnit
    overall_u_clean: ValueUnit
    overall_u_dirty: ValueUnit
    required_area: ValueUnit
    actual_area: ValueUnit
    excess_area_percent: float
    shell_side_htc: ValueUnit
    tube_side_htc: ValueUnit


class HydraulicResults(BaseModel):
    shell_side_pressure_drop: ValueUnit
    tube_side_pressure_drop: ValueUnit
    shell_side_velocity: ValueUnit
    tube_side_velocity: ValueUnit


class MechanicalSummary(BaseModel):
    tema_designation: str
    shell_id: ValueUnit
    tube_count: int
    tube_passes: int
    baffle_count: int
    baffle_spacing: ValueUnit
    tube_sheet_thickness: ValueUnit


class VibrationCheck(BaseModel):
    natural_frequency_hz: float
    vortex_shedding_hz: float
    fluidelastic_ratio: float
    status: str = Field(description="PASS or FAIL")


class ComplianceResult(BaseModel):
    tema_check: str
    asme_viii: str
    api_660: str
    velocity_limits: str


class HeatExchangerDesignOutput(BaseModel):
    """Complete output from a heat exchanger design calculation."""
    status: str
    calculation_id: str
    warnings: list[str] = []

    thermal_results: ThermalResults
    hydraulic_results: HydraulicResults
    mechanical_summary: MechanicalSummary
    vibration_check: VibrationCheck | None = None
    compliance: ComplianceResult
