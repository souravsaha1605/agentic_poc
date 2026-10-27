"""
analytics.py -- Composable analytical plan, governed registries, and deterministic query compiler.
============================================================================================================

PURPOSE
-------
Replaces narrow per-question tool functions with a single composable
``run_analytical_query`` tool.  The LLM produces a structured AnalyticalPlan
(JSON); this module validates it against governed registries, compiles it to
parameterized SQL, and executes it against approved Databricks views.

ARCHITECTURE
------------
  User Request
      ↓
  LLM interprets request → produces AnalyticalPlan JSON
      ↓
  PlanValidator  (metric / dimension / grain / operation whitelist)
      ↓
  AnalyticalQueryCompiler  (plan → parameterized SQL with CTEs)
      ↓
  Spark executes against governed views
      ↓
  Evidence package (structured dict)
      ↓
  LLM interprets evidence → user response

The LLM never directly controls table names, raw SQL, or arbitrary columns.

BRD REFERENCES: SS20 (Tool Definitions), SS23 (Governed Views), SS28 (Error Handling),
               SS29 (Trust Boundary), SS37 (Grounding), SS50 (Readiness Registry).
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.sql import SparkSession

from config import (
    VW_FORECAST_METRICS,
    VW_INVENTORY_HEALTH,
    VW_REVENUE_METRICS,
    VW_FORECAST_HISTORY,
    VW_RCA_FEATURES,
    FACT_TABLE,
)

logger = logging.getLogger(__name__)

# ============================================================
#  Governed Metric Registry
#  Maps business metric names → approved SQL expressions.
#  The LLM references metrics BY NAME only — never raw SQL.
# ============================================================

METRIC_REGISTRY: Dict[str, Dict[str, Any]] = {
    "revenue": {
        "sql": "SUM(gross_revenue)",
        "type": "DOUBLE",
        "view": "vw_forecast_metrics",
        "description": "Total gross revenue",
    },
    "net_revenue": {
        "sql": "SUM(net_revenue)",
        "type": "DOUBLE",
        "view": "vw_forecast_metrics",
        "description": "Total net revenue (after discount)",
    },
    "forecast": {
        "sql": "SUM(demand_forecast)",
        "type": "DOUBLE",
        "view": "vw_forecast_metrics",
        "description": "Total forecast units",
    },
    "actual": {
        "sql": "SUM(units_sold)",
        "type": "DOUBLE",
        "view": "vw_forecast_metrics",
        "description": "Total actual units sold",
    },
    "wmape": {
        "sql": "ROUND(SUM(absolute_error) / NULLIF(SUM(ABS(units_sold)), 0) * 100, 2)",
        "type": "DOUBLE",
        "view": "vw_forecast_metrics",
        "description": "Weighted Mean Absolute Percentage Error (%)",
    },
    "bias_pct": {
        "sql": "ROUND((SUM(demand_forecast) - SUM(units_sold)) / NULLIF(SUM(ABS(units_sold)), 0) * 100, 2)",
        "type": "DOUBLE",
        "view": "vw_forecast_metrics",
        "description": "Forecast bias %% (+ = over-forecast, - = under-forecast)",
    },
    "forecast_accuracy": {
        "sql": "ROUND(100 - SUM(absolute_error) / NULLIF(SUM(ABS(units_sold)), 0) * 100, 2)",
        "type": "DOUBLE",
        "view": "vw_forecast_metrics",
        "description": "Forecast accuracy (100 - WMAPE)",
    },
    "absolute_error": {
        "sql": "SUM(absolute_error)",
        "type": "DOUBLE",
        "view": "vw_forecast_metrics",
        "description": "Total absolute forecast error",
    },
    "inventory_level": {
        "sql": "AVG(inventory_level)",
        "type": "DOUBLE",
        "view": "vw_forecast_metrics",
        "description": "Average inventory level",
    },
    "stockout_days": {
        "sql": "SUM(CASE WHEN stockout_flag = 1 THEN 1 ELSE 0 END)",
        "type": "INT",
        "view": "vw_forecast_metrics",
        "description": "Total stockout days",
    },
    "n_obs": {
        "sql": "COUNT(*)",
        "type": "INT",
        "view": "vw_forecast_metrics",
        "description": "Number of observations",
    },
    "avg_price": {
        "sql": "ROUND(AVG(price), 2)",
        "type": "DOUBLE",
        "view": "vw_forecast_metrics",
        "description": "Average price",
    },
    "avg_discount": {
        "sql": "ROUND(AVG(discount), 2)",
        "type": "DOUBLE",
        "view": "vw_forecast_metrics",
        "description": "Average discount percentage",
    },
    "promotion_days": {
        "sql": "SUM(CASE WHEN holiday_promotion > 0 THEN 1 ELSE 0 END)",
        "type": "INT",
        "view": "vw_forecast_metrics",
        "description": "Number of promotion days",
    },
}

# ============================================================
#  Governed Dimension Registry
#  Maps business dimension names → approved column names.
# ============================================================

DIMENSION_REGISTRY: Dict[str, str] = {
    "SKU": "product_id",
    "REGION": "region",
    "CATEGORY": "category",
    "DATE": "date",
    "STORE": "store_id",
    "SEASONALITY": "seasonality",
    "WEATHER": "weather_condition",
    "INVENTORY_STATUS": "inventory_status",
}

# ============================================================
#  Grain → GROUP BY column mapping
# ============================================================

GRAIN_MAP: Dict[str, List[str]] = {
    "SKU": ["product_id"],
    "REGION": ["region"],
    "CATEGORY": ["category"],
    "SKU_REGION": ["product_id", "region"],
    "SKU_CATEGORY": ["product_id", "category"],
    "REGION_CATEGORY": ["region", "category"],
    "DATE": ["date"],
    "SKU_DATE": ["product_id", "date"],
    "ALL": [],
}

# ============================================================
#  View Registry — maps logical view name → fully qualified table
# ============================================================

VIEW_REGISTRY: Dict[str, str] = {
    "vw_forecast_metrics": VW_FORECAST_METRICS,
    "vw_inventory_health": VW_INVENTORY_HEALTH,
    "vw_revenue_metrics": VW_REVENUE_METRICS,
    "vw_forecast_history": VW_FORECAST_HISTORY,
    "vw_forecast_rca_features": VW_RCA_FEATURES,
}

# Allowed filter operators (whitelist for SQL generation)
_ALLOWED_OPERATORS = {
    "=",
    "!=",
    ">",
    "<",
    ">=",
    "<=",
    "IN",
    "NOT_IN",
    "IS_NULL",
    "IS_NOT_NULL",
}

# Allowed sort directions
_ALLOWED_DIRECTIONS = {"ASC", "DESC"}

# Max limit to prevent runaway queries
_MAX_LIMIT = 100


# ============================================================
#  Plan Validator
# ============================================================


class PlanValidator:
    """
    Validates an analytical plan against the governed registries.

    Rejects unsupported metrics, dimensions, grains, operators, or thresholds.
    Never silently approximates — returns a descriptive error dict.
    """

    @staticmethod
    def validate(plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a raw plan dict (from the LLM).
        Returns {"valid": True} or {"valid": False, "errors": [...]}.
        """
        errors: List[str] = []

        if plan_data.get("analysis_type") not in (
            "FORECAST_PERFORMANCE",
            "REVENUE_ANALYSIS",
            "INVENTORY_ANALYSIS",
            "PATTERN_ANALYSIS",
        ):
            errors.append("Unsupported analysis_type.")
        lookback = plan_data.get("lookback_weeks", 12)
        if (
            not isinstance(lookback, int)
            or isinstance(lookback, bool)
            or not 1 <= lookback <= 104
        ):
            errors.append("lookback_weeks must be 1..104.")
        if any(
            m in ("inventory_level", "stockout_days")
            for m in plan_data.get("metrics", [])
        ):
            errors.append(
                "Use get_inventory_context: balances are point-in-time snapshots, not averages or stockout days."
            )
        if plan_data.get("rank_by") and plan_data["rank_by"] not in plan_data.get(
            "metrics", []
        ):
            errors.append("rank_by must be a selected metric.")
        if plan_data.get("cumulative_share") and plan_data["cumulative_share"].get(
            "metric"
        ) not in plan_data.get("metrics", []):
            errors.append("Cumulative-share metric must be selected.")
        for condition in plan_data.get("filters", []):
            value = condition.get("value")
            op = condition.get("operator", "").upper()
            if op in ("IN", "NOT_IN") and (
                not isinstance(value, list) or not 1 <= len(value) <= 100
            ):
                errors.append("IN filters require 1..100 scalar values.")
            if op not in ("IS_NULL", "IS_NOT_NULL") and value is None:
                errors.append("Non-null filter value required.")

        # --- Grain ---
        grain = plan_data.get("grain", "")
        if grain not in GRAIN_MAP:
            errors.append(
                f"Unsupported grain '{grain}'. "
                f"Allowed: {', '.join(sorted(GRAIN_MAP.keys()))}"
            )

        # --- Metrics ---
        metrics = plan_data.get("metrics", [])
        if not metrics:
            errors.append("At least one metric is required.")
        for m in metrics:
            if m not in METRIC_REGISTRY:
                errors.append(
                    f"Unsupported metric '{m}'. "
                    f"Allowed: {', '.join(sorted(METRIC_REGISTRY.keys()))}"
                )

        # --- Filters ---
        for f in plan_data.get("filters", []):
            field = f.get("field", "")
            if field not in DIMENSION_REGISTRY:
                errors.append(
                    f"Unsupported filter field '{field}'. "
                    f"Allowed: {', '.join(sorted(DIMENSION_REGISTRY.keys()))}"
                )
            op = f.get("operator", "").upper()
            if op not in _ALLOWED_OPERATORS:
                errors.append(
                    f"Unsupported operator '{op}'. "
                    f"Allowed: {', '.join(sorted(_ALLOWED_OPERATORS))}"
                )

        # --- Cumulative share ---
        cum = plan_data.get("cumulative_share")
        if cum:
            cum_metric = cum.get("metric", "")
            if cum_metric not in METRIC_REGISTRY:
                errors.append(
                    f"Cumulative share metric '{cum_metric}' is not registered."
                )
            threshold = cum.get("threshold", 0)
            if not (0 < threshold <= 1.0):
                errors.append(
                    f"Cumulative share threshold must be between 0 and 1.0, got {threshold}."
                )
            cum_dir = cum.get("direction", "DESC").upper()
            if cum_dir not in _ALLOWED_DIRECTIONS:
                errors.append(
                    f"Cumulative share direction must be ASC or DESC, got '{cum_dir}'."
                )
        # --- Rank by ---
        rank_by = plan_data.get("rank_by")
        if rank_by and rank_by not in METRIC_REGISTRY:
            errors.append(
                f"Rank metric '{rank_by}' is not registered. "
                f"Allowed: {', '.join(sorted(METRIC_REGISTRY.keys()))}"
            )
        rank_dir = plan_data.get("rank_direction", "DESC").upper()
        if rank_dir not in _ALLOWED_DIRECTIONS:
            errors.append(f"rank_direction must be ASC or DESC, got '{rank_dir}'.")

        # --- Limit ---
        limit = plan_data.get("limit")
        if limit is not None:
            if not isinstance(limit, int) or limit < 1 or limit > _MAX_LIMIT:
                errors.append(
                    f"limit must be an integer between 1 and {_MAX_LIMIT}, got {limit}."
                )

        # --- Cross-metric view consistency ---
        if not errors and metrics:
            views = {
                METRIC_REGISTRY[m]["view"] for m in metrics if m in METRIC_REGISTRY
            }
            if len(views) > 1:
                errors.append(
                    f"Metrics span multiple views ({views}). "
                    "All metrics must come from the same governed view."
                )
            if cum and cum_metric in METRIC_REGISTRY:
                cum_view = METRIC_REGISTRY[cum_metric]["view"]
                if cum_view not in views:
                    errors.append(
                        f"Cumulative share metric '{cum_metric}' uses view '{cum_view}' "
                        f"which differs from the metrics' view."
                    )

        if errors:
            return {"valid": False, "errors": errors}
        return {"valid": True}


# ============================================================
#  Analytical Query Compiler
# ============================================================


class BoundSQL(str):
    """A SQL string plus separately bound values; never expose either to the model."""

    def __new__(cls, sql, parameters):
        obj = str.__new__(cls, sql)
        obj.parameters = parameters
        return obj


class AnalyticalQueryCompiler:
    """
    Converts a validated AnalyticalPlan into parameterized SQL.

    The generated SQL uses CTEs for cumulative-share filtering and always
    queries against governed views (never raw tables, never LLM-controlled SQL).
    """

    @staticmethod
    def compile(plan_data: Dict[str, Any], date_start: str, date_end: str) -> str:
        """
        Compile a validated plan dict to a SQL string.

        Args:
            plan_data: Validated analytical plan.
            date_start: ISO date string for the period start.
            date_end: ISO date string for the period end.

        Returns:
            A complete SQL string ready for spark.sql().
        """
        check = PlanValidator.validate(plan_data)
        if not check["valid"]:
            raise ValueError("; ".join(check["errors"]))
        # Dates and values are bound even when the caller bypasses the tool layer.
        date.fromisoformat(date_start)
        date.fromisoformat(date_end)
        parameters = {"date_start": date_start, "date_end": date_end}
        grain = plan_data.get("grain", "ALL")
        group_cols = GRAIN_MAP.get(grain, [])
        metrics = plan_data.get("metrics", [])
        filters = plan_data.get("filters", [])
        cum = plan_data.get("cumulative_share")
        rank_by = plan_data.get("rank_by")
        rank_dir = plan_data.get("rank_direction", "DESC").upper()
        limit = plan_data.get("limit") or _MAX_LIMIT

        # Determine the governed view from the first metric
        view_name = METRIC_REGISTRY[metrics[0]]["view"]
        view_fq = VIEW_REGISTRY[view_name]

        # --- Build dimension columns for SELECT and GROUP BY ---
        dim_select = ", ".join(group_cols) if group_cols else ""

        # --- Build metric expressions ---
        metric_selects = []
        for m in metrics:
            expr = METRIC_REGISTRY[m]["sql"]
            metric_selects.append(f"{expr} AS {m}")

        # --- Build SELECT clause for inner aggregation ---
        select_parts = []
        if dim_select:
            select_parts.append(dim_select)
        select_parts.extend(metric_selects)
        inner_select = ", ".join(select_parts)

        # --- Build GROUP BY ---
        group_by = ", ".join(group_cols) if group_cols else ""

        # --- Build WHERE clause ---
        where_parts = ["date >= :date_start", "date <= :date_end"]
        for index, f in enumerate(filters):
            column = DIMENSION_REGISTRY[f["field"]]
            operator = f["operator"].upper()
            value = f.get("value")
            key = f"filter_{index}"
            if operator in ("IS_NULL", "IS_NOT_NULL"):
                where_parts.append(
                    f"{column} {'IS NULL' if operator == 'IS_NULL' else 'IS NOT NULL'}"
                )
            elif operator in ("IN", "NOT_IN"):
                values = value if isinstance(value, list) else [value]
                markers = []
                for position, item in enumerate(values):
                    name = f"{key}_{position}"
                    markers.append(":" + name)
                    parameters[name] = item
                sql_operator = "NOT IN" if operator == "NOT_IN" else "IN"
                where_parts.append(f"{column} {sql_operator} ({', '.join(markers)})")
            else:
                parameters[key] = value
                where_parts.append(f"{column} {operator} :{key}")

        where_clause = " AND ".join(where_parts)

        # --- Build the inner aggregation CTE ---
        inner_sql = (
            f"SELECT {inner_select}\n"
            f"            FROM {view_fq}\n"
            f"            WHERE {where_clause}"
        )
        if group_by:
            inner_sql += f"\n            GROUP BY {group_by}"

        # --- Build cumulative share CTE if specified ---
        if cum:
            cum_metric = cum["metric"]
            cum_threshold = cum["threshold"]
            cum_dir = cum.get("direction", "DESC").upper()

            full_sql = (
                f"WITH aggregated AS (\n"
                f"            {inner_sql}\n"
                f"            ),\n"
                f"            cumulative AS (\n"
                f"                SELECT *,\n"
                f"                    SUM({cum_metric}) OVER (ORDER BY {cum_metric} {cum_dir}) AS _cum_sum,\n"
                f"                    SUM({cum_metric}) OVER () AS _total_sum\n"
                f"                FROM aggregated\n"
                f"            )\n"
                f"            SELECT {', '.join(group_cols + metrics)},\n"
                f"                   ROUND(_cum_sum / NULLIF(_total_sum, 0), 4) AS cumulative_share\n"
                f"            FROM cumulative\n"
                f"            WHERE (_cum_sum - {cum_metric}) / NULLIF(_total_sum, 0) < {cum_threshold}\n"
            )
        else:
            # No cumulative share — simple aggregate
            select_outer = (
                ", ".join((group_cols + metrics)) if group_cols else ", ".join(metrics)
            )
            full_sql = (
                f"WITH aggregated AS (\n"
                f"            {inner_sql}\n"
                f"            )\n"
                f"            SELECT {select_outer}\n"
                f"            FROM aggregated\n"
            )

        # --- ORDER BY ---
        if rank_by:
            full_sql += f"            ORDER BY {rank_by} {rank_dir}\n"

        # --- LIMIT ---
        if limit:
            full_sql += f"            LIMIT {limit}\n"

        return BoundSQL(full_sql, parameters)


# ============================================================
#  Analytical Query Service
# ============================================================


class AnalyticalQueryService:
    """
    Orchestrates: validate → compile → execute → return structured evidence.

    This is the single entry point for the run_analytical_query tool.
    """

    def execute(self, plan_data: Dict[str, Any], principal=None) -> Dict[str, Any]:
        """
        Execute an analytical plan.

        Args:
            plan_data: Raw analytical plan dict from the LLM.

        Returns:
            Structured evidence dict with rows, metrics, provenance.
        """
        # This utility is not an extra model tool. An authenticated development
        # caller must supply grants; shared SQL credentials never imply user access.
        if principal is None:
            raise PermissionError(
                "A trusted principal is required for analytical queries."
            )
        import copy

        plan_data = copy.deepcopy(plan_data)
        for field, grants in [
            ("SKU", principal.products),
            ("REGION", principal.regions),
            ("CATEGORY", principal.categories),
        ]:
            if not grants:
                raise PermissionError(
                    "Empty business entitlements deny analytical queries."
                )
            if "*" not in grants:
                plan_data.setdefault("filters", []).append(
                    {"field": field, "operator": "IN", "value": list(grants)}
                )
        # 1. Validate
        result = PlanValidator.validate(plan_data)
        if not result["valid"]:
            return {
                "success": False,
                "error": "Analytical plan validation failed.",
                "validation_errors": result["errors"],
            }

        # 2. Determine date range
        spark = _get_spark()
        lookback_weeks = plan_data.get("lookback_weeks", 12)
        from pyspark.sql import functions as F

        scoped = spark.table(FACT_TABLE)
        for column, grants in [
            ("product_id", principal.products),
            ("region", principal.regions),
            ("category", principal.categories),
        ]:
            if "*" not in grants:
                scoped = scoped.where(F.col(column).isin(list(grants)))
        max_row = scoped.select(F.max(F.to_date("date")).alias("max_d")).collect()
        max_date = (
            max_row[0]["max_d"] if max_row and max_row[0]["max_d"] else date.today()
        )
        start_date = max_date - timedelta(weeks=lookback_weeks)
        date_start = start_date.isoformat()
        date_end = max_date.isoformat()

        # 3. Compile to SQL
        try:
            sql = AnalyticalQueryCompiler.compile(plan_data, date_start, date_end)
            logger.info("Compiled analytical SQL:\n%s", sql)
        except Exception as exc:
            logger.exception("Query compilation failed")
            return {"success": False, "error": f"Query compilation failed: {exc}"}

        # 4. Execute
        try:
            from data_access import SparkQuery

            rows_raw = SparkQuery(spark).query(str(sql), sql.parameters)
        except Exception as exc:
            logger.exception("Query execution failed")
            return {"success": False, "error": f"Query execution failed: {exc}"}

        # 5. Build structured result (Spark Connect-safe: use row["key"] not row.get())
        grain = plan_data.get("grain", "ALL")
        group_cols = GRAIN_MAP.get(grain, [])
        metrics = plan_data.get("metrics", [])
        all_cols = group_cols + metrics
        if plan_data.get("cumulative_share"):
            all_cols.append("cumulative_share")

        rows = []
        for r in rows_raw:
            row_dict = {}
            for c in all_cols:
                row_dict[c] = r.get(c)
            rows.append(row_dict)

        # 6. Determine source view
        view_name = METRIC_REGISTRY[metrics[0]]["view"] if metrics else "unknown"

        return {
            "success": True,
            "analysis_type": plan_data.get("analysis_type", ""),
            "grain": grain,
            "metrics": metrics,
            "filters_applied": plan_data.get("filters", []),
            "cumulative_share": plan_data.get("cumulative_share"),
            "rank_by": plan_data.get("rank_by"),
            "rank_direction": plan_data.get("rank_direction", "DESC"),
            "limit": plan_data.get("limit"),
            "count": len(rows),
            "rows": rows,
            "source_view": view_name,
            "period": {
                "start": date_start,
                "end": date_end,
                "lookback_weeks": lookback_weeks,
            },
            "data_as_of": date_end,
        }


# ============================================================
#  Module-level singleton
# ============================================================
analytical_service = AnalyticalQueryService()


# ============================================================
#  Spark session helper (mirrors forecast_rca_service.py)
# ============================================================
_spark: Optional[SparkSession] = None


def _get_spark() -> SparkSession:
    from pyspark.sql import SparkSession

    global _spark
    if _spark is None:
        _spark = SparkSession.builder.getOrCreate()
    return _spark
