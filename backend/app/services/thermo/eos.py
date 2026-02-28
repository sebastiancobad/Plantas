"""
Equations of State — Peng-Robinson and Soave-Redlich-Kwong.

These cubic EOS are the workhorses of hydrocarbon thermodynamics.
They calculate compressibility factor Z, fugacity coefficients φᵢ,
and departure functions for enthalpy/entropy.

References:
    - Peng & Robinson, Ind. Eng. Chem. Fundam. 15(1), 59-64, 1976
    - Soave, Chem. Eng. Sci. 27(6), 1197-1203, 1972
"""

import math
from dataclasses import dataclass

import numpy as np

from app.utils.constants import R


@dataclass
class ComponentProps:
    """Pure component properties required by cubic EOS."""
    name: str
    Tc: float     # Critical temperature [K]
    Pc: float     # Critical pressure [Pa]
    omega: float  # Acentric factor [-]
    Mw: float     # Molecular weight [g/mol]


@dataclass
class EOSResult:
    """Result from an EOS calculation at given T, P, composition."""
    Z: float                        # Compressibility factor
    density: float                  # Molar density [mol/m³]
    molar_volume: float             # [m³/mol]
    fugacity_coefficients: list[float]  # φᵢ for each component
    departure_enthalpy: float       # H - H_ig [J/mol]
    phase: str                      # "vapor" or "liquid"


class PengRobinson:
    """
    Peng-Robinson Equation of State.

    P = RT/(V-b) - a·α(T) / [V(V+b) + b(V-b)]

    Mixing rules: van der Waals one-fluid (classical).
    """

    # PR constants
    OMEGA_A = 0.45724
    OMEGA_B = 0.07780
    DELTA1 = 1 + math.sqrt(2)
    DELTA2 = 1 - math.sqrt(2)

    def __init__(self, components: list[ComponentProps], kij: np.ndarray | None = None):
        self.components = components
        self.nc = len(components)
        # Binary interaction parameters (symmetric matrix)
        self.kij = kij if kij is not None else np.zeros((self.nc, self.nc))

    def _alpha(self, T: float, comp: ComponentProps) -> float:
        """Temperature-dependent alpha function."""
        Tr = T / comp.Tc
        if comp.omega <= 0.491:
            m = 0.37464 + 1.54226 * comp.omega - 0.26992 * comp.omega**2
        else:
            m = 0.3796 + 1.485 * comp.omega - 0.1644 * comp.omega**2 + 0.01667 * comp.omega**3
        return (1 + m * (1 - math.sqrt(Tr)))**2

    def _compute_ab(self, T: float) -> tuple[list[float], list[float]]:
        """Compute pure-component a·α(T) and b values."""
        a_vals = []
        b_vals = []
        for comp in self.components:
            ai = self.OMEGA_A * R**2 * comp.Tc**2 / comp.Pc
            bi = self.OMEGA_B * R * comp.Tc / comp.Pc
            a_vals.append(ai * self._alpha(T, comp))
            b_vals.append(bi)
        return a_vals, b_vals

    def _mixing_rules(self, z: list[float], a_vals: list[float],
                       b_vals: list[float]) -> tuple[float, float]:
        """Van der Waals one-fluid mixing rules."""
        am = 0.0
        bm = 0.0
        for i in range(self.nc):
            bm += z[i] * b_vals[i]
            for j in range(self.nc):
                aij = math.sqrt(a_vals[i] * a_vals[j]) * (1 - self.kij[i][j])
                am += z[i] * z[j] * aij
        return am, bm

    def _solve_cubic(self, A: float, B: float) -> list[float]:
        """
        Solve the cubic in Z:
          Z³ - (1-B)Z² + (A - 3B² - 2B)Z - (AB - B² - B³) = 0
        Returns real positive roots sorted ascending.
        """
        c2 = -(1 - B)
        c1 = A - 3 * B**2 - 2 * B
        c0 = -(A * B - B**2 - B**3)

        roots = np.roots([1, c2, c1, c0])
        real_positive = [float(r.real) for r in roots
                         if abs(r.imag) < 1e-10 and r.real > 0]
        return sorted(real_positive)

    def calculate(self, T: float, P: float, z: list[float],
                  phase_hint: str = "auto") -> EOSResult:
        """
        Calculate thermodynamic properties at given T, P, composition.

        Args:
            T: Temperature [K]
            P: Pressure [Pa]
            z: Mole fractions (must sum to 1)
            phase_hint: "vapor", "liquid", or "auto" (picks by Gibbs energy)

        Returns:
            EOSResult with Z, density, fugacity coefficients, etc.
        """
        a_vals, b_vals = self._compute_ab(T)
        am, bm = self._mixing_rules(z, a_vals, b_vals)

        A = am * P / (R * T)**2
        B = bm * P / (R * T)

        roots = self._solve_cubic(A, B)
        if not roots:
            raise ValueError(f"No real positive roots at T={T} K, P={P} Pa")

        # Phase selection
        if phase_hint == "vapor":
            Z = max(roots)
        elif phase_hint == "liquid":
            Z = min(roots)
        else:
            # Auto: pick Z that minimizes Gibbs energy
            Z = min(roots) if len(roots) == 1 else self._select_by_gibbs(roots, A, B)

        phase = "vapor" if Z == max(roots) else "liquid"

        Vm = Z * R * T / P
        rho = 1.0 / Vm  # mol/m³

        # Fugacity coefficients
        phi = self._fugacity_coefficients(T, P, z, Z, a_vals, b_vals, am, bm, A, B)

        # Departure enthalpy
        dep_h = self._departure_enthalpy(T, z, Z, a_vals, b_vals, am, bm, A, B)

        return EOSResult(
            Z=Z,
            density=rho,
            molar_volume=Vm,
            fugacity_coefficients=phi,
            departure_enthalpy=dep_h,
            phase=phase,
        )

    def _select_by_gibbs(self, roots: list[float], A: float, B: float) -> float:
        """Select root with minimum Gibbs energy departure."""
        def gibbs(Z):
            return Z - 1 - math.log(Z - B) - A / (2 * math.sqrt(2) * B) * math.log(
                (Z + self.DELTA1 * B) / (Z + self.DELTA2 * B)
            )
        return min(roots, key=gibbs)

    def _fugacity_coefficients(self, T: float, P: float, z: list[float],
                                Z: float, a_vals: list[float], b_vals: list[float],
                                am: float, bm: float, A: float, B: float) -> list[float]:
        """Compute ln(φᵢ) for each component in the mixture."""
        phi = []
        sqrt2 = math.sqrt(2)
        for i in range(self.nc):
            # ∂(n²am)/∂nᵢ
            sum_aij = sum(
                z[j] * math.sqrt(a_vals[i] * a_vals[j]) * (1 - self.kij[i][j])
                for j in range(self.nc)
            )
            da_dni = 2 * sum_aij

            bi = b_vals[i]
            ln_phi = (bi / bm) * (Z - 1) - math.log(Z - B) - \
                A / (2 * sqrt2 * B) * (da_dni / am - bi / bm) * \
                math.log((Z + self.DELTA1 * B) / (Z + self.DELTA2 * B))
            phi.append(math.exp(ln_phi))
        return phi

    def _departure_enthalpy(self, T: float, z: list[float], Z: float,
                             a_vals: list[float], b_vals: list[float],
                             am: float, bm: float, A: float, B: float) -> float:
        """Compute (H - H_ig) departure enthalpy [J/mol]."""
        # dα/dT contribution
        da_dT = 0.0
        for i in range(self.nc):
            for j in range(self.nc):
                comp_i = self.components[i]
                comp_j = self.components[j]
                # d(ai*alphai)/dT
                ai0 = self.OMEGA_A * R**2 * comp_i.Tc**2 / comp_i.Pc
                aj0 = self.OMEGA_A * R**2 * comp_j.Tc**2 / comp_j.Pc
                sqrt_ai_alpha_i = math.sqrt(a_vals[i])
                sqrt_aj_alpha_j = math.sqrt(a_vals[j])

                if comp_i.omega <= 0.491:
                    mi = 0.37464 + 1.54226 * comp_i.omega - 0.26992 * comp_i.omega**2
                else:
                    mi = 0.3796 + 1.485 * comp_i.omega - 0.1644 * comp_i.omega**2 + 0.01667 * comp_i.omega**3

                if comp_j.omega <= 0.491:
                    mj = 0.37464 + 1.54226 * comp_j.omega - 0.26992 * comp_j.omega**2
                else:
                    mj = 0.3796 + 1.485 * comp_j.omega - 0.1644 * comp_j.omega**2 + 0.01667 * comp_j.omega**3

                Tri = T / comp_i.Tc
                Trj = T / comp_j.Tc

                dai_dT = -mi * math.sqrt(ai0 / (T * comp_i.Tc)) * sqrt_ai_alpha_i / sqrt_ai_alpha_i if sqrt_ai_alpha_i > 0 else 0
                # Simplified: T * dam/dT
                da_dT += z[i] * z[j] * (1 - self.kij[i][j]) * (
                    -0.5 * math.sqrt(a_vals[i] * a_vals[j]) * (
                        mi / math.sqrt(Tri * self._alpha(T, comp_i)) +
                        mj / math.sqrt(Trj * self._alpha(T, comp_j))
                    )
                )

        sqrt2 = math.sqrt(2)
        # B = bm * P / (R * T), so bm * P / (R * T) = B
        ln_term = math.log(
            (Z + self.DELTA1 * B) /
            (Z + self.DELTA2 * B)
        )

        dep_h = R * T * (Z - 1) + (T * da_dT - am) / (2 * sqrt2 * bm) * ln_term
        return dep_h


class SRK(PengRobinson):
    """
    Soave-Redlich-Kwong Equation of State.

    Inherits from PengRobinson but overrides constants and alpha function.
    P = RT/(V-b) - a·α(T) / [V(V+b)]
    """

    OMEGA_A = 0.42748
    OMEGA_B = 0.08664
    DELTA1 = 1.0
    DELTA2 = 0.0

    def _alpha(self, T: float, comp: ComponentProps) -> float:
        Tr = T / comp.Tc
        m = 0.48 + 1.574 * comp.omega - 0.176 * comp.omega**2
        return (1 + m * (1 - math.sqrt(Tr)))**2

    def _solve_cubic(self, A: float, B: float) -> list[float]:
        """SRK cubic: Z³ - Z² + (A - B - B²)Z - AB = 0"""
        c2 = -1.0
        c1 = A - B - B**2
        c0 = -A * B

        roots = np.roots([1, c2, c1, c0])
        real_positive = [float(r.real) for r in roots
                         if abs(r.imag) < 1e-10 and r.real > 0]
        return sorted(real_positive)
