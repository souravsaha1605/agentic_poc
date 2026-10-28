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
        self.assertEqual(first["generated_rows"], first["rows"])
        count = self.spark.table(db + ".fact_sales_forecast").count()
        budget = DeltaCallBudget(self.spark, db + ".rca_paid_call_ledger", limit=1)
        self.assertEqual(budget.reserve(), 1)
        second = initialize(self.spark, db)
        self.assertEqual(second["generated_rows"], 0)
        self.assertTrue(second["source_unchanged"])
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
        category = BusinessService(provider).execute(
            AnalysisPlan(
                tool="get_forecast_context",
                product_id="*",
                region="North",
                category="Dairy",
            ),
            principal,
        )
        self.assertGreater(category["metrics"]["actual"], result["metrics"]["actual"])
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

    def test_missing_lab_rows_are_appended_without_overwriting_existing_grains(self):
        from bootstrap import initialize, _frame
        from lab import generate

        db = "spark_catalog.forecast_missing_lab"
        self.spark.sql(f"CREATE SCHEMA IF NOT EXISTS {db}")
        generated, _ = generate()
        existing = generated[:-7]
        # A matching business row is authoritative and must not be replaced by
        # the fixture value when other missing grains are added.
        existing[0] = {**existing[0], "price": 10.25}
        _frame(self.spark, existing).write.format("delta").mode(
            "errorifexists"
        ).saveAsTable(db + ".fact_sales_forecast")
        original = self.spark.table(db + ".fact_sales_forecast").count()
        first = initialize(self.spark, db)
        self.assertEqual(first["existing_rows"], original)
        self.assertEqual(first["generated_rows"], 7)
        self.assertEqual(
            self.spark.table(db + ".fact_sales_forecast").count(), len(generated)
        )
        preserved = self.spark.sql(
            f"SELECT price FROM {db}.fact_sales_forecast "
            f"WHERE product_id='{existing[0]['product_id']}' "
            f"AND store_id='{existing[0]['store_id']}' "
            f"AND date='{existing[0]['date']}'"
        ).first()["price"]
        self.assertEqual(preserved, 10.25)
        second = initialize(self.spark, db)
        self.assertEqual(second["generated_rows"], 0)
        self.assertEqual(second["source_version"], first["source_version"])

    def test_incompatible_schema_is_preserved_and_not_published(self):
        from pyspark.sql import functions as F
        from bootstrap import initialize, _frame
        from lab import generate

        db = "spark_catalog.forecast_bad_schema_lab"
        self.spark.sql(f"CREATE SCHEMA IF NOT EXISTS {db}")
        generated, _ = generate()
        incompatible = (
            _frame(self.spark, generated)
            .limit(0)
            .withColumn("product_id", F.col("seed").cast("bigint"))
        )
        incompatible.write.format("delta").mode("errorifexists").saveAsTable(
            db + ".fact_sales_forecast"
        )
        with self.assertRaisesRegex(ValueError, "incompatible types"):
            initialize(self.spark, db)
        self.assertEqual(self.spark.table(db + ".fact_sales_forecast").count(), 0)
        self.assertFalse(self.spark.catalog.tableExists(db + ".rca_readiness_registry"))
        self.assertFalse(self.spark.catalog.tableExists(db + ".rca_source_manifest"))

    def test_expected_signal_failure_blocks_rows_and_publication(self):
        from bootstrap import initialize, _frame
        from lab import generate

        db = "spark_catalog.forecast_bad_signal_lab"
        self.spark.sql(f"CREATE SCHEMA IF NOT EXISTS {db}")
        generated, _ = generate()
        broken = [dict(row) for row in generated]
        for row in broken:
            if row["product_id"] == "P0001":
                row["holiday_promotion"] = 0
                row["units_sold"] = 100.0
        _frame(self.spark, broken).write.format("delta").mode(
            "errorifexists"
        ).saveAsTable(db + ".fact_sales_forecast")
        before = self.spark.table(db + ".fact_sales_forecast").count()
        with self.assertRaisesRegex(RuntimeError, "expected-signal"):
            initialize(self.spark, db)
        self.assertEqual(self.spark.table(db + ".fact_sales_forecast").count(), before)
        self.assertFalse(self.spark.catalog.tableExists(db + ".rca_readiness_registry"))
        self.assertFalse(self.spark.catalog.tableExists(db + ".rca_source_manifest"))

    def test_rerun_recovers_interruption_after_source_append(self):
        from bootstrap import initialize, _frame
        from cost_control import DeltaCallBudget
        from lab import FIXTURE_GRAIN, generate

        db = "spark_catalog.forecast_recovery_lab"
        self.spark.sql(f"CREATE SCHEMA IF NOT EXISTS {db}")
        generated, _ = generate()
        existing = [dict(row) for row in generated[:-1]]
        existing[0]["price"] = 10.25
        _frame(self.spark, existing).write.format("delta").mode(
            "errorifexists"
        ).saveAsTable(db + ".fact_sales_forecast")

        # Create and spend from the same durable ledger initialization uses.
        self.spark.sql(
            f"CREATE TABLE {db}.rca_paid_call_ledger "
            "(id INT, used BIGINT, token STRING) USING DELTA"
        )
        self.spark.sql(f"INSERT INTO {db}.rca_paid_call_ledger VALUES (1,2,'existing')")
        budget = DeltaCallBudget(self.spark, db + ".rca_paid_call_ledger", limit=5)

        def interrupt():
            raise RuntimeError("simulated interruption after source append")

        with self.assertRaisesRegex(RuntimeError, "simulated interruption"):
            initialize(self.spark, db, _after_source_write=interrupt)
        self.assertEqual(
            self.spark.table(db + ".fact_sales_forecast").count(), len(generated)
        )
        self.assertFalse(self.spark.catalog.tableExists(db + ".rca_readiness_registry"))
        self.assertFalse(self.spark.catalog.tableExists(db + ".rca_source_manifest"))
        self.assertEqual(budget.used, 2)

        report = initialize(self.spark, db)
        self.assertEqual(report["generated_rows"], 0)
        self.assertTrue(
            self.spark.catalog.tableExists(db + ".vw_genie_forecast_observations")
        )
        grain = ",".join(FIXTURE_GRAIN)
        duplicates = self.spark.sql(
            f"SELECT {grain}, COUNT(*) count FROM {db}.fact_sales_forecast "
            f"GROUP BY {grain} HAVING COUNT(*) > 1"
        ).count()
        self.assertEqual(duplicates, 0)
        readiness = self.spark.table(db + ".rca_readiness_registry")
        self.assertEqual(readiness.where("validation = 'FAIL'").count(), 0)
        self.assertEqual(
            {
                row["source_version"]
                for row in readiness.select("source_version").distinct().collect()
            },
            {report["source_version"]},
        )
        manifest = self.spark.table(db + ".rca_source_manifest").collect()
        self.assertEqual(len(manifest), 1)
        self.assertEqual(manifest[0]["source_version"], report["source_version"])
        current_delta = self.spark.sql(
            f"DESCRIBE HISTORY {db}.fact_sales_forecast LIMIT 1"
        ).first()["version"]
        self.assertEqual(manifest[0]["delta_version"], current_delta)
        preserved = self.spark.sql(
            f"SELECT price FROM {db}.fact_sales_forecast "
            f"WHERE product_id='{existing[0]['product_id']}' "
            f"AND store_id='{existing[0]['store_id']}' "
            f"AND date='{existing[0]['date']}'"
        ).first()["price"]
        self.assertEqual(preserved, 10.25)
        self.assertEqual(budget.used, 2)

        # Repeat the interruption with an existing certified registry/manifest.
        # The old manifest must remain stale until the recovery rerun completes.
        missing = generated[-1]
        self.spark.sql(
            f"DELETE FROM {db}.fact_sales_forecast "
            f"WHERE product_id='{missing['product_id']}' "
            f"AND store_id='{missing['store_id']}' "
            f"AND region='{missing['region']}' "
            f"AND date='{missing['date']}' "
            f"AND forecast_generated_date='{missing['forecast_generated_date']}'"
        )
        old_manifest_version = self.spark.table(db + ".rca_source_manifest").first()[
            "delta_version"
        ]
        with self.assertRaisesRegex(RuntimeError, "simulated interruption"):
            initialize(self.spark, db, _after_source_write=interrupt)
        interrupted_version = self.spark.sql(
            f"DESCRIBE HISTORY {db}.fact_sales_forecast LIMIT 1"
        ).first()["version"]
        self.assertNotEqual(old_manifest_version, interrupted_version)
        self.assertEqual(
            self.spark.table(db + ".rca_source_manifest").first()["delta_version"],
            old_manifest_version,
        )
        recovered = initialize(self.spark, db)
        self.assertEqual(recovered["generated_rows"], 0)
        recovered_readiness = self.spark.table(db + ".rca_readiness_registry").where(
            f"source_version = '{recovered['source_version']}'"
        )
        self.assertGreater(recovered_readiness.count(), 0)
        self.assertEqual(recovered_readiness.where("validation = 'FAIL'").count(), 0)
        self.assertEqual(
            {
                row["source_version"]
                for row in recovered_readiness.select("source_version")
                .distinct()
                .collect()
            },
            {recovered["source_version"]},
        )
        recovered_manifest = self.spark.table(db + ".rca_source_manifest").where(
            f"source_version = '{recovered['source_version']}'"
        )
        self.assertEqual(recovered_manifest.count(), 1)
        manifest_row = recovered_manifest.first()
        self.assertEqual(manifest_row["source_version"], recovered["source_version"])
        self.assertEqual(
            manifest_row["delta_version"],
            interrupted_version,
        )
        self.assertEqual(
            self.spark.sql(
                f"SELECT {grain}, COUNT(*) count FROM {db}.fact_sales_forecast "
                f"GROUP BY {grain} HAVING COUNT(*) > 1"
            ).count(),
            0,
        )
        preserved_after_recovery = self.spark.sql(
            f"SELECT price FROM {db}.fact_sales_forecast "
            f"WHERE product_id='{existing[0]['product_id']}' "
            f"AND store_id='{existing[0]['store_id']}' "
            f"AND date='{existing[0]['date']}'"
        ).first()["price"]
        self.assertEqual(preserved_after_recovery, 10.25)
        self.assertEqual(budget.used, 2)

    def test_commercial_demo_rerun_is_idempotent_and_views_are_separate(self):
        from commercial_lab import publish_commercial_lab
        from genie_semantic import publish_commercial_genie_views

        db = "spark_catalog.forecast_commercial_lab"
        first = publish_commercial_lab(self.spark, db)
        views = publish_commercial_genie_views(self.spark, db)
        expected_counts = {
            "dim_sku": 3,
            "dim_customer": 3,
            "fact_sku_forecast": 78,
            "fact_customer_forecast": 130,
            "fact_sku_budget": 18,
            "fact_sku_price": 18,
            "fact_sku_promotion": 2,
        }
        self.assertEqual(
            {name: values["total_rows"] for name, values in first["tables"].items()},
            expected_counts,
        )
        second = publish_commercial_lab(self.spark, db)
        self.assertEqual(
            {name: values["generated_rows"] for name, values in second["tables"].items()},
            {name: 0 for name in expected_counts},
        )
        self.assertEqual(first["source_version"], second["source_version"])
        self.assertEqual(self.spark.table(db + ".rca_commercial_manifest").count(), 1)
        for view in views:
            self.assertTrue(self.spark.catalog.tableExists(view))
            self.assertGreater(self.spark.table(view).count(), 0)
        self.assertNotIn(
            "customer_id", self.spark.table(db + ".vw_genie_sku_budget").columns
        )
