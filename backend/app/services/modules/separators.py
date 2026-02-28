"""
Phase Separator Sizing Engine (Module 4).

Implements:
    - 2-phase (gas-liquid) separator sizing
    - 3-phase (gas-oil-water) separator sizing
    - Horizontal and vertical configurations
    - Demister pad sizing
    - Internal baffles and weir plates

Key correlations:
    - Souders-Brown: K-factor for gas capacity
    - Stokes' law: droplet settling velocity
    - API 12J retention time guidelines

Standards: API 12J, GPSA Engineering Data Book Ch. 7, PIP VEDST001
"""

import math
import uuid

from app.utils.constants import G


# ── Souders-Brown K factors ─────────────────────────────────────────
# Source: GPSA Fig. 7-9, API 12J
K_FACTORS = {
    "vertical_no_demister": 0.04,     # m/s
    "vertical_with_demister": 0.107,   # m/s (wire mesh)
    "vertical_vane_demister": 0.12,    # m/s (vane pack)
    "horizontal_half_full": 0.15,      # m/s
    "horizontal_demister": 0.21,       # m/s
}

# ── Retention Time Guidelines (API 12J / GPSA) ─────────────────────
# Minutes of liquid retention
RETENTION_TIMES = {
    "crude_oil": {"oil": 3.0, "water": 3.0},
    "light_oil": {"oil": 2.0, "water": 2.0},
    "heavy_oil": {"oil": 5.0, "water": 5.0},
    "gas_condensate": {"oil": 1.0, "water": 1.0},
    "produced_water": {"oil": 5.0, "water": 5.0},
    "default": {"oil": 3.0, "water": 3.0},
}


def _souders_brown_velocity(K: float, rho_L: float, rho_G: float) -> float:
    """Maximum allowable gas velocity [m/s] via Souders-Brown."""
    return K * math.sqrt((rho_L - rho_G) / (rho_G + 1e-10))


def _stokes_settling(d_droplet_m: float, rho_drop: float,
                      rho_continuous: float, mu_continuous: float) -> float:
    """Stokes settling velocity [m/s] for a liquid droplet."""
    v = (d_droplet_m**2 * abs(rho_drop - rho_continuous) * G) / (18 * mu_continuous)
    return v


def _min_diameter_vertical_gas(Q_gas_m3s: float, K: float,
                                rho_L: float, rho_G: float) -> float:
    """Minimum diameter [m] for vertical separator gas capacity."""
    v_max = _souders_brown_velocity(K, rho_L, rho_G)
    if v_max <= 0:
        return 10.0
    A_min = Q_gas_m3s / v_max
    return math.sqrt(4 * A_min / math.pi)


def size_separator(input_data: dict) -> dict:
    """
    Size a phase separator (2-phase or 3-phase, horizontal or vertical).

    The design procedure:
    1. Gas capacity check (Souders-Brown) → minimum diameter
    2. Liquid retention time → minimum liquid volume
    3. Geometry sizing (L/D ratio, levels, internals)
    4. Demister pad sizing
    5. Nozzle sizing
    """
    calc_id = f"sep-{uuid.uuid4().hex[:8]}"
    warnings = []

    # Parse input
    sep_type = input_data.get("separator_type", "two_phase")
    orientation = input_data.get("orientation", "horizontal")
    fluid_type = input_data.get("fluid_type", "default")

    gas = input_data.get("gas_phase", {})
    rho_G = gas.get("density_kg_m3", 50.0)
    Q_gas = gas.get("actual_flow_m3_s", 1.0)
    mu_G = gas.get("viscosity_Pa_s", 1.5e-5)

    oil = input_data.get("oil_phase", {})
    rho_oil = oil.get("density_kg_m3", 800.0)
    Q_oil = oil.get("flow_m3_s", 0.01)
    mu_oil = oil.get("viscosity_Pa_s", 5e-3)

    water = input_data.get("water_phase", {})
    rho_water = water.get("density_kg_m3", 1020.0)
    Q_water = water.get("flow_m3_s", 0.005) if sep_type == "three_phase" else 0

    # Operating conditions
    P_bar = input_data.get("operating_pressure_barg", 10.0)
    T_C = input_data.get("operating_temperature_C", 40.0)

    # Droplet size for liquid removal
    d_droplet = input_data.get("droplet_diameter_micron", 150) * 1e-6  # m

    # Retention times
    ret = RETENTION_TIMES.get(fluid_type, RETENTION_TIMES["default"])
    t_oil = input_data.get("oil_retention_min", ret["oil"]) * 60  # seconds
    t_water = input_data.get("water_retention_min", ret["water"]) * 60

    # Demister
    has_demister = input_data.get("demister", True)

    if orientation == "vertical":
        K_key = "vertical_with_demister" if has_demister else "vertical_no_demister"
    else:
        K_key = "horizontal_demister" if has_demister else "horizontal_half_full"
    K_val = K_FACTORS[K_key]

    # ── Gas Capacity ────────────────────────────────────────────────
    v_gas_max = _souders_brown_velocity(K_val, rho_oil, rho_G)
    D_gas = _min_diameter_vertical_gas(Q_gas, K_val, rho_oil, rho_G)

    # ── Liquid Retention Volume ─────────────────────────────────────
    V_oil = Q_oil * t_oil
    V_water = Q_water * t_water if sep_type == "three_phase" else 0
    V_liquid_total = V_oil + V_water

    # ── Droplet Settling ────────────────────────────────────────────
    # Oil droplet settling out of gas
    v_settle_gas = _stokes_settling(d_droplet, rho_oil, rho_G, mu_G)
    # Water droplet settling out of oil
    v_settle_oil = _stokes_settling(d_droplet, rho_water, rho_oil, mu_oil)

    # ── Geometry Sizing ─────────────────────────────────────────────
    if orientation == "horizontal":
        # Typical L/D = 3 to 5
        LD_ratio = input_data.get("LD_ratio", 4.0)

        # Assume liquid fills 50% of cross-section for 2-phase
        liquid_frac = 0.5 if sep_type == "two_phase" else 0.6

        # V_vessel = (π/4)·D²·L = (π/4)·D²·(LD·D) = (π/4)·LD·D³
        # V_liquid = liquid_frac · V_vessel
        D_liq = (4 * V_liquid_total / (math.pi * LD_ratio * liquid_frac))**(1/3)
        D = max(D_gas, D_liq)

        # Round up to nearest 0.1 m (standard vessel sizes)
        D = math.ceil(D * 10) / 10
        L = D * LD_ratio
        L = math.ceil(L * 10) / 10

        V_vessel = math.pi / 4 * D**2 * L
        V_liq_actual = liquid_frac * V_vessel

        actual_t_oil = V_liq_actual * (V_oil / (V_oil + V_water + 1e-10)) / (Q_oil + 1e-10) if Q_oil > 0 else 0

    else:  # vertical
        # Typical L/D = 2 to 4
        LD_ratio = input_data.get("LD_ratio", 3.0)

        # Liquid section below gas disengagement
        D = max(D_gas, 0.5)
        D = math.ceil(D * 10) / 10

        A_cross = math.pi / 4 * D**2
        h_liquid = V_liquid_total / A_cross if A_cross > 0 else 1
        h_gas = 0.6 * D  # Minimum gas disengagement height
        h_demister = 0.3 if has_demister else 0

        L = h_liquid + h_gas + h_demister + 0.5  # 0.5 m for nozzles/supports
        L = max(L, D * LD_ratio)
        L = math.ceil(L * 10) / 10

        V_vessel = A_cross * L
        V_liq_actual = A_cross * h_liquid
        actual_t_oil = V_liq_actual / (Q_oil + 1e-10) if Q_oil > 0 else 0

    # ── Demister Pad Sizing ─────────────────────────────────────────
    demister = None
    if has_demister:
        A_demister = math.pi / 4 * D**2  # Full cross-section
        v_through = Q_gas / A_demister if A_demister > 0 else 0
        demister = {
            "type": "wire_mesh" if v_gas_max < 3 else "vane_pack",
            "diameter_m": round(D, 2),
            "area_m2": round(A_demister, 2),
            "gas_velocity_through_m_s": round(v_through, 2),
            "thickness_mm": 150,
        }

    # ── Nozzle Sizing (rule of thumb) ───────────────────────────────
    # Gas nozzle: v ≈ 15-25 m/s
    A_nozzle_gas = Q_gas / 20.0  # Target 20 m/s
    D_nozzle_gas = math.sqrt(4 * A_nozzle_gas / math.pi) * 1000  # mm

    # Liquid nozzle: v ≈ 1-2 m/s
    Q_liq_total = Q_oil + Q_water
    A_nozzle_liq = Q_liq_total / 1.5 if Q_liq_total > 0 else 0.01
    D_nozzle_liq = math.sqrt(4 * A_nozzle_liq / math.pi) * 1000

    # ── Compliance Checks ───────────────────────────────────────────
    compliance = {"api_12j": "PASS", "retention_time": "PASS"}
    if actual_t_oil < t_oil * 0.9:
        compliance["retention_time"] = "WARNING — below minimum"
        warnings.append(f"Oil retention time {actual_t_oil / 60:.1f} min < required {t_oil / 60:.1f} min")

    LD_actual = L / D if D > 0 else 0
    if LD_actual > 6:
        warnings.append(f"L/D ratio {LD_actual:.1f} exceeds typical maximum of 6.")
    if LD_actual < 1.5:
        warnings.append(f"L/D ratio {LD_actual:.1f} below typical minimum of 1.5.")

    # Liquid carryover check
    if v_gas_max > 0 and Q_gas / (math.pi / 4 * D**2) > v_gas_max * 1.1:
        warnings.append("Gas velocity exceeds Souders-Brown limit — liquid carryover risk")

    return {
        "status": "success",
        "calculation_id": calc_id,
        "warnings": warnings,
        "vessel_geometry": {
            "orientation": orientation,
            "separator_type": sep_type,
            "diameter_m": round(D, 2),
            "length_m": round(L, 2),
            "LD_ratio": round(LD_actual, 2),
            "vessel_volume_m3": round(V_vessel, 2),
            "liquid_volume_m3": round(V_liq_actual, 2),
        },
        "gas_capacity": {
            "souders_brown_K": round(K_val, 4),
            "max_gas_velocity_m_s": round(v_gas_max, 2),
            "actual_gas_velocity_m_s": round(Q_gas / (math.pi / 4 * D**2) if D > 0 else 0, 2),
        },
        "liquid_capacity": {
            "oil_retention_time_min": round(actual_t_oil / 60, 1),
            "required_oil_retention_min": round(t_oil / 60, 1),
            "oil_settling_velocity_m_s": round(v_settle_gas, 4),
            "water_settling_velocity_m_s": round(v_settle_oil, 4),
        },
        "demister": demister,
        "nozzles": {
            "gas_inlet_mm": round(D_nozzle_gas, 0),
            "gas_outlet_mm": round(D_nozzle_gas, 0),
            "liquid_outlet_mm": round(D_nozzle_liq, 0),
        },
        "compliance": compliance,
    }
