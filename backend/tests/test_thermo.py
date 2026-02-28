"""
Tests for the Thermodynamic Property Engine.

Validates EOS calculations against known reference values
from NIST and Perry's Chemical Engineers' Handbook.
"""

import math
import pytest

from app.services.thermo.eos import PengRobinson, SRK, ComponentProps
from app.services.thermo.activity import NRTL, UNIQUAC
from app.services.thermo.properties import MixturePropertyCalculator
from app.services.components.database import get_component, list_components
from app.utils.constants import R
import numpy as np


# ── Component Database Tests ────────────────────────────────────────

class TestComponentDatabase:
    def test_get_known_component(self):
        comp = get_component("methane")
        assert comp.Tc == pytest.approx(190.56, abs=1.0)
        assert comp.Pc == pytest.approx(4599000, rel=0.01)
        assert comp.omega == pytest.approx(0.011, abs=0.01)
        assert comp.Mw == pytest.approx(16.043, abs=0.01)

    def test_get_water(self):
        comp = get_component("water")
        assert comp.Tc == pytest.approx(647.10, abs=1.0)
        assert comp.Mw == pytest.approx(18.015, abs=0.01)

    def test_unknown_component_raises(self):
        with pytest.raises(KeyError):
            get_component("unobtanium")

    def test_list_components_nonempty(self):
        comps = list_components()
        assert len(comps) >= 25
        assert "methane" in comps
        assert "water" in comps

    def test_n_hexane_lookup(self):
        """Verify that n-hexane can be found with the n- prefix."""
        comp = get_component("n-hexane")
        assert comp.Tc == pytest.approx(507.6, abs=1.0)


# ── Peng-Robinson EOS Tests ─────────────────────────────────────────

class TestPengRobinson:
    def setup_method(self):
        self.methane = ComponentProps("methane", Tc=190.56, Pc=4599000, omega=0.011, Mw=16.043)
        self.ethane = ComponentProps("ethane", Tc=305.32, Pc=4872000, omega=0.099, Mw=30.070)

    def test_pure_methane_vapor(self):
        """Pure methane at 200 K, 1 bar should be clearly vapor."""
        pr = PengRobinson([self.methane])
        result = pr.calculate(T=200, P=100000, z=[1.0], phase_hint="vapor")
        assert result.phase == "vapor"
        assert result.Z > 0.8  # Vapor-like Z
        assert result.density > 0

    def test_pure_methane_high_pressure(self):
        """Methane at 150 K, 40 bar — should find liquid root."""
        pr = PengRobinson([self.methane])
        result = pr.calculate(T=150, P=4000000, z=[1.0], phase_hint="liquid")
        assert result.phase == "liquid"
        assert result.Z < 0.5

    def test_binary_mixture(self):
        """Methane-ethane mixture at moderate conditions."""
        pr = PengRobinson([self.methane, self.ethane])
        result = pr.calculate(T=250, P=1000000, z=[0.7, 0.3], phase_hint="vapor")
        assert result.Z > 0
        assert len(result.fugacity_coefficients) == 2
        for phi in result.fugacity_coefficients:
            assert phi > 0

    def test_ideal_gas_limit(self):
        """At very low pressure, Z should approach 1.0."""
        pr = PengRobinson([self.methane])
        result = pr.calculate(T=400, P=1000, z=[1.0])  # 0.01 bar
        assert result.Z == pytest.approx(1.0, abs=0.01)


# ── SRK EOS Tests ──────────────────────────────────────────────────

class TestSRK:
    def test_srk_vs_pr_qualitative(self):
        """SRK and PR should give qualitatively similar results."""
        methane = ComponentProps("methane", Tc=190.56, Pc=4599000, omega=0.011, Mw=16.043)

        pr = PengRobinson([methane])
        srk = SRK([methane])

        r_pr = pr.calculate(T=200, P=100000, z=[1.0], phase_hint="vapor")
        r_srk = srk.calculate(T=200, P=100000, z=[1.0], phase_hint="vapor")

        # Both should give vapor
        assert r_pr.phase == "vapor"
        assert r_srk.phase == "vapor"
        # Z values should be close (within 5%)
        assert r_pr.Z == pytest.approx(r_srk.Z, rel=0.05)


# ── NRTL Activity Coefficient Tests ────────────────────────────────

class TestNRTL:
    def test_pure_component_gamma_is_one(self):
        """Activity coefficient of a pure component must be 1.0."""
        tau = np.array([[0.0, 1.5], [0.8, 0.0]])
        alpha = np.array([[0.0, 0.3], [0.3, 0.0]])
        nrtl = NRTL(tau, alpha)

        gamma = nrtl.activity_coefficients([1.0, 0.0], T=350)
        assert gamma[0] == pytest.approx(1.0, abs=0.01)

    def test_symmetric_binary(self):
        """Equimolar binary should give equal γ if params are symmetric."""
        tau = np.array([[0.0, 1.0], [1.0, 0.0]])
        alpha = np.array([[0.0, 0.3], [0.3, 0.0]])
        nrtl = NRTL(tau, alpha)

        gamma = nrtl.activity_coefficients([0.5, 0.5], T=350)
        assert gamma[0] == pytest.approx(gamma[1], rel=0.01)

    def test_gamma_greater_than_one(self):
        """Non-ideal mixtures should have γ > 1 (positive deviation)."""
        tau = np.array([[0.0, 2.0], [1.5, 0.0]])
        alpha = np.array([[0.0, 0.3], [0.3, 0.0]])
        nrtl = NRTL(tau, alpha)

        gamma = nrtl.activity_coefficients([0.3, 0.7], T=350)
        assert gamma[0] > 1.0
        assert gamma[1] > 1.0


# ── UNIQUAC Tests ──────────────────────────────────────────────────

class TestUNIQUAC:
    def test_pure_component(self):
        """Pure component must give γ = 1."""
        r = [2.1055, 0.92]
        q = [1.972, 1.40]
        u = np.array([[0.0, 200.0], [-100.0, 0.0]])
        model = UNIQUAC(r, q, u)

        gamma = model.activity_coefficients([1.0, 0.0], T=350)
        assert gamma[0] == pytest.approx(1.0, abs=0.01)


# ── Mixture Property Calculator Tests ──────────────────────────────

class TestMixturePropertyCalculator:
    def test_pure_water_properties(self):
        """Water properties at 25°C, 1 atm — sanity check."""
        water = get_component("water")
        calc = MixturePropertyCalculator([water])
        props = calc.properties(T=298.15, P=101325, z=[1.0], phase="liquid")

        assert props.molecular_weight == pytest.approx(18.015, abs=0.01)
        assert props.phase == "liquid"
        assert props.density > 0

    def test_hexane_heptane_mixture(self):
        """Binary hydrocarbon mix should give reasonable liquid density."""
        hexane = get_component("n-hexane")
        heptane = get_component("n-heptane")
        calc = MixturePropertyCalculator([hexane, heptane])
        props = calc.properties(T=350, P=500000, z=[0.5, 0.5], phase="liquid")

        assert props.density > 400  # kg/m³ — liquid range for hydrocarbons
        assert props.viscosity > 0
        assert props.thermal_conductivity > 0
