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
    }
    for view in COMMERCIAL_GENIE_VIEWS:
        spark.sql(statements[view])
    return tuple(f"{database}.{view}" for view in COMMERCIAL_GENIE_VIEWS)

