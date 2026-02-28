"""
Tests for the Material Selection & Metallurgy Engine (Module 2).
"""

import pytest
from app.services.modules.materials import (
    co2_corrosion_rate,
    h2s_sour_service_check,
    select_material,
    MATERIALS,
)


class TestMaterialsDatabase:
    """Verify material database integrity."""

    def test_carbon_steel_exists(self):
        """Carbon steel A106B should be in the database."""
        assert "carbon_steel_A106B" in MATERIALS

    def test_all_materials_have_required_fields(self):
        """Each material must have yield_MPa, tensile_MPa, max_temp_C."""
        for key, mat in MATERIALS.items():
            assert "yield_MPa" in mat, f"{key} missing yield_MPa"
            assert "tensile_MPa" in mat, f"{key} missing tensile_MPa"
            assert "max_temp_C" in mat, f"{key} missing max_temp_C"

    def test_material_count(self):
        """Should have at least 12 alloys."""
        assert len(MATERIALS) >= 12

    def test_pren_for_stainless(self):
        """Stainless steels should have PREN values."""
        for key in ["SS304", "SS316L", "duplex_2205", "super_duplex_2507"]:
            if key in MATERIALS:
                assert "PREN" in MATERIALS[key], f"{key} missing PREN"


class TestCO2Corrosion:
    """Test de Waard-Milliams CO₂ corrosion model."""

    def test_basic_corrosion_rate(self):
        """CO₂ corrosion at 60°C, 2 bar CO₂ should give measurable rate."""
        result = co2_corrosion_rate(T_C=60.0, co2_partial_bar=2.0)
        assert result["corrosion_rate_mm_yr"] > 0
        assert "severity" in result

    def test_higher_temp_higher_rate(self):
        """Higher temperature should increase corrosion rate (below scaling temp)."""
        r1 = co2_corrosion_rate(T_C=40.0, co2_partial_bar=1.0)
        r2 = co2_corrosion_rate(T_C=70.0, co2_partial_bar=1.0)
        assert r2["corrosion_rate_mm_yr"] > r1["corrosion_rate_mm_yr"]

    def test_higher_co2_higher_rate(self):
        """Higher CO₂ partial pressure should increase corrosion rate."""
        r1 = co2_corrosion_rate(T_C=50.0, co2_partial_bar=0.5)
        r2 = co2_corrosion_rate(T_C=50.0, co2_partial_bar=5.0)
        assert r2["corrosion_rate_mm_yr"] > r1["corrosion_rate_mm_yr"]

    def test_ph_correction(self):
        """Higher pH should reduce corrosion rate."""
        r1 = co2_corrosion_rate(T_C=60.0, co2_partial_bar=2.0, pH=4.0)
        r2 = co2_corrosion_rate(T_C=60.0, co2_partial_bar=2.0, pH=6.0)
        assert r2["corrosion_rate_mm_yr"] < r1["corrosion_rate_mm_yr"]


class TestH2SSourService:
    """Test NACE MR0175 H₂S sour service screening."""

    def test_sweet_service(self):
        """No H₂S should be Region 0 (sweet)."""
        result = h2s_sour_service_check(
            h2s_partial_bar=0.0, pH=6.0, T_C=60.0, material_key="carbon_steel_A106B"
        )
        assert result["nace_region"] == 0
        assert result["acceptable"] is True

    def test_sour_service_high_h2s(self):
        """High H₂S at low pH should flag sour service concern."""
        result = h2s_sour_service_check(
            h2s_partial_bar=1.0, pH=3.5, T_C=80.0, material_key="carbon_steel_A106B"
        )
        assert result["nace_region"] > 0

    def test_crp_material_sour(self):
        """CRAs like Inconel should have better sour service tolerance."""
        if "inconel_625" in MATERIALS:
            inc_result = h2s_sour_service_check(
                h2s_partial_bar=0.5, pH=4.0, T_C=60.0, material_key="inconel_625"
            )
            assert inc_result["acceptable"]


class TestMaterialSelection:
    """Test material selection scoring algorithm."""

    def test_mild_conditions_returns_result(self):
        """Mild, non-corrosive conditions should return a valid recommendation."""
        input_data = {
            "design_temperature_C": 150.0,
            "minimum_temperature_C": -10.0,
            "design_pressure_barg": 10.0,
            "co2_partial_pressure_bar": 0.0,
            "h2s_partial_pressure_bar": 0.0,
            "pH": 7.0,
            "chloride_ppm": 0.0,
            "service_type": "process_gas",
        }
        result = select_material(input_data)
        assert result["status"] == "success"
        assert "recommended" in result
        assert "material_key" in result["recommended"]
        # For mild conditions, cheapest material should rank high
        assert result["recommended"]["cost_factor"] <= 3.0

    def test_corrosive_conditions_upgrade(self):
        """High CO₂ + chlorides should recommend a corrosion-resistant alloy."""
        input_data = {
            "design_temperature_C": 120.0,
            "minimum_temperature_C": 0.0,
            "design_pressure_barg": 30.0,
            "co2_partial_pressure_bar": 5.0,
            "h2s_partial_pressure_bar": 0.1,
            "pH": 4.0,
            "chloride_ppm": 50000.0,
            "service_type": "sour_gas",
        }
        result = select_material(input_data)
        recommended = result["recommended"]["material_key"]
        # Should NOT be plain carbon steel for such harsh conditions
        assert "carbon_steel" not in recommended

    def test_returns_alternatives(self):
        """Should return a list of alternative materials."""
        input_data = {
            "design_temperature_C": 200.0,
            "minimum_temperature_C": -20.0,
            "design_pressure_barg": 20.0,
            "co2_partial_pressure_bar": 1.0,
            "h2s_partial_pressure_bar": 0.0,
            "pH": 5.5,
            "chloride_ppm": 100.0,
            "service_type": "process_liquid",
        }
        result = select_material(input_data)
        assert "alternatives" in result
        assert len(result["alternatives"]) >= 1
