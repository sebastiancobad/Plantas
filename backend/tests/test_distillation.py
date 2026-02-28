"""
Tests for the Distillation Column Design Engine (Module 7).
"""

import pytest
from app.services.modules.distillation import design_distillation_column


class TestBinaryDistillation:
    """Test FUG shortcut design for binary mixtures."""

    def test_benzene_toluene_separation(self):
        """Classic benzene-toluene separation."""
        input_data = {
            "feed": {
                "mole_fractions": [0.5, 0.5],
                "feed_quality": 1.0,
                "molar_flow_mol_s": 100.0,
            },
            "light_key_index": 0,
            "heavy_key_index": 1,
            "relative_volatilities": [2.5, 1.0],
            "distillate_lk_purity": 0.95,
            "bottoms_hk_purity": 0.95,
            "reflux_ratio_factor": 1.3,
            "liquid_density_kg_m3": 800.0,
            "vapor_density_kg_m3": 3.0,
            "surface_tension_N_m": 0.025,
            "avg_molecular_weight": 85.0,
            "internal_type": "tray",
            "tray_type": "sieve",
            "tray_spacing_m": 0.6,
            "heat_of_vaporization_J_mol": 33000.0,
        }
        result = design_distillation_column(input_data)

        assert result["status"] == "success"
        sr = result["shortcut_results"]
        assert sr["minimum_stages"] > 0
        assert sr["minimum_reflux_ratio"] > 0
        assert sr["theoretical_stages"] > sr["minimum_stages"]
        assert sr["actual_reflux_ratio"] > sr["minimum_reflux_ratio"]
        assert result["column_geometry"]["diameter_m"] > 0
        assert result["column_geometry"]["height_m"] > 0
        assert result["thermal_duties"]["condenser_kW"] > 0
        assert result["thermal_duties"]["reboiler_kW"] > 0

    def test_higher_purity_more_stages(self):
        """Higher purity requirement should need more stages."""
        base = {
            "feed": {
                "mole_fractions": [0.5, 0.5],
                "feed_quality": 1.0,
                "molar_flow_mol_s": 80.0,
            },
            "light_key_index": 0,
            "heavy_key_index": 1,
            "relative_volatilities": [2.0, 1.0],
            "liquid_density_kg_m3": 780.0,
            "vapor_density_kg_m3": 2.5,
            "surface_tension_N_m": 0.022,
            "avg_molecular_weight": 80.0,
            "internal_type": "tray",
            "tray_type": "valve",
            "tray_spacing_m": 0.6,
            "heat_of_vaporization_J_mol": 30000.0,
            "reflux_ratio_factor": 1.3,
        }

        low_purity = {**base, "distillate_lk_purity": 0.90, "bottoms_hk_purity": 0.90}
        high_purity = {**base, "distillate_lk_purity": 0.99, "bottoms_hk_purity": 0.99}

        r_low = design_distillation_column(low_purity)
        r_high = design_distillation_column(high_purity)

        assert r_high["shortcut_results"]["theoretical_stages"] > r_low["shortcut_results"]["theoretical_stages"]


class TestPackedColumn:
    """Test packed column design."""

    def test_packing_design(self):
        """Column with structured packing should return HETP-based height."""
        input_data = {
            "feed": {
                "mole_fractions": [0.4, 0.6],
                "feed_quality": 1.0,
                "molar_flow_mol_s": 50.0,
            },
            "light_key_index": 0,
            "heavy_key_index": 1,
            "relative_volatilities": [3.0, 1.0],
            "distillate_lk_purity": 0.95,
            "bottoms_hk_purity": 0.95,
            "reflux_ratio_factor": 1.2,
            "liquid_density_kg_m3": 820.0,
            "vapor_density_kg_m3": 2.0,
            "surface_tension_N_m": 0.02,
            "avg_molecular_weight": 70.0,
            "internal_type": "packing",
            "packing_type": "mellapak",
            "heat_of_vaporization_J_mol": 28000.0,
        }
        result = design_distillation_column(input_data)
        assert result["column_geometry"]["height_m"] > 0
        assert result["column_geometry"]["diameter_m"] > 0


class TestMulticomponentDistillation:
    """Test multi-component FUG shortcut."""

    def test_three_component(self):
        """Three-component mixture separation."""
        input_data = {
            "feed": {
                "mole_fractions": [0.3, 0.4, 0.3],
                "feed_quality": 1.0,
                "molar_flow_mol_s": 120.0,
            },
            "light_key_index": 0,
            "heavy_key_index": 1,
            "relative_volatilities": [4.0, 2.0, 1.0],
            "distillate_lk_purity": 0.95,
            "bottoms_hk_purity": 0.95,
            "reflux_ratio_factor": 1.3,
            "liquid_density_kg_m3": 750.0,
            "vapor_density_kg_m3": 3.5,
            "surface_tension_N_m": 0.018,
            "avg_molecular_weight": 60.0,
            "internal_type": "tray",
            "tray_type": "sieve",
            "tray_spacing_m": 0.6,
            "heat_of_vaporization_J_mol": 25000.0,
        }
        result = design_distillation_column(input_data)
        sr = result["shortcut_results"]
        assert sr["theoretical_stages"] > 0
        assert sr["feed_stage"] > 0
        assert sr["feed_stage"] < sr["theoretical_stages"]
