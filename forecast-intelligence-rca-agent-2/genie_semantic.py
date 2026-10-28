"""Certified semantic view used by the direct Databricks Genie experience.

The Teams application continues to use the governed provider and its existing
views. Keeping this view separate lets Genie see one unambiguous source grain
without changing or disabling the Teams delivery path.
"""

from state import checked_table


GENIE_VIEW = "vw_genie_forecast_observations"
COMMERCIAL_GENIE_VIEWS = (
    "vw_genie_entity_lookup",
    "vw_genie_sku_forecast",
    "vw_genie_customer_forecast",
    "vw_genie_sku_budget",
    "vw_genie_sku_price",
    "vw_genie_sku_promotion",
    "vw_genie_sku_monthly_performance",
    "vw_genie_customer_sku_monthly_performance",
    "vw_genie_sku_monthly_plan_vs_actual",
)


def publish_genie_view(spark, database):
    """Create the read-only Genie view after source certification succeeds."""
    database = checked_table(database)
    spark.sql(
        f"""
        CREATE OR REPLACE VIEW {database}.{GENIE_VIEW} AS
        SELECT
          product_id,
          region,
          category,
          store_id,
          CAST(target_date AS DATE) AS target_date,
          CAST(forecast_generated_date AS DATE) AS forecast_generated_date,
          forecast_horizon_days,
          units_sold,
          demand_forecast,
          forecast_error,
          absolute_error,
          inventory_level,
          CAST(inventory_timestamp AS TIMESTAMP) AS inventory_timestamp,
          price,
          discount,
          discount_unit,
          currency,
          unit_of_measure,
          gross_revenue,
          net_revenue,
          stockout_flag,
          holiday_promotion,
          weather_condition,
          weather_observed_at,
          competitor_pricing,
          seasonality,
          launch_date,
          lifecycle_stage,
          channel,
          fiscal_period,
          fiscal_calendar_policy,
          scenario,
          dataset_version
        FROM {database}.vw_forecast_metrics
        """
    )
    return f"{database}.{GENIE_VIEW}"


def publish_commercial_genie_views(spark, database):
    """Publish separate-grain commercial demo views for direct Genie use."""
    database = checked_table(database)
    statements = {
        "vw_genie_entity_lookup": f"""
            CREATE OR REPLACE VIEW {database}.vw_genie_entity_lookup AS
            SELECT sku_id AS entity_id, sku_name AS entity_name, 'SKU' AS entity_type,
                   region, country, active, dataset_version
            FROM {database}.dim_sku
            UNION ALL
            SELECT customer_id, customer_name, 'CUSTOMER', region, country, active,
                   dataset_version
            FROM {database}.dim_customer
        """,
        "vw_genie_sku_forecast": f"""
            CREATE OR REPLACE VIEW {database}.vw_genie_sku_forecast AS
            SELECT f.region, f.country, f.sku_id, s.sku_name, s.category,
                   CAST(f.target_date AS DATE) AS target_date,
                   CAST(f.forecast_generated_date AS DATE) AS forecast_generated_date,
                   f.forecast_horizon_days, f.actual_quantity, f.forecast_quantity,
                   f.forecast_quantity-f.actual_quantity AS forecast_error,
                   ABS(f.forecast_quantity-f.actual_quantity) AS absolute_error,
                   f.unit_of_measure, f.dataset_version
            FROM {database}.fact_sku_forecast f
            JOIN {database}.dim_sku s ON s.sku_id=f.sku_id
        """,
        "vw_genie_customer_forecast": f"""
            CREATE OR REPLACE VIEW {database}.vw_genie_customer_forecast AS
            SELECT f.region, f.country, f.customer_id, c.customer_name,
                   c.customer_segment, f.sku_id, s.sku_name, s.category,
                   CAST(f.target_date AS DATE) AS target_date,
                   CAST(f.forecast_generated_date AS DATE) AS forecast_generated_date,
                   f.forecast_horizon_days, f.actual_quantity, f.forecast_quantity,
                   f.forecast_quantity-f.actual_quantity AS forecast_error,
                   ABS(f.forecast_quantity-f.actual_quantity) AS absolute_error,
                   f.unit_of_measure, f.dataset_version
            FROM {database}.fact_customer_forecast f
            JOIN {database}.dim_customer c ON c.customer_id=f.customer_id
            JOIN {database}.dim_sku s ON s.sku_id=f.sku_id
        """,
        "vw_genie_sku_budget": f"""
            CREATE OR REPLACE VIEW {database}.vw_genie_sku_budget AS
            SELECT b.region, b.country, b.sku_id, s.sku_name, s.category,
                   b.fiscal_period, b.budget_version, b.budget_quantity,
                   b.budget_revenue, b.currency, b.status,
                   CAST(b.approved_at AS TIMESTAMP) AS approved_at,
                   b.dataset_version
            FROM {database}.fact_sku_budget b
            JOIN {database}.dim_sku s ON s.sku_id=b.sku_id
        """,
        "vw_genie_sku_price": f"""
            CREATE OR REPLACE VIEW {database}.vw_genie_sku_price AS
            SELECT s.region, p.country, p.sku_id, s.sku_name, s.category,
                   p.price_type, p.price, p.currency, p.unit_of_measure,
                   CAST(p.effective_from AS DATE) AS effective_from,
                   CAST(p.effective_to AS DATE) AS effective_to,
                   p.dataset_version
            FROM {database}.fact_sku_price p
            JOIN {database}.dim_sku s ON s.sku_id=p.sku_id
        """,
        "vw_genie_sku_promotion": f"""
            CREATE OR REPLACE VIEW {database}.vw_genie_sku_promotion AS
            SELECT p.region, p.country, p.sku_id, s.sku_name, s.category,
                   p.promotion_id, p.promotion_type,
                   CAST(p.start_date AS DATE) AS start_date,
                   CAST(p.end_date AS DATE) AS end_date,
                   p.discount_value, p.discount_unit, p.status,
                   p.dataset_version
            FROM {database}.fact_sku_promotion p
            JOIN {database}.dim_sku s ON s.sku_id=p.sku_id
        """,
        "vw_genie_sku_monthly_performance": f"""
            CREATE OR REPLACE VIEW {database}.vw_genie_sku_monthly_performance AS
            WITH ranked AS (
              SELECT f.*,
                     ROW_NUMBER() OVER (
                       PARTITION BY region, country, sku_id, target_date
                       ORDER BY forecast_generated_date DESC
                     ) AS vintage_rank
              FROM {database}.fact_sku_forecast f
            ), selected AS (
              SELECT * FROM ranked WHERE vintage_rank=1
            )
            SELECT f.region, f.country, f.sku_id, s.sku_name, s.category,
                   c.fiscal_period,
                   CAST(c.period_start AS DATE) AS period_start,
                   CAST(c.period_end AS DATE) AS period_end,
                   'LATEST_PER_TARGET' AS forecast_vintage_policy,
                   COUNT(*) AS observation_count,
                   MIN(CAST(f.target_date AS DATE)) AS first_observation_date,
                   MAX(CAST(f.target_date AS DATE)) AS last_observation_date,
                   SUM(f.actual_quantity) AS actual_quantity,
                   SUM(f.forecast_quantity) AS forecast_quantity,
                   SUM(ABS(f.forecast_quantity-f.actual_quantity)) AS absolute_error,
                   SUM(f.forecast_quantity-f.actual_quantity) AS signed_error,
                   CASE WHEN SUM(ABS(f.actual_quantity))=0 THEN NULL ELSE
                     100.0*SUM(ABS(f.forecast_quantity-f.actual_quantity)) /
                     SUM(ABS(f.actual_quantity)) END AS wmape_pct,
                   CASE WHEN SUM(ABS(f.actual_quantity))=0 THEN NULL ELSE
                     100.0-100.0*SUM(ABS(f.forecast_quantity-f.actual_quantity)) /
                     SUM(ABS(f.actual_quantity)) END AS accuracy_pct,
                   CASE WHEN SUM(ABS(f.actual_quantity))=0 THEN NULL ELSE
                     100.0*SUM(f.forecast_quantity-f.actual_quantity) /
                     SUM(ABS(f.actual_quantity)) END AS bias_pct,
                   f.unit_of_measure, f.dataset_version
            FROM selected f
            JOIN {database}.dim_sku s ON s.sku_id=f.sku_id
            JOIN {database}.dim_fiscal_period c
              ON c.country=f.country
             AND CAST(f.target_date AS DATE) BETWEEN
                 CAST(c.period_start AS DATE) AND CAST(c.period_end AS DATE)
            GROUP BY f.region, f.country, f.sku_id, s.sku_name, s.category,
                     c.fiscal_period, c.period_start, c.period_end,
                     f.unit_of_measure, f.dataset_version
        """,
        "vw_genie_customer_sku_monthly_performance": f"""
            CREATE OR REPLACE VIEW {database}.vw_genie_customer_sku_monthly_performance AS
            WITH ranked AS (
              SELECT f.*,
                     ROW_NUMBER() OVER (
                       PARTITION BY region, country, customer_id, sku_id, target_date
                       ORDER BY forecast_generated_date DESC
                     ) AS vintage_rank
              FROM {database}.fact_customer_forecast f
            ), selected AS (
              SELECT * FROM ranked WHERE vintage_rank=1
            )
            SELECT f.region, f.country, f.customer_id, d.customer_name,
                   d.customer_segment, f.sku_id, s.sku_name, s.category,
                   c.fiscal_period,
                   CAST(c.period_start AS DATE) AS period_start,
                   CAST(c.period_end AS DATE) AS period_end,
                   'LATEST_PER_TARGET' AS forecast_vintage_policy,
                   COUNT(*) AS observation_count,
                   MIN(CAST(f.target_date AS DATE)) AS first_observation_date,
                   MAX(CAST(f.target_date AS DATE)) AS last_observation_date,
                   SUM(f.actual_quantity) AS actual_quantity,
                   SUM(f.forecast_quantity) AS forecast_quantity,
                   SUM(ABS(f.forecast_quantity-f.actual_quantity)) AS absolute_error,
                   SUM(f.forecast_quantity-f.actual_quantity) AS signed_error,
                   CASE WHEN SUM(ABS(f.actual_quantity))=0 THEN NULL ELSE
                     100.0*SUM(ABS(f.forecast_quantity-f.actual_quantity)) /
                     SUM(ABS(f.actual_quantity)) END AS wmape_pct,
                   CASE WHEN SUM(ABS(f.actual_quantity))=0 THEN NULL ELSE
                     100.0-100.0*SUM(ABS(f.forecast_quantity-f.actual_quantity)) /
                     SUM(ABS(f.actual_quantity)) END AS accuracy_pct,
                   CASE WHEN SUM(ABS(f.actual_quantity))=0 THEN NULL ELSE
                     100.0*SUM(f.forecast_quantity-f.actual_quantity) /
                     SUM(ABS(f.actual_quantity)) END AS bias_pct,
                   f.unit_of_measure, f.dataset_version
            FROM selected f
            JOIN {database}.dim_customer d ON d.customer_id=f.customer_id
            JOIN {database}.dim_sku s ON s.sku_id=f.sku_id
            JOIN {database}.dim_fiscal_period c
              ON c.country=f.country
             AND CAST(f.target_date AS DATE) BETWEEN
                 CAST(c.period_start AS DATE) AND CAST(c.period_end AS DATE)
            GROUP BY f.region, f.country, f.customer_id, d.customer_name,
                     d.customer_segment, f.sku_id, s.sku_name, s.category,
                     c.fiscal_period, c.period_start, c.period_end,
                     f.unit_of_measure, f.dataset_version
        """,
        "vw_genie_sku_monthly_plan_vs_actual": f"""
            CREATE OR REPLACE VIEW {database}.vw_genie_sku_monthly_plan_vs_actual AS
            SELECT p.region, p.country, p.sku_id, p.sku_name, p.category,
                   p.fiscal_period, p.period_start, p.period_end,
                   p.forecast_vintage_policy, p.observation_count,
                   p.first_observation_date, p.last_observation_date,
                   p.actual_quantity, p.forecast_quantity,
                   b.budget_quantity, b.budget_revenue, b.currency,
                   b.budget_version, b.status AS budget_status,
                   p.forecast_quantity-p.actual_quantity AS forecast_vs_actual_quantity,
                   b.budget_quantity-p.actual_quantity AS budget_vs_actual_quantity,
                   p.forecast_quantity-b.budget_quantity AS forecast_vs_budget_quantity,
                   CASE WHEN p.actual_quantity=0 THEN NULL ELSE
                     100.0*(p.forecast_quantity-p.actual_quantity)/ABS(p.actual_quantity)
                   END AS forecast_vs_actual_pct,
                   CASE WHEN p.actual_quantity=0 THEN NULL ELSE
                     100.0*(b.budget_quantity-p.actual_quantity)/ABS(p.actual_quantity)
                   END AS budget_vs_actual_pct,
                   CASE WHEN b.budget_quantity=0 THEN NULL ELSE
                     100.0*(p.forecast_quantity-b.budget_quantity)/ABS(b.budget_quantity)
                   END AS forecast_vs_budget_pct,
                   p.wmape_pct, p.accuracy_pct, p.bias_pct,
                   p.unit_of_measure, p.dataset_version
            FROM {database}.vw_genie_sku_monthly_performance p
            JOIN {database}.fact_sku_budget b
              ON b.region=p.region AND b.country=p.country
             AND b.sku_id=p.sku_id AND b.fiscal_period=p.fiscal_period
             AND b.dataset_version=p.dataset_version
            WHERE b.status='APPROVED'
        """,
    }
    for view in COMMERCIAL_GENIE_VIEWS:
        spark.sql(statements[view])
    return tuple(f"{database}.{view}" for view in COMMERCIAL_GENIE_VIEWS)

