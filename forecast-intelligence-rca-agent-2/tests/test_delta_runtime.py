"""Real Spark/Delta integration. Opt in with RUN_DELTA_TESTS=true and trusted jars.

The default suite does not download jars, start a JVM, or contact cloud services.
Databricks Runtime already supplies Delta. Local execution can supply verified
DELTA_TEST_JARS paths for its matching Spark/Delta release.
"""

import os
import tempfile
import unittest


@unittest.skipUnless(
    os.getenv("RUN_DELTA_TESTS") == "true", "Optional Spark/Delta runtime integration"
)
class DeltaRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from pyspark.sql import SparkSession

        cls.temp = tempfile.TemporaryDirectory()
        os.environ.setdefault("SPARK_LOCAL_IP", "127.0.0.1")
        builder = (
            SparkSession.builder.master("local[2]")
            .appName("rca-review-integration")
            .config("spark.ui.enabled", "false")
            .config("spark.sql.shuffle.partitions", "2")
            .config("spark.databricks.delta.snapshotPartitions", "2")
            .config("spark.sql.warehouse.dir", cls.temp.name + "/warehouse")
            .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
            .config(
                "spark.sql.catalog.spark_catalog",
                "org.apache.spark.sql.delta.catalog.DeltaCatalog",
            )
        )
        if os.getenv("DELTA_TEST_JARS"):
            builder = builder.config("spark.jars", os.environ["DELTA_TEST_JARS"])
        cls.spark = builder.getOrCreate()
        cls.spark.sparkContext.setLogLevel("ERROR")

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()
        cls.temp.cleanup()

    def test_initialize_rerun_state_budget_and_bound_queries(self):
        from bootstrap import initialize
        from contracts import Principal, AnalysisPlan
        from data_access import GovernedProvider, SparkQuery
        from business import BusinessService
        from state import DeltaStateStore, ConflictError
        from cost_control import DeltaCallBudget, BudgetExceeded

        db = "spark_catalog.forecast_review_lab"
        first = initialize(self.spark, db)
        count = self.spark.table(db + ".fact_sales_forecast").count()
        budget = DeltaCallBudget(self.spark, db + ".rca_paid_call_ledger", limit=1)
        self.assertEqual(budget.reserve(), 1)
        second = initialize(self.spark, db)
        self.assertEqual(first["source_version"], second["source_version"])
        self.assertEqual(count, self.spark.table(db + ".fact_sales_forecast").count())
        with self.assertRaises(BudgetExceeded):
            budget.reserve()
        provider = GovernedProvider(SparkQuery(self.spark), db)
        principal = Principal(
            tenant="lab",
            subject="alice",
            regions=("*",),
            products=("*",),
            categories=("*",),
        )
        result = BusinessService(provider).execute(
            AnalysisPlan(
                tool="get_forecast_context",
                product_id="P0001",
                region="North",
                category="Dairy",
            ),
            principal,
        )
        self.assertEqual(result["metrics"]["forecast"], 1200)
        self.assertEqual(result["metrics"]["actual"], 1350)
        store = DeltaStateStore(self.spark, db + ".rca_owned_sessions")
        document = store.load(principal.owner, "session")
        document["cases"]["case"] = {
            "versions": [{"version": 1, "evidence": {"forecast": 100}}]
        }
        store.commit(principal.owner, "session", 0, document)
        reloaded = DeltaStateStore(self.spark, db + ".rca_owned_sessions").load(
            principal.owner, "session"
        )
        self.assertEqual(
            reloaded["cases"]["case"]["versions"][0]["evidence"]["forecast"], 100
        )
        with self.assertRaises(PermissionError):
            store.load("another-owner", "session")
        with self.assertRaises(ConflictError):
            store.commit(principal.owner, "session", 0, document)
        # Readiness must become invalid if the actual Delta source changes.
        self.spark.sql(
            f"UPDATE {db}.fact_sales_forecast SET price=11 WHERE product_id='P0001'"
        )
        with self.assertRaises(ValueError):
            provider.fetch(
                AnalysisPlan(
                    tool="get_forecast_context",
                    product_id="P0001",
                    region="North",
                    category="Dairy",
                )
            )
