"""Deployment defaults. Secret values are read lazily in client.py.

Flags are operator settings, never chat commands. Use the same FORECAST_DATABASE
in initialization, notebook execution and the hosted worker.
"""

import os
from state import checked_table

DB_PREFIX = checked_table(os.getenv("FORECAST_DATABASE", "workspace.forecast_rca_lab"))
FACT_TABLE = f"{DB_PREFIX}.fact_sales_forecast"
VW_FORECAST_METRICS = f"{DB_PREFIX}.vw_forecast_metrics"
VW_INVENTORY_HEALTH = f"{DB_PREFIX}.vw_inventory_health"
VW_REVENUE_METRICS = f"{DB_PREFIX}.vw_revenue_metrics"
VW_FORECAST_HISTORY = f"{DB_PREFIX}.vw_forecast_history"
VW_RCA_FEATURES = f"{DB_PREFIX}.vw_forecast_rca_features"
MAX_ROWS_RETURNED = 100
MAX_AGENT_TURNS = 1
MAX_TOOL_CALLS_PER_MESSAGE = 6
MAX_HISTORY_TOKENS = 0  # transcript is retained in state, never replayed to the model
MAX_MODEL_INPUT_BYTES = 1500
MAX_OUTPUT_TOKENS = 150
MAX_PAID_CALLS = 70
TOOL_TIMEOUT_SECONDS = 30
