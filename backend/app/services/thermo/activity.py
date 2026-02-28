"""
Activity Coefficient Models — NRTL and UNIQUAC.

Used for strongly non-ideal liquid mixtures where cubic EOS
mixing rules are insufficient (e.g., alcohol-water, polar systems).

The γ-φ approach:
    yᵢ · φᵢ · P = xᵢ · γᵢ · Pᵢˢᵃᵗ · φᵢˢᵃᵗ · POYᵢ

References:
    - Renon & Prausnitz, AIChE J. 14(1), 135-144, 1968 (NRTL)
    - Abrams & Prausnitz, AIChE J. 21(1), 116-128, 1975 (UNIQUAC)
"""

import math

import numpy as np


class NRTL:
    """
    Non-Random Two-Liquid model.

    Parameters:
        tau_ij: Interaction energy parameters (asymmetric matrix)
        alpha_ij: Non-randomness parameters (typically 0.2-0.47)
    """

    def __init__(self, tau: np.ndarray, alpha: np.ndarray):
        """
        Args:
            tau: (n x n) matrix of τᵢⱼ = (gᵢⱼ - gⱼⱼ) / RT
            alpha: (n x n) matrix of αᵢⱼ (non-randomness, symmetric)
        """
        self.tau = np.array(tau, dtype=float)
        self.alpha = np.array(alpha, dtype=float)
        self.nc = self.tau.shape[0]

    def activity_coefficients(self, x: list[float], T: float) -> list[float]:
        """
        Compute activity coefficients γᵢ at given liquid composition.

        Args:
            x: Mole fractions in liquid phase
            T: Temperature [K] (τ may be T-dependent; here treated as constant)

        Returns:
            List of γᵢ values for each component.
        """
        x = np.array(x, dtype=float)
        tau = self.tau
        alpha = self.alpha
        nc = self.nc

        # G_ij = exp(-alpha_ij * tau_ij)
        G = np.exp(-alpha * tau)

        ln_gamma = np.zeros(nc)

        for i in range(nc):
            # Numerator and denominator of first term
            sum_tau_G_x = sum(tau[j][i] * G[j][i] * x[j] for j in range(nc))
            sum_G_x_i = sum(G[j][i] * x[j] for j in range(nc))

            term1 = sum_tau_G_x / sum_G_x_i

            term2 = 0.0
            for j in range(nc):
                sum_G_x_j = sum(G[k][j] * x[k] for k in range(nc))
                sum_tau_G_x_j = sum(tau[k][j] * G[k][j] * x[k] for k in range(nc))

                term2 += (x[j] * G[i][j] / sum_G_x_j) * (
                    tau[i][j] - sum_tau_G_x_j / sum_G_x_j
                )

            ln_gamma[i] = term1 + term2

        return [math.exp(lg) for lg in ln_gamma]


class UNIQUAC:
    """
    Universal Quasi-Chemical Activity Coefficient model.

    Combines a combinatorial (size/shape) and residual (energy) contribution.

    Parameters:
        r: Volume parameters (van der Waals) for each component
        q: Surface area parameters for each component
        u_ij: Interaction energy parameters [K] (u_ij - u_jj)/R
    """

    # Coordination number (lattice)
    Z_COORD = 10

    def __init__(self, r: list[float], q: list[float], u: np.ndarray):
        """
        Args:
            r: Pure-component volume parameters
            q: Pure-component surface area parameters
            u: (n x n) interaction parameter matrix (uᵢⱼ - uⱼⱼ)/R [K]
        """
        self.r = np.array(r, dtype=float)
        self.q = np.array(q, dtype=float)
        self.u = np.array(u, dtype=float)
        self.nc = len(r)

    def activity_coefficients(self, x: list[float], T: float) -> list[float]:
        """
        Compute activity coefficients γᵢ = γᵢᶜᵒᵐᵇ · γᵢʳᵉˢ.

        Args:
            x: Liquid mole fractions
            T: Temperature [K]

        Returns:
            List of γᵢ for each component.
        """
        x = np.array(x, dtype=float)
        nc = self.nc
        r = self.r
        q = self.q

        # Segment and area fractions
        sum_rx = np.dot(r, x)
        sum_qx = np.dot(q, x)
        phi = r * x / sum_rx  # Volume fraction
        theta = q * x / sum_qx  # Area fraction

        # l parameter
        l = (self.Z_COORD / 2) * (r - q) - (r - 1)

        # Boltzmann factors τᵢⱼ = exp(-uᵢⱼ / T)
        tau = np.exp(-self.u / T)

        ln_gamma = np.zeros(nc)

        for i in range(nc):
            # Combinatorial contribution
            ln_comb = (
                math.log(phi[i] / x[i])
                + (self.Z_COORD / 2) * q[i] * math.log(theta[i] / phi[i])
                + l[i]
                - (phi[i] / x[i]) * np.dot(x, l)
            )

            # Residual contribution
            sum_theta_tau_i = sum(theta[j] * tau[j][i] for j in range(nc))

            ln_res = q[i] * (
                1 - math.log(sum_theta_tau_i)
                - sum(
                    theta[j] * tau[i][j] / sum(theta[k] * tau[k][j] for k in range(nc))
                    for j in range(nc)
                )
            )

            ln_gamma[i] = ln_comb + ln_res

        return [math.exp(lg) for lg in ln_gamma]
