"""
models.py -- Pydantic models for the Forecast Intelligence & RCA Agent.
============================================================================

PURPOSE
-------
Defines every typed data structure used across the agent pipeline:

  Entity / Context:
    EntityContext      -- resolved business entities (product, region, store)
    TimeRange          -- time window for retrieval and analysis

  Message Classification (BRD SS15):
    MessageClassification -- intent + scenario action (two independent dims)
    ScenarioDecision      -- output of the classify_message step

  Scenario State (BRD SS14, SS16):
    ScenarioState   -- authoritative state of the active business case
    ConversationTurn -- a single conversational exchange persisted to Delta

  Tool Request Models (BRD SS20 -- six tools):
    ForecastContextRequest, InventoryContextRequest, RevenueContextRequest,
    HistoricalPatternRequest, RCARequest, ScenarioComparisonRequest

  RCA Models (BRD SS9, SS25):
    RCAEvidence, RCAHypothesis, RCAResult

  Data Quality (BRD SS11):
    DataQualityStatus

  Tool Result (BRD SS28):
    ToolResult -- standardised tool response wrapper

  Service-level response models (backward-compatible):
    ForecastSummary, InventorySummary, RevenueSummary, BusinessContext

  Agent Response:
    AgentResponse -- final response returned to the user/caller

BRD REFERENCES: SS9, SS11, SS13, SS14, SS15, SS16, SS20, SS25, SS28, SS40.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field


# ============================================================
#  Entity & Context Resolution  (BRD §13, §6.4)
# ============================================================

class EntityContext(BaseModel):
    """Resolved business entities for the active scenario (BRD §13)."""
    product_id:   Optional[str] = None
    product_name: Optional[str] = None
    store_id:     Optional[str] = None
    store_name:   Optional[str] = None
    region:       Optional[str] = None
    category:     Optional[str] = None
    sub_category: Optional[str] = None
    brand:        Optional[str] = None
    resolved: bool = False
    ambiguous: bool = False
    candidates: List[Dict[str, Any]] = Field(default_factory=list)


class TimeRange(BaseModel):
    """Time window for retrieval and analysis (BRD FR-01, FR-04)."""
    start_date:  Optional[date] = None
    end_date:    Optional[date] = None
    lookback_weeks: Optional[int] = None
    lookback_months: Optional[int] = None
    fiscal_period:  Optional[str] = None
    comparison_start: Optional[date] = None
    comparison_end:   Optional[date] = None


# ============================================================
#  Message Classification  (BRD §15)
# ============================================================

class MessageClassification(BaseModel):
    """Two independent dimensions: intent + scenario action (BRD §15)."""
    intent: str = Field(description="FORECAST_RETRIEVAL | REVENUE_RETRIEVAL | "
                                   "INVENTORY_RETRIEVAL | TREND_ANALYSIS | RCA | "
                                   "COMPARISON | WHAT_IF | OUTCOME_UPDATE | EXPLANATION")
    scenario_action: str = Field(description="CONTINUE_ACTIVE_SCENARIO | "
                                             "CREATE_NEW_SCENARIO | "
                                             "UPDATE_ACTIVE_SCENARIO | "
                                             "AMBIGUOUS_NEEDS_CLARIFICATION")
    confidence: float = 0.0
    reasoning: str = ""


class ScenarioDecision(BaseModel):
    """Output of the classify_message step."""
    classification: MessageClassification
    resolved_entities: EntityContext
    time_range: Optional[TimeRange] = None
    clarification_question: Optional[str] = None


# ============================================================
#  Scenario State  (BRD §14, FR-09, §16, §17)
# ============================================================

class ScenarioState(BaseModel):
    """Authoritative state of the active business case (BRD §14 FR-09)."""
    scenario_id:   str = ""
    session_id:    str = ""
    user_id:       str = "demand_planner"
    status:        str = "NEW"
    resolved_entities: EntityContext = Field(default_factory=EntityContext)
    time_range:    Optional[TimeRange] = None
    analysis_type: str = ""
    active_issue:  str = ""
    baseline_state:   Optional[Dict[str, Any]] = None
    current_state:    Optional[Dict[str, Any]] = None
    previous_state:   Optional[Dict[str, Any]] = None
    last_tool_results: Optional[Dict[str, Any]] = None
    rca_summary:      Optional[str] = None
    rca_evidence:     Optional[List[Dict[str, Any]]] = None
    rca_hypotheses:   Optional[List[Dict[str, Any]]] = None
    recommendations:  Optional[List[str]] = None
    what_if_parameters: Optional[Dict[str, Any]] = None
    reported_outcomes: Optional[List[str]] = None
    assumptions:       Optional[List[str]] = None
    data_timestamp:   Optional[datetime] = None
    scenario_version: int = 1
    created_at:       Optional[datetime] = None
    updated_at:       Optional[datetime] = None


# ============================================================
#  Conversation Memory  (BRD §14, FR-08)
# ============================================================

class ConversationTurn(BaseModel):
    """A single conversational exchange (BRD §31 Iteration 1)."""
    session_id: str
    turn_id:    int
    user_id:    str = "demand_planner"
    timestamp:  Optional[datetime] = None
    role:       str = "user"
    message:    str = ""
    scenario_id: Optional[str] = None
    intent:      Optional[str] = None
    scenario_action: Optional[str] = None


# ============================================================
#  Tool Request Models  (BRD §20 – six tools)
# ============================================================

class ForecastContextRequest(BaseModel):
    """Tool 1: get_forecast_context (BRD §20)."""
    product_id: Optional[str] = None
    region:     Optional[str] = None
    store_id:   Optional[str] = None
    category:   Optional[str] = None
    start_date: Optional[str] = None
    end_date:   Optional[str] = None
    lookback_weeks: Optional[int] = 12
    include_summary:  bool = True
    include_history:  bool = False
    include_accuracy: bool = True
    include_bias:     bool = True
    include_trend:    bool = False


class InventoryContextRequest(BaseModel):
    """Tool 2: get_inventory_context (BRD §20)."""
    product_id: Optional[str] = None
    region:     Optional[str] = None
    store_id:   Optional[str] = None
    as_of_date: Optional[str] = None
    lookback_weeks: Optional[int] = 12
    include_history:    bool = False
    include_stockout:   bool = True
    include_trend:      bool = False


class RevenueContextRequest(BaseModel):
    """Tool 3: get_revenue_context (BRD §20, FR-02)."""
    product_id: Optional[str] = None
    region:     Optional[str] = None
    store_id:   Optional[str] = None
    category:   Optional[str] = None
    start_date: Optional[str] = None
    end_date:   Optional[str] = None
    lookback_weeks: Optional[int] = 12
    revenue_type: str = "net"   # "gross" | "net" | "both"
    include_trend: bool = False


class HistoricalPatternRequest(BaseModel):
    """Tool 4: analyze_historical_pattern (BRD §20, FR-04)."""
    product_id: Optional[str] = None
    region:     Optional[str] = None
    store_id:   Optional[str] = None
    category:   Optional[str] = None
    lookback_weeks: int = 12
    patterns: List[str] = Field(default_factory=lambda: [
        "trend", "level_shift", "seasonality", "volatility",
        "bias_drift", "accuracy_deterioration",
        "actual_vs_forecast_divergence", "demand_spikes",
        "promotion_linked", "price_linked", "inventory_constrained",
    ])


class RCARequest(BaseModel):
    """Tool 5: run_forecast_rca (BRD §20, §9, §25)."""
    product_id: str
    region:     Optional[str] = None
    store_id:   Optional[str] = None
    lookback_weeks: int = 12
    hypotheses: List[str] = Field(default_factory=list)
    # If empty, engine evaluates all applicable hypotheses


class ScenarioComparisonRequest(BaseModel):
    """Tool 6: compare_scenarios (BRD §20, §17, §18)."""
    scenario_id: str
    baseline_state: Optional[Dict[str, Any]] = None
    current_state:   Optional[Dict[str, Any]] = None
    what_if_parameters: Optional[Dict[str, Any]] = None


class ForecastRankingRequest(BaseModel):
    """Tool 7: get_forecast_ranking -- top-N SKU ranking by error metric."""
    region: Optional[str] = None
    category: Optional[str] = None
    top_n: int = 10
    sort_by: str = "wmape"  # wmape | bias | absolute_error


# ============================================================
#  Analytical Plan Models  (composable analytical DSL)
# ============================================================

class AnalyticalFilter(BaseModel):
    """A single filter condition in an analytical plan."""
    field: str           # dimension name from DIMENSION_REGISTRY (e.g. "REGION")
    operator: str        # =, !=, >, <, >=, <=, IN, NOT_IN, IS_NULL, IS_NOT_NULL
    value: Optional[Union[str, int, float, List[str]]] = None


class CumulativeShareSpec(BaseModel):
    """Cumulative share filter (e.g. top 80% of revenue)."""
    metric: str          # metric name from METRIC_REGISTRY (e.g. "revenue")
    threshold: float     # 0 < threshold <= 1.0 (e.g. 0.80 for top 80%)
    direction: str = "DESC"   # DESC for top share, ASC for bottom share


class AnalyticalQueryRequest(BaseModel):
    """Tool: run_analytical_query -- composable analytical query via structured plan.

    The LLM produces this plan to express analytical questions generically.
    The backend validates it against governed registries and compiles it
    to parameterized SQL against approved Databricks views.
    """
    analysis_type: str   # FORECAST_PERFORMANCE | REVENUE_ANALYSIS | INVENTORY_ANALYSIS | PATTERN_ANALYSIS
    grain: str           # SKU | REGION | CATEGORY | SKU_REGION | DATE | ALL
    filters: List[AnalyticalFilter] = Field(default_factory=list)
    metrics: List[str] = Field(default_factory=list)  # metric names from METRIC_REGISTRY
    cumulative_share: Optional[CumulativeShareSpec] = None
    rank_by: Optional[str] = None     # metric name to sort by
    rank_direction: str = "DESC"     # ASC or DESC
    limit: Optional[int] = None       # 1..100
    lookback_weeks: int = 12


# ============================================================
#  Data Quality  (BRD §11, §27)
# ============================================================

class DataQualityStatus(BaseModel):
    """Structured data-sufficiency assessment (BRD §11)."""
    data_status: str = "SUFFICIENT"  # SUFFICIENT | PARTIAL | INSUFFICIENT
    coverage_start:   Optional[date] = None
    coverage_end:     Optional[date] = None
    total_observations: int = 0
    missing_fields:  List[str] = Field(default_factory=list)
    data_quality_flags: List[str] = Field(default_factory=list)
    stale_data: bool = False
    cross_source_conflict: Optional[str] = None
    data_as_of: Optional[date] = None
    data_refresh_timestamp: Optional[datetime] = None


# ============================================================
#  RCA Evidence & Hypotheses  (BRD §9, FR-06, FR-07, §25)
# ============================================================

class RCAEvidence(BaseModel):
    """A single piece of evidence in the RCA package (BRD FR-06)."""
    evidence_type: str = ""    # e.g. "bias", "trend", "inventory", "promotion"
    description: str = ""
    metric: Optional[str] = None
    value:  Optional[Any] = None
    period: Optional[str] = None
    source: str = "vw_forecast_rca_features"


class RCAHypothesis(BaseModel):
    """A structured RCA hypothesis (BRD FR-07, §25).

    Status values:
      VALIDATED     -- evidence meets defined validation criteria (strongest)
      SUPPORTED     -- evidence supports but does not fully validate
      POSSIBLE      -- circumstantial evidence, not conclusive
      NOT_SUPPORTED -- evidence does not support the hypothesis
      NOT_TESTABLE  -- required data is unavailable
    """
    cause: str = ""
    evidence: List[RCAEvidence] = Field(default_factory=list)
    strength: str = "LOW"     # HIGH | MEDIUM | LOW
    status: str = "NOT_SUPPORTED"  # VALIDATED | SUPPORTED | POSSIBLE | NOT_SUPPORTED | NOT_TESTABLE
    reasoning: str = ""
    business_event: Optional[str] = None    # supporting business event (promotion, price change, etc.)
    confidence: Optional[str] = None        # per-hypothesis confidence: HIGH | MEDIUM | LOW
    provenance: Optional[str] = None        # data source / derivation trail


# ============================================================
#  Historical Deviation Evidence  (BRD §24, FR-04)
#  Structured evidence from the deterministic analytical layer.
#  The LLM interprets these; it does NOT calculate the values.
# ============================================================

class HistoricalDeviationEvidence(BaseModel):
    """Structured evidence for a single historical deviation hypothesis.

    Every historical hypothesis returns this structure so the LLM can
    reason over validated analytical evidence rather than manufacturing it.
    """
    hypothesis: str = ""
    status: str = "NOT_TESTABLE"      # VALIDATED | SUPPORTED | NOT_SUPPORTED | NOT_TESTABLE
    evidence: Dict[str, Any] = Field(default_factory=dict)
    comparison_periods: Optional[Dict[str, Any]] = None
    detected_change: Optional[Dict[str, Any]] = None
    business_event: Optional[str] = None
    confidence: str = "LOW"               # HIGH | MEDIUM | LOW
    provenance: str = "deterministic_analytical_layer"


class HistoricalDeviationResult(BaseModel):
    """Collection of all historical deviation evidence for one entity."""
    product_id: str = ""
    region: Optional[str] = None
    period: Dict[str, Any] = Field(default_factory=dict)
    observations: int = 0
    deviation_evidence: List[HistoricalDeviationEvidence] = Field(default_factory=list)
    data_sufficient: bool = True
    insufficiency_reason: Optional[str] = None


class RCAResult(BaseModel):
    """Full deterministic RCA output (BRD §25)."""
    scenario_id: str = ""
    entity: Dict[str, Any] = Field(default_factory=dict)
    period: Dict[str, Any] = Field(default_factory=dict)
    data_quality: Optional[DataQualityStatus] = None
    observations: List[str] = Field(default_factory=list)
    evidence: List[RCAEvidence] = Field(default_factory=list)
    hypotheses: List[RCAHypothesis] = Field(default_factory=list)
    historical_deviation: Optional[HistoricalDeviationResult] = None
    recommendations: List[str] = Field(default_factory=list)
    confidence: str = "LOW"
    limitations: List[str] = Field(default_factory=list)


# ============================================================
#  Tool Result  (BRD §28, §29)
# ============================================================

class ToolResult(BaseModel):
    """Standardised tool response wrapper (BRD §28)."""
    success: bool = True
    tool_name: str = ""
    data: Optional[Any] = None
    error: Optional[str] = None
    data_quality: Optional[DataQualityStatus] = None
    rows_returned: int = 0
    execution_time_ms: float = 0.0


# ============================================================
#  Service-level response models (backward-compatible)
# ============================================================

class ForecastSummary(BaseModel):
    average_forecast: float = 0.0
    average_actual_sales: float = 0.0
    forecast_accuracy: float = 0.0
    forecast_bias: float = 0.0
    wmape: float = 0.0
    total_forecast: float = 0.0
    total_actual: float = 0.0
    period: str = ""


class InventorySummary(BaseModel):
    inventory_level: float = 0.0
    inventory_status: str = ""
    stockout_flag: bool = False
    inventory_days: float = 0.0
    as_of_date: Optional[date] = None


class RevenueSummary(BaseModel):
    gross_revenue: float = 0.0
    net_revenue: float = 0.0
    revenue_change_pct: float = 0.0
    period: str = ""
    revenue_type: str = "net"


class BusinessContext(BaseModel):
    forecast: Optional[ForecastSummary] = None
    inventory: Optional[InventorySummary] = None
    revenue: Optional[RevenueSummary] = None
    data_quality: Optional[DataQualityStatus] = None


class AgentResponse(BaseModel):
    response: str = ""
    scenario_id: Optional[str] = None
    intent: Optional[str] = None
    scenario_action: Optional[str] = None
    tools_called: List[str] = Field(default_factory=list)
    data_as_of: Optional[date] = None