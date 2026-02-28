"""
Tests for the Pipe Sizing & Hydraulics Engine (Module 1).
"""

import pytest
from app.services.modules.piping import size_pipe, PIPE_SCHEDULES, PIPE_ROUGHNESS


class TestPipeScheduleData:
    """Verify pipe schedule reference data integrity."""

    def test_schedule_40_exists(self):
        """Schedule 40 should have entries for common NPS sizes."""
        for nps in [2, 4, 6, 8, 10, 12]:
            assert nps in PIPE_SCHEDULES, f"Missing NPS {nps}"
            assert "40" in PIPE_SCHEDULES[nps], f"Missing Sch 40 for NPS {nps}"

    def test_od_greater_than_id(self):
        """OD must always exceed ID for all schedule entries."""
        for nps, schedules in PIPE_SCHEDULES.items():
            for sch, (od_mm, wall_mm, id_mm) in schedules.items():
                assert od_mm > id_mm, f"OD <= ID for NPS {nps} Sch {sch}"

    def test_roughness_values_positive(self):
        """All roughness values must be positive."""
        for material, eps in PIPE_ROUGHNESS.items():
            assert eps > 0, f"Non-positive roughness for {material}"

    def test_carbon_steel_roughness(self):
        """Carbon steel roughness ~0.046 mm."""
        assert PIPE_ROUGHNESS["carbon_steel"] == pytest.approx(0.046, abs=0.01)


class TestSizePipeCheckMode:
    """Test pipe sizing in 'check' mode — given pipe, calculate dP."""

    def test_water_flow_check_mode(self):
        """Water at 1 kg/s through 4-inch Sch 40 pipe, 100 m."""
        input_data = {
            "fluid": {
                "density_kg_m3": 998.0,
                "viscosity_Pa_s": 0.001,
                "mass_flow_kg_s": 1.0,
                "phase": "liquid",
            },
            "pipe": {
                "material": "carbon_steel",
                "schedule": "40",
                "length_m": 100.0,
                "elevation_change_m": 0.0,
                "nps_inches": 4,
            },
            "fittings": [],
            "mode": "check",
        }
        result = size_pipe(input_data)
        assert result["status"] == "success"
        hyd = result["hydraulics"]
        assert hyd["velocity_m_s"] > 0
        assert hyd["reynolds_number"] > 4000
        assert hyd["dp_total_bar"] > 0
        assert hyd["friction_factor_darcy"] > 0

    def test_velocity_range(self):
        """Velocity for water should be in a reasonable range."""
        input_data = {
            "fluid": {
                "density_kg_m3": 998.0,
                "viscosity_Pa_s": 0.001,
                "mass_flow_kg_s": 5.0,
                "phase": "liquid",
            },
            "pipe": {
                "material": "carbon_steel",
                "schedule": "40",
                "length_m": 50.0,
                "elevation_change_m": 0.0,
                "nps_inches": 6,
            },
            "fittings": [],
            "mode": "check",
        }
        result = size_pipe(input_data)
        assert 0.1 < result["hydraulics"]["velocity_m_s"] < 15.0

    def test_fittings_increase_dp(self):
        """Adding fittings should increase total pressure drop."""
        base = {
            "fluid": {
                "density_kg_m3": 998.0,
                "viscosity_Pa_s": 0.001,
                "mass_flow_kg_s": 2.0,
                "phase": "liquid",
            },
            "pipe": {
                "material": "carbon_steel",
                "schedule": "40",
                "length_m": 50.0,
                "elevation_change_m": 0.0,
                "nps_inches": 4,
            },
            "fittings": [],
            "mode": "check",
        }
        result_no_fittings = size_pipe(base)

        with_fittings = {**base, "fittings": [
            {"type": "elbow_90", "count": 4},
            {"type": "tee_branch", "count": 2},
        ]}
        result_with_fittings = size_pipe(with_fittings)

        assert (result_with_fittings["hydraulics"]["dp_total_bar"]
                > result_no_fittings["hydraulics"]["dp_total_bar"])


class TestSizePipeSizeMode:
    """Test pipe sizing in 'size' mode — find optimal NPS."""

    def test_selects_valid_nps(self):
        """Should return a valid standard NPS."""
        input_data = {
            "fluid": {
                "density_kg_m3": 998.0,
                "viscosity_Pa_s": 0.001,
                "mass_flow_kg_s": 3.0,
                "phase": "liquid",
            },
            "pipe": {
                "material": "carbon_steel",
                "schedule": "40",
                "length_m": 200.0,
                "elevation_change_m": 5.0,
            },
            "fittings": [],
            "mode": "size",
            "velocity_max_m_s": 3.0,
        }
        result = size_pipe(input_data)
        assert result["status"] == "success"
        assert result["selected_pipe"]["nps_inches"] > 0

    def test_gas_pipe(self):
        """Gas pipe sizing should produce valid results."""
        input_data = {
            "fluid": {
                "density_kg_m3": 50.0,
                "viscosity_Pa_s": 1.2e-5,
                "mass_flow_kg_s": 5.0,
                "phase": "vapor",
            },
            "pipe": {
                "material": "carbon_steel",
                "schedule": "40",
                "length_m": 100.0,
                "elevation_change_m": 0.0,
            },
            "fittings": [],
            "mode": "size",
        }
        result = size_pipe(input_data)
        assert result["status"] == "success"
        assert result["selected_pipe"]["nps_inches"] > 0
