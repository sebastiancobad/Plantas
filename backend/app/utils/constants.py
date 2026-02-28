"""
Universal physical constants and standard conditions for ChemScale.

All values are in SI units. Module code should NEVER hardcode these values —
always import from this module for single-source-of-truth consistency.
"""

# Universal gas constant
R = 8.314462618  # J/(mol·K)

# Standard conditions (IUPAC)
T_STD = 273.15    # K  (0 °C)
P_STD = 101325.0  # Pa (1 atm)

# Normal conditions (industry common)
T_NORMAL = 288.15  # K  (15 °C)
P_NORMAL = 101325.0  # Pa

# Gravitational acceleration
G = 9.80665  # m/s²

# Stefan-Boltzmann constant (radiation heat transfer)
SIGMA = 5.670374419e-8  # W/(m²·K⁴)

# Water properties at 25 °C (quick reference)
WATER_DENSITY_25C = 997.05       # kg/m³
WATER_VISCOSITY_25C = 8.9e-4     # Pa·s
WATER_CP_25C = 4181.3            # J/(kg·K)
WATER_THERMAL_COND_25C = 0.6065  # W/(m·K)
