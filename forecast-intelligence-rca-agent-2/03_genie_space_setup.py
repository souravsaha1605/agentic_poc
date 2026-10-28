# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
"""Publish and validate the single table exposed to the Forecast RCA Genie Space.

Run this notebook only after ``01_data_initialization.ipynb`` succeeds. It does
not invoke Genie, an LLM, or any paid model API. The only write is a replaceable
view in the isolated lab schema.
"""

import os
from genie_semantic import publish_genie_view
from state import checked_table

DATABASE = checked_table(
    os.getenv("FORECAST_DATABASE", "workspace.forecast_rca_lab")
)
if not DATABASE.endswith("_lab"):
    raise ValueError("Genie pilot setup is restricted to an isolated *_lab schema.")

required = [
    "fact_sales_forecast",
    "rca_readiness_registry",
    "rca_source_manifest",
    "vw_forecast_metrics",
]
missing = [
    name for name in required if not spark.catalog.tableExists(f"{DATABASE}.{name}")
]
if missing:
    raise ValueError(
        "Run 01_data_initialization.ipynb first; missing: " + ", ".join(missing)
    )

# COMMAND ----------

manifest_rows = (
    spark.table(f"{DATABASE}.rca_source_manifest")
    .orderBy("published_at", ascending=False)
    .limit(1)
    .collect()
)
if len(manifest_rows) != 1:
    raise ValueError("Exactly one current certified source manifest is required.")

current = manifest_rows[0]
failed = (
    spark.table(f"{DATABASE}.rca_readiness_registry")
    .where(f"source_version = '{current.source_version}'")
    .where("validation = 'FAIL' OR status = 'BLOCKED'")
    .count()
)
if failed:
    raise ValueError("Genie view publication blocked by failed readiness records.")

delta_version = spark.sql(
    f"DESCRIBE HISTORY {DATABASE}.fact_sales_forecast LIMIT 1"
).first()["version"]
if int(delta_version) != int(current.delta_version):
    raise ValueError(
        "Fact data changed after certification; rerun initialization before Genie setup."
    )

# COMMAND ----------

# Re-publishing is idempotent. One semantic view prevents Genie from joining
# five application views with the same grain and multiplying measures.
view_name = publish_genie_view(spark, DATABASE)

# COMMAND ----------

view = spark.table(view_name)
row_count = view.count()
if row_count == 0:
    raise ValueError("The certified Genie view is empty.")

duplicate_vintages = (
    view.groupBy(
        "product_id", "store_id", "region", "target_date", "forecast_generated_date"
    )
    .count()
    .where("count > 1")
    .count()
)
if duplicate_vintages:
    raise ValueError("Duplicate forecast-vintage grains block Genie publication.")

print("Genie source is ready:", view_name)
print("Certified source version:", current.source_version)
print("Delta version:", current.delta_version)
print("Rows:", row_count)
print("Next: create a Genie Space and paste genie/SPACE_INSTRUCTIONS.md into its instructions.")
