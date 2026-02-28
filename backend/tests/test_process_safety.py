"""
Tests for the Process Safety & Industrial Hygiene Engine (Module 9).
"""

import pytest
from app.services.modules.process_safety import (
    calculate_dow_fei,
    generate_hazop,
    inherently_safer_design_checklist,
)


class TestDowFEI:
    """Test Dow Fire & Explosion Index calculation."""

    def test_basic_fei_calculation(self):
        """Calculate F&EI for a simple propane storage unit."""
        input_data = {
            "material_name": "propane",
            "general_process_hazards": {
                "exothermic_reaction": False,
                "endothermic_reaction": False,
                "material_handling_transfer": True,
                "enclosed_unit": False,
                "access_limitations": False,
                "drainage_spill_control": True,
            },
            "special_process_hazards": {
                "toxic_materials": False,
                "toxic_Nh": 0,
                "operating_temperature_C": 25.0,
                "operating_pressure_barg": 8.0,
                "flammable_quantity_kg": 5000.0,
                "corrosion_erosion": False,
                "joint_leakage_potential": False,
                "fired_equipment_nearby": False,
            },
            "replacement_cost_usd": 2000000.0,
        }
        result = calculate_dow_fei(input_data)

        assert result["status"] == "success"
        assert result["material_factor"] > 0
        assert result["general_process_hazard_factor_F1"] >= 1.0
        assert result["special_process_hazard_factor_F2"] >= 1.0
        assert result["unit_hazard_factor_F3"] >= 1.0
        assert result["fire_explosion_index"] > 0
        assert "degree_of_hazard" in result
        assert result["radius_of_exposure_m"] > 0

    def test_fei_classification(self):
        """FEI should produce a valid hazard degree classification."""
        input_data = {
            "material_name": "hydrogen",
            "general_process_hazards": {
                "exothermic_reaction": True,
                "endothermic_reaction": False,
                "material_handling_transfer": True,
                "enclosed_unit": True,
                "access_limitations": True,
                "drainage_spill_control": False,
            },
            "special_process_hazards": {
                "toxic_materials": False,
                "toxic_Nh": 0,
                "operating_temperature_C": 400.0,
                "operating_pressure_barg": 50.0,
                "flammable_quantity_kg": 1000.0,
                "corrosion_erosion": True,
                "joint_leakage_potential": True,
                "fired_equipment_nearby": True,
            },
            "replacement_cost_usd": 10000000.0,
        }
        result = calculate_dow_fei(input_data)
        valid_degrees = ["Light", "Moderate", "Intermediate", "Heavy", "Severe"]
        assert result["degree_of_hazard"] in valid_degrees

    def test_higher_hazards_higher_fei(self):
        """More hazard penalties should produce higher FEI."""
        base = {
            "material_name": "methane",
            "general_process_hazards": {
                "exothermic_reaction": False,
                "endothermic_reaction": False,
                "material_handling_transfer": False,
                "enclosed_unit": False,
                "access_limitations": False,
                "drainage_spill_control": False,
            },
            "special_process_hazards": {
                "toxic_materials": False,
                "toxic_Nh": 0,
                "operating_temperature_C": 25.0,
                "operating_pressure_barg": 1.0,
                "flammable_quantity_kg": 100.0,
                "corrosion_erosion": False,
                "joint_leakage_potential": False,
                "fired_equipment_nearby": False,
            },
            "replacement_cost_usd": 1000000.0,
        }
        r_low = calculate_dow_fei(base)

        import copy
        high_hazard = copy.deepcopy(base)
        high_hazard["special_process_hazards"] = {
            "toxic_materials": True,
            "toxic_Nh": 4,
            "operating_temperature_C": 300.0,
            "operating_pressure_barg": 100.0,
            "flammable_quantity_kg": 50000.0,
            "corrosion_erosion": True,
            "joint_leakage_potential": True,
            "fired_equipment_nearby": True,
        }
        r_high = calculate_dow_fei(high_hazard)

        assert r_high["fire_explosion_index"] > r_low["fire_explosion_index"]


class TestHAZOP:
    """Test HAZOP worksheet generation."""

    def test_basic_hazop_generation(self):
        """Generate HAZOP for a simple heat exchanger node."""
        input_data = {
            "node_description": "Shell-side of E-101 Heat Exchanger",
            "design_intent": "Cool process gas from 120°C to 40°C using cooling water",
            "parameters": ["flow", "temperature", "pressure"],
        }
        result = generate_hazop(input_data)

        assert "worksheet" in result
        assert len(result["worksheet"]) > 0
        assert len(result["worksheet"]) >= 6

    def test_hazop_has_required_fields(self):
        """Each HAZOP entry should have guideword, parameter, deviation."""
        input_data = {
            "node_description": "Feed line to reactor R-201",
            "design_intent": "Transfer feed at 50 m3/hr and 25°C",
            "parameters": ["flow"],
        }
        result = generate_hazop(input_data)
        for entry in result["worksheet"]:
            assert "guideword" in entry
            assert "parameter" in entry
            assert "deviation" in entry


class TestISDChecklist:
    """Test Inherently Safer Design checklist."""

    def test_isd_principles(self):
        """ISD checklist should include Kletz's four principles."""
        input_data = {"process_description": "Ammonia storage tank"}
        result = inherently_safer_design_checklist(input_data)

        assert result["status"] == "success"
        assert "principles" in result
        principle_names = [p["principle"] for p in result["principles"]]
        for expected in ["Minimize", "Substitute", "Moderate", "Simplify"]:
            assert expected in principle_names

    def test_isd_has_questions(self):
        """Each principle should have associated questions."""
        input_data = {"process_description": "Reactor system"}
        result = inherently_safer_design_checklist(input_data)
        for principle in result["principles"]:
            assert "questions" in principle
            assert len(principle["questions"]) >= 1
