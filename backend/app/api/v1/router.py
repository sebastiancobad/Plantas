"""
Central API router — aggregates all 12 engineering module endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    thermo, heat_exchangers, economics, piping, materials,
    plant_layout, separators, pumps, distillation, psv,
    process_safety, apc, pid_development,
)

api_router = APIRouter()

api_router.include_router(thermo.router, prefix="/thermo", tags=["Thermodynamic Properties"])
api_router.include_router(piping.router, prefix="/piping", tags=["Pipe Sizing & Hydraulics"])
api_router.include_router(materials.router, prefix="/materials", tags=["Material Selection"])
api_router.include_router(plant_layout.router, prefix="/plant-layout", tags=["Plant Layout"])
api_router.include_router(separators.router, prefix="/separators", tags=["Phase Separators"])
api_router.include_router(pumps.router, prefix="/pumps", tags=["Pump Selection"])
api_router.include_router(heat_exchangers.router, prefix="/heat-exchangers", tags=["Heat Exchangers"])
api_router.include_router(distillation.router, prefix="/distillation", tags=["Distillation"])
api_router.include_router(psv.router, prefix="/psv", tags=["Safety Relief Valves"])
api_router.include_router(process_safety.router, prefix="/process-safety", tags=["Process Safety"])
api_router.include_router(apc.router, prefix="/apc", tags=["Advanced Process Control"])
api_router.include_router(pid_development.router, prefix="/pid", tags=["P&ID Development"])
api_router.include_router(economics.router, prefix="/economics", tags=["Economic Evaluation"])
