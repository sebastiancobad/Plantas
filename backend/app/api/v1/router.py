"""
Central API router that aggregates all module endpoints.

Each engineering module gets its own prefix and tag for
clean OpenAPI documentation grouping.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import thermo, heat_exchangers, economics

api_router = APIRouter()

# ── Core System ─────────────────────────────────────────────────────
api_router.include_router(
    thermo.router,
    prefix="/thermo",
    tags=["Thermodynamic Properties"],
)

# ── Module 6: Heat Exchanger Design ────────────────────────────────
api_router.include_router(
    heat_exchangers.router,
    prefix="/heat-exchangers",
    tags=["Heat Exchanger Design"],
)

# ── Module 12: Economic Evaluation ─────────────────────────────────
api_router.include_router(
    economics.router,
    prefix="/economics",
    tags=["Economic Evaluation"],
)
