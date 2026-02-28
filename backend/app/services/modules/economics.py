"""
Economic Evaluation Engine (Module 12).

Provides:
    - CAPEX estimation via cost correlations, CEPCI escalation, and Lang factors
    - OPEX evaluation (utilities, labor, maintenance, insurance, overhead)
    - Utility demand calculations (steam, cooling water, instrument air, electricity)

Cost Estimation Methodology:
    1. Base equipment cost from power-law correlations: C = C_ref × (S/S_ref)^n
    2. Material and pressure factors applied
    3. CEPCI time-escalation: C_new = C_old × (CEPCI_new / CEPCI_old)
    4. Installation via Lang factors or detailed module factors
    5. Engineering fees + contingency

References:
    - Turton et al., "Analysis, Synthesis and Design of Chemical Processes", 5th ed.
    - Peters, Timmerhaus & West, "Plant Design and Economics", 5th ed.
    - AACE International Recommended Practices
"""

import math
import uuid


# ── CEPCI Historical Data ───────────────────────────────────────────
# Chemical Engineering Plant Cost Index (annual averages)
# Source: Chemical Engineering Magazine

CEPCI_DATA = {
    2000: 394.1, 2001: 394.3, 2002: 395.6, 2003: 402.0,
    2004: 444.2, 2005: 468.2, 2006: 499.6, 2007: 525.4,
    2008: 575.4, 2009: 521.9, 2010: 550.8, 2011: 585.7,
    2012: 584.6, 2013: 567.3, 2014: 576.1, 2015: 556.8,
    2016: 541.7, 2017: 567.5, 2018: 603.1, 2019: 607.5,
    2020: 596.2, 2021: 708.0, 2022: 816.0, 2023: 797.9,
    2024: 810.5, 2025: 817.0, 2026: 823.5,
}


# ── Equipment Cost Correlations ─────────────────────────────────────
# Format: { "type": { "C_ref": base cost USD, "S_ref": reference size,
#                      "n": scaling exponent (six-tenths rule default = 0.6),
#                      "size_param": what the size represents,
#                      "ref_year": CEPCI base year } }

COST_CORRELATIONS = {
    "shell_and_tube_heat_exchanger": {
        "C_ref": 32800, "S_ref": 80, "n": 0.68,
        "size_param": "area", "ref_year": 2020,
    },
    "air_cooled_heat_exchanger": {
        "C_ref": 62000, "S_ref": 100, "n": 0.60,
        "size_param": "area", "ref_year": 2020,
    },
    "centrifugal_pump": {
        "C_ref": 9800, "S_ref": 10, "n": 0.55,
        "size_param": "driver_power", "ref_year": 2020,
    },
    "positive_displacement_pump": {
        "C_ref": 15000, "S_ref": 10, "n": 0.60,
        "size_param": "driver_power", "ref_year": 2020,
    },
    "vertical_pressure_vessel": {
        "C_ref": 12500, "S_ref": 5, "n": 0.62,
        "size_param": "volume", "ref_year": 2020,
    },
    "horizontal_pressure_vessel": {
        "C_ref": 11000, "S_ref": 5, "n": 0.62,
        "size_param": "volume", "ref_year": 2020,
    },
    "distillation_column": {
        "C_ref": 85000, "S_ref": 50, "n": 0.72,
        "size_param": "volume", "ref_year": 2020,
    },
    "storage_tank": {
        "C_ref": 5500, "S_ref": 10, "n": 0.51,
        "size_param": "volume", "ref_year": 2020,
    },
    "plate_heat_exchanger": {
        "C_ref": 18000, "S_ref": 30, "n": 0.58,
        "size_param": "area", "ref_year": 2020,
    },
    "compressor_centrifugal": {
        "C_ref": 220000, "S_ref": 500, "n": 0.62,
        "size_param": "driver_power", "ref_year": 2020,
    },
}

# ── Material Factors ────────────────────────────────────────────────
# Multiplier applied to base cost for non-CS materials

MATERIAL_FACTORS = {
    "carbon_steel": 1.0,
    "stainless_steel_304": 1.7,
    "stainless_steel_316": 2.1,
    "stainless_steel_316L": 2.2,
    "duplex_2205": 3.2,
    "monel_400": 3.6,
    "inconel_625": 4.5,
    "hastelloy_C276": 5.0,
    "titanium": 6.0,
    "nickel_200": 4.0,
    "copper": 1.5,
    "aluminum": 1.3,
    "carbon_steel_clad_316": 1.8,
}

# ── Pressure Factors ───────────────────────────────────────────────
# Approximate multiplier based on design pressure

def _pressure_factor(pressure_barg: float) -> float:
    """Pressure factor per Turton et al. correlation."""
    if pressure_barg <= 5:
        return 1.0
    elif pressure_barg <= 10:
        return 1.0 + 0.03 * (pressure_barg - 5)
    elif pressure_barg <= 20:
        return 1.15 + 0.04 * (pressure_barg - 10)
    elif pressure_barg <= 50:
        return 1.55 + 0.02 * (pressure_barg - 20)
    elif pressure_barg <= 100:
        return 2.15 + 0.015 * (pressure_barg - 50)
    else:
        return 2.90 + 0.01 * (pressure_barg - 100)


# ── Lang Factors ────────────────────────────────────────────────────
# Converts purchased equipment cost to total installed plant cost

LANG_FACTORS = {
    # Overall factors (Peters & Timmerhaus)
    "solids_processing": 3.10,
    "fluids_processing": 4.74,
    "mixed_processing": 3.63,

    # Default for process plants
    "default": 4.28,
}

# Detailed module factors (installation multiplier per equipment type)
MODULE_FACTORS = {
    "shell_and_tube_heat_exchanger": 3.17,
    "air_cooled_heat_exchanger": 2.17,
    "centrifugal_pump": 3.30,
    "positive_displacement_pump": 3.30,
    "vertical_pressure_vessel": 4.16,
    "horizontal_pressure_vessel": 3.85,
    "distillation_column": 4.16,
    "storage_tank": 2.00,
    "plate_heat_exchanger": 2.80,
    "compressor_centrifugal": 2.70,
}


def get_cepci(year: int) -> float:
    """
    Return CEPCI index for a given year.
    Interpolates or extrapolates if exact year not available.
    """
    if year in CEPCI_DATA:
        return CEPCI_DATA[year]

    # Linear extrapolation from nearest two years
    years = sorted(CEPCI_DATA.keys())
    if year < years[0]:
        return CEPCI_DATA[years[0]]
    if year > years[-1]:
        # Extrapolate from last two years
        slope = (CEPCI_DATA[years[-1]] - CEPCI_DATA[years[-2]]) / (years[-1] - years[-2])
        return CEPCI_DATA[years[-1]] + slope * (year - years[-1])
    # Interpolate
    for i in range(len(years) - 1):
        if years[i] <= year <= years[i + 1]:
            frac = (year - years[i]) / (years[i + 1] - years[i])
            return CEPCI_DATA[years[i]] + frac * (CEPCI_DATA[years[i + 1]] - CEPCI_DATA[years[i]])
    return CEPCI_DATA[years[-1]]


def estimate_equipment_cost(equipment: dict) -> dict:
    """
    Estimate the purchased and installed cost of a single equipment item.

    Args:
        equipment: Dict with keys: tag, type, material, design_pressure_barg,
                   size_parameter, base_cost_usd, cost_source

    Returns:
        Dict with base_cost, escalated_cost, material/pressure factors, installed_cost
    """
    eq_type = equipment["type"]
    size_val = equipment["size_parameter"]["value"]

    # Base purchased cost
    if equipment.get("base_cost_usd") and equipment.get("cost_source") == "manual":
        base_cost = equipment["base_cost_usd"]
        ref_year = 2020  # Assume recent
    elif eq_type in COST_CORRELATIONS:
        corr = COST_CORRELATIONS[eq_type]
        # Power-law scaling: C = C_ref × (S / S_ref)^n
        base_cost = corr["C_ref"] * (size_val / corr["S_ref"])**corr["n"]
        ref_year = corr["ref_year"]
    else:
        # Fallback: six-tenths rule with generic base
        base_cost = 50000 * (size_val / 10)**0.6
        ref_year = 2020

    # Material factor
    mat = equipment.get("material", "carbon_steel")
    mat_factor = MATERIAL_FACTORS.get(mat, 1.0)

    # Pressure factor
    p_barg = equipment.get("design_pressure_barg", 0)
    pf = _pressure_factor(p_barg)

    return {
        "tag": equipment["tag"],
        "type": eq_type,
        "base_cost_usd": round(base_cost, 0),
        "ref_year": ref_year,
        "material_factor": mat_factor,
        "pressure_factor": round(pf, 2),
    }


def calculate_capex(input_data: dict) -> dict:
    """
    Full CAPEX estimation for a list of equipment.

    Pipeline:
        1. Estimate base cost per item (correlations or manual)
        2. Apply material & pressure factors
        3. Escalate via CEPCI
        4. Apply Lang/module installation factors
        5. Add engineering fees + contingency
        6. Apply location factor

    Args:
        input_data: Validated CapexInput dict

    Returns:
        CapexOutput dict
    """
    calc_id = f"econ-{uuid.uuid4().hex[:8]}"

    base_year = input_data["base_year"]
    target_year = input_data["target_year"]
    cepci_base = get_cepci(base_year)
    cepci_target = get_cepci(target_year)
    escalation = cepci_target / cepci_base

    lang_method = input_data.get("lang_factor_method", "overall")
    location_factor = input_data.get("location_factor", 1.0)
    contingency_pct = input_data.get("contingency_percent", 15.0) / 100
    engineering_pct = input_data.get("engineering_fee_percent", 12.0) / 100

    equipment_costs = []
    total_equipment = 0.0
    total_installed = 0.0

    for eq in input_data["equipment_list"]:
        cost_data = estimate_equipment_cost(eq)

        # Escalate from reference year to target year
        ref_cepci = get_cepci(cost_data["ref_year"])
        escalated = cost_data["base_cost_usd"] * (cepci_target / ref_cepci)

        # Apply factors
        factored_cost = escalated * cost_data["material_factor"] * cost_data["pressure_factor"]

        # Installation
        if lang_method == "detailed":
            mod_factor = MODULE_FACTORS.get(eq["type"], 3.5)
            installed = factored_cost * mod_factor / cost_data["material_factor"]  # Module factor includes mat
        else:
            installed = factored_cost  # Will multiply by overall Lang at the end

        equipment_costs.append({
            "tag": cost_data["tag"],
            "type": cost_data["type"],
            "base_cost_usd": round(cost_data["base_cost_usd"], 0),
            "escalated_cost_usd": round(escalated, 0),
            "material_factor": cost_data["material_factor"],
            "pressure_factor": cost_data["pressure_factor"],
            "installed_cost_usd": round(installed, 0),
        })

        total_equipment += factored_cost
        total_installed += installed

    # Overall Lang factor (if using overall method)
    if lang_method == "overall":
        lang = LANG_FACTORS["default"]
        total_installed = total_equipment * lang
    else:
        lang = total_installed / total_equipment if total_equipment > 0 else 3.5

    # Engineering and contingency
    eng_fee = total_installed * engineering_pct
    contingency = total_installed * contingency_pct
    total_capital = total_installed + eng_fee + contingency
    location_adjusted = total_capital * location_factor

    return {
        "status": "success",
        "calculation_id": calc_id,
        "cepci": {
            "base_year": base_year,
            "base_index": round(cepci_base, 1),
            "target_year": target_year,
            "target_index": round(cepci_target, 1),
            "escalation_factor": round(escalation, 3),
        },
        "equipment_costs": equipment_costs,
        "cost_summary": {
            "total_equipment_cost_usd": round(total_equipment, 0),
            "lang_factor": round(lang, 2),
            "total_installed_cost_usd": round(total_installed, 0),
            "engineering_fee_usd": round(eng_fee, 0),
            "contingency_usd": round(contingency, 0),
            "total_capital_cost_usd": round(total_capital, 0),
            "location_adjusted_usd": round(location_adjusted, 0),
        },
    }


def calculate_utility_demand(input_data: dict) -> dict:
    """
    Calculate utility demands and annual costs.

    Supported utilities:
        - Steam (LP/MP/HP): demand in ton/hr, cost per ton
        - Cooling water: demand in m³/hr, cost per m³
        - Instrument air: demand in Nm³/hr, cost per Nm³
        - Electricity: demand in kW, cost per kWh

    Args:
        input_data: Validated UtilityInput dict

    Returns:
        UtilityDemandSummary dict
    """
    utilities = input_data.get("utilities", {})
    unit_costs = input_data.get("unit_costs", {})
    annual_hours = 8400  # Typical operating hours per year

    # Steam demand
    steam_demand = {"LP": 0.0, "MP": 0.0, "HP": 0.0}
    # Latent heat of steam [kJ/kg] by pressure level
    steam_latent = {"LP": 2230, "MP": 2015, "HP": 1800}

    steam_consumers = utilities.get("steam", {}).get("consumers", [])
    for consumer in steam_consumers:
        pressure = consumer.get("steam_pressure", "LP")
        duty_kW = consumer.get("duty_kW", 0)
        # ton/hr = duty_kW / (latent_kJ_kg) * 3.6
        demand = duty_kW / steam_latent.get(pressure, 2230) * 3.6
        steam_demand[pressure] += demand

    # Cooling water demand
    cw_demand_m3_hr = 0.0
    cw_consumers = utilities.get("cooling_water", {}).get("consumers", [])
    for consumer in cw_consumers:
        duty_kW = consumer.get("duty_kW", 0)
        dt = consumer.get("delta_t_degC", 10)
        # m³/hr = duty_kW / (ρ·Cp·ΔT) × 3600
        # ρ·Cp ≈ 4180 kJ/(m³·K)
        cw_demand_m3_hr += duty_kW / (4.18 * dt) * 3.6

    # Instrument air demand
    ia_demand_nm3_hr = 0.0
    ia_consumers = utilities.get("instrument_air", {}).get("consumers", [])
    for consumer in ia_consumers:
        ia_demand_nm3_hr += consumer.get("flow_nm3_hr", 0)

    # Electricity demand
    elec_demand_kW = 0.0
    elec_consumers = utilities.get("electricity", {}).get("consumers", [])
    for consumer in elec_consumers:
        elec_demand_kW += consumer.get("power_kW", 0)

    # Annual costs
    steam_cost = (
        steam_demand["LP"] * unit_costs.get("lp_steam_per_ton", 25) +
        steam_demand["MP"] * unit_costs.get("mp_steam_per_ton", 35) +
        steam_demand["HP"] * unit_costs.get("hp_steam_per_ton", 45)
    ) * annual_hours

    cw_cost = cw_demand_m3_hr * unit_costs.get("cooling_water_per_m3", 0.05) * annual_hours
    ia_cost = ia_demand_nm3_hr * unit_costs.get("instrument_air_per_nm3", 0.02) * annual_hours
    elec_cost = elec_demand_kW * unit_costs.get("electricity_per_kWh", 0.08) * annual_hours

    total_utility_cost = steam_cost + cw_cost + ia_cost + elec_cost

    return {
        "lp_steam_ton_hr": round(steam_demand["LP"], 2),
        "mp_steam_ton_hr": round(steam_demand["MP"], 2),
        "hp_steam_ton_hr": round(steam_demand["HP"], 2),
        "cooling_water_m3_hr": round(cw_demand_m3_hr, 1),
        "instrument_air_nm3_hr": round(ia_demand_nm3_hr, 1),
        "electricity_kW": round(elec_demand_kW, 1),
        "annual_utility_cost_usd": round(total_utility_cost, 0),
    }


def calculate_opex(input_data: dict) -> dict:
    """
    Annual operating cost estimation.

    Categories:
        - Utilities (from utility demand calculation)
        - Labor (operators × salary)
        - Maintenance (% of CAPEX)
        - Insurance (% of CAPEX)
        - Overhead (% of labor)

    Args:
        input_data: Validated OpexInput dict

    Returns:
        OpexOutput dict
    """
    utility_cost = input_data.get("annual_utility_cost_usd", 0)
    n_operators = input_data.get("num_operators", 4)
    salary = input_data.get("operator_salary_usd", 80000)
    maint_pct = input_data.get("maintenance_percent_of_capex", 4.0) / 100
    ins_pct = input_data.get("insurance_percent_of_capex", 2.0) / 100
    overhead_pct = input_data.get("overhead_percent_of_labor", 40.0) / 100
    total_installed = input_data.get("total_installed_cost_usd", 0)

    labor = n_operators * salary * 5  # 5 shifts for 24/7 operation
    maintenance = total_installed * maint_pct
    insurance = total_installed * ins_pct
    overhead = labor * overhead_pct

    total_opex = utility_cost + labor + maintenance + insurance + overhead

    result = {
        "status": "success",
        "annual_opex": {
            "utilities_usd": round(utility_cost, 0),
            "labor_usd": round(labor, 0),
            "maintenance_usd": round(maintenance, 0),
            "insurance_usd": round(insurance, 0),
            "overhead_usd": round(overhead, 0),
            "total_annual_opex_usd": round(total_opex, 0),
        },
    }

    # Unit production cost if production rate given
    prod = input_data.get("production_rate")
    if prod and prod.get("value", 0) > 0:
        result["unit_production_cost"] = {
            "value": round(total_opex / prod["value"], 2),
            "unit": f"USD/{prod['unit']}",
        }

    return result
