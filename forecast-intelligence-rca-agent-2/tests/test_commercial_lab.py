import copy
import json
import unittest
from pathlib import Path

from commercial_lab import (
    COMMERCIAL_DATASET_VERSION,
    TABLE_KEYS,
    generate_commercial_data,
    validate_commercial_data,
)
from genie_semantic import COMMERCIAL_GENIE_VIEWS, publish_commercial_genie_views


ROOT = Path(__file__).resolve().parents[1]


class CommercialLabTests(unittest.TestCase):
    def setUp(self):
        self.tables = generate_commercial_data()

    def test_tables_are_separate_certified_grains(self):
        self.assertEqual(
            {name: len(rows) for name, rows in self.tables.items()},
            {
                "dim_sku": 3,
                "dim_customer": 3,
                "dim_fiscal_period": 6,
                "fact_sku_forecast": 78,
                "fact_customer_forecast": 130,
                "fact_sku_budget": 18,
                "fact_sku_price": 18,
                "fact_sku_promotion": 2,
            },
        )
        self.assertEqual(validate_commercial_data(self.tables), [])
        for table, keys in TABLE_KEYS.items():
            grains = [tuple(row[key] for key in keys) for row in self.tables[table]]
            self.assertEqual(len(grains), len(set(grains)), table)
            self.assertTrue(
                all(
                    row["dataset_version"] == COMMERCIAL_DATASET_VERSION
                    for row in self.tables[table]
                )
            )

    def test_customer_budget_and_promotion_are_forbidden(self):
        broken = copy.deepcopy(self.tables)
        broken["fact_sku_budget"][0]["customer_id"] = "CUST-001"
        broken["fact_sku_promotion"][0]["customer_id"] = "CUST-001"
        self.assertIn(
            "fact_sku_budget:CUSTOMER_BUDGET_FORBIDDEN",
            validate_commercial_data(broken),
        )
        self.assertIn(
            "fact_sku_promotion:CUSTOMER_PROMOTION_FORBIDDEN",
            validate_commercial_data(broken),
        )

    def test_unknown_entities_and_duplicate_vintages_fail(self):
        broken = copy.deepcopy(self.tables)
        broken["fact_customer_forecast"][0]["customer_id"] = "UNKNOWN"
        broken["fact_sku_forecast"].append(
            copy.deepcopy(broken["fact_sku_forecast"][0])
        )
        failures = validate_commercial_data(broken)
        self.assertIn("fact_customer_forecast:UNKNOWN_CUSTOMER", failures)
        self.assertIn("fact_sku_forecast:DUPLICATE_GRAIN", failures)

    def test_unknown_and_overlapping_fiscal_periods_fail(self):
        broken = copy.deepcopy(self.tables)
        broken["fact_sku_budget"][0]["fiscal_period"] = "UNKNOWN"
        self.assertIn(
            "fact_sku_budget:UNKNOWN_FISCAL_PERIOD",
            validate_commercial_data(broken),
        )
        broken = copy.deepcopy(self.tables)
        broken["dim_fiscal_period"][1]["period_start"] = "2026-04-30"
        self.assertIn(
            "dim_fiscal_period:OVERLAPPING_PERIODS",
            validate_commercial_data(broken),
        )
        broken = copy.deepcopy(self.tables)
        august = next(
            row for row in broken["fact_sku_price"]
            if row["sku_id"] == "SKU-1001"
            and row["effective_from"] == "2026-08-01"
        )
        august["effective_from"] = "2026-07-31"
        self.assertIn(
            "fact_sku_price:OVERLAPPING_EFFECTIVE_DATES",
            validate_commercial_data(broken),
        )

    @staticmethod
    def metrics(rows):
        actual = sum(row["actual_quantity"] for row in rows)
        forecast = sum(row["forecast_quantity"] for row in rows)
        absolute_error = sum(
            abs(row["forecast_quantity"] - row["actual_quantity"]) for row in rows
        )
        wmape = 100 * absolute_error / abs(actual)
        return actual, forecast, wmape, 100 - wmape, 100 * (forecast - actual) / abs(actual)

    def test_benchmarks_are_independently_correct(self):
        cases = {
            case["id"]: case
            for case in json.loads(
                (ROOT / "genie" / "commercial_benchmark_questions.json").read_text()
            )["questions"]
        }
        sku_rows = [
            row
            for row in self.tables["fact_sku_forecast"]
            if row["sku_id"] == "SKU-1001"
        ]
        actual, forecast, wmape, accuracy, bias = self.metrics(sku_rows)
        expected = cases["sku_forecast"]["expected"]
        self.assertEqual(expected["observations"], len(sku_rows))
        self.assertEqual(expected["actual_quantity"], actual)
        self.assertEqual(expected["forecast_quantity"], forecast)
        self.assertAlmostEqual(expected["wmape_pct"], wmape, places=4)
        self.assertAlmostEqual(expected["accuracy_pct"], accuracy, places=4)
        self.assertAlmostEqual(expected["bias_pct"], bias, places=4)

        customer_sku_rows = [
            row
            for row in self.tables["fact_customer_forecast"]
            if row["customer_id"] == "CUST-001" and row["sku_id"] == "SKU-1001"
        ]
        actual, forecast, wmape, accuracy, bias = self.metrics(customer_sku_rows)
        expected = cases["customer_sku_forecast"]["expected"]
        self.assertEqual(expected["observations"], len(customer_sku_rows))
        self.assertEqual(expected["actual_quantity"], actual)
        self.assertEqual(expected["forecast_quantity"], forecast)
        self.assertAlmostEqual(expected["wmape_pct"], wmape, places=3)
        self.assertAlmostEqual(expected["accuracy_pct"], accuracy, places=3)
        self.assertAlmostEqual(expected["bias_pct"], bias, places=3)

        customer_rows = [
            row
            for row in self.tables["fact_customer_forecast"]
            if row["customer_id"] == "CUST-001"
        ]
        actual, forecast, wmape, accuracy, bias = self.metrics(customer_rows)
        expected = cases["customer_forecast_all_skus"]["expected"]
        self.assertEqual(expected["included_skus"], sorted({r["sku_id"] for r in customer_rows}))
        self.assertEqual(expected["actual_quantity"], actual)
        self.assertEqual(expected["forecast_quantity"], forecast)
        self.assertAlmostEqual(expected["wmape_pct"], wmape, places=4)
        self.assertAlmostEqual(expected["accuracy_pct"], accuracy, places=4)
        self.assertAlmostEqual(expected["bias_pct"], bias, places=4)

        budget = next(
            row
            for row in self.tables["fact_sku_budget"]
            if row["sku_id"] == "SKU-1001" and row["fiscal_period"] == "FY2026-P08"
        )
        expected = cases["sku_budget"]["expected"]
        self.assertEqual(expected["budget_quantity"], budget["budget_quantity"])
        self.assertEqual(expected["budget_revenue_inr"], budget["budget_revenue"])
        self.assertEqual(expected["budget_version"], budget["budget_version"])

        price = next(
            row
            for row in self.tables["fact_sku_price"]
            if row["sku_id"] == "SKU-1001"
            and row["effective_from"] == "2026-08-01"
        )
        promotion = next(
            row
            for row in self.tables["fact_sku_promotion"]
            if row["sku_id"] == "SKU-1001"
        )
        expected = cases["sku_price_and_promotion"]["expected"]
        self.assertEqual(expected["price_inr"], price["price"])
        self.assertEqual(expected["promotion_id"], promotion["promotion_id"])
        self.assertEqual(expected["discount_value_pct"], promotion["discount_value"])

    def test_semantic_views_remain_separate_and_explicit(self):
        class FakeSpark:
            def __init__(self):
                self.statements = []

            def sql(self, statement):
                self.statements.append(" ".join(statement.split()))

        spark = FakeSpark()
        names = publish_commercial_genie_views(spark, "workspace.forecast_rca_lab")
        self.assertEqual(len(names), len(COMMERCIAL_GENIE_VIEWS))
        self.assertEqual(len(spark.statements), len(COMMERCIAL_GENIE_VIEWS))
        combined = "\n".join(spark.statements)
        for table in (
            "fact_sku_forecast",
            "fact_customer_forecast",
            "fact_sku_budget",
            "fact_sku_price",
            "fact_sku_promotion",
        ):
            self.assertIn(table, combined)
        budget_statement = next(s for s in spark.statements if "vw_genie_sku_budget" in s)
        self.assertNotIn("customer_id", budget_statement)
        monthly = next(
            s for s in spark.statements
            if "vw_genie_sku_monthly_performance AS" in s
        )
        self.assertIn("ROW_NUMBER() OVER", monthly)
        self.assertIn("WHERE vintage_rank=1", monthly)
        self.assertIn("dim_fiscal_period", monthly)
        plan = next(
            s for s in spark.statements
            if "vw_genie_sku_monthly_plan_vs_actual AS" in s
        )
        self.assertIn("vw_genie_sku_monthly_performance", plan)
        self.assertIn("b.status='APPROVED'", plan)
        self.assertNotIn("SELECT DISTINCT", combined.upper())

    def test_monthly_plan_vs_actual_benchmark_is_exact(self):
        rows = [
            row for row in self.tables["fact_sku_forecast"]
            if row["sku_id"] == "SKU-1001"
            and row["target_date"].startswith("2026-08")
        ]
        budget = next(
            row for row in self.tables["fact_sku_budget"]
            if row["sku_id"] == "SKU-1001"
            and row["fiscal_period"] == "FY2026-P08"
        )
        actual = sum(row["actual_quantity"] for row in rows)
        forecast = sum(row["forecast_quantity"] for row in rows)
        self.assertEqual((len(rows), actual, forecast), (5, 635.0, 565.0))
        self.assertEqual(budget["budget_quantity"], 480.0)
        self.assertEqual(forecast - actual, -70.0)
        self.assertEqual(budget["budget_quantity"] - actual, -155.0)
        self.assertEqual(forecast - budget["budget_quantity"], 85.0)
        self.assertAlmostEqual(100 * (forecast - actual) / actual, -11.023622, 6)
        self.assertAlmostEqual(
            100 * (budget["budget_quantity"] - actual) / actual,
            -24.409449,
            6,
        )
        self.assertAlmostEqual(
            100 * (forecast - budget["budget_quantity"])
            / budget["budget_quantity"],
            17.708333,
            6,
        )

    def test_genie_instructions_define_entity_routing(self):
        raw = (ROOT / "genie" / "SPACE_INSTRUCTIONS.md").read_text()
        instructions = " ".join(raw.split())
        for phrase in (
            "SKU_FORECAST",
            "CUSTOMER_FORECAST",
            "Customer budget, price and promotion are unsupported",
            "State included product/SKU IDs",
            "synthetic disclosure",
            "never underlying `fact_*` or `dim_*`",
            "Never use `SELECT DISTINCT`",
            "Use those published fields directly",
            "do not recalculate, average or redefine certified percentages",
        ):
            self.assertIn(phrase, instructions)
        self.assertNotIn("SUM(units_sold)", raw)
        self.assertNotIn("SUM(demand_forecast)", raw)
        self.assertNotIn("SUM(units_sold * price)", raw)
        self.assertLess(len(raw), 6000)


if __name__ == "__main__":
    unittest.main()

