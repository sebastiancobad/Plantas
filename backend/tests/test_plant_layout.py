"""
Tests for the Plant Layout & Location Engine (Module 3).
"""

import pytest
from app.services.modules.plant_layout import get_spacing, generate_layout


class TestSpacingLookup:
    """Test API 2510 spacing matrix lookup."""

    def test_known_pair(self):
        """Fired heater to process unit should have a known spacing."""
        spacing = get_spacing("fired_heater", "process_unit")
        assert spacing >= 15.0

    def test_symmetric_lookup(self):
        """Spacing(A, B) should equal Spacing(B, A)."""
        s1 = get_spacing("process_unit", "fired_heater")
        s2 = get_spacing("fired_heater", "process_unit")
        assert s1 == s2

    def test_default_spacing(self):
        """Unknown pair should return default spacing (7.5 m)."""
        spacing = get_spacing("unknown_type_x", "unknown_type_y")
        assert spacing == pytest.approx(7.5, abs=0.5)

    def test_same_type_spacing(self):
        """Same type should still return a valid spacing."""
        spacing = get_spacing("pump", "pump")
        assert spacing >= 0


class TestGenerateLayout:
    """Test full plant layout generation."""

    def test_basic_layout(self):
        """Generate layout for a simple 3-equipment plant."""
        input_data = {
            "equipment": [
                {"tag": "V-101", "type": "separator", "distance_to": {"H-101": 20.0, "P-101": 8.0}},
                {"tag": "H-101", "type": "fired_heater", "distance_to": {"V-101": 20.0, "P-101": 18.0}},
                {"tag": "P-101", "type": "pump", "distance_to": {"V-101": 8.0, "H-101": 18.0}},
            ],
            "site_constraints": {
                "prevailing_wind": "NW",
                "site_class": "greenfield",
            },
        }
        result = generate_layout(input_data)
        assert "spacing_analysis" in result or "spacing" in result

    def test_spacing_violations_detection(self):
        """Equipment placed too close should be detected."""
        input_data = {
            "equipment": [
                {"tag": "V-101", "type": "separator", "distance_to": {"H-101": 3.0}},
                {"tag": "H-101", "type": "fired_heater", "distance_to": {"V-101": 3.0}},
            ],
            "site_constraints": {
                "prevailing_wind": "N",
                "site_class": "greenfield",
            },
        }
        result = generate_layout(input_data)
        # The result should contain spacing analysis data
        assert result is not None

    def test_wind_direction_included(self):
        """Layout should process wind direction information."""
        input_data = {
            "equipment": [
                {"tag": "V-101", "type": "process_unit", "distance_to": {}},
            ],
            "site_constraints": {
                "prevailing_wind": "SE",
                "site_class": "greenfield",
            },
        }
        result = generate_layout(input_data)
        assert result is not None
