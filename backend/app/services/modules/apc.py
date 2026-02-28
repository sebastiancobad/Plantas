"""
Advanced Process Control Engine (Module 10).

Implements:
    - PID tuning parameter estimation (Ziegler-Nichols, Cohen-Coon, Lambda)
    - Control strategy selection matrices (cascade, feedforward, ratio, MPC)
    - Standard control loop configurations for unit operations
    - ISA function block definitions

Standards: ISA-5.1, ISA-95, ISA-88
"""

import math
import uuid


# ── First-Order Plus Dead Time (FOPDT) Tuning Methods ──────────────

def _ziegler_nichols_tuning(K: float, tau: float, theta: float,
                             loop_type: str = "PI") -> dict:
    """
    Ziegler-Nichols open-loop tuning (reaction curve method).

    Args:
        K: Process gain
        tau: Time constant [s]
        theta: Dead time [s]
        loop_type: "P", "PI", or "PID"
    """
    ratio = tau / theta if theta > 0 else 100
    if loop_type == "P":
        Kc = 1.0 / K * ratio
        return {"Kc": round(Kc, 3), "Ti": None, "Td": None, "method": "Ziegler-Nichols"}
    elif loop_type == "PI":
        Kc = 0.9 / K * ratio
        Ti = 3.33 * theta
        return {"Kc": round(Kc, 3), "Ti": round(Ti, 2), "Td": None, "method": "Ziegler-Nichols"}
    else:  # PID
        Kc = 1.2 / K * ratio
        Ti = 2.0 * theta
        Td = 0.5 * theta
        return {"Kc": round(Kc, 3), "Ti": round(Ti, 2), "Td": round(Td, 2), "method": "Ziegler-Nichols"}


def _cohen_coon_tuning(K: float, tau: float, theta: float,
                        loop_type: str = "PI") -> dict:
    """
    Cohen-Coon tuning — better for processes with larger dead time.
    """
    r = theta / tau if tau > 0 else 0.5
    if loop_type == "PI":
        Kc = (1.0 / K) * (tau / theta) * (0.9 + r / 12)
        Ti = theta * (30 + 3 * r) / (9 + 20 * r)
        return {"Kc": round(Kc, 3), "Ti": round(Ti, 2), "Td": None, "method": "Cohen-Coon"}
    else:  # PID
        Kc = (1.0 / K) * (tau / theta) * (4.0/3 + r / 4)
        Ti = theta * (32 + 6 * r) / (13 + 8 * r)
        Td = theta * 4.0 / (11 + 2 * r)
        return {"Kc": round(Kc, 3), "Ti": round(Ti, 2), "Td": round(Td, 2), "method": "Cohen-Coon"}


def _lambda_tuning(K: float, tau: float, theta: float,
                    lambda_factor: float = 3.0) -> dict:
    """
    Lambda (IMC-based) tuning — most robust, adjustable aggressiveness.

    Lambda = desired closed-loop time constant = lambda_factor × theta
    """
    lam = lambda_factor * theta
    Kc = tau / (K * (lam + theta))
    Ti = tau
    return {"Kc": round(Kc, 3), "Ti": round(Ti, 2), "Td": None,
            "lambda_factor": lambda_factor, "method": "Lambda (IMC)"}


# ── Control Strategy Selection Matrix ───────────────────────────────

CONTROL_STRATEGIES = {
    "heat_exchanger": {
        "primary": "Feedback PID — outlet temperature controlling cooling water flow",
        "enhanced": "Cascade — outlet temp (master) → CW flow (slave) with flow controller",
        "advanced": "Feedforward — compensate for process-side flow disturbances",
        "typical_loops": [
            {"tag": "TIC", "variable": "Outlet temperature", "manipulated": "CW flow valve", "type": "PID"},
            {"tag": "FIC", "variable": "CW flow rate", "manipulated": "CW flow valve", "type": "Cascade slave"},
        ],
    },
    "distillation_column": {
        "primary": "Multi-loop PID — composition (or T) at top and bottom",
        "enhanced": "DV control (reflux controls top, boilup controls bottom)",
        "advanced": "MPC — multivariable predictive control for coupled variables",
        "typical_loops": [
            {"tag": "TIC", "variable": "Tray temperature (top)", "manipulated": "Reflux flow", "type": "PID"},
            {"tag": "TIC", "variable": "Tray temperature (bottom)", "manipulated": "Reboiler duty", "type": "PID"},
            {"tag": "LIC", "variable": "Reflux drum level", "manipulated": "Distillate flow", "type": "PID"},
            {"tag": "LIC", "variable": "Sump level", "manipulated": "Bottoms flow", "type": "PID"},
            {"tag": "PIC", "variable": "Column pressure", "manipulated": "Condenser duty", "type": "PID"},
            {"tag": "FIC", "variable": "Feed flow", "manipulated": "Feed valve", "type": "PID"},
        ],
    },
    "reactor": {
        "primary": "Feedback PID — temperature control",
        "enhanced": "Cascade — reactor temp (master) → coolant flow (slave)",
        "advanced": "MPC with inferential composition control",
        "typical_loops": [
            {"tag": "TIC", "variable": "Reactor temperature", "manipulated": "Coolant flow", "type": "Cascade"},
            {"tag": "PIC", "variable": "Reactor pressure", "manipulated": "Vent valve", "type": "PID"},
            {"tag": "FIC", "variable": "Reactant flow", "manipulated": "Feed valve", "type": "Ratio"},
            {"tag": "LIC", "variable": "Reactor level", "manipulated": "Product flow", "type": "PID"},
        ],
    },
    "compressor": {
        "primary": "Anti-surge control with recycle valve",
        "enhanced": "Performance control — maintain efficiency on compressor map",
        "advanced": "MPC for multi-compressor load optimization",
        "typical_loops": [
            {"tag": "FIC", "variable": "Suction flow", "manipulated": "Anti-surge valve", "type": "PID"},
            {"tag": "PIC", "variable": "Discharge pressure", "manipulated": "Speed/guide vanes", "type": "PID"},
            {"tag": "TIC", "variable": "Discharge temperature", "manipulated": "Intercooler", "type": "PID"},
        ],
    },
    "separator": {
        "primary": "Level and pressure control",
        "enhanced": "Interface level control (3-phase)",
        "advanced": "Feedforward from upstream flow changes",
        "typical_loops": [
            {"tag": "LIC", "variable": "Oil/gas interface level", "manipulated": "Oil outlet valve", "type": "PID"},
            {"tag": "LIC", "variable": "Oil/water interface level", "manipulated": "Water outlet valve", "type": "PID"},
            {"tag": "PIC", "variable": "Separator pressure", "manipulated": "Gas outlet valve", "type": "PID"},
        ],
    },
    "pump": {
        "primary": "Discharge pressure or flow control",
        "enhanced": "Minimum flow protection with recirculation",
        "advanced": "Variable speed drive (VSD) for energy optimization",
        "typical_loops": [
            {"tag": "FIC", "variable": "Discharge flow", "manipulated": "Discharge valve or VSD", "type": "PID"},
            {"tag": "PIC", "variable": "Discharge pressure", "manipulated": "Discharge valve", "type": "PID"},
        ],
    },
    "fired_heater": {
        "primary": "Process outlet temperature control via fuel gas",
        "enhanced": "Cross-limiting combustion control (fuel/air ratio)",
        "advanced": "O₂ trim + stack temperature optimization",
        "typical_loops": [
            {"tag": "TIC", "variable": "Process outlet temperature", "manipulated": "Fuel gas valve", "type": "PID"},
            {"tag": "FIC", "variable": "Fuel gas flow", "manipulated": "Fuel valve", "type": "PID"},
            {"tag": "FIC", "variable": "Combustion air flow", "manipulated": "Air damper", "type": "Ratio"},
            {"tag": "AIC", "variable": "Excess O₂ in stack", "manipulated": "Air damper trim", "type": "PID"},
        ],
    },
}


def tune_pid_loop(input_data: dict) -> dict:
    """
    Calculate PID tuning parameters for a given FOPDT process model.
    """
    calc_id = f"apc-{uuid.uuid4().hex[:8]}"

    K = input_data.get("process_gain", 1.0)
    tau = input_data.get("time_constant_s", 60.0)
    theta = input_data.get("dead_time_s", 10.0)
    loop_type = input_data.get("controller_type", "PID")

    # Calculate using all methods
    zn = _ziegler_nichols_tuning(K, tau, theta, loop_type)
    cc = _cohen_coon_tuning(K, tau, theta, loop_type)
    lam = _lambda_tuning(K, tau, theta, input_data.get("lambda_factor", 3.0))

    # Controllability ratio
    ratio = theta / tau if tau > 0 else float('inf')
    if ratio < 0.1:
        difficulty = "easy"
    elif ratio < 0.3:
        difficulty = "moderate"
    elif ratio < 0.7:
        difficulty = "difficult"
    else:
        difficulty = "very_difficult"

    # Recommendation
    if ratio < 0.3:
        recommended = "Ziegler-Nichols or Lambda"
    elif ratio < 0.7:
        recommended = "Lambda (conservative) or Cohen-Coon"
    else:
        recommended = "Lambda with high lambda_factor (≥5), consider cascade or feedforward"

    return {
        "status": "success",
        "calculation_id": calc_id,
        "process_model": {
            "gain_K": K,
            "time_constant_tau_s": tau,
            "dead_time_theta_s": theta,
            "dead_time_ratio": round(ratio, 3),
            "controllability": difficulty,
        },
        "tuning_results": {
            "ziegler_nichols": zn,
            "cohen_coon": cc,
            "lambda_imc": lam,
        },
        "recommendation": recommended,
    }


def get_control_strategy(input_data: dict) -> dict:
    """
    Get recommended control strategy for a unit operation.
    """
    unit_type = input_data.get("unit_type", "heat_exchanger")
    strategy = CONTROL_STRATEGIES.get(unit_type)

    if not strategy:
        return {
            "status": "error",
            "message": f"No strategy defined for '{unit_type}'. "
                       f"Available: {list(CONTROL_STRATEGIES.keys())}",
        }

    return {
        "status": "success",
        "unit_type": unit_type,
        "strategy": strategy,
        "available_unit_types": list(CONTROL_STRATEGIES.keys()),
    }
