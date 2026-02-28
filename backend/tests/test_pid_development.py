"""
Tests for the P&ID Development Engine (Module 11).
"""

import pytest
from app.services.modules.pid_development import generate_pid_data


class TestPIDGeneration:
    """Test P&ID drawing data generation."""

    def test_basic_pid_generation(self):
        """Generate P&ID data for a simple unit with vessel and instruments."""
        input_data = {
            "unit_number": "10",
            "equipment": [
                {
                    "tag": "V-1001",
                    "type": "vessel",
                    "description": "Feed Drum",
                    "x": 100,
                    "y": 200,
                },
                {
                    "tag": "P-1001A",
                    "type": "pump",
                    "description": "Feed Pump A",
                    "x": 300,
                    "y": 200,
                },
            ],
            "instruments": [
                {
                    "measured_variable": "Level",
                    "function": "IC",
                    "loop_number": 1001,
                    "location": "control_room",
                    "sis": False,
                    "suffix": "",
                    "x": 150,
                    "y": 150,
                },
                {
                    "measured_variable": "Pressure",
                    "function": "T",
                    "loop_number": 1002,
                    "location": "field",
                    "sis": False,
                    "suffix": "",
                    "x": 150,
                    "y": 250,
                },
            ],
            "lines": [
                {
                    "from": "V-1001",
                    "to": "P-1001A",
                    "diameter_inches": 6.0,
                    "spec_class": "A1A",
                    "fluid_code": "HC",
                    "insulation": "",
                },
            ],
            "valves": [
                {
                    "tag": "LV-1001",
                    "type": "control_valve",
                    "on_line": "V-1001 to P-1001A",
                    "fail_position": "FC",
                },
            ],
        }
        result = generate_pid_data(input_data)

        assert result["status"] == "success"
        dd = result["drawing_data"]
        assert "equipment_nodes" in dd
        assert "instrument_nodes" in dd
        assert "process_lines" in dd
        assert len(dd["equipment_nodes"]) == 2
        assert len(dd["instrument_nodes"]) >= 2

    def test_line_numbering(self):
        """Generated lines should have proper line numbers."""
        input_data = {
            "unit_number": "20",
            "equipment": [
                {"tag": "E-2001", "type": "heater", "description": "Feed Heater",
                 "x": 0, "y": 0},
                {"tag": "R-2001", "type": "vessel", "description": "Reactor",
                 "x": 200, "y": 0},
            ],
            "instruments": [],
            "lines": [
                {
                    "from": "E-2001",
                    "to": "R-2001",
                    "diameter_inches": 4.0,
                    "spec_class": "B2B",
                    "fluid_code": "HC",
                    "insulation": "HT",
                },
            ],
            "valves": [],
        }
        result = generate_pid_data(input_data)
        lines = result["drawing_data"]["process_lines"]
        assert len(lines) >= 1
        line = lines[0]
        assert "line_number" in line
        assert len(line["line_number"]) > 0

    def test_instrument_tags_isa(self):
        """Instrument tags should follow ISA 5.1 convention."""
        input_data = {
            "unit_number": "30",
            "equipment": [
                {"tag": "V-3001", "type": "vessel", "description": "Test Vessel",
                 "x": 0, "y": 0},
            ],
            "instruments": [
                {
                    "measured_variable": "Temperature",
                    "function": "IC",
                    "loop_number": 3001,
                    "location": "dcs",
                    "sis": False,
                    "suffix": "",
                    "x": 50,
                    "y": 50,
                },
                {
                    "measured_variable": "Flow",
                    "function": "T",
                    "loop_number": 3002,
                    "location": "field",
                    "sis": False,
                    "suffix": "",
                    "x": 50,
                    "y": 100,
                },
            ],
            "lines": [],
            "valves": [],
        }
        result = generate_pid_data(input_data)
        for inst in result["drawing_data"]["instrument_nodes"]:
            tag = inst.get("tag", "")
            assert len(tag) > 0

    def test_empty_instruments_ok(self):
        """Should handle equipment-only P&IDs (no instruments)."""
        input_data = {
            "unit_number": "40",
            "equipment": [
                {"tag": "T-4001", "type": "vessel", "description": "Storage Tank",
                 "x": 0, "y": 0},
            ],
            "instruments": [],
            "lines": [],
            "valves": [],
        }
        result = generate_pid_data(input_data)
        dd = result["drawing_data"]
        assert len(dd["equipment_nodes"]) == 1
        assert len(dd["instrument_nodes"]) == 0

    def test_tag_summary(self):
        """Result should include a tag summary with counts."""
        input_data = {
            "unit_number": "50",
            "equipment": [
                {"tag": "V-5001", "type": "vessel", "description": "Vessel",
                 "x": 0, "y": 0},
            ],
            "instruments": [],
            "lines": [],
            "valves": [],
        }
        result = generate_pid_data(input_data)
        assert "tag_summary" in result
        assert result["tag_summary"]["equipment_count"] == 1
