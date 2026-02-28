"""
SQLAlchemy ORM models for the Chemical Component Database.

This is the ChemScale equivalent of DIPPR — a structured repository
of pure-component physical and thermodynamic properties.
"""

from sqlalchemy import Column, Float, Integer, String, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.database import Base


class ChemicalComponent(Base):
    """
    Pure chemical component with critical properties and correlations.

    Each compound has scalar critical properties stored as columns
    and temperature-dependent correlations stored as JSONB (coefficient arrays).
    """
    __tablename__ = "chemical_components"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    formula = Column(String(50), nullable=False)
    cas_number = Column(String(20), unique=True, nullable=True)

    # Critical properties
    molecular_weight = Column(Float, nullable=False)          # g/mol
    critical_temperature = Column(Float, nullable=False)      # K
    critical_pressure = Column(Float, nullable=False)         # Pa
    critical_volume = Column(Float, nullable=True)            # m³/mol
    acentric_factor = Column(Float, nullable=False)           # dimensionless

    # Normal boiling/melting points
    normal_boiling_point = Column(Float, nullable=True)       # K
    normal_melting_point = Column(Float, nullable=True)       # K

    # Temperature-dependent correlations (DIPPR-style polynomial coefficients)
    # Stored as JSONB: {"A": ..., "B": ..., "C": ..., "D": ..., "E": ..., "Tmin": ..., "Tmax": ...}
    cp_ideal_gas_coeffs = Column(JSON, nullable=True)         # J/(mol·K)
    vapor_pressure_coeffs = Column(JSON, nullable=True)       # Pa (Antoine or Wagner)
    liquid_density_coeffs = Column(JSON, nullable=True)       # kg/m³
    liquid_viscosity_coeffs = Column(JSON, nullable=True)     # Pa·s
    vapor_viscosity_coeffs = Column(JSON, nullable=True)      # Pa·s
    liquid_thermal_cond_coeffs = Column(JSON, nullable=True)  # W/(m·K)
    heat_of_vaporization_coeffs = Column(JSON, nullable=True) # J/mol
    surface_tension_coeffs = Column(JSON, nullable=True)      # N/m

    # Safety properties
    autoignition_temperature = Column(Float, nullable=True)   # K
    flash_point = Column(Float, nullable=True)                # K
    lower_flammability_limit = Column(Float, nullable=True)   # vol%
    upper_flammability_limit = Column(Float, nullable=True)   # vol%
    idlh = Column(Float, nullable=True)                       # ppm

    # Relationships
    binary_params = relationship("BinaryInteractionParameter",
                                  foreign_keys="BinaryInteractionParameter.component_i_id",
                                  back_populates="component_i")

    def __repr__(self):
        return f"<Component {self.name} ({self.formula})>"


class BinaryInteractionParameter(Base):
    """
    Binary interaction parameters between component pairs.

    Stores kᵢⱼ (EOS), τᵢⱼ (NRTL), and uᵢⱼ (UNIQUAC) parameters.
    These are temperature-independent for MVP; T-dependent forms
    can be added via the coefficients JSONB field.
    """
    __tablename__ = "binary_interaction_parameters"

    id = Column(Integer, primary_key=True, index=True)
    component_i_id = Column(Integer, ForeignKey("chemical_components.id"), nullable=False)
    component_j_id = Column(Integer, ForeignKey("chemical_components.id"), nullable=False)

    # EOS binary interaction parameter
    kij_pr = Column(Float, nullable=True)    # Peng-Robinson kᵢⱼ
    kij_srk = Column(Float, nullable=True)   # SRK kᵢⱼ

    # NRTL parameters
    nrtl_tau_ij = Column(Float, nullable=True)    # τᵢⱼ = (gᵢⱼ - gⱼⱼ)/R [K]
    nrtl_tau_ji = Column(Float, nullable=True)    # τⱼᵢ = (gⱼᵢ - gᵢᵢ)/R [K]
    nrtl_alpha = Column(Float, nullable=True)     # αᵢⱼ (non-randomness)

    # UNIQUAC parameters
    uniquac_u_ij = Column(Float, nullable=True)   # (uᵢⱼ - uⱼⱼ)/R [K]
    uniquac_u_ji = Column(Float, nullable=True)   # (uⱼᵢ - uᵢᵢ)/R [K]

    # Optional: T-dependent parameter coefficients
    coefficients = Column(JSON, nullable=True)

    # Data source / reference
    source = Column(String(200), nullable=True)

    # Relationships
    component_i = relationship("ChemicalComponent", foreign_keys=[component_i_id],
                                back_populates="binary_params")
    component_j = relationship("ChemicalComponent", foreign_keys=[component_j_id])

    __table_args__ = (
        UniqueConstraint("component_i_id", "component_j_id", name="uq_binary_pair"),
    )

    def __repr__(self):
        return f"<BIP {self.component_i_id}-{self.component_j_id}>"
