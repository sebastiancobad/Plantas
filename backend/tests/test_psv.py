"""
Tests for the Safety Relief Valve Sizing Engine (Module 8).
"""

import pytest
from app.services.modules.psv import (
    size_gas_vapor,
    size_liquid,
    fire_case_heat_input,
    size_psv,
    API_ORIFICES,
)


class TestAPIorifices:
    """Verify API 520 orifice data."""

    def test_orifice_d_exists(self):
        """Standard orifice D should be in the database."""
        assert "D" in API_ORIFICES

    def test_orifice_areas_increasing(self):
        """Orifice areas should increase with letter designation."""
        letters = list(API_ORIFICES.keys())
        areas = [API_ORIFICES[l] for l in letters]
        for i in range(1, len(areas)):
            assert areas[i] > areas[i - 1], f"Orifice {letters[i]} not larger than {letters[i-1]}"


class TestGasVaporSizing:
    """Test API 520 gas/vapor relief valve sizing."""

    def test_methane_relief(self):
        """Size a PSV for methane relief at moderate conditions."""
        result = size_gas_vapor(
            W_kg_hr=5000.0,
            T_K=400.0,
            Mw=16.04,
            Z=0.95,
            k=1.31,
            P_set_kPa=1500.0,
            P_back_kPa=101.325,
        )
        assert result["required_area_mm2"] > 0
        assert "selected_orifice" in result
        assert result["selected_orifice"]["designation"] in API_ORIFICES

    def test_higher_flow_larger_orifice(self):
        """Higher relief rate should require larger orifice area."""
        r1 = size_gas_vapor(
            W_kg_hr=1000.0, T_K=350.0, Mw=28.0, Z=1.0, k=1.4,
            P_set_kPa=1000.0, P_back_kPa=101.325,
        )
        r2 = size_gas_vapor(
            W_kg_hr=10000.0, T_K=350.0, Mw=28.0, Z=1.0, k=1.4,
            P_set_kPa=1000.0, P_back_kPa=101.325,
        )
        assert r2["required_area_mm2"] > r1["required_area_mm2"]

    def test_higher_pressure_smaller_area(self):
        """Higher set pressure should require smaller orifice area for same flow."""
        r_low = size_gas_vapor(
            W_kg_hr=5000.0, T_K=400.0, Mw=16.04, Z=0.95, k=1.31,
            P_set_kPa=500.0, P_back_kPa=101.325,
        )
        r_high = size_gas_vapor(
            W_kg_hr=5000.0, T_K=400.0, Mw=16.04, Z=0.95, k=1.31,
            P_set_kPa=3000.0, P_back_kPa=101.325,
        )
        assert r_high["required_area_mm2"] < r_low["required_area_mm2"]


class TestLiquidSizing:
    """Test API 520 liquid relief valve sizing."""

    def test_water_relief(self):
        """Size a PSV for water thermal relief."""
        result = size_liquid(
            Q_m3_hr=10.0,
            rho_kg_m3=998.0,
            P_set_kPa=1000.0,
            P_back_kPa=101.325,
            mu_cP=1.0,
        )
        assert result["required_area_mm2"] > 0
        assert "selected_orifice" in result

    def test_viscous_liquid_larger_area(self):
        """More viscous liquid should require larger orifice area."""
        r_low = size_liquid(
            Q_m3_hr=5.0, rho_kg_m3=900.0,
            P_set_kPa=1500.0, P_back_kPa=101.325, mu_cP=1.0,
        )
        r_high = size_liquid(
            Q_m3_hr=5.0, rho_kg_m3=900.0,
            P_set_kPa=1500.0, P_back_kPa=101.325, mu_cP=100.0,
        )
        assert r_high["required_area_mm2"] >= r_low["required_area_mm2"]


class TestFireCase:
    """Test API 521 fire case heat absorption."""

    def test_basic_fire_case(self):
        """Fire case heat input should be positive."""
        Q = fire_case_heat_input(A_wetted_m2=50.0)
        assert Q > 0

    def test_larger_area_more_heat(self):
        """Larger wetted area should absorb more heat."""
        Q1 = fire_case_heat_input(A_wetted_m2=20.0)
        Q2 = fire_case_heat_input(A_wetted_m2=100.0)
        assert Q2 > Q1

    def test_insulation_reduces_heat(self):
        """Insulation should reduce heat absorption."""
        Q_bare = fire_case_heat_input(A_wetted_m2=50.0, insulated=False)
        Q_ins = fire_case_heat_input(A_wetted_m2=50.0, insulated=True)
        assert Q_ins < Q_bare


class TestSizePSV:
    """Test orchestrator function for complete PSV sizing."""

    def test_blocked_outlet_gas(self):
        """Full PSV sizing for blocked outlet gas scenario."""
        input_data = {
            "scenario": "blocked_outlet",
            "fluid_phase": "vapor",
            "set_pressure_kPa": 2000.0,
            "back_pressure_kPa": 101.325,
            "valve_type": "conventional",
            "relief_rate_kg_hr": 8000.0,
            "relieving_temperature_K": 420.0,
            "molecular_weight": 44.0,
            "compressibility_Z": 0.92,
            "cp_cv_ratio": 1.28,
        }
        result = size_psv(input_data)
        assert result["status"] == "success"
        assert "valve_sizing" in result
        assert result["valve_sizing"]["required_area_mm2"] > 0

    def test_fire_case_scenario(self):
        """Full PSV sizing for fire case scenario."""
        input_data = {
            "scenario": "fire",
            "fluid_phase": "vapor",
            "set_pressure_kPa": 1500.0,
            "back_pressure_kPa": 101.325,
            "valve_type": "balanced_bellows",
            "wetted_area_m2": 60.0,
            "insulated": False,
            "latent_heat_J_kg": 350000.0,
            "relieving_temperature_K": 380.0,
            "molecular_weight": 58.12,
            "compressibility_Z": 0.85,
            "cp_cv_ratio": 1.1,
        }
        result = size_psv(input_data)
        # Fire case should compute heat input
        assert result is not None
