"""
services/forecast_rca_service.py
============================================================================

PURPOSE
-------
Consolidated deterministic service layer for the Forecast Intelligence
& RCA Agent.  All business logic, SQL queries, metric calculations, and
RCA hypothesis testing live here.  The tools/ layer and agent/ layer are
thin wrappers that delegate to these services.

TEN SERVICES (BRD SS21)
------------------------
  1.  EntityResolutionService   -- resolve product/region/store from user input
  2.  ConversationMemoryService  -- persist and retrieve conversation turns in Delta
  3.  ScenarioStateService       -- manage structured scenario state (SCD-Type-2)
  4.  ForecastService            -- forecast retrieval with WMAPE-based accuracy (BRD SS10)
  5.  InventoryService           -- inventory levels, stockout flags, supply constraints
  6.  RevenueService              -- gross/net revenue calculations (BRD FR-02)
  7.  HistoricalPatternService    -- trend, volatility, level-shift, seasonality detection
  8.  ForecastRCAService           -- deterministic evidence package + hypothesis testing
  9.  ScenarioComparisonService   -- baseline vs current/what-if comparison
  10. DataQualityService          -- data sufficiency and quality assessment

DESIGN PRINCIPLES
-----------------
- Every method returns structured, sanitised evidence dicts suitable for
  LLM consumption.  Raw transactional rows are never passed through.
- All SQL uses parameterised string interpolation with values from config.py
  constants (not user input) to prevent injection.
- The RCA engine is fully deterministic: given the same data, it always
  produces the same hypotheses, strengths, and statuses.

BRD REFERENCES: SS9 (RCA), SS10 (Metrics), SS11 (Data Sufficiency),
               SS13 (Entity Resolution), SS14 (Scenario State),
               SS21 (Services), SS25 (RCA Engine), SS49 (Evidence Contract).
"""

from __future__ import annotations

import logging
import math
import uuid
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DoubleType, StructType, StructField, StringType, IntegerType, TimestampType,
)

from config import (
    FACT_TABLE, DIM_PRODUCT_TABLE, DIM_ENTITY_ALIAS_TABLE,
    VW_FORECAST_METRICS, VW_INVENTORY_HEALTH, VW_REVENUE_METRICS,
    VW_FORECAST_HISTORY, VW_RCA_FEATURES,
    CONVERSATION_TURNS_TABLE, SCENARIO_STATE_TABLE,
    RCA_READINESS_TABLE, DB_PREFIX,
    MAX_ROWS_RETURNED,
    MIN_HISTORY_BIAS, MIN_HISTORY_TREND, MIN_HISTORY_PROMOTION,
    MIN_HISTORY_INVENTORY, MIN_HISTORY_REVENUE, MIN_HISTORY_SEASONALITY,
    STOCKOUT_THRESHOLD, LOW_INVENTORY_THRESHOLD,
    SCENARIO_NEW, SCENARIO_ACTIVE, SCENARIO_ANALYZING,
    SCENARIO_RCA_IDENT, SCENARIO_WHAT_IF, SCENARIO_OUTCOME,
    SCENARIO_RESOLVED, SCENARIO_CLOSED,
    HYPOTHESIS_FORECAST_BIAS, HYPOTHESIS_DEMAND_TREND,
    HYPOTHESIS_SEASONALITY, HYPOTHESIS_PROMOTION,
    HYPOTHESIS_PRICE, HYPOTHESIS_INVENTORY, HYPOTHESIS_DATA_QUALITY,
    HYP_STATUS_SUPPORTED, HYP_STATUS_POSSIBLE, HYP_STATUS_NOT_SUPPORTED,
    HYP_STATUS_NOT_TESTABLE,
    DATA_SUFFICIENT, DATA_PARTIAL, DATA_INSUFFICIENT,
)
from models import (
    EntityContext, TimeRange, ScenarioState, ConversationTurn,
    ForecastSummary, InventorySummary, RevenueSummary,
    DataQualityStatus, RCAEvidence, RCAHypothesis, RCAResult,
    ToolResult,
)

logger = logging.getLogger(__name__)
_spark: Optional[SparkSession] = None


def _get_spark() -> SparkSession:
    """Return the active Spark session (singleton, lazily initialised)."""
    global _spark
    if _spark is None:
        _spark = SparkSession.getActiveSession()
    return _spark


# ============================================================
#  1. EntityResolutionService  (BRD §13, §6.4)
# ============================================================

class EntityResolutionService:
    """
    Mandatory entity resolution before tool selection (BRD SS13).

    Resolution strategy (in order of priority):
      1. Exact product_id match on fact table
      2. SKU match on dim_product
      3. Name LIKE match on dim_product (returns multiple candidates if ambiguous)
      4. If multiple matches -> mark ambiguous and return candidates for clarification
    """

    def resolve_product(
        self,
        product_id: Optional[str] = None,
        product_name: Optional[str] = None,
    ) -> EntityContext:
        spark = _get_spark()
        ctx = EntityContext(product_id=product_id, product_name=product_name)

        # Try exact ID match on fact table
        if product_id:
            df = spark.sql(
                f"""SELECT DISTINCT product_id, region, category
                    FROM {FACT_TABLE}
                    WHERE product_id = '{product_id}' LIMIT 1"""
            )
            row = df.collect()
            if row:
                r = row[0]
                ctx.product_id = r["product_id"]
                ctx.region = r["region"]
                ctx.category = r["category"]
                ctx.resolved = True
                return ctx

            # Try dim_product sku match
            df2 = spark.sql(
                f"""SELECT sku, product_name, category, region
                    FROM {DIM_PRODUCT_TABLE}
                    WHERE sku = '{product_id}' LIMIT 1"""
            )
            row2 = df2.collect()
            if row2:
                r = row2[0]
                ctx.product_id = r["sku"]
                ctx.product_name = r["product_name"]
                ctx.category = r["category"]
                ctx.region = r["region"]
                ctx.resolved = True
                return ctx

        # Try name match on dim_product
        if product_name:
            df = spark.sql(
                f"""SELECT sku, product_name, category, region
                    FROM {DIM_PRODUCT_TABLE}
                    WHERE LOWER(product_name) LIKE LOWER('%{product_name}%')"""
            )
            rows = df.collect()
            if len(rows) == 1:
                r = rows[0]
                ctx.product_id = r["sku"]
                ctx.product_name = r["product_name"]
                ctx.category = r["category"]
                ctx.region = r["region"]
                ctx.resolved = True
            elif len(rows) > 1:
                ctx.ambiguous = True
                ctx.candidates = [
                    {"product_id": r["sku"], "product_name": r["product_name"]}
                    for r in rows[:5]
                ]

        return ctx

    def resolve_entity(
        self,
        product_id: Optional[str] = None,
        product_name: Optional[str] = None,
        region: Optional[str] = None,
        store_id: Optional[str] = None,
        category: Optional[str] = None,
    ) -> EntityContext:
        """Full entity resolution (BRD §13)."""
        ctx = self.resolve_product(product_id, product_name)
        if region:
            ctx.region = region
        if store_id:
            ctx.store_id = store_id
        if category:
            ctx.category = category
        return ctx


# ============================================================
#  2. ConversationMemoryService  (BRD §14 FR-08, §31)
# ============================================================

class ConversationMemoryService:
    """
    Persists and retrieves conversation turns in Delta (BRD SS31 Iteration 1).
    Each turn is appended to the conversation_turns table with session_id,
    turn_id, role, message, scenario_id, intent, and scenario_action.
    """

    def save_turn(self, turn: ConversationTurn) -> None:
        spark = _get_spark()
        data = [(turn.session_id, turn.turn_id, turn.user_id,
                 datetime.now(), turn.role, turn.message,
                 turn.scenario_id, turn.intent, turn.scenario_action)]
        schema_fields = StructType([
            StructField("session_id", StringType(), True),
            StructField("turn_id", IntegerType(), True),
            StructField("user_id", StringType(), True),
            StructField("timestamp", TimestampType(), True),
            StructField("role", StringType(), True),
            StructField("message", StringType(), True),
            StructField("scenario_id", StringType(), True),
            StructField("intent", StringType(), True),
            StructField("scenario_action", StringType(), True),
        ])
        df = spark.createDataFrame(data, schema=schema_fields)
        df.write.format("delta").mode("append").saveAsTable(CONVERSATION_TURNS_TABLE)

    def get_history(self, session_id: str, limit: int = 20) -> List[Dict]:
        spark = _get_spark()
        df = spark.sql(f"""
            SELECT role, message, timestamp, scenario_id, intent
            FROM {CONVERSATION_TURNS_TABLE}
            WHERE session_id = '{session_id}'
            ORDER BY turn_id DESC
            LIMIT {limit}
        """)
        rows = df.collect()
        return [{"role": r["role"], "message": r["message"],
                 "timestamp": str(r["timestamp"]), "scenario_id": r["scenario_id"],
                 "intent": r["intent"]} for r in reversed(rows)]

    def get_next_turn_id(self, session_id: str) -> int:
        spark = _get_spark()
        try:
            row = spark.sql(f"""
                SELECT COALESCE(MAX(turn_id), 0) + 1 AS next_id
                FROM {CONVERSATION_TURNS_TABLE}
                WHERE session_id = '{session_id}'
            """).collect()
            return row[0]["next_id"] if row else 1
        except Exception:
            return 1


# ============================================================
#  3. ScenarioStateService  (BRD §14 FR-09, §16, §17, §31)
# ============================================================

class ScenarioStateService:
    """
    Manages structured scenario state in Delta (BRD SS31 Iteration 1).
    Uses SCD-Type-2 pattern: every update appends a new row with an incremented
    version, preserving the full history of scenario evolution.
    """

    def create_scenario(
        self,
        session_id: str,
        user_id: str = "demand_planner",
        entities: Optional[EntityContext] = None,
        time_range: Optional[TimeRange] = None,
        analysis_type: str = "",
    ) -> ScenarioState:
        scenario_id = f"SCN-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now()
        state = ScenarioState(
            scenario_id=scenario_id,
            session_id=session_id,
            user_id=user_id,
            status=SCENARIO_NEW,
            resolved_entities=entities or EntityContext(),
            time_range=time_range,
            analysis_type=analysis_type,
            created_at=now,
            updated_at=now,
        )
        self._persist(state)
        return state

    def load_scenario(self, scenario_id: str) -> Optional[ScenarioState]:
        spark = _get_spark()
        try:
            df = spark.sql(f"""
                SELECT * FROM {SCENARIO_STATE_TABLE}
                WHERE scenario_id = '{scenario_id}'
                ORDER BY version DESC LIMIT 1
            """)
            row = df.collect()
            if not row:
                return None
            r = row[0]
            import json
            return ScenarioState(
                scenario_id=r["scenario_id"],
                session_id=r["session_id"],
                user_id=r["user_id"],
                status=r["status"],
                resolved_entities=EntityContext(
                    **json.loads(r["resolved_entities"]) if r["resolved_entities"] else {}
                ),
                analysis_type=r["analysis_type"] or "",
                active_issue=r["active_issue"] or "",
                rca_summary=r["rca_summary"],
                scenario_version=r["version"] or 1,
                created_at=r["created_at"],
                updated_at=r["updated_at"],
            )
        except Exception as exc:
            logger.warning("Could not load scenario %s: %s", scenario_id, exc)
            return None

    def load_active_scenario(self, session_id: str) -> Optional[ScenarioState]:
        spark = _get_spark()
        try:
            df = spark.sql(f"""
                SELECT scenario_id FROM {SCENARIO_STATE_TABLE}
                WHERE session_id = '{session_id}'
                  AND status NOT IN ('{SCENARIO_RESOLVED}', '{SCENARIO_CLOSED}')
                ORDER BY updated_at DESC LIMIT 1
            """)
            row = df.collect()
            if row:
                return self.load_scenario(row[0]["scenario_id"])
        except Exception:
            pass
        return None

    def update_scenario(self, state: ScenarioState) -> None:
        state.updated_at = datetime.now()
        state.scenario_version += 1
        self._persist(state)

    def _persist(self, state: ScenarioState) -> None:
        spark = _get_spark()
        import json
        data = [(
            state.scenario_id, state.session_id, state.user_id,
            state.status, json.dumps(state.resolved_entities.model_dump()),
            json.dumps(state.time_range.model_dump()) if state.time_range else None,
            state.analysis_type, state.active_issue,
            json.dumps(state.baseline_state) if state.baseline_state else None,
            json.dumps(state.current_state) if state.current_state else None,
            json.dumps(state.previous_state) if state.previous_state else None,
            json.dumps(state.last_tool_results) if state.last_tool_results else None,
            state.rca_summary,
            json.dumps(state.rca_evidence) if state.rca_evidence else None,
            json.dumps(state.rca_hypotheses) if state.rca_hypotheses else None,
            json.dumps(state.recommendations) if state.recommendations else None,
            json.dumps(state.what_if_parameters) if state.what_if_parameters else None,
            json.dumps(state.reported_outcomes) if state.reported_outcomes else None,
            json.dumps(state.assumptions) if state.assumptions else None,
            state.scenario_version, state.created_at, state.updated_at,
        )]
        cols = StructType([
            StructField("scenario_id", StringType(), True),
            StructField("session_id", StringType(), True),
            StructField("user_id", StringType(), True),
            StructField("status", StringType(), True),
            StructField("resolved_entities", StringType(), True),
            StructField("time_range", StringType(), True),
            StructField("analysis_type", StringType(), True),
            StructField("active_issue", StringType(), True),
            StructField("baseline_state", StringType(), True),
            StructField("current_state", StringType(), True),
            StructField("previous_state", StringType(), True),
            StructField("last_tool_results", StringType(), True),
            StructField("rca_summary", StringType(), True),
            StructField("rca_evidence", StringType(), True),
            StructField("rca_hypotheses", StringType(), True),
            StructField("recommendations", StringType(), True),
            StructField("what_if_parameters", StringType(), True),
            StructField("reported_outcomes", StringType(), True),
            StructField("assumptions", StringType(), True),
            StructField("version", IntegerType(), True),
            StructField("created_at", TimestampType(), True),
            StructField("updated_at", TimestampType(), True),
        ])
        df = spark.createDataFrame(data, schema=cols)
        df.write.format("delta").mode("append").saveAsTable(SCENARIO_STATE_TABLE)


# ============================================================
#  4. ForecastService  (BRD FR-01, §10)
# ============================================================

class ForecastService:
    """
    Deterministic forecast retrieval with time-window controls (BRD FR-01, SS10).

    Computes WMAPE-based forecast accuracy (not simple average MAPE):
      WMAPE    = SUM(|Forecast - Actual|) / SUM(Actual)
      Accuracy = (1 - WMAPE) * 100
      Bias %   = (SUM(Forecast) - SUM(Actual)) / SUM(Actual) * 100
    """

    def get_forecast_data(
        self,
        product_id: str,
        region: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        lookback_weeks: int = 12,
        include_history: bool = False,
    ) -> Dict[str, Any]:
        spark = _get_spark()

        # Build date filter
        date_filter = self._build_date_filter(start_date, end_date, lookback_weeks)

        where_clauses = [f"product_id = '{product_id}'", date_filter]
        if region:
            where_clauses.append(f"region = '{region}'")

        where_sql = " AND ".join(where_clauses)

        # Aggregate metrics (WMAPE-based, not simple average — BRD §10)
        agg_df = spark.sql(f"""
            SELECT
                SUM(demand_forecast)                    AS total_forecast,
                SUM(units_sold)                         AS total_actual,
                SUM(ABS(demand_forecast - units_sold))  AS sum_abs_error,
                COUNT(*)                                AS n_obs,
                MIN(date)                               AS coverage_start,
                MAX(date)                               AS coverage_end
            FROM {FACT_TABLE}
            WHERE {where_sql}
        """)
        agg = agg_df.collect()
        if not agg or agg[0]["n_obs"] == 0:
            return {
                "success": False,
                "error": f"No forecast data found for {product_id}"
                         + (f" in {region}" if region else ""),
            }

        r = agg[0]
        total_forecast = float(r["total_forecast"] or 0)
        total_actual = float(r["total_actual"] or 0)
        sum_abs_error = float(r["sum_abs_error"] or 0)
        n_obs = int(r["n_obs"] or 0)

        # WMAPE (BRD §10)
        wmape = (sum_abs_error / total_actual * 100) if total_actual > 0 else None
        accuracy = (100 - wmape) if wmape is not None else None
        bias_pct = ((total_forecast - total_actual) / total_actual * 100) if total_actual > 0 else None

        result = {
            "product_id": product_id,
            "region": region,
            "period": f"{r['coverage_start']} to {r['coverage_end']}",
            "total_forecast": round(total_forecast, 2),
            "total_actual": round(total_actual, 2),
            "avg_forecast": round(total_forecast / n_obs, 2) if n_obs else 0,
            "avg_actual": round(total_actual / n_obs, 2) if n_obs else 0,
            "wmape": round(wmape, 2) if wmape is not None else None,
            "forecast_accuracy": round(accuracy, 2) if accuracy is not None else None,
            "forecast_bias_pct": round(bias_pct, 2) if bias_pct is not None else None,
            "observations": n_obs,
            "coverage_start": str(r["coverage_start"]),
            "coverage_end": str(r["coverage_end"]),
        }

        # Optional history
        if include_history:
            hist_df = spark.sql(f"""
                SELECT date, demand_forecast, units_sold,
                       demand_forecast - units_sold AS forecast_error,
                       CASE WHEN units_sold > 0
                            THEN ROUND(ABS(demand_forecast - units_sold) / units_sold * 100, 2)
                            ELSE NULL END AS abs_pct_error
                FROM {FACT_TABLE}
                WHERE {where_sql}
                ORDER BY date DESC
                LIMIT {MAX_ROWS_RETURNED}
            """)
            result["history"] = [
                {"date": str(row["date"]),
                 "forecast": row["demand_forecast"],
                 "actual": row["units_sold"],
                 "error": row["forecast_error"],
                 "abs_pct_error": row["abs_pct_error"]}
                for row in hist_df.collect()
            ]

        return result

    def _build_date_filter(
        self,
        start: Optional[date],
        end: Optional[date],
        lookback_weeks: int,
    ) -> str:
        if start and end:
            return f"date >= '{start}' AND date <= '{end}'"
        # Compute lookback from max available date
        spark = _get_spark()
        max_row = spark.sql(f"SELECT MAX(date) AS max_d FROM {FACT_TABLE}").collect()
        max_date = max_row[0]["max_d"] if max_row else date.today()
        cutoff = max_date - timedelta(weeks=lookback_weeks)
        return f"date >= '{cutoff}' AND date <= '{max_date}'"

    # ------------------------------------------------------------------
    def get_forecast_ranking(
        self,
        region: Optional[str] = None,
        category: Optional[str] = None,
        top_n: int = 10,
        sort_by: str = "wmape",
    ) -> Dict[str, Any]:
        """
        Return a ranking of SKUs by forecast error metric for a given region.

        Args:
            region: Filter by region (optional, but typically required).
            category: Filter by category (optional).
            top_n: Number of top SKUs to return (default 10).
            sort_by: Sort metric -- 'wmape', 'bias', or 'absolute_error' (default wmape).

        Returns:
            Dict with success, rankings list, and count.
        """
        spark = _get_spark()

        # Whitelist sort columns to prevent SQL injection
        sort_map = {
            "wmape": "wmape DESC",
            "bias": "ABS(bias_pct) DESC",
            "absolute_error": "sum_abs_error DESC",
        }
        order_clause = sort_map.get(sort_by, "wmape DESC")
        top_n = min(max(top_n, 1), 100)  # Clamp 1..100

        where_parts = []
        if region:
            where_parts.append(f"region = '{region}'")
        if category:
            where_parts.append(f"category = '{category}'")
        where_clause = ("WHERE " + " AND ".join(where_parts)) if where_parts else ""

        df = spark.sql(f"""
            SELECT
                product_id,
                region,
                category,
                SUM(demand_forecast) AS total_forecast,
                SUM(units_sold)      AS total_actual,
                SUM(absolute_error)   AS sum_abs_error,
                ROUND(SUM(absolute_error) / NULLIF(SUM(units_sold), 0) * 100, 2) AS wmape,
                ROUND((SUM(demand_forecast) - SUM(units_sold)) / NULLIF(SUM(units_sold), 0) * 100, 2) AS bias_pct,
                ROUND(100 - SUM(absolute_error) / NULLIF(SUM(units_sold), 0) * 100, 2) AS forecast_accuracy,
                COUNT(*) AS n_obs
            FROM {FACT_TABLE}
            {where_clause}
            GROUP BY product_id, region, category
            ORDER BY {order_clause}
            LIMIT {top_n}
        """)
        rows = df.collect()

        rankings = []
        for r in rows:
            rankings.append({
                "product_id": r["product_id"],
                "region": r["region"],
                "category": r["category"],
                "total_forecast": r["total_forecast"],
                "total_actual": r["total_actual"],
                "wmape": r["wmape"],
                "bias_pct": r["bias_pct"],
                "forecast_accuracy": r["forecast_accuracy"],
                "n_obs": r["n_obs"],
            })

        return {
            "success": True,
            "region": region or "ALL",
            "category": category or "ALL",
            "sort_by": sort_by,
            "top_n": top_n,
            "count": len(rankings),
            "rankings": rankings,
        }


# ============================================================
#  5. InventoryService  (BRD FR-03, §12)
# ============================================================

class InventoryService:
    """Deterministic inventory retrieval with freshness / as-of handling."""

    def get_inventory_data(
        self,
        product_id: str,
        region: Optional[str] = None,
        as_of_date: Optional[str] = None,
        lookback_weeks: int = 12,
        include_history: bool = False,
    ) -> Dict[str, Any]:
        spark = _get_spark()

        if as_of_date:
            date_filter = f"date <= '{as_of_date}'"
        else:
            max_row = spark.sql(f"SELECT MAX(date) AS max_d FROM {FACT_TABLE} WHERE product_id = '{product_id}'").collect()
            max_date = max_row[0]["max_d"] if max_row and max_row[0]["max_d"] else date.today()
            cutoff = max_date - timedelta(weeks=lookback_weeks)
            date_filter = f"date >= '{cutoff}' AND date <= '{max_date}'"

        where_parts = [f"product_id = '{product_id}'", date_filter]
        if region:
            where_parts.append(f"region = '{region}'")
        where_sql = " AND ".join(where_parts)

        # Latest inventory (not blindly most-recent row — BRD FR-03)
        latest_df = spark.sql(f"""
            SELECT date, inventory_level, units_sold,
                   CASE
                       WHEN inventory_level <= {STOCKOUT_THRESHOLD} THEN 'Stockout'
                       WHEN inventory_level < units_sold * 1.5 THEN 'Low Inventory'
                       ELSE 'Healthy'
                   END AS inventory_status,
                   CASE WHEN inventory_level <= {STOCKOUT_THRESHOLD} THEN true ELSE false END AS stockout_flag
            FROM {FACT_TABLE}
            WHERE {where_sql}
            ORDER BY date DESC
            LIMIT 1
        """)
        latest = latest_df.collect()
        if not latest:
            return {
                "success": False,
                "error": f"No inventory data found for {product_id}"
                         + (f" in {region}" if region else ""),
            }

        r = latest[0]
        inv_level = float(r["inventory_level"] or 0)
        units = float(r["units_sold"] or 1)
        inv_days = round(inv_level / units, 1) if units > 0 else None

        result = {
            "product_id": product_id,
            "region": region,
            "as_of_date": str(r["date"]),
            "inventory_level": inv_level,
            "inventory_status": r["inventory_status"],
            "stockout_flag": bool(r["stockout_flag"]),
            "inventory_days": inv_days,
        }

        if include_history:
            hist_df = spark.sql(f"""
                SELECT date, inventory_level, units_sold,
                       CASE WHEN inventory_level <= {STOCKOUT_THRESHOLD} THEN true ELSE false END AS stockout_flag
                FROM {FACT_TABLE}
                WHERE {where_sql}
                ORDER BY date DESC
                LIMIT {MAX_ROWS_RETURNED}
            """)
            result["history"] = [
                {"date": str(row["date"]),
                 "inventory_level": row["inventory_level"],
                 "units_sold": row["units_sold"],
                 "stockout_flag": bool(row["stockout_flag"])}
                for row in hist_df.collect()
            ]

        return result


# ============================================================
#  6. RevenueService  (BRD FR-02, §10)
# ============================================================

class RevenueService:
    """Deterministic revenue retrieval (BRD FR-02).

    Gross Revenue = Units Sold × Price
    Net Revenue   = Units Sold × Price × (1 - Discount / 100)
    """

    def get_revenue_data(
        self,
        product_id: str,
        region: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        lookback_weeks: int = 12,
        revenue_type: str = "net",
        include_trend: bool = False,
    ) -> Dict[str, Any]:
        spark = _get_spark()

        # Build date filter
        if start_date and end_date:
            date_filter = f"date >= '{start_date}' AND date <= '{end_date}'"
        else:
            max_row = spark.sql(f"SELECT MAX(date) AS max_d FROM {FACT_TABLE} WHERE product_id = '{product_id}'").collect()
            max_date = max_row[0]["max_d"] if max_row and max_row[0]["max_d"] else date.today()
            cutoff = max_date - timedelta(weeks=lookback_weeks)
            date_filter = f"date >= '{cutoff}' AND date <= '{max_date}'"

        where_parts = [f"product_id = '{product_id}'", date_filter]
        if region:
            where_parts.append(f"region = '{region}'")
        where_sql = " AND ".join(where_parts)

        df = spark.sql(f"""
            SELECT
                SUM(units_sold * price)                                       AS gross_revenue,
                SUM(units_sold * price * (1 - discount / 100))                 AS net_revenue,
                SUM(units_sold)                                               AS total_units,
                AVG(price)                                                    AS avg_price,
                AVG(discount)                                                  AS avg_discount,
                MIN(date)                                                      AS coverage_start,
                MAX(date)                                                      AS coverage_end,
                COUNT(*)                                                       AS n_obs
            FROM {FACT_TABLE}
            WHERE {where_sql}
        """)
        row = df.collect()
        if not row or row[0]["n_obs"] == 0:
            return {
                "success": False,
                "error": f"No revenue data found for {product_id}"
                         + (f" in {region}" if region else ""),
            }

        r = row[0]
        gross = float(r["gross_revenue"] or 0)
        net = float(r["net_revenue"] or 0)

        result = {
            "product_id": product_id,
            "region": region,
            "period": f"{r['coverage_start']} to {r['coverage_end']}",
            "gross_revenue": round(gross, 2),
            "net_revenue": round(net, 2),
            "total_units": int(r["total_units"] or 0),
            "avg_price": round(float(r["avg_price"] or 0), 2),
            "avg_discount": round(float(r["avg_discount"] or 0), 2),
            "revenue_type": revenue_type,
            "primary_revenue": round(net if revenue_type == "net" else gross, 2),
        }

        if include_trend:
            trend_df = spark.sql(f"""
                SELECT date,
                       SUM(units_sold * price) AS gross_revenue,
                       SUM(units_sold * price * (1 - discount / 100)) AS net_revenue
                FROM {FACT_TABLE}
                WHERE {where_sql}
                GROUP BY date
                ORDER BY date DESC
                LIMIT 30
            """)
            result["trend"] = [
                {"date": str(row2["date"]),
                 "gross_revenue": round(row2["gross_revenue"], 2),
                 "net_revenue": round(row2["net_revenue"], 2)}
                for row2 in trend_df.collect()
            ]

        return result


# ============================================================
#  7. HistoricalPatternService  (BRD FR-04, §24)
# ============================================================

class HistoricalPatternService:
    """Deterministic pattern detection over configurable lookback."""

    def analyze_patterns(
        self,
        product_id: str,
        region: Optional[str] = None,
        lookback_weeks: int = 12,
        patterns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        spark = _get_spark()
        all_patterns = patterns or [
            "trend", "volatility", "level_shift", "bias_drift",
            "accuracy_deterioration", "actual_vs_forecast_divergence",
            "demand_spikes", "promotion_linked", "inventory_constrained",
        ]

        where_parts = [f"product_id = '{product_id}'"]
        if region:
            where_parts.append(f"region = '{region}'")
        where_sql = " AND ".join(where_parts)

        max_row = spark.sql(f"SELECT MAX(date) AS max_d FROM {FACT_TABLE} WHERE {where_sql}").collect()
        if not max_row or not max_row[0]["max_d"]:
            return {"success": False, "error": f"No data for {product_id}"}
        max_date = max_row[0]["max_d"]
        cutoff = max_date - timedelta(weeks=lookback_weeks)

        df = spark.sql(f"""
            SELECT date, units_sold, demand_forecast, inventory_level,
                   holiday_promotion, price, discount
            FROM {FACT_TABLE}
            WHERE {where_sql} AND date >= '{cutoff}' AND date <= '{max_date}'
            ORDER BY date
        """)
        rows = df.collect()
        if len(rows) < 4:
            return {
                "success": False,
                "error": f"Insufficient history ({len(rows)} obs) for pattern analysis",
            }

        actuals = [r["units_sold"] for r in rows]
        forecasts = [r["demand_forecast"] for r in rows]
        dates = [r["date"] for r in rows]
        n = len(rows)

        result: Dict[str, Any] = {
            "product_id": product_id,
            "region": region,
            "period": f"{dates[0]} to {dates[-1]}",
            "observations": n,
            "patterns": {},
        }

        # --- Trend (linear regression slope) ---
        if "trend" in all_patterns:
            x_mean = sum(range(n)) / n
            y_mean = sum(actuals) / n
            num = sum((i - x_mean) * (actuals[i] - y_mean) for i in range(n))
            den = sum((i - x_mean) ** 2 for i in range(n))
            slope = num / den if den != 0 else 0
            result["patterns"]["trend"] = {
                "slope": round(slope, 4),
                "direction": "increasing" if slope > 1 else "decreasing" if slope < -1 else "stable",
                "avg_actual": round(y_mean, 2),
            }

        # --- Volatility (coefficient of variation) ---
        if "volatility" in all_patterns:
            mean_a = sum(actuals) / n if n else 0
            var_a = sum((a - mean_a) ** 2 for a in actuals) / n if n else 0
            std_a = math.sqrt(var_a)
            cv = (std_a / mean_a * 100) if mean_a > 0 else 0
            result["patterns"]["volatility"] = {
                "std_dev": round(std_a, 2),
                "cv_pct": round(cv, 2),
                "level": "high" if cv > 40 else "medium" if cv > 20 else "low",
            }

        # --- Level shift (compare first half vs second half) ---
        if "level_shift" in all_patterns:
            mid = n // 2
            first_half = sum(actuals[:mid]) / max(mid, 1)
            second_half = sum(actuals[mid:]) / max(n - mid, 1)
            shift_pct = ((second_half - first_half) / first_half * 100) if first_half > 0 else 0
            result["patterns"]["level_shift"] = {
                "first_half_avg": round(first_half, 2),
                "second_half_avg": round(second_half, 2),
                "shift_pct": round(shift_pct, 2),
                "detected": abs(shift_pct) > 15,
            }

        # --- Bias drift ---
        if "bias_drift" in all_patterns:
            errors = [(forecasts[i] - actuals[i]) for i in range(n)]
            rolling_errors = []
            window = min(4, n)
            for i in range(window, n + 1):
                w_errors = errors[i - window:i]
                rolling_errors.append(sum(w_errors) / len(w_errors))
            if len(rolling_errors) >= 2:
                first_re = rolling_errors[0]
                last_re = rolling_errors[-1]
                drift = last_re - first_re
                result["patterns"]["bias_drift"] = {
                    "initial_rolling_bias": round(first_re, 2),
                    "final_rolling_bias": round(last_re, 2),
                    "drift": round(drift, 2),
                    "direction": "worsening_overforecast" if drift > 0 else "worsening_underforecast" if drift < 0 else "stable",
                }

        # --- Accuracy deterioration ---
        if "accuracy_deterioration" in all_patterns:
            mid = n // 2
            first_errors = [abs(forecasts[i] - actuals[i]) for i in range(mid)]
            second_errors = [abs(forecasts[i] - actuals[i]) for i in range(mid, n)]
            first_mae = sum(first_errors) / max(len(first_errors), 1)
            second_mae = sum(second_errors) / max(len(second_errors), 1)
            deterioration_pct = ((second_mae - first_mae) / first_mae * 100) if first_mae > 0 else 0
            result["patterns"]["accuracy_deterioration"] = {
                "first_half_mae": round(first_mae, 2),
                "second_half_mae": round(second_mae, 2),
                "deterioration_pct": round(deterioration_pct, 2),
                "deteriorating": deterioration_pct > 10,
            }

        # --- Actual vs forecast divergence ---
        if "actual_vs_forecast_divergence" in all_patterns:
            total_f = sum(forecasts)
            total_a = sum(actuals)
            divergence_pct = ((total_f - total_a) / total_a * 100) if total_a > 0 else 0
            result["patterns"]["actual_vs_forecast_divergence"] = {
                "total_forecast": round(total_f, 2),
                "total_actual": round(total_a, 2),
                "divergence_pct": round(divergence_pct, 2),
                "direction": "overcast" if divergence_pct > 0 else "undercast" if divergence_pct < 0 else "aligned",
            }

        # --- Demand spikes ---
        if "demand_spikes" in all_patterns:
            mean_a = sum(actuals) / n if n else 0
            std_a = math.sqrt(sum((a - mean_a) ** 2 for a in actuals) / n) if n else 0
            spikes = []
            if std_a > 0:
                for i in range(n):
                    if actuals[i] > mean_a + 2 * std_a:
                        spikes.append({"date": str(dates[i]), "value": actuals[i]})
            result["patterns"]["demand_spikes"] = {
                "count": len(spikes),
                "spikes": spikes[:5],
            }

        # --- Promotion-linked ---
        if "promotion_linked" in all_patterns:
            promo_df = spark.sql(f"""
                SELECT
                    AVG(CASE WHEN holiday_promotion > 0 THEN units_sold ELSE NULL END) AS promo_avg,
                    AVG(CASE WHEN holiday_promotion = 0 THEN units_sold ELSE NULL END) AS nonpromo_avg
                FROM {FACT_TABLE}
                WHERE {where_sql} AND date >= '{cutoff}' AND date <= '{max_date}'
            """)
            promo_row = promo_df.collect()
            if promo_row and promo_row[0]["promo_avg"] is not None:
                pr = promo_row[0]
                promo_avg = float(pr["promo_avg"])
                nonpromo_avg = float(pr["nonpromo_avg"] or 0)
                uplift_pct = ((promo_avg - nonpromo_avg) / nonpromo_avg * 100) if nonpromo_avg > 0 else 0
                result["patterns"]["promotion_linked"] = {
                    "promo_avg_sales": round(promo_avg, 2),
                    "nonpromo_avg_sales": round(nonpromo_avg, 2),
                    "uplift_pct": round(uplift_pct, 2),
                    "significant": abs(uplift_pct) > 10,
                }

        # --- Inventory-constrained (BRD §12) ---
        if "inventory_constrained" in all_patterns:
            stockout_days = sum(1 for r in rows if r["inventory_level"] <= STOCKOUT_THRESHOLD)
            low_inv_days = sum(1 for r in rows if r["inventory_level"] < r["units_sold"] * 1.5)
            result["patterns"]["inventory_constrained"] = {
                "stockout_days": stockout_days,
                "low_inventory_days": low_inv_days,
                "total_days": n,
                "constrained": stockout_days > 0 or low_inv_days > n * 0.3,
            }

        result["success"] = True
        return result


# ============================================================
#  8. ForecastRCAService  (BRD §9, FR-05/06/07, §25, §12)
# ============================================================

class ForecastRCAService:
    """Deterministic RCA evidence-package generator (BRD §25)."""

    def run_rca(
        self,
        product_id: str,
        region: Optional[str] = None,
        lookback_weeks: int = 12,
        hypotheses: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        spark = _get_spark()

        # Gather data
        where_parts = [f"product_id = '{product_id}'"]
        if region:
            where_parts.append(f"region = '{region}'")
        where_sql = " AND ".join(where_parts)

        max_row = spark.sql(f"SELECT MAX(date) AS max_d FROM {FACT_TABLE} WHERE {where_sql}").collect()
        if not max_row or not max_row[0]["max_d"]:
            return {
                "success": False,
                "error": f"No data for product {product_id}" + (f" in {region}" if region else ""),
            }
        max_date = max_row[0]["max_d"]
        cutoff = max_date - timedelta(weeks=lookback_weeks)

        df = spark.sql(f"""
            SELECT date, product_id, region, units_sold, demand_forecast,
                   inventory_level, price, discount, holiday_promotion,
                   weather_condition, seasonality, competitor_pricing
            FROM {FACT_TABLE}
            WHERE {where_sql} AND date >= '{cutoff}' AND date <= '{max_date}'
            ORDER BY date
        """)
        rows = df.collect()
        n = len(rows)

        # --- Data quality assessment ---
        dq = self._assess_data_quality(rows, n, lookback_weeks)

        if n < 4:
            return {
                "success": False,
                "error": "Insufficient history for RCA",
                "data_quality": dq,
            }

        actuals = [r["units_sold"] for r in rows]
        forecasts = [r["demand_forecast"] for r in rows]
        dates = [r["date"] for r in rows]

        observations: List[str] = []
        evidence: List[Dict] = []
        hyps: List[Dict] = []
        recommendations: List[str] = []

        # --- Observed facts ---
        total_f = sum(forecasts)
        total_a = sum(actuals)
        total_abs_err = sum(abs(forecasts[i] - actuals[i]) for i in range(n))
        wmape = (total_abs_err / total_a * 100) if total_a > 0 else None
        bias_pct = ((total_f - total_a) / total_a * 100) if total_a > 0 else None

        observations.append(
            f"{n} observations from {dates[0]} to {dates[-1]}. "
            f"Total forecast: {total_f}, Total actual: {total_a}."
        )
        if wmape is not None:
            observations.append(f"WMAPE: {round(wmape, 2)}%. Forecast accuracy: {round(100 - wmape, 2)}%.")
        if bias_pct is not None:
            direction = "over-forecast" if bias_pct > 0 else "under-forecast"
            observations.append(f"Bias: {round(bias_pct, 2)}% ({direction}).")

        evidence.append({
            "evidence_type": "summary_metrics",
            "description": f"WMAPE={round(wmape or 0, 2)}%, Bias={round(bias_pct or 0, 2)}%",
            "metric": "wmape",
            "value": round(wmape or 0, 2),
            "period": f"{dates[0]} to {dates[-1]}",
        })

        all_hyps = hypotheses or [
            HYPOTHESIS_FORECAST_BIAS, HYPOTHESIS_DEMAND_TREND,
            HYPOTHESIS_PROMOTION, HYPOTHESIS_INVENTORY,
            HYPOTHESIS_PRICE, HYPOTHESIS_DATA_QUALITY,
        ]

        # --- H1: Forecast bias ---
        if HYPOTHESIS_FORECAST_BIAS in all_hyps:
            if bias_pct is not None and abs(bias_pct) > 10:
                hyps.append({
                    "cause": HYPOTHESIS_FORECAST_BIAS,
                    "evidence": [{
                        "evidence_type": "bias",
                        "description": f"Persistent {'over' if bias_pct > 0 else 'under'}-forecast bias of {round(bias_pct, 2)}%",
                        "metric": "bias_pct",
                        "value": round(bias_pct, 2),
                    }],
                    "strength": "HIGH" if abs(bias_pct) > 25 else "MEDIUM",
                    "status": HYP_STATUS_SUPPORTED,
                    "reasoning": f"Bias exceeds 10% threshold at {round(bias_pct, 2)}%",
                })
                recommendations.append(
                    "Review forecast model calibration to address systematic "
                    f"{'over' if bias_pct > 0 else 'under'}-forecasting."
                )

        # --- H2: Demand trend shift ---
        if HYPOTHESIS_DEMAND_TREND in all_hyps:
            mid = n // 2
            first_avg = sum(actuals[:mid]) / max(mid, 1)
            second_avg = sum(actuals[mid:]) / max(n - mid, 1)
            shift_pct = ((second_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0
            if abs(shift_pct) > 15:
                hyps.append({
                    "cause": HYPOTHESIS_DEMAND_TREND,
                    "evidence": [{
                        "evidence_type": "trend",
                        "description": f"Demand {'increased' if shift_pct > 0 else 'decreased'} by {round(shift_pct, 2)}% between first and second half",
                        "metric": "shift_pct",
                        "value": round(shift_pct, 2),
                    }],
                    "strength": "HIGH" if abs(shift_pct) > 30 else "MEDIUM",
                    "status": HYP_STATUS_SUPPORTED,
                    "reasoning": f"Level shift of {round(shift_pct, 2)}% detected",
                })
                recommendations.append(
                    f"Investigate structural demand {'increase' if shift_pct > 0 else 'decrease'} "
                    "and update baseline forecast assumptions."
                )

        # --- H3: Promotion effect ---
        if HYPOTHESIS_PROMOTION in all_hyps:
            promo_rows = [r for r in rows if r["holiday_promotion"] and r["holiday_promotion"] > 0]
            nonpromo_rows = [r for r in rows if not r["holiday_promotion"] or r["holiday_promotion"] == 0]
            if promo_rows and nonpromo_rows:
                promo_avg = sum(r["units_sold"] for r in promo_rows) / len(promo_rows)
                nonpromo_avg = sum(r["units_sold"] for r in nonpromo_rows) / len(nonpromo_rows)
                uplift = ((promo_avg - nonpromo_avg) / nonpromo_avg * 100) if nonpromo_avg > 0 else 0
                if abs(uplift) > 10:
                    hyps.append({
                        "cause": HYPOTHESIS_PROMOTION,
                        "evidence": [{
                            "evidence_type": "promotion",
                            "description": f"Promotion periods show {round(uplift, 2)}% difference in sales vs non-promotion",
                            "metric": "uplift_pct",
                            "value": round(uplift, 2),
                        }],
                        "strength": "HIGH" if abs(uplift) > 30 else "MEDIUM",
                        "status": HYP_STATUS_SUPPORTED,
                        "reasoning": f"Promotion uplift of {round(uplift, 2)}% detected",
                    })
                    recommendations.append(
                        "Review promotion calendar alignment with forecast assumptions."
                    )

        # --- H4: Inventory constraint (BRD §12) ---
        if HYPOTHESIS_INVENTORY in all_hyps:
            stockout_days = sum(1 for r in rows if r["inventory_level"] <= STOCKOUT_THRESHOLD)
            low_inv_days = sum(1 for r in rows if r["inventory_level"] < r["units_sold"] * 1.5)
            if stockout_days > 0 or low_inv_days > n * 0.3:
                hyps.append({
                    "cause": HYPOTHESIS_INVENTORY,
                    "evidence": [{
                        "evidence_type": "inventory",
                        "description": f"{stockout_days} stockout days, {low_inv_days} low-inventory days out of {n}",
                        "metric": "stockout_days",
                        "value": stockout_days,
                    }],
                    "strength": "HIGH" if stockout_days > 3 else "MEDIUM",
                    "status": HYP_STATUS_SUPPORTED,
                    "reasoning": "Observed sales may be supply-constrained rather than demand-driven",
                })
                recommendations.append(
                    "Observed sales may be supply-constrained. "
                    "Do not interpret low sales as demand decline without verifying inventory availability."
                )

        # --- H5: Price effect ---
        if HYPOTHESIS_PRICE in all_hyps:
            prices = [r["price"] for r in rows]
            if max(prices) != min(prices):
                price_change = ((max(prices) - min(prices)) / min(prices) * 100) if min(prices) > 0 else 0
                if abs(price_change) > 10:
                    hyps.append({
                        "cause": HYPOTHESIS_PRICE,
                        "evidence": [{
                            "evidence_type": "price",
                            "description": f"Price varied by {round(price_change, 2)}% during the period",
                            "metric": "price_change_pct",
                            "value": round(price_change, 2),
                        }],
                        "strength": "MEDIUM",
                        "status": HYP_STATUS_POSSIBLE,
                        "reasoning": "Price variation may correlate with demand changes",
                    })

        # --- H6: Data quality ---
        if HYPOTHESIS_DATA_QUALITY in all_hyps:
            if dq.data_status != DATA_SUFFICIENT:
                hyps.append({
                    "cause": HYPOTHESIS_DATA_QUALITY,
                    "evidence": [{
                        "evidence_type": "data_quality",
                        "description": "; ".join(dq.data_quality_flags) or "Data quality issues detected",
                        "metric": "data_status",
                        "value": dq.data_status,
                    }],
                    "strength": "LOW",
                    "status": HYP_STATUS_POSSIBLE,
                    "reasoning": "Data quality issues may affect RCA reliability",
                })

        # --- Confidence ---
        supported_count = sum(1 for h in hyps if h["status"] == HYP_STATUS_SUPPORTED)
        if supported_count >= 2:
            confidence = "HIGH"
        elif supported_count == 1:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        # --- Limitations ---
        limitations: List[str] = []
        if n < 28:
            limitations.append(f"Only {n} observations; longer history would improve confidence.")
        if dq.data_status == DATA_PARTIAL:
            limitations.append("Data is partial; some metrics may be incomplete.")
        limitations.append("Hypotheses are evidence-based, not causal claims.")

        return {
            "success": True,
            "entity": {"product_id": product_id, "region": region},
            "period": {"start": str(dates[0]), "end": str(dates[-1]), "weeks": lookback_weeks},
            "data_quality": dq.model_dump() if hasattr(dq, 'model_dump') else dq,
            "observations": observations,
            "evidence": evidence,
            "hypotheses": hyps,
            "recommendations": recommendations,
            "confidence": confidence,
            "limitations": limitations,
        }

    def _assess_data_quality(
        self, rows: List, n: int, lookback_weeks: int,
    ) -> DataQualityStatus:
        flags: List[str] = []
        missing: List[str] = []

        if n < 4:
            flags.append(f"Insufficient observations: {n}")
        if n < lookback_weeks * 5:  # ~5 days per week
            flags.append(f"Incomplete coverage: {n} obs vs expected ~{lookback_weeks * 5}")

        null_forecasts = sum(1 for r in rows if r["demand_forecast"] is None)
        if null_forecasts:
            missing.append("demand_forecast")
            flags.append(f"{null_forecasts} null forecast values")

        zero_actuals = sum(1 for r in rows if r["units_sold"] == 0)
        if zero_actuals > n * 0.5:
            flags.append(f"{zero_actuals} zero-actual observations")

        duplicate_dates = len(rows) - len(set(r["date"] for r in rows))
        if duplicate_dates > 0:
            flags.append(f"{duplicate_dates} duplicate dates")

        status = DATA_SUFFICIENT
        if len(flags) >= 2:
            status = DATA_INSUFFICIENT
        elif len(flags) == 1:
            status = DATA_PARTIAL

        coverage_start = str(rows[0]["date"]) if rows else None
        coverage_end = str(rows[-1]["date"]) if rows else None

        return DataQualityStatus(
            data_status=status,
            coverage_start=coverage_start,
            coverage_end=coverage_end,
            total_observations=n,
            missing_fields=missing,
            data_quality_flags=flags,
        )


# ============================================================
#  9. ScenarioComparisonService  (BRD §17, §18)
# ============================================================

class ScenarioComparisonService:
    """Compare baseline vs current/what-if scenario (BRD §17, §18)."""

    def compare(
        self,
        baseline_state: Dict[str, Any],
        current_state: Dict[str, Any],
        what_if_parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        deltas: Dict[str, Any] = {}
        for key in set(list(baseline_state.keys()) + list(current_state.keys())):
            b = baseline_state.get(key)
            c = current_state.get(key)
            if isinstance(b, (int, float)) and isinstance(c, (int, float)):
                deltas[key] = {
                    "baseline": b,
                    "current": c,
                    "delta": round(c - b, 2),
                    "delta_pct": round(((c - b) / b * 100) if b != 0 else 0, 2),
                }

        return {
            "baseline": baseline_state,
            "current": current_state,
            "what_if_parameters": what_if_parameters,
            "deltas": deltas,
            "summary": self._build_summary(deltas, what_if_parameters),
        }

    def _build_summary(self, deltas: Dict, what_if: Optional[Dict]) -> str:
        parts = []
        if what_if:
            for k, v in what_if.items():
                parts.append(f"{k}: {v}")
        if not deltas:
            return "No numeric differences detected."
        for k, d in deltas.items():
            parts.append(f"{k}: {d['baseline']} → {d['current']} (Δ {d['delta']})")
        return " | ".join(parts)


# ============================================================
# 10. DataQualityService  (BRD §11, §27)
# ============================================================

class DataQualityService:
    """Explicit validation for entity, date, and metric exceptions."""

    def check_entity(self, product_id: str, region: Optional[str] = None) -> Dict[str, Any]:
        spark = _get_spark()
        df = spark.sql(f"SELECT COUNT(DISTINCT region) AS n_regions FROM {FACT_TABLE} WHERE product_id = '{product_id}'")
        cnt = df.collect()
        if not cnt or cnt[0]["n_regions"] == 0:
            return {"valid": False, "error": f"Unknown product: {product_id}"}
        return {"valid": True}

    def check_date_range(
        self, product_id: str,
        start: Optional[date] = None,
        end: Optional[date] = None,
    ) -> Dict[str, Any]:
        spark = _get_spark()
        df = spark.sql(f"SELECT MIN(date) AS min_d, MAX(date) AS max_d FROM {FACT_TABLE} WHERE product_id = '{product_id}'")
        row = df.collect()
        if not row:
            return {"valid": False, "error": "No data"}
        min_d = row[0]["min_d"]
        max_d = row[0]["max_d"]
        issues = []
        if start and start < min_d:
            issues.append(f"Requested start {start} precedes data start {min_d}")
        if end and end > max_d:
            issues.append(f"Requested end {end} exceeds data end {max_d}")
        if start and end and end > date.today():
            issues.append("Future dates requested for actuals")
        return {"valid": len(issues) == 0, "issues": issues,
                "coverage": {"start": str(min_d), "end": str(max_d)}}

    def check_metrics(self, product_id: str, region: Optional[str] = None) -> Dict[str, Any]:
        spark = _get_spark()
        where_sql = f"product_id = '{product_id}'"
        if region:
            where_sql += f" AND region = '{region}'"
        df = spark.sql(f"""
            SELECT
                SUM(CASE WHEN demand_forecast IS NULL THEN 1 ELSE 0 END) AS null_forecasts,
                SUM(CASE WHEN units_sold = 0 THEN 1 ELSE 0 END) AS zero_actuals,
                SUM(CASE WHEN units_sold < 0 THEN 1 ELSE 0 END) AS negative_units,
                SUM(CASE WHEN inventory_level < 0 THEN 1 ELSE 0 END) AS negative_inventory,
                SUM(CASE WHEN price <= 0 THEN 1 ELSE 0 END) AS invalid_price,
                SUM(CASE WHEN discount < 0 OR discount > 100 THEN 1 ELSE 0 END) AS invalid_discount
            FROM {FACT_TABLE}
            WHERE {where_sql}
        """)
        r = df.collect()[0]
        issues = []
        if r["null_forecasts"]:  issues.append(f"{r['null_forecasts']} null forecasts")
        if r["zero_actuals"]:   issues.append(f"{r['zero_actuals']} zero-actual rows")
        if r["negative_units"]:  issues.append(f"{r['negative_units']} negative units")
        if r["negative_inventory"]: issues.append(f"{r['negative_inventory']} negative inventory")
        if r["invalid_price"]:   issues.append(f"{r['invalid_price']} invalid prices")
        if r["invalid_discount"]: issues.append(f"{r['invalid_discount']} invalid discounts")
        return {"valid": len(issues) == 0, "issues": issues}


# ============================================================
#  Service singletons
# ============================================================

entity_service         = EntityResolutionService()
conversation_service   = ConversationMemoryService()
scenario_service       = ScenarioStateService()
forecast_service       = ForecastService()
inventory_service      = InventoryService()
revenue_service        = RevenueService()
pattern_service        = HistoricalPatternService()
rca_service            = ForecastRCAService()
comparison_service     = ScenarioComparisonService()
data_quality_service   = DataQualityService()