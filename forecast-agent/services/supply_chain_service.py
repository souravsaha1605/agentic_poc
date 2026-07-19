from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, col, desc

from models import (
    ForecastSummary,
    InventorySummary,
    BusinessContext
)


class SupplyChainService:

    def __init__(self):

        self.spark = SparkSession.getActiveSession()

        self.forecast_view = "workspace.forecast_db.vw_forecast_metrics"

        self.inventory_view = "workspace.forecast_db.vw_inventory_health"

    # ==========================================================
    # Forecast Summary
    # ==========================================================

    def get_forecast_summary(
        self,
        product_id: str,
        store_id: str = None
    ) -> ForecastSummary:

        df = self.spark.table(self.forecast_view)

        df = df.filter(
            col("product_id") == product_id
        )

        if store_id:
            df = df.filter(
                col("store_id") == store_id
            )

        result = (
            df.agg(
                avg("demand_forecast").alias("average_forecast"),
                avg("units_sold").alias("average_actual_sales"),
                avg("forecast_accuracy").alias("forecast_accuracy"),
                avg("forecast_bias").alias("forecast_bias")
            )
            .first()
        )

        return ForecastSummary(
            average_forecast=round(result["average_forecast"], 2),
            average_actual_sales=round(result["average_actual_sales"], 2),
            forecast_accuracy=round(result["forecast_accuracy"], 2),
            forecast_bias=round(result["forecast_bias"], 2)
        )

    # ==========================================================
    # Forecast Accuracy
    # ==========================================================

    def calculate_forecast_accuracy(
        self,
        product_id: str,
        store_id: str = None
    ):

        df = self.spark.table(self.forecast_view)

        df = df.filter(
            col("product_id") == product_id
        )

        if store_id:
            df = df.filter(
                col("store_id") == store_id
            )

        result = (
            df.agg(
                avg("forecast_accuracy").alias("forecast_accuracy")
            )
            .first()
        )

        return {
            "forecast_accuracy": round(
                result["forecast_accuracy"],
                2
            )
        }

    # ==========================================================
    # Forecast Bias
    # ==========================================================

    def calculate_forecast_bias(
        self,
        product_id: str,
        store_id: str = None
    ):

        df = self.spark.table(self.forecast_view)

        df = df.filter(
            col("product_id") == product_id
        )

        if store_id:
            df = df.filter(
                col("store_id") == store_id
            )

        result = (
            df.agg(
                avg("forecast_bias").alias("forecast_bias")
            )
            .first()
        )

        return {
            "forecast_bias": round(
                result["forecast_bias"],
                2
            )
        }

    # ==========================================================
    # Inventory Summary
    # ==========================================================

    def get_inventory_summary(
        self,
        product_id: str,
        store_id: str = None
    ) -> InventorySummary:

        df = self.spark.table(self.inventory_view)

        df = df.filter(
            col("product_id") == product_id
        )

        if store_id:
            df = df.filter(
                col("store_id") == store_id
            )

        result = (
            df.orderBy(
                desc("date")
            )
            .first()
        )

        return InventorySummary(
            inventory_level=float(result["inventory_level"]),
            inventory_status=result["inventory_status"]
        )

    # ==========================================================
    # Region Comparison
    # ==========================================================

    def compare_regions(
        self,
        region_1: str,
        region_2: str
    ):

        df = self.spark.table(self.forecast_view)

        result = (
            df.filter(
                col("region").isin(
                    region_1,
                    region_2
                )
            )
            .groupBy("region")
            .agg(
                avg("forecast_accuracy").alias("forecast_accuracy"),
                avg("forecast_bias").alias("forecast_bias"),
                avg("units_sold").alias("average_units_sold")
            )
            .orderBy("region")
        )

        return result.toPandas().to_dict(
            orient="records"
        )

    # ==========================================================
    # Trend Summary
    # ==========================================================

    def get_trend_summary(
        self,
        product_id: str,
        store_id: str = None
    ):

        df = self.spark.table(self.forecast_view)

        df = df.filter(
            col("product_id") == product_id
        )

        if store_id:
            df = df.filter(
                col("store_id") == store_id
            )

        data = (
            df.orderBy(desc("date"))
            .select("date", "units_sold", "demand_forecast")
            .limit(8)
            .toPandas()
        )

        return data.to_dict(
            orient="records"
        )

    # ==========================================================
    # Composite Business Context
    # ==========================================================

    def get_forecast_context(
        self,
        product_id: str,
        store_id: str = None
    ) -> BusinessContext:

        forecast = self.get_forecast_summary(
            product_id,
            store_id
        )

        inventory = self.get_inventory_summary(
            product_id,
            store_id
        )

        return BusinessContext(
            forecast=forecast,
            inventory=inventory
        )