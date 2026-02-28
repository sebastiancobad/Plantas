"""
Component Database Service.

Provides lookup and query functions for chemical components.
Includes seed data for the most commonly used compounds in
oil & gas and petrochemical engineering.

The seed data covers critical properties sourced from DIPPR / NIST.
Temperature-dependent correlation coefficients are placeholders
for MVP and will be populated from validated DIPPR data.
"""

from app.services.thermo.eos import ComponentProps


# ──────────────────────────────────────────────────────────────────────
# Seed Data: Core Compounds (Critical Properties)
#
# Sources: DIPPR 801, Perry's Chemical Engineers' Handbook (9th ed.)
# Tc [K], Pc [Pa], ω [-], Mw [g/mol]
# ──────────────────────────────────────────────────────────────────────

SEED_COMPONENTS: dict[str, dict] = {
    # ── Light Gases ──
    "hydrogen": {
        "formula": "H2", "cas": "1333-74-0",
        "Mw": 2.016, "Tc": 33.19, "Pc": 1313000, "omega": -0.216,
        "Tb": 20.39, "Tm": 14.01,
    },
    "nitrogen": {
        "formula": "N2", "cas": "7727-37-9",
        "Mw": 28.014, "Tc": 126.20, "Pc": 3390000, "omega": 0.037,
        "Tb": 77.36, "Tm": 63.15,
    },
    "oxygen": {
        "formula": "O2", "cas": "7782-44-7",
        "Mw": 31.999, "Tc": 154.58, "Pc": 5043000, "omega": 0.022,
        "Tb": 90.19, "Tm": 54.36,
    },
    "carbon_dioxide": {
        "formula": "CO2", "cas": "124-38-9",
        "Mw": 44.010, "Tc": 304.13, "Pc": 7375000, "omega": 0.225,
        "Tb": 194.65, "Tm": 216.55,
    },
    "hydrogen_sulfide": {
        "formula": "H2S", "cas": "7783-06-4",
        "Mw": 34.081, "Tc": 373.53, "Pc": 8963000, "omega": 0.094,
        "Tb": 212.84, "Tm": 187.68,
    },
    "ammonia": {
        "formula": "NH3", "cas": "7664-41-7",
        "Mw": 17.031, "Tc": 405.40, "Pc": 11353000, "omega": 0.256,
        "Tb": 239.82, "Tm": 195.41,
    },

    # ── Water & Common Solvents ──
    "water": {
        "formula": "H2O", "cas": "7732-18-5",
        "Mw": 18.015, "Tc": 647.10, "Pc": 22064000, "omega": 0.345,
        "Tb": 373.15, "Tm": 273.15,
    },
    "methanol": {
        "formula": "CH3OH", "cas": "67-56-1",
        "Mw": 32.042, "Tc": 512.64, "Pc": 8097000, "omega": 0.565,
        "Tb": 337.69, "Tm": 175.47,
    },
    "ethanol": {
        "formula": "C2H5OH", "cas": "64-17-5",
        "Mw": 46.069, "Tc": 513.92, "Pc": 6148000, "omega": 0.649,
        "Tb": 351.44, "Tm": 159.05,
    },
    "acetone": {
        "formula": "C3H6O", "cas": "67-64-1",
        "Mw": 58.080, "Tc": 508.10, "Pc": 4700000, "omega": 0.307,
        "Tb": 329.22, "Tm": 178.45,
    },

    # ── Paraffins (Alkanes) ──
    "methane": {
        "formula": "CH4", "cas": "74-82-8",
        "Mw": 16.043, "Tc": 190.56, "Pc": 4599000, "omega": 0.011,
        "Tb": 111.66, "Tm": 90.69,
    },
    "ethane": {
        "formula": "C2H6", "cas": "74-84-0",
        "Mw": 30.070, "Tc": 305.32, "Pc": 4872000, "omega": 0.099,
        "Tb": 184.55, "Tm": 90.37,
    },
    "propane": {
        "formula": "C3H8", "cas": "74-98-6",
        "Mw": 44.096, "Tc": 369.83, "Pc": 4248000, "omega": 0.152,
        "Tb": 231.11, "Tm": 85.47,
    },
    "n-butane": {
        "formula": "C4H10", "cas": "106-97-8",
        "Mw": 58.123, "Tc": 425.12, "Pc": 3796000, "omega": 0.200,
        "Tb": 272.65, "Tm": 134.86,
    },
    "isobutane": {
        "formula": "C4H10", "cas": "75-28-5",
        "Mw": 58.123, "Tc": 407.81, "Pc": 3640000, "omega": 0.181,
        "Tb": 261.43, "Tm": 113.73,
    },
    "n-pentane": {
        "formula": "C5H12", "cas": "109-66-0",
        "Mw": 72.150, "Tc": 469.70, "Pc": 3370000, "omega": 0.251,
        "Tb": 309.22, "Tm": 143.42,
    },
    "n-hexane": {
        "formula": "C6H14", "cas": "110-54-3",
        "Mw": 86.177, "Tc": 507.60, "Pc": 3025000, "omega": 0.301,
        "Tb": 341.88, "Tm": 177.83,
    },
    "n-heptane": {
        "formula": "C7H16", "cas": "142-82-5",
        "Mw": 100.204, "Tc": 540.20, "Pc": 2740000, "omega": 0.350,
        "Tb": 371.58, "Tm": 182.57,
    },
    "n-octane": {
        "formula": "C8H18", "cas": "111-65-9",
        "Mw": 114.231, "Tc": 568.70, "Pc": 2490000, "omega": 0.399,
        "Tb": 398.83, "Tm": 216.38,
    },
    "n-nonane": {
        "formula": "C9H20", "cas": "111-84-2",
        "Mw": 128.258, "Tc": 594.60, "Pc": 2290000, "omega": 0.443,
        "Tb": 423.97, "Tm": 219.66,
    },
    "n-decane": {
        "formula": "C10H22", "cas": "124-18-5",
        "Mw": 142.285, "Tc": 617.70, "Pc": 2110000, "omega": 0.492,
        "Tb": 447.31, "Tm": 243.51,
    },

    # ── Olefins ──
    "ethylene": {
        "formula": "C2H4", "cas": "74-85-1",
        "Mw": 28.054, "Tc": 282.34, "Pc": 5041000, "omega": 0.087,
        "Tb": 169.42, "Tm": 104.00,
    },
    "propylene": {
        "formula": "C3H6", "cas": "115-07-1",
        "Mw": 42.081, "Tc": 364.90, "Pc": 4600000, "omega": 0.142,
        "Tb": 225.46, "Tm": 87.90,
    },

    # ── Aromatics ──
    "benzene": {
        "formula": "C6H6", "cas": "71-43-2",
        "Mw": 78.114, "Tc": 562.05, "Pc": 4895000, "omega": 0.210,
        "Tb": 353.24, "Tm": 278.68,
    },
    "toluene": {
        "formula": "C7H8", "cas": "108-88-3",
        "Mw": 92.141, "Tc": 591.75, "Pc": 4108000, "omega": 0.264,
        "Tb": 383.78, "Tm": 178.18,
    },
    "xylene_p": {
        "formula": "C8H10", "cas": "106-42-3",
        "Mw": 106.167, "Tc": 616.20, "Pc": 3511000, "omega": 0.322,
        "Tb": 411.51, "Tm": 286.41,
    },

    # ── Acid Gases & Inorganics ──
    "carbon_monoxide": {
        "formula": "CO", "cas": "630-08-0",
        "Mw": 28.010, "Tc": 132.85, "Pc": 3494000, "omega": 0.048,
        "Tb": 81.66, "Tm": 68.15,
    },
    "sulfur_dioxide": {
        "formula": "SO2", "cas": "7446-09-5",
        "Mw": 64.065, "Tc": 430.80, "Pc": 7884000, "omega": 0.245,
        "Tb": 263.13, "Tm": 197.69,
    },
}


def get_component(name: str) -> ComponentProps:
    """
    Retrieve a ComponentProps object by name (case-insensitive).

    Raises KeyError if component not found.
    """
    key = name.lower().replace(" ", "_")
    # Try multiple key formats: original, underscored, hyphenated
    candidates = [
        key,
        key.replace("-", "_"),
        key.replace("_", "-"),
        f"n_{key}",
        f"n-{key}",
    ]
    for candidate in candidates:
        if candidate in SEED_COMPONENTS:
            data = SEED_COMPONENTS[candidate]
            return ComponentProps(
                name=name,
                Tc=data["Tc"],
                Pc=data["Pc"],
                omega=data["omega"],
                Mw=data["Mw"],
            )
    raise KeyError(f"Component '{name}' not found in database. Available: {list(SEED_COMPONENTS.keys())}")


def list_components() -> list[str]:
    """Return sorted list of all available component names."""
    return sorted(SEED_COMPONENTS.keys())


def get_component_data(name: str) -> dict:
    """Return full seed data dict for a component."""
    key = name.lower().replace(" ", "_")
    for candidate in [key, key.replace("-", "_"), key.replace("_", "-"),
                      f"n_{key}", f"n-{key}"]:
        if candidate in SEED_COMPONENTS:
            return SEED_COMPONENTS[candidate]
    raise KeyError(f"Component '{name}' not found")
