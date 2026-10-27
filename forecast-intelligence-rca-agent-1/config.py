"""
config.py – Central configuration for the Forecast Intelligence & RCA Agent.
============================================================================

PURPOSE
-------
Single source of truth for all configuration values used across the agent
pipeline.  Loads Azure OpenAI credentials from a local .env file (never
hard-coded -- BRD SS33) and defines:

  - Loop / cost-protection limits         (BRD SS30)
  - Unity Catalog table and view names   (BRD SS6.3)
  - Metric formulas as comments            (BRD SS10)
  - Minimum-history thresholds per RCA     (BRD SS11)
  - Scenario lifecycle state constants     (BRD SS16)
  - Message intent and scenario-action enums(BRD SS15)
  - RCA hypothesis categories               (BRD SS9, FR-07)
  - Data-sufficiency and readiness enums    (BRD SS11, SS50)
  - Synthetic data generation parameters

IMPORT ORDER: config.py is imported by almost every other module.
It must remain side-effect free apart from load_dotenv().

BRD REFERENCES: SS10, SS11, SS15, SS16, SS20, SS30, SS33.
"""

import os
from dotenv import load_dotenv

# ------------------------------------------------------------------
# Secrets  (BRD §33 – do not hard-code in source)
# ------------------------------------------------------------------
load_dotenv()

AZURE_OPENAI_ENDPOINT    = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY     = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT  = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-08-07-preview")

# ------------------------------------------------------------------
# Loop / cost protection  (BRD §30)
# Prevents runaway agent loops and unbounded data retrieval.
# Enforced by ToolExecutor and the agent loop.
# ------------------------------------------------------------------
MAX_AGENT_TURNS           = 10   # max LLM round-trips per user message
MAX_TOOL_CALLS_PER_MESSAGE = 6  # max tool calls within one agent turn
MAX_ROWS_RETURNED         = 500  # row cap on any single tool query result
MAX_HISTORY_TOKENS         = 8000  # conversation history token budget
TOOL_TIMEOUT_SECONDS       = 30  # per-tool execution timeout
MAX_RETRY_ATTEMPTS         = 2   # retries on transient tool failures

# ------------------------------------------------------------------
# Databricks / Unity Catalog
# ------------------------------------------------------------------
CATALOG    = "workspace"
SCHEMA     = "forecast_db"
DB_PREFIX  = f"{CATALOG}.{SCHEMA}"

# Core business tables (fact + dimensions)
FACT_TABLE             = f"{DB_PREFIX}.fact_sales_forecast"     # central fact: forecast, actuals, revenue, inventory
DIM_PRODUCT_TABLE      = f"{DB_PREFIX}.dim_product"            # product master (sku, name, category, region)
DIM_CALENDAR_TABLE     = f"{DB_PREFIX}.dim_calendar"           # fiscal calendar dimension
DIM_STORE_TABLE        = f"{DB_PREFIX}.dim_store"               # store master (store_id, region mapping)
DIM_REGION_TABLE       = f"{DB_PREFIX}.dim_region"             # region dimension
DIM_ENTITY_ALIAS_TABLE = f"{DB_PREFIX}.dim_entity_alias"        # alias mapping for entity resolution (BRD SS13)

# Memory / scenario state tables (BRD SS14, SS31 -- persistent agent state in Delta)
CONVERSATION_TURNS_TABLE = f"{DB_PREFIX}.conversation_turns"     # every user+assistant message
SCENARIO_STATE_TABLE     = f"{DB_PREFIX}.scenario_state"        # SCD-Type-2 scenario versioning
RCA_READINESS_TABLE      = f"{DB_PREFIX}.rca_readiness_registry"  # capability readiness per entity
AGENT_OBSERVABILITY_TABLE= f"{DB_PREFIX}.agent_observability"   # structured logs for audit

# Governed analytical views (pre-aggregated for service-layer consumption)
VW_FORECAST_METRICS   = f"{DB_PREFIX}.vw_forecast_metrics"       # forecast vs actual aggregated by product/region/week
VW_INVENTORY_HEALTH   = f"{DB_PREFIX}.vw_inventory_health"       # inventory levels + stockout flags
VW_REVENUE_METRICS    = f"{DB_PREFIX}.vw_revenue_metrics"        # gross/net revenue by product/region/week
VW_FORECAST_HISTORY   = f"{DB_PREFIX}.vw_forecast_history"     # long-form forecast history for trend analysis
VW_RCA_FEATURES        = f"{DB_PREFIX}.vw_forecast_rca_features"  # feature store for RCA hypothesis testing

# ------------------------------------------------------------------
# Metric definitions  (BRD §10)
# ------------------------------------------------------------------
# Forecast Error  = Forecast - Actual
# Absolute Error  = |Forecast - Actual|
# Bias %          = (Forecast - Actual) / Actual × 100
# WMAPE           = Σ|Forecast - Actual| / Σ|Actual|
# Accuracy        = (1 - WMAPE) × 100
# Gross Revenue   = Units Sold × Price
# Net Revenue     = Units Sold × Price × (1 - Discount / 100)

# Minimum weekly observations required before each RCA capability can fire.
# If actual history is shorter, the capability is marked NOT_TESTABLE (BRD SS11).
MIN_HISTORY_BIAS       = 4    # weeks -- bias analysis needs at least 4 data points
MIN_HISTORY_TREND      = 8    # weeks -- trend detection needs 8+ points
MIN_HISTORY_PROMOTION  = 8    # weeks -- promotion effect analysis
MIN_HISTORY_INVENTORY  = 8    # weeks -- inventory/supply constraint analysis
MIN_HISTORY_REVENUE    = 4    # weeks -- revenue trend
MIN_HISTORY_SEASONALITY = 26  # weeks (~6 months) -- seasonal pattern detection

# Stockout / low-inventory thresholds (BRD SS10)
STOCKOUT_THRESHOLD       = 0     # inventory_level <= STOCKOUT_THRESHOLD => stockout=True
LOW_INVENTORY_THRESHOLD  = 0.5   # inventory_level < units_sold * (1 + LOW_INVENTORY_THRESHOLD) => low

# Data quality thresholds
MAX_FORECAST_BIAS_PCT   = 50.0   # |bias %| beyond this flags a quality issue
DISCOUNT_MIN            = 0.0
DISCOUNT_MAX            = 100.0

# ------------------------------------------------------------------
# Scenario lifecycle states  (BRD §16)
# ------------------------------------------------------------------
SCENARIO_NEW           = "NEW"
SCENARIO_ACTIVE        = "ACTIVE"
SCENARIO_ANALYZING     = "ANALYZING"
SCENARIO_RCA_IDENT     = "RCA_IDENTIFIED"
SCENARIO_INFO_RETRIEVAL= "INFORMATION_RETRIEVAL"
SCENARIO_WHAT_IF       = "WHAT_IF"
SCENARIO_FOLLOW_UP     = "FOLLOW_UP"
SCENARIO_OUTCOME       = "OUTCOME_REPORTED"
SCENARIO_RESOLVED      = "RESOLVED"
SCENARIO_CLOSED        = "CLOSED"

# ------------------------------------------------------------------
# Message intent classification  (BRD §15)
# ------------------------------------------------------------------
INTENT_FORECAST_RETRIEVAL = "FORECAST_RETRIEVAL"
INTENT_REVENUE_RETRIEVAL  = "REVENUE_RETRIEVAL"
INTENT_INVENTORY_RETRIEVAL= "INVENTORY_RETRIEVAL"
INTENT_TREND_ANALYSIS     = "TREND_ANALYSIS"
INTENT_RCA                = "RCA"
INTENT_COMPARISON         = "COMPARISON"
INTENT_WHAT_IF            = "WHAT_IF"
INTENT_OUTCOME_UPDATE     = "OUTCOME_UPDATE"
INTENT_EXPLANATION        = "EXPLANATION"

# Scenario actions  (BRD §15)
ACTION_CONTINUE   = "CONTINUE_ACTIVE_SCENARIO"
ACTION_NEW        = "CREATE_NEW_SCENARIO"
ACTION_UPDATE     = "UPDATE_ACTIVE_SCENARIO"
ACTION_AMBIGUOUS = "AMBIGUOUS_NEEDS_CLARIFICATION"

# ------------------------------------------------------------------
# RCA hypothesis categories  (BRD §9, FR-07)
# ------------------------------------------------------------------
HYPOTHESIS_FORECAST_BIAS    = "FORECAST_LEVEL_BIAS_ISSUE"
HYPOTHESIS_DEMAND_TREND     = "DEMAND_TREND_SHIFT"
HYPOTHESIS_SEASONALITY      = "SEASONAL_PATTERN_MISMATCH"
HYPOTHESIS_PROMOTION        = "PROMOTION_CALENDAR_EFFECT"
HYPOTHESIS_PRICE            = "PRICE_EFFECT"
HYPOTHESIS_COMPETITOR       = "COMPETITOR_PRICING_EFFECT"
HYPOTHESIS_INVENTORY        = "INVENTORY_STOCKOUT_CONSTRAINT"
HYPOTHESIS_LIFECYCLE        = "PRODUCT_LIFECYCLE_LAUNCH_EFFECT"
HYPOTHESIS_REGIONAL_SHIFT   = "REGIONAL_STORE_MIX_SHIFT"
HYPOTHESIS_DATA_QUALITY     = "DATA_QUALITY_OR_MISSING_DATA_ISSUE"

# Hypothesis statuses
HYP_STATUS_SUPPORTED    = "SUPPORTED"
HYP_STATUS_POSSIBLE     = "POSSIBLE"
HYP_STATUS_NOT_SUPPORTED= "NOT_SUPPORTED"
HYP_STATUS_NOT_TESTABLE= "NOT_TESTABLE"

# Evidence strength
STRENGTH_HIGH   = "HIGH"
STRENGTH_MEDIUM = "MEDIUM"   # FIXED: was RENGTH_MEDIUM (typo)
STRENGTH_LOW    = "LOW"

# Data sufficiency  (BRD §11)
DATA_SUFFICIENT   = "SUFFICIENT"
DATA_PARTIAL      = "PARTIAL"
DATA_INSUFFICIENT = "INSUFFICIENT"

# Readiness statuses  (BRD §50)
READINESS_READY        = "READY"
READINESS_PARTIAL      = "PARTIAL"
READINESS_NOT_TESTABLE = "NOT_TESTABLE"

# Synthetic data generation parameters (used by 01_data_initialization notebook)
# SEED ensures reproducibility across runs (BRD SS38 test consistency)
SEED = 42
DATASET_VERSION = "v2.1"           # bumped from v2.0 when extended lookback was added
GENERATION_DATE = "2026-10-02"     # date the v2.1 dataset was first generated