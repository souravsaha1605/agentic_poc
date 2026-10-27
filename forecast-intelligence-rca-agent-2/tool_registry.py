"""
tool_registry.py -- Defines the six governed, read-only tools exposed to the LLM.
============================================================================

PURPOSE
-------
Produces the JSON schema array (TOOLS) that is passed to the OpenAI
Responses API as the ``tools`` parameter.  Each entry describes one
callable function, its parameters (as a Pydantic JSON schema), and a
human-readable description that the LLM uses for tool selection.

DESIGN PRINCIPLE (BRD SS20)
---------------------------
The LLM-facing toolset is intentionally small (six tools).  This keeps
the LLM's decision space narrow, reduces hallucinated tool calls, and
makes the agent's behaviour predictable and auditable.

THE SIX TOOLS
------------
  1. get_forecast_context     -- forecast, actual, accuracy, bias, trend
  2. get_inventory_context    -- inventory level, stockout, trend
  3. get_revenue_context      -- gross/net revenue, trend, exposure
  4. analyze_historical_pattern -- trend, volatility, level-shift, seasonality
  5. run_forecast_rca         -- evidence package + structured hypotheses
  6. compare_scenarios        -- baseline vs current/what-if comparison

All tools are read-only.  No tool can mutate data.

BRD REFERENCES: SS20 (Tool Definitions), SS29 (Trust Boundary).
"""

from models import (
    RCARequest,
    ScenarioComparisonRequest,
    AnalyticalQueryRequest,
)


TOOLS = [
    # ----------------------------------------------------------
    # Tool 1 – run_analytical_query  (composable analytical retrieval)
    # ----------------------------------------------------------
    {
        "type": "function",
        "name": "run_analytical_query",
        "description": (
            "Execute a composable analytical query against governed Databricks views. "
            "Use this for ALL data retrieval: forecast metrics, revenue, inventory, "
            "rankings, top-N, cumulative-share filters, trend analysis, comparisons across "
            "multiple SKUs/regions/categories. Produce a structured analytical plan (JSON) "
            "with analysis_type, grain, filters, metrics, cumulative_share, rank_by, and limit. "
            "Read-only."
        ),
        "parameters": AnalyticalQueryRequest.model_json_schema(),
    },

    # ----------------------------------------------------------
    # Tool 2 – run_forecast_rca  (deterministic RCA engine)
    # ----------------------------------------------------------
    {
        "type": "function",
        "name": "run_forecast_rca",
        "description": (
            "Generate a deterministic evidence package and structured RCA "
            "hypotheses for a single product/region. Returns observations, evidence, "
            "hypotheses (with strength and status), recommendations, confidence, and "
            "limitations. Read-only."
        ),
        "parameters": RCARequest.model_json_schema(),
    },

    # ----------------------------------------------------------
    # Tool 3 – compare_scenarios  (baseline vs what-if)
    # ----------------------------------------------------------
    {
        "type": "function",
        "name": "compare_scenarios",
        "description": (
            "Compare baseline vs current/what-if scenario. Returns deltas "
            "and business impact. Read-only."
        ),
        "parameters": ScenarioComparisonRequest.model_json_schema(),
    },
]