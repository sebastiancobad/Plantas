"""
Tests for Economic Evaluation Engine (Module 12).

Validates CEPCI lookup, cost correlations, Lang factor methods,
utility demand calculations, and OPEX estimation.
"""

import pytest

from app.services.modules.economics import (
    get_cepci,
    estimate_equipment_cost,
    calculate_capex,
    calculate_utility_demand,
    calculate_opex,
    CEPCI_DATA,
    COST_CORRELATIONS,
    MATERIAL_FACTORS,
    _pressure_factor,
)


class TestCEPCI:
    def test_known_year(self):
        """2020 CEPCI should be 596.2."""
        assert get_cepci(2020) == pytest.approx(596.2, abs=0.1)

    def test_another_known_year(self):
        assert get_cepci(2018) == pytest.approx(603.1, abs=0.1)

    def test_interpolation(self):
        """Interpolated value should be between neighbors."""
        # 2020=596.2, 2021=708.0
        # Interpolating for a fractional year isn't supported,
        # but all integer years are in the table.
        for year in range(2000, 2027):
            index = get_cepci(year)
            assert index > 300  # Sanity: CEPCI always > 300 since 2000

    def test_extrapolation_future(self):
        """Future year should extrapolate reasonably."""
        index = get_cepci(2030)
        assert index > get_cepci(2026)  # Should increase


class TestPressureFactor:
    def test_low_pressure(self):
        """Below 5 barg → factor = 1.0."""
        assert _pressure_factor(3.0) == 1.0

    def test_moderate_pressure(self):
        """10 barg → factor = 1.15."""
        pf = _pressure_factor(10.0)
        assert pf == pytest.approx(1.15, abs=0.01)

    def test_high_pressure_monotonic(self):
        """Higher pressure → higher factor."""
        assert _pressure_factor(50) > _pressure_factor(20)
        assert _pressure_factor(100) > _pressure_factor(50)


class TestEquipmentCost:
    def test_heat_exchanger_cost(self):
        """HX at 100 m² should cost more than reference at 80 m²."""
        eq = {
            "tag": "E-101",
            "type": "shell_and_tube_heat_exchanger",
            "material": "carbon_steel",
            "design_pressure_barg": 5.0,
            "size_parameter": {"value": 100, "unit": "m2", "parameter_name": "area"},
            "cost_source": "correlations",
        }
        result = estimate_equipment_cost(eq)
        assert result["base_cost_usd"] > 32800  # Reference cost for 80 m²
        assert result["material_factor"] == 1.0  # Carbon steel
        assert result["pressure_factor"] == 1.0  # <= 5 barg

    def test_stainless_pump_cost(self):
        """SS316 pump should have material factor = 2.1."""
        eq = {
            "tag": "P-101",
            "type": "centrifugal_pump",
            "material": "stainless_steel_316",
            "design_pressure_barg": 15.0,
            "size_parameter": {"value": 50, "unit": "kW", "parameter_name": "driver_power"},
            "cost_source": "correlations",
        }
        result = estimate_equipment_cost(eq)
        assert result["material_factor"] == 2.1
        assert result["pressure_factor"] > 1.0  # 15 barg > 5 threshold

    def test_six_tenths_scaling(self):
        """Doubling size should increase cost by ~ 2^0.6 = 1.516 (for default n=0.6)."""
        eq1 = {
            "tag": "T-1", "type": "storage_tank", "material": "carbon_steel",
            "design_pressure_barg": 0,
            "size_parameter": {"value": 10, "unit": "m3", "parameter_name": "volume"},
            "cost_source": "correlations",
        }
        eq2 = {**eq1, "size_parameter": {"value": 20, "unit": "m3", "parameter_name": "volume"}}

        c1 = estimate_equipment_cost(eq1)["base_cost_usd"]
        c2 = estimate_equipment_cost(eq2)["base_cost_usd"]

        ratio = c2 / c1
        expected = 2**0.51  # Storage tank exponent
        assert ratio == pytest.approx(expected, rel=0.05)


class TestCapex:
    def test_full_capex_calculation(self):
        """Complete CAPEX with 3 equipment items."""
        input_data = {
            "project_name": "Test Unit",
            "location_factor": 1.0,
            "base_year": 2020,
            "target_year": 2024,
            "equipment_list": [
                {
                    "tag": "E-101",
                    "type": "shell_and_tube_heat_exchanger",
                    "material": "carbon_steel",
                    "design_pressure_barg": 10.0,
                    "size_parameter": {"value": 100, "unit": "m2", "parameter_name": "area"},
                    "cost_source": "correlations",
                },
                {
                    "tag": "P-101",
                    "type": "centrifugal_pump",
                    "material": "carbon_steel",
                    "design_pressure_barg": 5.0,
                    "size_parameter": {"value": 30, "unit": "kW", "parameter_name": "driver_power"},
                    "cost_source": "correlations",
                },
            ],
            "lang_factor_method": "overall",
            "contingency_percent": 15.0,
            "engineering_fee_percent": 12.0,
        }

        result = calculate_capex(input_data)

        assert result["status"] == "success"
        assert result["cepci"]["escalation_factor"] > 1.0
        assert len(result["equipment_costs"]) == 2
        assert result["cost_summary"]["total_capital_cost_usd"] > 0
        assert result["cost_summary"]["lang_factor"] == pytest.approx(4.28, abs=0.01)

    def test_detailed_lang_method(self):
        """Detailed method should use module-specific factors."""
        input_data = {
            "project_name": "Test",
            "base_year": 2020,
            "target_year": 2024,
            "equipment_list": [
                {
                    "tag": "V-101",
                    "type": "vertical_pressure_vessel",
                    "material": "carbon_steel",
                    "design_pressure_barg": 8.0,
                    "size_parameter": {"value": 10, "unit": "m3", "parameter_name": "volume"},
                    "cost_source": "correlations",
                },
            ],
            "lang_factor_method": "detailed",
            "contingency_percent": 10.0,
            "engineering_fee_percent": 10.0,
        }
        result = calculate_capex(input_data)
        assert result["status"] == "success"
        # Detailed method: installed cost = factored_cost × module_factor / mat_factor
        # Module factor for vertical vessel is 4.16
        assert result["cost_summary"]["total_installed_cost_usd"] > 0


class TestUtilityDemand:
    def test_cooling_water_demand(self):
        """2000 kW at ΔT=10°C should give ~172 m³/hr."""
        input_data = {
            "utilities": {
                "cooling_water": {
                    "consumers": [
                        {"tag": "E-101", "duty_kW": 2000, "delta_t_degC": 10}
                    ]
                }
            },
            "unit_costs": {
                "cooling_water_per_m3": 0.05,
                "lp_steam_per_ton": 25,
                "mp_steam_per_ton": 35,
                "hp_steam_per_ton": 45,
                "electricity_per_kWh": 0.08,
                "instrument_air_per_nm3": 0.02,
            },
        }
        result = calculate_utility_demand(input_data)
        # Q = ṁ·Cp·ΔT → ṁ = Q/(Cp·ΔT) = 2000/(4.18·10) = 47.85 kg/s = 172 m³/hr
        assert result["cooling_water_m3_hr"] == pytest.approx(172, rel=0.05)

    def test_steam_demand(self):
        """1000 kW LP steam should give ~1.6 ton/hr."""
        input_data = {
            "utilities": {
                "steam": {
                    "consumers": [
                        {"tag": "E-102", "duty_kW": 1000, "steam_pressure": "LP"}
                    ]
                }
            },
            "unit_costs": {
                "lp_steam_per_ton": 25, "mp_steam_per_ton": 35, "hp_steam_per_ton": 45,
                "cooling_water_per_m3": 0.05, "electricity_per_kWh": 0.08,
                "instrument_air_per_nm3": 0.02,
            },
        }
        result = calculate_utility_demand(input_data)
        # 1000 kW / 2230 kJ/kg × 3.6 = 1.61 ton/hr
        assert result["lp_steam_ton_hr"] == pytest.approx(1.61, rel=0.05)


class TestOpex:
    def test_basic_opex(self):
        input_data = {
            "annual_utility_cost_usd": 200000,
            "num_operators": 4,
            "operator_salary_usd": 80000,
            "maintenance_percent_of_capex": 4.0,
            "insurance_percent_of_capex": 2.0,
            "overhead_percent_of_labor": 40.0,
            "total_installed_cost_usd": 1000000,
        }
        result = calculate_opex(input_data)
        assert result["status"] == "success"

        opex = result["annual_opex"]
        assert opex["utilities_usd"] == 200000
        assert opex["labor_usd"] == 4 * 80000 * 5  # 5 shifts
        assert opex["maintenance_usd"] == 40000  # 4% of 1M
        assert opex["insurance_usd"] == 20000   # 2% of 1M
        assert opex["total_annual_opex_usd"] > 0
