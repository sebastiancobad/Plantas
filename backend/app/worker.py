"""
Celery Worker — Async Task Processing for Heavy Computations.

Heavy iterative calculations are offloaded to background workers:
    - Rigorous distillation convergence (stage-by-stage)
    - Heat exchanger rating with Bell-Delaware
    - Full economic evaluation (CAPEX + OPEX + NPV)
    - VLE flash calculations for multi-component systems
"""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "chemscale",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,      # 5 min hard limit
    task_soft_time_limit=240,  # 4 min soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)


@celery_app.task(bind=True, name="chemscale.design_heat_exchanger")
def task_design_heat_exchanger(self, input_data: dict) -> dict:
    """Async heat exchanger design (for rigorous Bell-Delaware)."""
    from app.services.modules.heat_exchanger import design_heat_exchanger
    self.update_state(state="RUNNING", meta={"stage": "thermo_properties"})
    result = design_heat_exchanger(input_data)
    return result


@celery_app.task(bind=True, name="chemscale.design_distillation")
def task_design_distillation(self, input_data: dict) -> dict:
    """Async distillation column design (for rigorous stage-by-stage)."""
    from app.services.modules.distillation import design_distillation_column
    self.update_state(state="RUNNING", meta={"stage": "shortcut_design"})
    result = design_distillation_column(input_data)
    return result


@celery_app.task(bind=True, name="chemscale.full_economic_evaluation")
def task_full_evaluation(self, capex_data: dict, utility_data: dict | None,
                          opex_data: dict | None) -> dict:
    """Async full economic evaluation."""
    from app.services.modules.economics import (
        calculate_capex, calculate_utility_demand, calculate_opex
    )
    self.update_state(state="RUNNING", meta={"stage": "capex"})
    capex = calculate_capex(capex_data)

    utility = None
    annual_util_cost = 0.0
    if utility_data:
        self.update_state(state="RUNNING", meta={"stage": "utilities"})
        utility = calculate_utility_demand(utility_data)
        annual_util_cost = utility.get("annual_utility_cost_usd", 0)

    self.update_state(state="RUNNING", meta={"stage": "opex"})
    opex_input = opex_data or {}
    opex_input["annual_utility_cost_usd"] = annual_util_cost
    opex_input["total_installed_cost_usd"] = capex["cost_summary"]["total_installed_cost_usd"]
    opex = calculate_opex(opex_input)

    return {"capex": capex, "utility": utility, "opex": opex}
