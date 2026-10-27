"""
tools/forecast_rca_tools.py -- Thin LLM-facing wrappers.
============================================================================

PURPOSE
-------
Each function in this module is a thin adapter that:
  1. Accepts a Pydantic request model (validated by ToolExecutor),
  2. Translates the request into service-layer method calls,
  3. Returns a plain dict result suitable for JSON serialisation to the LLM.

IMPORTANT: All business logic lives in services/forecast_rca_service.py.
These wrappers contain NO business logic, NO SQL, and NO data access.
They exist solely to bridge the Pydantic request/response contract of the
tool executor with the rich service-layer API.

THE SIX TOOLS (BRD SS20)
-----------------------
  1. get_forecast_context       -> forecast_service.get_forecast_data()
  2. get_inventory_context      -> inventory_service.get_inventory_data()
  3. get_revenue_context        -> revenue_service.get_revenue_data()
  4. analyze_historical_pattern -> pattern_service.analyze_patterns()
  5. run_forecast_rca           -> rca_service.run_rca()
  6. compare_scenarios          -> comparison_service.compare()

All tools are read-only.  No tool mutates data.

BRD REFERENCES: SS20 (Tool Definitions), SS49 (Evidence Contract).
"""

from __future__ import annotations

import logging
from typing import Dict, Any

from models import (
    RCARequest,
    ScenarioComparisonRequest,
    AnalyticalQueryRequest,
)
from services.forecast_rca_service import (
    rca_service,
    comparison_service,
)
from analytics import analytical_service

logger = logging.getLogger(__name__)


# ============================================================
# Tool 1 – run_analytical_query  (composable analytical retrieval)
# ============================================================

def run_analytical_query(request: AnalyticalQueryRequest) -> Dict[str, Any]:
    """
    Execute a composable analytical query against governed Databricks views.

    The request is a validated AnalyticalQueryRequest (Pydantic model) whose
    fields form a structured analytical plan.  The analytics module validates
    the plan, compiles it to parameterized SQL, and executes it.
    """
    plan_data = request.model_dump()
    return analytical_service.execute(plan_data)


# ============================================================
# Tool 2 – run_forecast_rca  (BRD §20, §9, §25)
# ============================================================

def run_forecast_rca(request: RCARequest) -> Dict[str, Any]:
    """Generate an evidence package and structured RCA hypotheses."""
    result = rca_service.run_rca(
        product_id=request.product_id,
        region=request.region,
        lookback_weeks=request.lookback_weeks or 12,
        hypotheses=request.hypotheses if request.hypotheses else None,
    )
    return result


# ============================================================
# Tool 3 – compare_scenarios  (BRD §20, §17, §18)
# ============================================================

def compare_scenarios(request: ScenarioComparisonRequest) -> Dict[str, Any]:
    """Compare baseline vs current/what-if scenario."""
    result = comparison_service.compare(
        baseline_state=request.baseline_state or {},
        current_state=request.current_state or {},
        what_if_parameters=request.what_if_parameters,
    )
    return result