"""
Tests for the Pump Selection & Sizing Engine (Module 5).
"""

import pytest
from app.services.modules.pumps import size_pump


class TestPumpSizing:
    """Test pump sizing with realistic process data."""

    def test_basic_water_pump(self):
        """Size a pump for water transfer at moderate flow."""
        input_data = {
            "fluid": {
                "density_kg_m3": 998.0,
                "viscosity_Pa_s": 0.001,
                "vapor_pressure_Pa": 2340.0,
            },
            "flow": {
                "design_flow_m3_s": 0.02,
                "rated_factor": 1.10,
            },
            "suction": {
                "pressure_Pa": 101325.0,
                "static_head_m": 2.0,
                "friction_loss_m": 1.0,
            },
            "discharge": {
                "pressure_Pa": 500000.0,
                "static_head_m": 15.0,
            },
            "pipe_segments": [
                {
                    "id_m": 0.1023,
                    "length_m": 50.0,
                    "roughness_m": 0.000046,
                    "K_fittings": 5.0,
                }
            ],
            "speed_rpm": 2950.0,
        }
        result = size_pump(input_data)
        assert result["status"] == "success"
        assert result["operating_point"]["total_dynamic_head_m"] > 0
        assert result["power"]["hydraulic_kW"] > 0
        assert result["power"]["selected_motor_kW"] > 0
        assert result["npsh"]["npsh_available_m"] > 0
        assert "pump_selection" in result

    def test_npsh_positive(self):
        """NPSH available should be positive for adequate suction."""
        input_data = {
            "fluid": {
                "density_kg_m3": 998.0,
                "viscosity_Pa_s": 0.001,
                "vapor_pressure_Pa": 2340.0,
            },
            "flow": {
                "design_flow_m3_s": 0.01,
            },
            "suction": {
                "pressure_Pa": 200000.0,
                "static_head_m": 3.0,
                "friction_loss_m": 0.5,
            },
            "discharge": {
                "pressure_Pa": 400000.0,
                "static_head_m": 10.0,
            },
            "pipe_segments": [
                {
                    "id_m": 0.0779,
                    "length_m": 20.0,
                    "roughness_m": 0.000046,
                    "K_fittings": 3.0,
                }
            ],
            "speed_rpm": 1450.0,
        }
        result = size_pump(input_data)
        assert result["npsh"]["npsh_available_m"] > 0
        assert result["npsh"]["status"] == "PASS"

    def test_system_curve_points(self):
        """System curve should have multiple operating points."""
        input_data = {
            "fluid": {
                "density_kg_m3": 800.0,
                "viscosity_Pa_s": 0.005,
                "vapor_pressure_Pa": 5000.0,
            },
            "flow": {
                "design_flow_m3_s": 0.015,
            },
            "suction": {
                "pressure_Pa": 101325.0,
                "static_head_m": 1.0,
                "friction_loss_m": 0.5,
            },
            "discharge": {
                "pressure_Pa": 300000.0,
                "static_head_m": 8.0,
            },
            "pipe_segments": [
                {
                    "id_m": 0.1023,
                    "length_m": 80.0,
                    "roughness_m": 0.000046,
                    "K_fittings": 8.0,
                }
            ],
            "speed_rpm": 2950.0,
        }
        result = size_pump(input_data)
        assert "system_curve" in result
        assert len(result["system_curve"]) >= 3

    def test_motor_sizing_standard(self):
        """Motor size should match a standard motor kW value."""
        input_data = {
            "fluid": {
                "density_kg_m3": 998.0,
                "viscosity_Pa_s": 0.001,
                "vapor_pressure_Pa": 2340.0,
            },
            "flow": {
                "design_flow_m3_s": 0.05,
            },
            "suction": {
                "pressure_Pa": 101325.0,
                "static_head_m": 2.0,
                "friction_loss_m": 1.0,
            },
            "discharge": {
                "pressure_Pa": 800000.0,
                "static_head_m": 20.0,
            },
            "pipe_segments": [
                {
                    "id_m": 0.1541,
                    "length_m": 100.0,
                    "roughness_m": 0.000046,
                    "K_fittings": 10.0,
                }
            ],
            "speed_rpm": 2950.0,
        }
        result = size_pump(input_data)
        standard_motors = [0.75, 1.1, 1.5, 2.2, 3.0, 4.0, 5.5, 7.5, 11, 15,
                           18.5, 22, 30, 37, 45, 55, 75, 90, 110, 132, 160, 200, 250, 315]
        assert result["power"]["selected_motor_kW"] in standard_motors
