"""Certified semantic view used by the direct Databricks Genie experience.

The Teams application continues to use the governed provider and its existing
views. Keeping this view separate lets Genie see one unambiguous source grain
without changing or disabling the Teams delivery path.
"""

from state import checked_table


GENIE_VIEW = "vw_genie_forecast_observations"


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

