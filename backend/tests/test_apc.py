"""
Tests for the Advanced Process Control Engine (Module 10).
"""

import pytest
from app.services.modules.apc import tune_pid_loop, get_control_strategy


class TestPIDTuning:
    """Test PID tuning methods."""

    def test_ziegler_nichols_pi(self):
        """Ziegler-Nichols PI tuning should give valid Kc, Ti."""
        input_data = {
            "process_gain": 2.0,
            "time_constant_s": 60.0,
            "dead_time_s": 10.0,
            "controller_type": "PI",
        }
        result = tune_pid_loop(input_data)

        assert result["status"] == "success"
        zn = result["tuning_results"]["ziegler_nichols"]
        assert zn["Kc"] > 0
        assert zn["Ti"] > 0

    def test_cohen_coon_pid(self):
        """Cohen-Coon PID tuning for a standard FOPDT process."""
        input_data = {
            "process_gain": 1.5,
            "time_constant_s": 120.0,
            "dead_time_s": 20.0,
            "controller_type": "PID",
        }
        result = tune_pid_loop(input_data)

        cc = result["tuning_results"]["cohen_coon"]
        assert cc["Kc"] > 0
        assert cc["Ti"] > 0
        assert cc["Td"] is not None and cc["Td"] >= 0

    def test_lambda_tuning(self):
        """Lambda tuning should give conservative Kc."""
        input_data = {
            "process_gain": 3.0,
            "time_constant_s": 100.0,
            "dead_time_s": 15.0,
            "controller_type": "PI",
            "lambda_factor": 3.0,
        }
        result = tune_pid_loop(input_data)

        lt = result["tuning_results"]["lambda_imc"]
        assert lt["Kc"] > 0
        assert lt["Ti"] > 0

    def test_lambda_most_conservative(self):
        """Lambda tuning should generally give lower Kc than Z-N or C-C."""
        input_data = {
            "process_gain": 2.0,
            "time_constant_s": 80.0,
            "dead_time_s": 10.0,
            "controller_type": "PI",
            "lambda_factor": 3.0,
        }
        result = tune_pid_loop(input_data)

        kc_zn = result["tuning_results"]["ziegler_nichols"]["Kc"]
        kc_lambda = result["tuning_results"]["lambda_imc"]["Kc"]
        # Lambda with factor=3 should be more conservative (lower Kc)
        assert kc_lambda < kc_zn

    def test_recommendation_included(self):
        """Result should include a tuning recommendation."""
        input_data = {
            "process_gain": 1.0,
            "time_constant_s": 50.0,
            "dead_time_s": 5.0,
            "controller_type": "PI",
        }
        result = tune_pid_loop(input_data)
        assert "recommendation" in result

    def test_high_dead_time_ratio(self):
        """High dead-time-to-time-constant ratio should still work."""
        input_data = {
            "process_gain": 1.0,
            "time_constant_s": 10.0,
            "dead_time_s": 8.0,
            "controller_type": "PI",
        }
        result = tune_pid_loop(input_data)
        assert result["tuning_results"]["ziegler_nichols"]["Kc"] > 0

    def test_process_model_info(self):
        """Should return process model characterization."""
        input_data = {
            "process_gain": 2.0,
            "time_constant_s": 60.0,
            "dead_time_s": 10.0,
            "controller_type": "PI",
        }
        result = tune_pid_loop(input_data)
        pm = result["process_model"]
        assert pm["gain_K"] == 2.0
        assert pm["dead_time_ratio"] == pytest.approx(10.0 / 60.0, rel=0.01)
        assert "controllability" in pm


class TestControlStrategy:
    """Test control strategy recommendations."""

    def test_heat_exchanger_strategy(self):
        """Heat exchanger should have a recognized control strategy."""
        input_data = {"unit_type": "heat_exchanger"}
        result = get_control_strategy(input_data)
        assert result is not None

    def test_distillation_strategy(self):
        """Distillation column should have strategy info."""
        input_data = {"unit_type": "distillation_column"}
        result = get_control_strategy(input_data)
        assert result is not None

    def test_unknown_unit_type(self):
        """Unknown unit type should return a graceful response."""
        input_data = {"unit_type": "unknown_widget"}
        result = get_control_strategy(input_data)
        assert result is not None

    def test_reactor_strategy(self):
        """Reactor control strategy should exist."""
        input_data = {"unit_type": "reactor"}
        result = get_control_strategy(input_data)
        assert result is not None
