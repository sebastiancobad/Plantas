"""
Plant Layout & Location Engine (Module 3).

Implements:
    - Intra-plant spacing tables (API 2510, NFPA 30, PIP STC01015)
    - Equipment spacing matrix for passive safety
    - Plot plan area estimation
    - Road and access requirements

Standards: API 2510, NFPA 30, PIP STC01015, API RP 752
"""

import uuid


# ── Minimum Spacing Table (meters) ──────────────────────────────────
# Source: API 2510 Table 2, PIP STC01015 Table 1
# Format: SPACING[type_A][type_B] = distance in meters
# Symmetric: SPACING[A][B] = SPACING[B][A]

EQUIPMENT_TYPES = [
    "process_unit", "fired_heater", "compressor", "pump",
    "pressure_vessel", "atmospheric_tank", "pressurized_storage",
    "flare", "cooling_tower", "control_room", "substation",
    "loading_rack", "pipe_rack", "heat_exchanger",
]

# Minimum distances in meters
SPACING_MATRIX = {
    ("process_unit", "fired_heater"): 15,
    ("process_unit", "compressor"): 15,
    ("process_unit", "pump"): 4.5,
    ("process_unit", "pressure_vessel"): 3,
    ("process_unit", "atmospheric_tank"): 30,
    ("process_unit", "pressurized_storage"): 60,
    ("process_unit", "flare"): 60,
    ("process_unit", "cooling_tower"): 15,
    ("process_unit", "control_room"): 15,
    ("process_unit", "substation"): 15,
    ("process_unit", "loading_rack"): 30,
    ("process_unit", "pipe_rack"): 3,
    ("process_unit", "heat_exchanger"): 3,
    ("fired_heater", "compressor"): 15,
    ("fired_heater", "pump"): 15,
    ("fired_heater", "pressure_vessel"): 15,
    ("fired_heater", "atmospheric_tank"): 30,
    ("fired_heater", "pressurized_storage"): 60,
    ("fired_heater", "flare"): 60,
    ("fired_heater", "cooling_tower"): 15,
    ("fired_heater", "control_room"): 30,
    ("compressor", "pump"): 4.5,
    ("compressor", "pressure_vessel"): 4.5,
    ("compressor", "atmospheric_tank"): 30,
    ("compressor", "pressurized_storage"): 60,
    ("atmospheric_tank", "pressurized_storage"): 30,
    ("atmospheric_tank", "flare"): 60,
    ("atmospheric_tank", "control_room"): 60,
    ("pressurized_storage", "flare"): 60,
    ("pressurized_storage", "control_room"): 100,
    ("pressurized_storage", "loading_rack"): 30,
    ("flare", "control_room"): 100,
    ("flare", "cooling_tower"): 30,
    ("control_room", "substation"): 15,
    ("cooling_tower", "control_room"): 30,
    ("pump", "heat_exchanger"): 3,
    ("pressure_vessel", "heat_exchanger"): 3,
}

# Default minimum spacing when not in table
DEFAULT_SPACING = 7.5


def get_spacing(type_a: str, type_b: str) -> float:
    """Look up minimum spacing [m] between two equipment types."""
    key = (type_a, type_b)
    if key in SPACING_MATRIX:
        return SPACING_MATRIX[key]
    key_rev = (type_b, type_a)
    if key_rev in SPACING_MATRIX:
        return SPACING_MATRIX[key_rev]
    if type_a == type_b:
        return 3.0
    return DEFAULT_SPACING


def generate_layout(input_data: dict) -> dict:
    """
    Generate plant layout with spacing analysis and plot plan estimate.
    """
    calc_id = f"layout-{uuid.uuid4().hex[:8]}"
    warnings = []

    equipment_list = input_data.get("equipment", [])
    site_constraints = input_data.get("site_constraints", {})
    wind_direction = site_constraints.get("prevailing_wind", "NW")
    site_class = site_constraints.get("site_class", "greenfield")

    # ── Spacing Matrix ──────────────────────────────────────────────
    spacing_results = []
    for i, eq_a in enumerate(equipment_list):
        for j, eq_b in enumerate(equipment_list):
            if j <= i:
                continue
            type_a = eq_a.get("type", "process_unit")
            type_b = eq_b.get("type", "process_unit")
            min_dist = get_spacing(type_a, type_b)
            actual_dist = eq_a.get("distance_to", {}).get(eq_b.get("tag", ""), None)

            status = "PASS"
            if actual_dist is not None and actual_dist < min_dist:
                status = "FAIL"
                warnings.append(
                    f"Distance {eq_a.get('tag', '')} to {eq_b.get('tag', '')} "
                    f"({actual_dist}m) < minimum ({min_dist}m)"
                )

            spacing_results.append({
                "equipment_a": eq_a.get("tag", f"EQ-{i}"),
                "equipment_b": eq_b.get("tag", f"EQ-{j}"),
                "type_a": type_a,
                "type_b": type_b,
                "minimum_distance_m": min_dist,
                "actual_distance_m": actual_dist,
                "status": status,
            })

    # ── Plot Plan Area Estimation ───────────────────────────────────
    # Estimate total area based on equipment count and type
    area_factors = {
        "process_unit": 2000,     # m² per unit
        "fired_heater": 400,
        "compressor": 200,
        "pump": 50,
        "pressure_vessel": 100,
        "atmospheric_tank": 1000,
        "pressurized_storage": 2000,
        "flare": 500,
        "cooling_tower": 800,
        "control_room": 300,
        "substation": 200,
        "loading_rack": 500,
        "pipe_rack": 150,
        "heat_exchanger": 80,
    }

    total_area = 0
    for eq in equipment_list:
        eq_type = eq.get("type", "process_unit")
        total_area += area_factors.get(eq_type, 200)

    # Add roads, firewater, drainage (typically 40-60% of equipment area)
    infrastructure_factor = 1.5
    total_plot = total_area * infrastructure_factor

    # ── Wind Direction Recommendations ──────────────────────────────
    wind_notes = []
    fired_heaters = [e for e in equipment_list if e.get("type") == "fired_heater"]
    flares = [e for e in equipment_list if e.get("type") == "flare"]

    if fired_heaters:
        wind_notes.append(f"Place fired heaters UPWIND ({wind_direction}) of process units.")
    if flares:
        wind_notes.append(f"Place flare DOWNWIND of all occupied buildings.")
    wind_notes.append("Orient control room crosswind to minimize vapor cloud exposure.")

    # ── Road Access ─────────────────────────────────────────────────
    roads = {
        "main_road_width_m": 7.5,
        "secondary_road_width_m": 4.5,
        "fire_truck_access": "Two-way access required on at least two sides of each process unit",
        "minimum_turning_radius_m": 12.0,
    }

    return {
        "status": "success",
        "calculation_id": calc_id,
        "warnings": warnings,
        "spacing_analysis": spacing_results,
        "plot_plan": {
            "equipment_area_m2": round(total_area, 0),
            "total_plot_area_m2": round(total_plot, 0),
            "total_plot_area_hectares": round(total_plot / 10000, 2),
            "infrastructure_factor": infrastructure_factor,
        },
        "wind_recommendations": wind_notes,
        "road_access": roads,
        "standards_reference": ["API 2510", "NFPA 30", "PIP STC01015", "API RP 752"],
    }
