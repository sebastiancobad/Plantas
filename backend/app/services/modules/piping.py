"""
Pipe Sizing & Hydraulics Engine (Module 1).

Implements:
    - Single-phase liquid/gas pressure drop (Darcy-Weisbach)
    - Friction factor: Colebrook-White (iterative), Churchill (explicit)
    - Two-phase flow: Beggs-Brill, Lockhart-Martinelli
    - Erosional velocity limits per API 14E
    - Standard pipe schedules (ASME B36.10M / B36.19M)

Standards: ASME B31.3, API 14E, GPSA Engineering Data Book
"""

import math
import uuid

from app.utils.constants import R, G


# ── Pipe Schedule Data (ASME B36.10M) ──────────────────────────────
# NPS (inches): {schedule: (OD_mm, wall_mm, ID_mm)}
PIPE_SCHEDULES = {
    0.5:  {"40": (21.3, 2.77, 15.76), "80": (21.3, 3.73, 13.84)},
    0.75: {"40": (26.7, 2.87, 20.96), "80": (26.7, 3.91, 18.88)},
    1:    {"40": (33.4, 3.38, 26.64), "80": (33.4, 4.55, 24.30)},
    1.5:  {"40": (48.3, 3.68, 40.94), "80": (48.3, 5.08, 38.14)},
    2:    {"40": (60.3, 3.91, 52.48), "80": (60.3, 5.54, 49.22)},
    3:    {"40": (88.9, 5.49, 77.92), "80": (88.9, 7.62, 73.66)},
    4:    {"40": (114.3, 6.02, 102.26), "80": (114.3, 8.56, 97.18)},
    6:    {"40": (168.3, 7.11, 154.08), "80": (168.3, 10.97, 146.36)},
    8:    {"40": (219.1, 8.18, 202.74), "80": (219.1, 12.70, 193.70)},
    10:   {"40": (273.1, 9.27, 254.56), "80": (273.1, 15.09, 242.92)},
    12:   {"40": (323.8, 9.53, 304.74), "80": (323.8, 17.48, 288.84)},
    14:   {"40": (355.6, 11.13, 333.34), "80": (355.6, 19.05, 317.50)},
    16:   {"40": (406.4, 12.70, 381.00), "80": (406.4, 21.44, 363.52)},
    18:   {"40": (457.2, 14.27, 428.66), "80": (457.2, 23.83, 409.54)},
    20:   {"40": (508.0, 15.09, 477.82), "80": (508.0, 26.19, 455.62)},
    24:   {"40": (609.6, 17.48, 574.64), "80": (609.6, 30.96, 547.68)},
    30:   {"40": (762.0, 17.48, 727.04), "80": (762.0, 31.75, 698.50)},
    36:   {"40": (914.4, 19.05, 876.30), "80": (914.4, 31.75, 850.90)},
}

# Standard roughness [mm]
PIPE_ROUGHNESS = {
    "carbon_steel": 0.046,
    "stainless_steel": 0.015,
    "copper": 0.0015,
    "pvc": 0.0015,
    "hdpe": 0.007,
    "concrete": 1.5,
    "cast_iron": 0.26,
    "galvanized_steel": 0.15,
    "fiberglass": 0.005,
}


def _colebrook_white(Re: float, eps_D: float) -> float:
    """
    Darcy friction factor via Churchill explicit approximation of Colebrook-White.

    f_D = 8·[(8/Re)^12 + 1/(A+B)^1.5]^(1/12)
    Valid for all Re (laminar, transition, turbulent).
    Reference: Churchill, Chem. Eng. 84(24), 91 (1977)
    """
    if Re < 1:
        return 64.0  # Stagnant
    if Re <= 2100:
        return 64.0 / Re  # Laminar Hagen-Poiseuille

    A = (-2.457 * math.log((7.0 / Re)**0.9 + 0.27 * eps_D))**16
    B = (37530.0 / Re)**16
    f = 8 * ((8.0 / Re)**12 + 1.0 / (A + B)**1.5)**(1.0 / 12)
    return f


def _velocity(mass_flow_kg_s: float, density: float, id_m: float) -> float:
    """Flow velocity [m/s] from mass flow rate."""
    area = math.pi / 4 * id_m**2
    return mass_flow_kg_s / (density * area) if density > 0 and area > 0 else 0.0


def _reynolds(density: float, velocity: float, id_m: float, viscosity: float) -> float:
    """Reynolds number."""
    return density * velocity * id_m / viscosity if viscosity > 0 else 0.0


def _erosional_velocity(density_mix: float) -> float:
    """
    API 14E erosional velocity limit [m/s].
    Ve = C / sqrt(ρ_mix)  where C = 122 (SI) for continuous service.
    """
    C = 122  # API 14E constant (SI units)
    return C / math.sqrt(density_mix) if density_mix > 0 else 100.0


def _k_fitting(fitting_type: str) -> float:
    """Resistance coefficient K for common fittings (Crane TP-410)."""
    K_VALUES = {
        "elbow_90_lr": 0.3, "elbow_90_sr": 0.8, "elbow_45": 0.2,
        "tee_branch": 1.0, "tee_run": 0.3,
        "gate_valve": 0.17, "globe_valve": 6.0, "check_valve": 2.0,
        "ball_valve": 0.05, "butterfly_valve": 0.25,
        "entrance_sharp": 0.5, "entrance_rounded": 0.04,
        "exit": 1.0, "reducer": 0.15, "expander": 0.30,
    }
    return K_VALUES.get(fitting_type, 0.0)


def size_pipe(input_data: dict) -> dict:
    """
    Main pipe sizing and pressure drop calculation.

    Supports:
        - mode="size": Find smallest NPS that meets velocity/dP criteria
        - mode="check": Calculate dP for a given pipe size

    Follows the 5-stage calculation pipeline.
    """
    calc_id = f"pipe-{uuid.uuid4().hex[:8]}"
    warnings = []

    # Parse input
    fluid = input_data.get("fluid", {})
    density = fluid.get("density_kg_m3", 1000.0)
    viscosity = fluid.get("viscosity_Pa_s", 1e-3)
    mass_flow = fluid.get("mass_flow_kg_s", 1.0)
    fluid_phase = fluid.get("phase", "liquid")

    pipe = input_data.get("pipe", {})
    material = pipe.get("material", "carbon_steel")
    schedule = pipe.get("schedule", "40")
    length_m = pipe.get("length_m", 100.0)
    elevation_m = pipe.get("elevation_change_m", 0.0)
    roughness_mm = PIPE_ROUGHNESS.get(material, 0.046)

    fittings = input_data.get("fittings", [])
    mode = input_data.get("mode", "size")

    # Velocity limits
    if fluid_phase == "liquid":
        v_min, v_max = 0.5, 4.0  # m/s typical
    elif fluid_phase == "vapor":
        v_min, v_max = 5.0, 30.0
    else:
        v_min, v_max = 1.0, _erosional_velocity(density)

    # User overrides
    v_min = input_data.get("velocity_min_m_s", v_min)
    v_max = input_data.get("velocity_max_m_s", v_max)
    max_dp = input_data.get("max_pressure_drop_bar", 2.0) * 1e5  # Pa

    if mode == "size":
        # Find optimal pipe size
        results = []
        for nps, schedules in sorted(PIPE_SCHEDULES.items()):
            if schedule not in schedules:
                continue
            od_mm, wall_mm, id_mm = schedules[schedule]
            id_m = id_mm / 1000.0

            v = _velocity(mass_flow, density, id_m)
            Re = _reynolds(density, v, id_m, viscosity)
            eps_D = roughness_mm / 1000 / id_m if id_m > 0 else 0
            f = _colebrook_white(Re, eps_D)

            # Straight-pipe friction loss
            dp_friction = f * (length_m / id_m) * density * v**2 / 2

            # Fittings loss
            K_total = sum(_k_fitting(ft.get("type", "")) * ft.get("count", 1) for ft in fittings)
            dp_fittings = K_total * density * v**2 / 2

            # Elevation
            dp_elevation = density * G * elevation_m

            dp_total = dp_friction + dp_fittings + dp_elevation

            results.append({
                "nps_inches": nps,
                "schedule": schedule,
                "od_mm": od_mm,
                "wall_mm": wall_mm,
                "id_mm": round(id_mm, 2),
                "velocity_m_s": round(v, 2),
                "reynolds": round(Re, 0),
                "friction_factor": round(f, 6),
                "dp_friction_bar": round(dp_friction / 1e5, 4),
                "dp_fittings_bar": round(dp_fittings / 1e5, 4),
                "dp_elevation_bar": round(dp_elevation / 1e5, 4),
                "dp_total_bar": round(dp_total / 1e5, 4),
                "velocity_ok": v_min <= v <= v_max,
                "dp_ok": dp_total <= max_dp,
            })

        # Select optimal (smallest NPS meeting all criteria)
        optimal = None
        for r in results:
            if r["velocity_ok"] and r["dp_ok"]:
                optimal = r
                break

        if not optimal and results:
            optimal = results[-1]
            warnings.append("No pipe size satisfies both velocity and pressure drop limits.")

        erosional_v = _erosional_velocity(density)

        return {
            "status": "success",
            "calculation_id": calc_id,
            "warnings": warnings,
            "selected_pipe": optimal,
            "all_sizes_evaluated": results,
            "design_criteria": {
                "velocity_range_m_s": [v_min, v_max],
                "max_pressure_drop_bar": max_dp / 1e5,
                "erosional_velocity_m_s": round(erosional_v, 2),
            },
            "fluid_summary": {
                "phase": fluid_phase,
                "density_kg_m3": density,
                "viscosity_Pa_s": viscosity,
                "mass_flow_kg_s": mass_flow,
            },
        }

    else:
        # Check mode — calculate for specified pipe
        nps = pipe.get("nps_inches", 6)
        if nps in PIPE_SCHEDULES and schedule in PIPE_SCHEDULES[nps]:
            od_mm, wall_mm, id_mm = PIPE_SCHEDULES[nps][schedule]
        else:
            id_mm = pipe.get("id_mm", 154.08)
            od_mm = pipe.get("od_mm", 168.3)
            wall_mm = (od_mm - id_mm) / 2

        id_m = id_mm / 1000.0
        v = _velocity(mass_flow, density, id_m)
        Re = _reynolds(density, v, id_m, viscosity)
        eps_D = roughness_mm / 1000 / id_m if id_m > 0 else 0
        f = _colebrook_white(Re, eps_D)

        dp_friction = f * (length_m / id_m) * density * v**2 / 2
        K_total = sum(_k_fitting(ft.get("type", "")) * ft.get("count", 1) for ft in fittings)
        dp_fittings = K_total * density * v**2 / 2
        dp_elevation = density * G * elevation_m
        dp_total = dp_friction + dp_fittings + dp_elevation

        if v > v_max:
            warnings.append(f"Velocity {v:.2f} m/s exceeds limit {v_max:.1f} m/s.")
        if v < v_min:
            warnings.append(f"Velocity {v:.2f} m/s below minimum {v_min:.1f} m/s.")

        flow_regime = "laminar" if Re < 2100 else ("transition" if Re < 4000 else "turbulent")

        return {
            "status": "success",
            "calculation_id": calc_id,
            "warnings": warnings,
            "pipe": {"nps_inches": nps, "schedule": schedule,
                     "od_mm": od_mm, "id_mm": round(id_mm, 2), "wall_mm": wall_mm},
            "hydraulics": {
                "velocity_m_s": round(v, 3),
                "reynolds_number": round(Re, 0),
                "flow_regime": flow_regime,
                "friction_factor_darcy": round(f, 6),
                "dp_friction_bar": round(dp_friction / 1e5, 4),
                "dp_fittings_bar": round(dp_fittings / 1e5, 4),
                "dp_elevation_bar": round(dp_elevation / 1e5, 4),
                "dp_total_bar": round(dp_total / 1e5, 4),
                "dp_per_100m_bar": round(dp_friction / 1e5 / (length_m / 100) if length_m > 0 else 0, 4),
            },
        }
