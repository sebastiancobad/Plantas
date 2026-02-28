"""
Tests for the Phase Separator Sizing Engine (Module 4).
"""

import pytest
from app.services.modules.separators import size_separator


class TestTwoPhaseVertical:
    """Test 2-phase vertical separator sizing."""

    def test_basic_gas_liquid_vertical(self):
        """Standard gas-liquid vertical separator."""
        input_data = {
            "separator_type": "two_phase",
            "orientation": "vertical",
            "fluid_type": "gas_condensate",
            "gas_phase": {
                "density_kg_m3": 30.0,
                "actual_flow_m3_s": 0.5,
                "viscosity_Pa_s": 1.2e-5,
            },
            "oil_phase": {
                "density_kg_m3": 750.0,
                "flow_m3_s": 0.01,
                "viscosity_Pa_s": 0.002,
            },
            "operating_pressure_barg": 40.0,
            "operating_temperature_C": 60.0,
            "demister": True,
        }
        result = size_separator(input_data)
        assert result["status"] == "success"
        vg = result["vessel_geometry"]
        assert vg["diameter_m"] > 0
        assert vg["length_m"] > 0
        assert vg["diameter_m"] < 6.0

    def test_higher_flow_larger_diameter(self):
        """Doubling gas flow should increase separator diameter."""
        base = {
            "separator_type": "two_phase",
            "orientation": "vertical",
            "fluid_type": "default",
            "gas_phase": {
                "density_kg_m3": 25.0,
                "actual_flow_m3_s": 0.3,
                "viscosity_Pa_s": 1.5e-5,
            },
            "oil_phase": {
                "density_kg_m3": 800.0,
                "flow_m3_s": 0.005,
                "viscosity_Pa_s": 0.003,
            },
            "operating_pressure_barg": 20.0,
            "operating_temperature_C": 40.0,
        }
        r1 = size_separator(base)

        larger = {**base}
        larger["gas_phase"] = {**base["gas_phase"], "actual_flow_m3_s": 0.6}
        r2 = size_separator(larger)

        assert r2["vessel_geometry"]["diameter_m"] >= r1["vessel_geometry"]["diameter_m"]


class TestTwoPhaseHorizontal:
    """Test 2-phase horizontal separator sizing."""

    def test_basic_horizontal(self):
        """Standard horizontal 2-phase separator."""
        input_data = {
            "separator_type": "two_phase",
            "orientation": "horizontal",
            "fluid_type": "crude_oil",
            "gas_phase": {
                "density_kg_m3": 20.0,
                "actual_flow_m3_s": 0.8,
                "viscosity_Pa_s": 1.0e-5,
            },
            "oil_phase": {
                "density_kg_m3": 850.0,
                "flow_m3_s": 0.05,
                "viscosity_Pa_s": 0.01,
            },
            "operating_pressure_barg": 10.0,
            "operating_temperature_C": 50.0,
        }
        result = size_separator(input_data)
        vg = result["vessel_geometry"]
        assert vg["diameter_m"] > 0
        assert vg["length_m"] > vg["diameter_m"]  # L/D typically > 1


class TestThreePhase:
    """Test 3-phase separator sizing."""

    def test_three_phase_horizontal(self):
        """3-phase separator with gas, oil, and water."""
        input_data = {
            "separator_type": "three_phase",
            "orientation": "horizontal",
            "fluid_type": "crude_oil",
            "gas_phase": {
                "density_kg_m3": 15.0,
                "actual_flow_m3_s": 0.4,
                "viscosity_Pa_s": 1.0e-5,
            },
            "oil_phase": {
                "density_kg_m3": 850.0,
                "flow_m3_s": 0.03,
                "viscosity_Pa_s": 0.005,
            },
            "water_phase": {
                "density_kg_m3": 1020.0,
                "flow_m3_s": 0.02,
            },
            "operating_pressure_barg": 8.0,
            "operating_temperature_C": 55.0,
        }
        result = size_separator(input_data)
        vg = result["vessel_geometry"]
        assert vg["diameter_m"] > 0
        assert vg["length_m"] > 0
