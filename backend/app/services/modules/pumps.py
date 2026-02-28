"""
Pump Selection & Sizing Engine (Module 5).

Implements:
    - System head curve generation (static + friction + velocity head)
    - NPSH available vs required calculation
    - Centrifugal pump selection (specific speed, efficiency)
    - Positive displacement pump selection
    - Affinity laws for speed/impeller changes
    - Power and driver sizing

Standards: API 610, Hydraulic Institute (HI), ASME B73.1
"""

import math
import uuid

from app.utils.constants import G


# ── Pump Performance Data ───────────────────────────────────────────
# Typical centrifugal pump efficiency ranges by specific speed
# Ns = N·Q^0.5 / H^0.75  (US units: rpm, gpm, ft)
PUMP_EFFICIENCY = {
    # (Ns_min, Ns_max, peak_efficiency)
    "radial":     (500, 1500, 0.78),
    "mixed_flow": (1500, 4000, 0.85),
    "axial":      (4000, 15000, 0.87),
}


def _system_head(Q_m3s: float, static_head_m: float, pipe_data: list[dict],
                  density: float, viscosity: float) -> float:
    """
    Calculate total system head [m] at a given flow rate.

    H_sys = H_static + H_friction(Q) + H_velocity
    """
    H_static = static_head_m

    # Friction head from each pipe segment
    H_friction = 0.0
    for seg in pipe_data:
        D = seg.get("id_m", 0.1)
        L = seg.get("length_m", 100)
        eps = seg.get("roughness_m", 4.6e-5)
        K_fittings = seg.get("K_fittings", 0)

        A = math.pi / 4 * D**2
        v = Q_m3s / A if A > 0 else 0
        Re = density * v * D / viscosity if viscosity > 0 else 0

        # Churchill friction factor
        if Re < 1:
            f = 0
        elif Re <= 2100:
            f = 64.0 / Re
        else:
            eps_D = eps / D if D > 0 else 0
            Af = (-2.457 * math.log((7.0 / Re)**0.9 + 0.27 * eps_D))**16
            Bf = (37530.0 / Re)**16
            f = 8 * ((8.0 / Re)**12 + 1.0 / (Af + Bf)**1.5)**(1.0 / 12)

        h_pipe = f * (L / D) * v**2 / (2 * G) if D > 0 else 0
        h_fittings = K_fittings * v**2 / (2 * G)
        H_friction += h_pipe + h_fittings

    # Velocity head at discharge
    if pipe_data:
        D_disch = pipe_data[-1].get("id_m", 0.1)
        v_disch = Q_m3s / (math.pi / 4 * D_disch**2) if D_disch > 0 else 0
        H_velocity = v_disch**2 / (2 * G)
    else:
        H_velocity = 0

    return H_static + H_friction + H_velocity


def _npsh_available(P_suction_Pa: float, P_vapor_Pa: float,
                     h_suction_m: float, h_friction_suction_m: float,
                     density: float) -> float:
    """NPSH available [m] = (P_s - P_v) / (ρg) + h_s - h_f_s"""
    return (P_suction_Pa - P_vapor_Pa) / (density * G) + h_suction_m - h_friction_suction_m


def _specific_speed(N_rpm: float, Q_m3s: float, H_m: float) -> float:
    """
    Specific speed (metric): Ns = N·Q^0.5 / H^0.75
    N in rpm, Q in m³/s, H in m.
    """
    if H_m <= 0 or Q_m3s <= 0:
        return 0
    return N_rpm * Q_m3s**0.5 / H_m**0.75


def _pump_efficiency(Ns_metric: float, Q_m3s: float) -> float:
    """Estimate pump efficiency from specific speed and flow rate."""
    Q_gpm = Q_m3s * 15850.3  # Convert to US GPM for correlation
    # Correlation from HI standards (simplified)
    if Q_gpm < 50:
        eta_base = 0.40
    elif Q_gpm < 200:
        eta_base = 0.55
    elif Q_gpm < 1000:
        eta_base = 0.70
    elif Q_gpm < 5000:
        eta_base = 0.80
    else:
        eta_base = 0.85

    # Adjust for Ns
    if Ns_metric < 15:
        eta_base *= 0.85
    elif Ns_metric > 80:
        eta_base *= 0.95

    return min(eta_base, 0.90)


def _affinity_laws(Q1: float, H1: float, P1: float,
                    N1: float, N2: float) -> dict:
    """
    Affinity laws for centrifugal pumps.

    Q₂/Q₁ = N₂/N₁
    H₂/H₁ = (N₂/N₁)²
    P₂/P₁ = (N₂/N₁)³
    """
    ratio = N2 / N1 if N1 > 0 else 1
    return {
        "Q2_m3_s": Q1 * ratio,
        "H2_m": H1 * ratio**2,
        "P2_kW": P1 * ratio**3,
        "speed_ratio": ratio,
    }


def size_pump(input_data: dict) -> dict:
    """
    Complete pump sizing calculation.

    Steps:
    1. Generate system curve H_sys(Q)
    2. Calculate operating point
    3. Compute NPSH_a and compare to NPSH_r
    4. Select pump type (centrifugal vs PD)
    5. Calculate power and motor sizing
    """
    calc_id = f"pump-{uuid.uuid4().hex[:8]}"
    warnings = []

    # Parse input
    fluid = input_data.get("fluid", {})
    density = fluid.get("density_kg_m3", 1000.0)
    viscosity = fluid.get("viscosity_Pa_s", 1e-3)
    P_vapor = fluid.get("vapor_pressure_Pa", 3170)  # Water at 25°C default

    flow = input_data.get("flow", {})
    Q_design = flow.get("design_flow_m3_s", 0.01)
    Q_rated = Q_design * flow.get("rated_factor", 1.10)  # API 610: rate at 110%

    suction = input_data.get("suction", {})
    P_suction = suction.get("pressure_Pa", 101325)
    h_suction = suction.get("static_head_m", 2.0)
    h_friction_s = suction.get("friction_loss_m", 0.5)

    discharge = input_data.get("discharge", {})
    P_discharge = discharge.get("pressure_Pa", 500000)
    h_static = discharge.get("static_head_m", 20.0)

    pipe_segments = input_data.get("pipe_segments", [
        {"id_m": 0.1, "length_m": 200, "roughness_m": 4.6e-5, "K_fittings": 10},
    ])

    speed_rpm = input_data.get("speed_rpm", 2950)  # 2-pole motor at 50Hz

    # ── Total Dynamic Head ──────────────────────────────────────────
    # Differential pressure head
    H_pressure = (P_discharge - P_suction) / (density * G)
    H_system = _system_head(Q_rated, h_static, pipe_segments, density, viscosity)
    TDH = max(H_pressure, H_system)

    # ── NPSH Analysis ───────────────────────────────────────────────
    NPSH_a = _npsh_available(P_suction, P_vapor, h_suction, h_friction_s, density)
    NPSH_r_estimated = 3.0 + 0.3 * Q_rated * 15850.3 / 1000  # Rough estimate
    NPSH_margin = NPSH_a - NPSH_r_estimated

    if NPSH_margin < 1.0:
        warnings.append(f"NPSH margin ({NPSH_margin:.1f} m) is below 1.0 m — cavitation risk.")
    if NPSH_a < NPSH_r_estimated:
        warnings.append("NPSH_available < NPSH_required — pump WILL cavitate!")

    # ── Pump Type Selection ─────────────────────────────────────────
    Ns = _specific_speed(speed_rpm, Q_rated, TDH)
    eta = _pump_efficiency(Ns, Q_rated)

    # Selection criteria
    if Q_rated < 0.0001 or TDH > 1000:
        pump_type = "positive_displacement"
        pump_subtype = "reciprocating" if TDH > 500 else "gear"
    elif viscosity > 0.5:
        pump_type = "positive_displacement"
        pump_subtype = "screw" if Q_rated > 0.01 else "gear"
    else:
        pump_type = "centrifugal"
        if Ns < 15:
            pump_subtype = "radial"
        elif Ns < 80:
            pump_subtype = "mixed_flow"
        else:
            pump_subtype = "axial_flow"

    # ── Power Calculation ───────────────────────────────────────────
    hydraulic_power = density * G * Q_rated * TDH / 1000  # kW
    brake_power = hydraulic_power / eta if eta > 0 else hydraulic_power
    motor_power = brake_power / 0.95  # Motor efficiency ~95%

    # Motor sizing: next standard size up
    STD_MOTORS = [0.75, 1.1, 1.5, 2.2, 3.0, 4.0, 5.5, 7.5, 11, 15,
                  18.5, 22, 30, 37, 45, 55, 75, 90, 110, 132, 160, 200, 250, 315]
    selected_motor = motor_power
    for m in STD_MOTORS:
        if m >= motor_power:
            selected_motor = m
            break

    # ── System Curve Points ─────────────────────────────────────────
    system_curve = []
    for frac in [0, 0.25, 0.5, 0.75, 1.0, 1.1, 1.2]:
        Q_pt = Q_rated * frac
        H_pt = _system_head(Q_pt, h_static, pipe_segments, density, viscosity)
        system_curve.append({"Q_m3_s": round(Q_pt, 5), "H_m": round(max(H_pt, h_static), 2)})

    # ── Affinity Law Predictions ────────────────────────────────────
    affinity = None
    if input_data.get("alternate_speed_rpm"):
        N2 = input_data["alternate_speed_rpm"]
        affinity = _affinity_laws(Q_rated, TDH, brake_power, speed_rpm, N2)

    return {
        "status": "success",
        "calculation_id": calc_id,
        "warnings": warnings,
        "operating_point": {
            "design_flow_m3_s": round(Q_design, 5),
            "rated_flow_m3_s": round(Q_rated, 5),
            "total_dynamic_head_m": round(TDH, 2),
            "differential_pressure_bar": round(TDH * density * G / 1e5, 2),
        },
        "npsh": {
            "npsh_available_m": round(NPSH_a, 2),
            "npsh_required_m": round(NPSH_r_estimated, 2),
            "npsh_margin_m": round(NPSH_margin, 2),
            "status": "PASS" if NPSH_margin >= 1.0 else "FAIL",
        },
        "pump_selection": {
            "type": pump_type,
            "subtype": pump_subtype,
            "specific_speed_metric": round(Ns, 1),
            "efficiency_percent": round(eta * 100, 1),
            "speed_rpm": speed_rpm,
        },
        "power": {
            "hydraulic_kW": round(hydraulic_power, 2),
            "brake_kW": round(brake_power, 2),
            "motor_kW": round(motor_power, 2),
            "selected_motor_kW": selected_motor,
        },
        "system_curve": system_curve,
        "affinity_law": affinity,
    }
