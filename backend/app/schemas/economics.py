"""
Pydantic schemas for Economic Evaluation (Module 12).

Covers CAPEX estimation (equipment costing, Lang factors, CEPCI escalation),
OPEX evaluation, utility demand calculations, and full economic analysis.
"""

from pydantic import BaseModel, Field


class ValueUnit(BaseModel):
    value: float
    unit: str


# ── CAPEX Input ─────────────────────────────────────────────────────

class SizeParameter(BaseModel):
    value: float
    unit: str
    parameter_name: str = Field(
        ..., description="The sizing basis: area, volume, power, flow_rate, etc."
    )


class EquipmentItem(BaseModel):
    tag: str = Field(..., description="Equipment tag number (e.g., E-101)")
    type: str = Field(..., description="Equipment type key for cost correlation lookup")
    material: str = Field(default="carbon_steel")
    design_pressure_barg: float = Field(default=0.0)
    size_parameter: SizeParameter
    base_cost_usd: float | None = Field(
        default=None,
        description="Manual base cost override. If null, uses built-in correlations."
    )
    cost_source: str = Field(default="correlations", pattern="^(correlations|manual|vendor_quote)$")


class CapexInput(BaseModel):
    """Input for CAPEX estimation."""
    project_name: str
    location_factor: float = Field(default=1.0, ge=0.5, le=3.0)
    base_year: int = Field(default=2020)
    target_year: int = Field(default=2026)
    equipment_list: list[EquipmentItem] = Field(..., min_length=1)
    lang_factor_method: str = Field(
        default="overall",
        pattern="^(overall|detailed)$",
        description="'overall' uses single Lang factor; 'detailed' uses module factors"
    )
    contingency_percent: float = Field(default=15.0, ge=0, le=50)
    engineering_fee_percent: float = Field(default=12.0, ge=0, le=30)


# ── Utility Demand Input ────────────────────────────────────────────

class SteamConsumer(BaseModel):
    tag: str
    duty_kW: float
    steam_pressure: str = Field(..., pattern="^(LP|MP|HP)$")
    description: str = ""


class CoolingWaterConsumer(BaseModel):
    tag: str
    duty_kW: float
    delta_t_degC: float = Field(default=10.0, gt=0)
    description: str = ""


class InstrumentAirConsumer(BaseModel):
    tag: str
    flow_nm3_hr: float
    description: str = ""


class ElectricityConsumer(BaseModel):
    tag: str
    power_kW: float
    operating_hours: float = Field(default=8400, description="Annual operating hours")


class UtilityConsumers(BaseModel):
    steam: dict[str, list[SteamConsumer]] = Field(
        default_factory=lambda: {"consumers": []}
    )
    cooling_water: dict[str, list[CoolingWaterConsumer]] = Field(
        default_factory=lambda: {"consumers": []}
    )
    instrument_air: dict[str, list[InstrumentAirConsumer]] = Field(
        default_factory=lambda: {"consumers": []}
    )
    electricity: dict[str, list[ElectricityConsumer]] = Field(
        default_factory=lambda: {"consumers": []}
    )


class UnitCosts(BaseModel):
    lp_steam_per_ton: float = 25.0
    mp_steam_per_ton: float = 35.0
    hp_steam_per_ton: float = 45.0
    cooling_water_per_m3: float = 0.05
    electricity_per_kWh: float = 0.08
    instrument_air_per_nm3: float = 0.02


class UtilityInput(BaseModel):
    utilities: UtilityConsumers
    unit_costs: UnitCosts = Field(default_factory=UnitCosts)


# ── OPEX Input ──────────────────────────────────────────────────────

class OpexInput(BaseModel):
    annual_utility_cost_usd: float = 0.0
    num_operators: int = Field(default=4, ge=1)
    operator_salary_usd: float = Field(default=80000)
    maintenance_percent_of_capex: float = Field(default=4.0, ge=0, le=20)
    insurance_percent_of_capex: float = Field(default=2.0, ge=0, le=10)
    overhead_percent_of_labor: float = Field(default=40.0, ge=0, le=100)
    total_installed_cost_usd: float = Field(default=0, ge=0)
    production_rate: ValueUnit | None = None


# ── Full Evaluation Input ───────────────────────────────────────────

class EconomicEvaluationInput(BaseModel):
    capex: CapexInput
    utility: UtilityInput | None = None
    opex: OpexInput | None = None
    discount_rate: float = Field(default=0.10, ge=0, le=0.5)
    project_lifetime_years: int = Field(default=20, ge=1, le=50)
    annual_revenue_usd: float = Field(default=0, ge=0)


# ── Output Schemas ──────────────────────────────────────────────────

class CEPCIResult(BaseModel):
    base_year: int
    base_index: float
    target_year: int
    target_index: float
    escalation_factor: float


class EquipmentCostResult(BaseModel):
    tag: str
    type: str
    base_cost_usd: float
    escalated_cost_usd: float
    material_factor: float
    pressure_factor: float
    installed_cost_usd: float


class CostSummary(BaseModel):
    total_equipment_cost_usd: float
    lang_factor: float
    total_installed_cost_usd: float
    engineering_fee_usd: float
    contingency_usd: float
    total_capital_cost_usd: float
    location_adjusted_usd: float


class UtilityDemandSummary(BaseModel):
    lp_steam_ton_hr: float = 0.0
    mp_steam_ton_hr: float = 0.0
    hp_steam_ton_hr: float = 0.0
    cooling_water_m3_hr: float = 0.0
    instrument_air_nm3_hr: float = 0.0
    electricity_kW: float = 0.0
    annual_utility_cost_usd: float = 0.0


class CapexOutput(BaseModel):
    status: str
    calculation_id: str
    cepci: CEPCIResult
    equipment_costs: list[EquipmentCostResult]
    cost_summary: CostSummary
    utility_demand_summary: UtilityDemandSummary | None = None


class OpexOutput(BaseModel):
    status: str
    annual_opex: dict[str, float]
    unit_production_cost: ValueUnit | None = None
