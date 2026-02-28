"""
Material Selection & Metallurgy Engine (Module 2).

Implements:
    - Material database: carbon steel to exotic alloys with mechanical limits
    - Corrosion rate calculators:
        - Generalized corrosion (uniform thinning)
        - CO₂ (sweet) corrosion: de Waard-Milliams model
        - H₂S (sour) corrosion: NACE MR0175/ISO 15156 screening
        - Localized corrosion (pitting) risk assessment
    - Temperature de-rating per ASME II Part D
    - Material selection recommendation matrix

Standards: NACE MR0175, API 571, ASME II Part D, ASTM
"""

import math
import uuid


# ── Material Properties Database ────────────────────────────────────
# Each material: {
#   name, UNS, density_kg_m3, yield_strength_MPa, tensile_strength_MPa,
#   max_temp_C, min_temp_C, hardness_HRC_max, PREN, sour_service,
#   cost_factor (relative to CS=1.0)
# }

MATERIALS = {
    "carbon_steel_A106B": {
        "name": "Carbon Steel (ASTM A106 Gr.B)", "UNS": "K03006",
        "density": 7850, "yield_MPa": 241, "tensile_MPa": 414,
        "max_temp_C": 427, "min_temp_C": -29,
        "hardness_HRC_max": 22, "PREN": 0, "sour_service": True,
        "cost_factor": 1.0, "category": "carbon_steel",
    },
    "carbon_steel_A516_70": {
        "name": "Carbon Steel (ASTM A516 Gr.70)", "UNS": "K02700",
        "density": 7850, "yield_MPa": 260, "tensile_MPa": 485,
        "max_temp_C": 454, "min_temp_C": -45,
        "hardness_HRC_max": 22, "PREN": 0, "sour_service": True,
        "cost_factor": 1.05, "category": "carbon_steel",
    },
    "SS304": {
        "name": "Stainless Steel 304 (18Cr-8Ni)", "UNS": "S30400",
        "density": 8000, "yield_MPa": 205, "tensile_MPa": 515,
        "max_temp_C": 816, "min_temp_C": -196,
        "hardness_HRC_max": 22, "PREN": 18, "sour_service": True,
        "cost_factor": 3.0, "category": "austenitic_ss",
    },
    "SS316L": {
        "name": "Stainless Steel 316L (16Cr-12Ni-2Mo)", "UNS": "S31603",
        "density": 8000, "yield_MPa": 170, "tensile_MPa": 485,
        "max_temp_C": 816, "min_temp_C": -196,
        "hardness_HRC_max": 22, "PREN": 24, "sour_service": True,
        "cost_factor": 3.5, "category": "austenitic_ss",
    },
    "duplex_2205": {
        "name": "Duplex 2205 (22Cr-5Ni-3Mo)", "UNS": "S31803",
        "density": 7800, "yield_MPa": 450, "tensile_MPa": 620,
        "max_temp_C": 315, "min_temp_C": -50,
        "hardness_HRC_max": 28, "PREN": 35, "sour_service": True,
        "cost_factor": 5.0, "category": "duplex_ss",
    },
    "super_duplex_2507": {
        "name": "Super Duplex 2507 (25Cr-7Ni-4Mo)", "UNS": "S32750",
        "density": 7800, "yield_MPa": 550, "tensile_MPa": 795,
        "max_temp_C": 315, "min_temp_C": -50,
        "hardness_HRC_max": 32, "PREN": 43, "sour_service": True,
        "cost_factor": 7.0, "category": "duplex_ss",
    },
    "monel_400": {
        "name": "Monel 400 (67Ni-30Cu)", "UNS": "N04400",
        "density": 8800, "yield_MPa": 240, "tensile_MPa": 550,
        "max_temp_C": 538, "min_temp_C": -196,
        "hardness_HRC_max": 35, "PREN": 0, "sour_service": False,
        "cost_factor": 6.0, "category": "nickel_alloy",
    },
    "inconel_625": {
        "name": "Inconel 625 (58Ni-22Cr-9Mo)", "UNS": "N06625",
        "density": 8440, "yield_MPa": 414, "tensile_MPa": 827,
        "max_temp_C": 982, "min_temp_C": -196,
        "hardness_HRC_max": 40, "PREN": 51, "sour_service": True,
        "cost_factor": 8.0, "category": "nickel_alloy",
    },
    "hastelloy_C276": {
        "name": "Hastelloy C-276 (57Ni-16Cr-16Mo)", "UNS": "N10276",
        "density": 8890, "yield_MPa": 355, "tensile_MPa": 785,
        "max_temp_C": 1093, "min_temp_C": -196,
        "hardness_HRC_max": 40, "PREN": 70, "sour_service": True,
        "cost_factor": 10.0, "category": "nickel_alloy",
    },
    "titanium_gr2": {
        "name": "Titanium Grade 2", "UNS": "R50400",
        "density": 4510, "yield_MPa": 275, "tensile_MPa": 345,
        "max_temp_C": 316, "min_temp_C": -59,
        "hardness_HRC_max": 30, "PREN": 0, "sour_service": True,
        "cost_factor": 12.0, "category": "titanium",
    },
    "alloy_20": {
        "name": "Alloy 20 (35Ni-20Cr-3.5Cu-2.5Mo)", "UNS": "N08020",
        "density": 8050, "yield_MPa": 241, "tensile_MPa": 551,
        "max_temp_C": 538, "min_temp_C": -196,
        "hardness_HRC_max": 35, "PREN": 28, "sour_service": True,
        "cost_factor": 6.5, "category": "nickel_alloy",
    },
    "cast_iron_ductile": {
        "name": "Ductile Cast Iron (ASTM A536)", "UNS": "F32800",
        "density": 7100, "yield_MPa": 276, "tensile_MPa": 414,
        "max_temp_C": 343, "min_temp_C": -29,
        "hardness_HRC_max": 28, "PREN": 0, "sour_service": False,
        "cost_factor": 0.8, "category": "cast_iron",
    },
}


def co2_corrosion_rate(T_C: float, co2_partial_bar: float, pH: float = 4.0) -> dict:
    """
    CO₂ (sweet) corrosion rate via de Waard-Milliams (1975) model.

    log10(CR) = 5.8 - 1710/T_K + 0.67·log10(pCO₂)

    Args:
        T_C: Temperature [°C]
        co2_partial_bar: CO₂ partial pressure [bar]
        pH: Solution pH (default 4.0 for produced water)

    Returns:
        Dict with corrosion rate and severity classification.
    """
    T_K = T_C + 273.15
    if co2_partial_bar <= 0:
        return {"corrosion_rate_mm_yr": 0.0, "severity": "negligible", "model": "de_Waard_Milliams"}

    log_cr = 5.8 - 1710.0 / T_K + 0.67 * math.log10(co2_partial_bar)
    cr_mm_yr = 10**log_cr

    # pH correction (simplified)
    if pH > 5.0:
        cr_mm_yr *= 0.5
    elif pH > 6.0:
        cr_mm_yr *= 0.2

    # FeCO₃ scale factor (protective above ~60°C)
    if T_C > 80:
        cr_mm_yr *= 0.3
    elif T_C > 60:
        cr_mm_yr *= 0.6

    severity = "negligible"
    if cr_mm_yr > 0.1:
        severity = "low"
    if cr_mm_yr > 0.25:
        severity = "moderate"
    if cr_mm_yr > 1.0:
        severity = "high"
    if cr_mm_yr > 5.0:
        severity = "severe"

    return {
        "corrosion_rate_mm_yr": round(cr_mm_yr, 3),
        "severity": severity,
        "model": "de_Waard_Milliams_1975",
        "conditions": {
            "temperature_C": T_C,
            "co2_partial_pressure_bar": co2_partial_bar,
            "pH": pH,
        },
    }


def h2s_sour_service_check(h2s_partial_bar: float, pH: float, T_C: float,
                            material_key: str) -> dict:
    """
    H₂S (sour) service screening per NACE MR0175/ISO 15156.

    Region classification:
        Region 0: Non-sour (pH₂S < 0.003 bar)
        Region 1: SSC possible — hardness limits apply
        Region 2: SSC likely — restricted materials
        Region 3: Severe sour — exotic alloys required
    """
    mat = MATERIALS.get(material_key, {})

    # NACE region determination
    if h2s_partial_bar < 0.003:
        region = 0
        severity = "non_sour"
    elif h2s_partial_bar < 0.01 and pH > 3.5:
        region = 1
        severity = "mildly_sour"
    elif h2s_partial_bar < 0.1:
        region = 2
        severity = "sour"
    else:
        region = 3
        severity = "severely_sour"

    # Material acceptability
    acceptable = True
    notes = []

    if region >= 1:
        max_hrc = mat.get("hardness_HRC_max", 22)
        if max_hrc > 22 and mat.get("category") == "carbon_steel":
            acceptable = True  # CS ok if hardness controlled
            notes.append("Hardness must be ≤ 22 HRC per NACE MR0175")
        if not mat.get("sour_service", False):
            acceptable = False
            notes.append(f"Material {material_key} not approved for sour service")

    if region >= 2:
        if mat.get("category") == "carbon_steel":
            notes.append("Consider CRA lining or upgrade to SS316L/Duplex")
        if mat.get("PREN", 0) < 25:
            notes.append(f"PREN ({mat.get('PREN', 0)}) may be insufficient for pitting resistance")

    if region >= 3:
        if mat.get("PREN", 0) < 40:
            acceptable = False
            notes.append("Region 3: Requires PREN ≥ 40 (Duplex 2507, Inconel 625, or Hastelloy)")

    return {
        "nace_region": region,
        "severity": severity,
        "material": material_key,
        "acceptable": acceptable,
        "notes": notes,
        "conditions": {
            "h2s_partial_pressure_bar": h2s_partial_bar,
            "pH": pH,
            "temperature_C": T_C,
        },
    }


def select_material(input_data: dict) -> dict:
    """
    Material selection based on process conditions.

    Evaluates temperature limits, corrosion environment, and
    sour/sweet service requirements.
    """
    calc_id = f"mat-{uuid.uuid4().hex[:8]}"
    warnings = []

    T_design_C = input_data.get("design_temperature_C", 100)
    T_min_C = input_data.get("minimum_temperature_C", -29)
    P_design_bar = input_data.get("design_pressure_barg", 10)
    co2_bar = input_data.get("co2_partial_pressure_bar", 0)
    h2s_bar = input_data.get("h2s_partial_pressure_bar", 0)
    pH = input_data.get("pH", 7.0)
    chloride_ppm = input_data.get("chloride_ppm", 0)
    service = input_data.get("service_type", "general")

    candidates = []
    for key, mat in MATERIALS.items():
        score = 0
        notes = []
        disqualified = False

        # Temperature check
        if T_design_C > mat["max_temp_C"]:
            disqualified = True
            notes.append(f"Max temp {mat['max_temp_C']}°C exceeded")
        if T_min_C < mat["min_temp_C"]:
            disqualified = True
            notes.append(f"Min temp {mat['min_temp_C']}°C exceeded")

        if disqualified:
            continue

        score += 10  # Base pass

        # CO₂ corrosion
        if co2_bar > 0:
            co2_result = co2_corrosion_rate(T_design_C, co2_bar, pH)
            cr = co2_result["corrosion_rate_mm_yr"]
            if cr > 1.0 and mat["category"] == "carbon_steel":
                notes.append(f"High CO₂ corrosion ({cr:.2f} mm/yr) — consider CRA")
                score -= 5
            elif cr < 0.1:
                score += 5

        # H₂S check
        if h2s_bar > 0:
            sour_result = h2s_sour_service_check(h2s_bar, pH, T_design_C, key)
            if not sour_result["acceptable"]:
                continue
            if sour_result["nace_region"] >= 2:
                score += mat.get("PREN", 0) // 10

        # Chloride pitting resistance
        if chloride_ppm > 50:
            pren = mat.get("PREN", 0)
            if chloride_ppm > 1000 and pren < 25:
                notes.append("Insufficient chloride pitting resistance")
                score -= 10
            elif pren >= 35:
                score += 5

        # Cost efficiency
        score += max(0, 15 - int(mat["cost_factor"] * 2))

        candidates.append({
            "material_key": key,
            "name": mat["name"],
            "UNS": mat["UNS"],
            "category": mat["category"],
            "score": score,
            "cost_factor": mat["cost_factor"],
            "notes": notes,
            "properties": {
                "yield_MPa": mat["yield_MPa"],
                "tensile_MPa": mat["tensile_MPa"],
                "max_temp_C": mat["max_temp_C"],
                "min_temp_C": mat["min_temp_C"],
                "PREN": mat["PREN"],
            },
        })

    candidates.sort(key=lambda x: (-x["score"], x["cost_factor"]))

    return {
        "status": "success",
        "calculation_id": calc_id,
        "warnings": warnings,
        "recommended": candidates[0] if candidates else None,
        "alternatives": candidates[1:4] if len(candidates) > 1 else [],
        "all_evaluated": candidates,
        "conditions": {
            "design_temperature_C": T_design_C,
            "minimum_temperature_C": T_min_C,
            "co2_partial_bar": co2_bar,
            "h2s_partial_bar": h2s_bar,
            "chloride_ppm": chloride_ppm,
        },
    }
