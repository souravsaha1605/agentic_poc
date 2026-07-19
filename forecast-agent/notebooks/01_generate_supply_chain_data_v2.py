# Placeholder header for enterprise generator. See chat for architecture.
# This starter file should be extended incrementally.
from pyspark.sql.functions import col

import pandas as pd

# pdf = pd.read_csv("../data/retail_store_inventory.csv")
# df = spark.createDataFrame(pdf)

# df = (
#     df.select(
#         col("Date").alias("date"),
#         col("Store ID").alias("store_id"),
#         col("Product ID").alias("product_id"),
#         col("Category").alias("category"),
#         col("Region").alias("region"),
#         col("Inventory Level").alias("inventory_level"),
#         col("Units Sold").alias("units_sold"),
#         col("Units Ordered").alias("units_ordered"),
#         col("Demand Forecast").alias("demand_forecast"),
#         col("Price").alias("price"),
#         col("Discount").alias("discount"),
#         col("Weather Condition").alias("weather_condition"),
#         col("Holiday/Promotion").alias("holiday_promotion"),
#         col("Competitor Pricing").alias("competitor_pricing"),
#         col("Seasonality").alias("seasonality")
#     )
# )

# spark.sql("CREATE DATABASE IF NOT EXISTS forecast_db")

# (
#     df.write
#       .format("delta")
#       .mode("overwrite")
#       .saveAsTable("forecast_db.fact_sales_forecast")
# )


spark.sql("""
CREATE OR REPLACE VIEW forecast_db.vw_forecast_metrics AS
SELECT *,
ROUND(
    (1 - ABS(units_sold - demand_forecast) / NULLIF(units_sold, 0)) * 100,
    2
) AS forecast_accuracy,
ROUND(
    ((demand_forecast - units_sold) / NULLIF(units_sold, 0)) * 100,
    2
) AS forecast_bias
FROM forecast_db.fact_sales_forecast
""")

spark.sql("""
CREATE OR REPLACE VIEW forecast_db.vw_inventory_health AS
SELECT *,
CASE
    WHEN inventory_level < units_sold THEN 'Stockout Risk'
    WHEN inventory_level < units_sold * 1.5 THEN 'Low Inventory'
    ELSE 'Healthy'
END AS inventory_status
FROM forecast_db.fact_sales_forecast
""")