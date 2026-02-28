"""
Mixture Property Calculator.

Orchestrates EOS and activity models to produce the fluid properties
needed by all downstream engineering modules:
    - Density, viscosity, thermal conductivity, heat capacity
    - VLE (bubble/dew point) calculations
    - Enthalpy and entropy at process conditions

This is the single entry point that modules call — they never
interact with EOS or activity models directly.
"""

import math
from dataclasses import dataclass

from app.services.thermo.eos import ComponentProps, PengRobinson, SRK
from app.utils.constants import R


@dataclass
class FluidProperties:
    """Complete fluid property set at a given T, P, composition."""
    temperature: float           # K
    pressure: float              # Pa
    density: float               # kg/m³
    molar_density: float         # mol/m³
    viscosity: float             # Pa·s
    thermal_conductivity: float  # W/(m·K)
    heat_capacity_cp: float      # J/(mol·K)
    heat_capacity_cv: float      # J/(mol·K)
    enthalpy: float              # J/mol (departure from ideal gas ref)
    compressibility: float       # Z factor
    molecular_weight: float      # g/mol (mixture average)
    phase: str                   # "vapor" or "liquid"
    surface_tension: float       # N/m (liquid only, 0 for vapor)


class MixturePropertyCalculator:
    """
    High-level property calculator for multi-component mixtures.

    Usage:
        calc = MixturePropertyCalculator(components, eos_model="PR")
        props = calc.properties(T=350, P=500000, z=[0.5, 0.3, 0.2], phase="liquid")
    """

    def __init__(self, components: list[ComponentProps],
                 eos_model: str = "PR",
                 kij: list[list[float]] | None = None):
        self.components = components
        self.nc = len(components)

        import numpy as np
        kij_arr = np.array(kij) if kij else None

        if eos_model.upper() == "PR":
            self.eos = PengRobinson(components, kij=kij_arr)
        elif eos_model.upper() == "SRK":
            self.eos = SRK(components, kij=kij_arr)
        else:
            raise ValueError(f"Unsupported EOS model: {eos_model}")

    def mixture_mw(self, z: list[float]) -> float:
        """Mixture molecular weight [g/mol]."""
        return sum(z[i] * self.components[i].Mw for i in range(self.nc))

    def properties(self, T: float, P: float, z: list[float],
                   phase: str = "auto") -> FluidProperties:
        """
        Calculate complete fluid properties at T, P, composition.

        Args:
            T: Temperature [K]
            P: Pressure [Pa]
            z: Mole fractions
            phase: "vapor", "liquid", or "auto"

        Returns:
            FluidProperties dataclass
        """
        eos_result = self.eos.calculate(T, P, z, phase_hint=phase)
        Mw = self.mixture_mw(z)

        # Mass density [kg/m³]
        mass_density = eos_result.density * Mw / 1000.0

        # Viscosity estimation (Lucas correlation for gas, Letsou-Stiel for liquid)
        mu = self._estimate_viscosity(T, P, z, eos_result.phase, mass_density)

        # Thermal conductivity (Stiel-Thodos / Latini)
        k = self._estimate_thermal_conductivity(T, z, eos_result.phase, mass_density)

        # Heat capacity (ideal gas contribution + departure)
        cp_ig = self._ideal_gas_cp(T, z)
        cp = cp_ig + 2.0  # Simplified departure; rigorous requires d²α/dT²
        cv = cp - R  # Simplified for ideal gas; real fluid uses (Cp - Cv) relation

        # Surface tension (Macleod-Sugden for liquid)
        sigma = self._estimate_surface_tension(T, z) if eos_result.phase == "liquid" else 0.0

        return FluidProperties(
            temperature=T,
            pressure=P,
            density=mass_density,
            molar_density=eos_result.density,
            viscosity=mu,
            thermal_conductivity=k,
            heat_capacity_cp=cp,
            heat_capacity_cv=cv,
            enthalpy=eos_result.departure_enthalpy,
            compressibility=eos_result.Z,
            molecular_weight=Mw,
            phase=eos_result.phase,
            surface_tension=sigma,
        )

    def _ideal_gas_cp(self, T: float, z: list[float]) -> float:
        """
        Ideal gas heat capacity [J/(mol·K)] using polynomial Cp°(T).
        Simplified: Cp_ig ≈ 3.5R for light hydrocarbons (placeholder).
        Full implementation will use DIPPR polynomial coefficients.
        """
        return 3.5 * R + 0.01 * T  # Approximate for light HCs

    def _estimate_viscosity(self, T: float, P: float, z: list[float],
                             phase: str, density: float) -> float:
        """
        Estimate mixture viscosity [Pa·s].

        Gas: Lucas corresponding-states method.
        Liquid: Letsou-Stiel correlation (simplified).
        """
        Tc_mix = sum(z[i] * self.components[i].Tc for i in range(self.nc))
        Pc_mix = sum(z[i] * self.components[i].Pc for i in range(self.nc))
        Mw_mix = self.mixture_mw(z)

        Tr = T / Tc_mix

        if phase == "vapor":
            # Lucas: μ·ξ = f(Tr) where ξ = Tc^(1/6) / (Mw^(1/2) · Pc^(2/3))
            xi = Tc_mix**(1/6) / (Mw_mix**0.5 * (Pc_mix / 1e5)**(2/3))
            if Tr <= 1.0:
                mu_xi = 0.807 * Tr**0.618 - 0.357 * math.exp(-0.449 * Tr) + \
                        0.340 * math.exp(-4.058 * Tr) + 0.018
            else:
                mu_xi = 0.0017 * Tr**0.618  # Simplified high-Tr
            return mu_xi / xi * 1e-7  # Convert to Pa·s
        else:
            # Simplified liquid viscosity estimate
            # Real implementation would use Letsou-Stiel or DIPPR correlation
            return max(1e-4 * math.exp(500 / T - 1.0), 1e-5)

    def _estimate_thermal_conductivity(self, T: float, z: list[float],
                                        phase: str, density: float) -> float:
        """
        Estimate thermal conductivity [W/(m·K)].
        Simplified correlations — to be replaced with Stiel-Thodos (gas)
        and Latini (liquid) in production.
        """
        if phase == "vapor":
            # Rough estimate for hydrocarbon vapors
            return 0.01 + 0.00005 * T
        else:
            # Rough estimate for hydrocarbon liquids
            return 0.15 - 0.0001 * T

    def _estimate_surface_tension(self, T: float, z: list[float]) -> float:
        """
        Surface tension [N/m] via simplified Macleod-Sugden.
        Placeholder: returns typical hydrocarbon value.
        """
        Tc_mix = sum(z[i] * self.components[i].Tc for i in range(self.nc))
        Tr = T / Tc_mix
        if Tr >= 1.0:
            return 0.0
        return 0.025 * (1 - Tr)**1.2  # Approximate
