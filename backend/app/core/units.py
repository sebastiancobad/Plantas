"""
ChemScale Unit Conversion Engine.

Wraps the `pint` library to provide a centralized, consistent
unit registry for the entire application. All modules MUST use
this registry to avoid unit mismatch errors.

Supported unit systems: SI, US Customary, and common process-eng units.
"""

import pint

ureg = pint.UnitRegistry()
Q_ = ureg.Quantity

# ── Common aliases for process engineering ──────────────────────────
ureg.define("barg = bar")
ureg.define("psig = psi")

# Precomputed conversion factors for hot-path calculations
PSI_TO_PA = Q_(1, "psi").to("Pa").magnitude            # 6894.76
BAR_TO_PA = Q_(1, "bar").to("Pa").magnitude             # 100000
BTU_HR_TO_W = Q_(1, "BTU/hr").to("W").magnitude         # 0.29307
USGPM_TO_M3S = Q_(1, "gallon/min").to("m**3/s").magnitude


def convert(value: float, from_unit: str, to_unit: str) -> float:
    """Convert a scalar value between two compatible unit strings."""
    return Q_(value, from_unit).to(to_unit).magnitude
