# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
"""Create certified SKU/customer/budget demo tables and Genie views.

The notebook writes only to an isolated ``*_lab`` schema. Data is deterministic,
synthetic and explicitly labelled as such. It makes no model or paid API calls.
"""

import os

from commercial_lab import publish_commercial_lab
from genie_semantic import COMMERCIAL_GENIE_VIEWS, publish_commercial_genie_views
from state import checked_table


DATABASE = checked_table(
    os.getenv("FORECAST_DATABASE", "workspace.forecast_rca_lab")
)
if not DATABASE.endswith("_lab"):
    raise ValueError("Commercial Genie demo setup is restricted to a *_lab schema.")

# COMMAND ----------

report = publish_commercial_lab(spark, DATABASE)
if report["validation"] != "PASS":
    raise RuntimeError("Commercial lab certification did not pass.")

views = publish_commercial_genie_views(spark, DATABASE)

# COMMAND ----------

for view in views:
    if not spark.catalog.tableExists(view):
        raise RuntimeError(f"Required Genie view was not published: {view}")
    if spark.table(view).count() == 0:
        raise RuntimeError(f"Required Genie view is empty: {view}")

sku_duplicates = (
    spark.table(f"{DATABASE}.vw_genie_sku_forecast")
    .groupBy(
        "region", "country", "sku_id", "target_date", "forecast_generated_date"
    )
    .count()
    .where("count > 1")
    .count()
)
customer_duplicates = (
    spark.table(f"{DATABASE}.vw_genie_customer_forecast")
    .groupBy(
        "region",
        "country",
        "customer_id",
        "sku_id",
        "target_date",
        "forecast_generated_date",
    )
    .count()
    .where("count > 1")
    .count()
)
if sku_duplicates or customer_duplicates:
    raise RuntimeError("Duplicate forecast-vintage grains block Genie publication.")

# Fact-to-dimension enrichment must preserve every source row. A larger view
# would indicate a many-to-many join; a smaller view would indicate an orphan.
cardinality_pairs = (
    ("fact_sku_forecast", "vw_genie_sku_forecast"),
    ("fact_customer_forecast", "vw_genie_customer_forecast"),
    ("fact_sku_budget", "vw_genie_sku_budget"),
    ("fact_sku_price", "vw_genie_sku_price"),
    ("fact_sku_promotion", "vw_genie_sku_promotion"),
)
for fact, view in cardinality_pairs:
    fact_count = spark.table(f"{DATABASE}.{fact}").count()
    view_count = spark.table(f"{DATABASE}.{view}").count()
    if fact_count != view_count:
        raise RuntimeError(
            f"Join-cardinality certification failed for {view}: "
            f"fact rows={fact_count}, view rows={view_count}."
        )

semantic_grains = {
    "vw_genie_sku_monthly_performance": (
        "region", "country", "sku_id", "fiscal_period",
        "unit_of_measure", "dataset_version",
    ),
    "vw_genie_customer_sku_monthly_performance": (
        "region", "country", "customer_id", "sku_id", "fiscal_period",
        "unit_of_measure", "dataset_version",
    ),
    "vw_genie_sku_monthly_plan_vs_actual": (
        "region", "country", "sku_id", "fiscal_period", "budget_version",
        "unit_of_measure", "dataset_version",
    ),
}
for view, grain in semantic_grains.items():
    duplicates = (
        spark.table(f"{DATABASE}.{view}")
        .groupBy(*grain)
        .count()
        .where("count > 1")
        .count()
    )
    if duplicates:
        raise RuntimeError(f"Duplicate certified semantic grain in {view}.")

print("Commercial Genie demo is ready.")
print("Dataset version:", report["dataset_version"])
print("Source version:", report["source_version"])
for table, counts in report["tables"].items():
    print(table, counts)
print("Add these sources to the existing Genie Agent:")
for view in views:
    print(" -", view)

