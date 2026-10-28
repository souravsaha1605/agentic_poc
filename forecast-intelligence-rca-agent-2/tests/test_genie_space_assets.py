import json
import unittest
from pathlib import Path

from lab import generate
from genie_semantic import GENIE_VIEW, publish_genie_view


ROOT = Path(__file__).resolve().parents[1]


class GenieSpaceAssetTests(unittest.TestCase):
    def setUp(self):
        self.rows, _ = generate()
        document = json.loads(
            (ROOT / "genie" / "benchmark_questions.json").read_text()
        )
        self.cases = {case["id"]: case for case in document["questions"]}

    def selected(self, product, region, start, end):
        return [
            row
            for row in self.rows
            if row["product_id"] == product
            and row["region"] == region
            and start <= row["date"] <= end
        ]

    def test_forecast_benchmark_is_an_independent_numeric_oracle(self):
        expected = self.cases["forecast_retrieval"]["expected"]
        rows = self.selected(
            "P0099", "West", expected["period_start"], expected["period_end"]
        )
        actual = sum(row["units_sold"] for row in rows)
        forecast = sum(row["demand_forecast"] for row in rows)
        absolute_error = sum(
            abs(row["demand_forecast"] - row["units_sold"]) for row in rows
        )
        wmape = 100 * absolute_error / abs(actual)
        self.assertEqual(expected["observations"], len(rows))
        self.assertEqual(expected["actual"], actual)
        self.assertEqual(expected["forecast"], forecast)
        self.assertEqual(expected["wmape_pct"], wmape)
        self.assertEqual(expected["accuracy_pct"], 100 - wmape)
        self.assertEqual(expected["bias_pct"], 100 * (forecast - actual) / abs(actual))

    def test_revenue_benchmark_has_exact_period_values_and_deltas(self):
        expected = self.cases["revenue_comparison"]["expected"]

        def revenue(period):
            rows = self.selected("P0070", "North", period[0], period[1])
            gross = sum(row["units_sold"] * row["price"] for row in rows)
            net = sum(
                row["units_sold"] * row["price"] * (1 - row["discount"] / 100)
                for row in rows
            )
            return gross, net

        primary = revenue(expected["primary_period"])
        comparison = revenue(expected["comparison_period"])
        self.assertEqual(expected["primary_gross_revenue_inr"], primary[0])
        self.assertEqual(expected["primary_net_revenue_inr"], primary[1])
        self.assertEqual(expected["comparison_gross_revenue_inr"], comparison[0])
        self.assertEqual(expected["comparison_net_revenue_inr"], comparison[1])
        self.assertEqual(expected["gross_revenue_delta_inr"], primary[0] - comparison[0])
        self.assertEqual(expected["net_revenue_delta_inr"], primary[1] - comparison[1])

    def test_inventory_benchmark_uses_latest_balance_without_summing_dates(self):
        expected = self.cases["inventory_balance"]["expected"]
        rows = self.selected("P0020", "North", "0001-01-01", expected["as_of"])
        store_rows = [row for row in rows if row["store_id"] == expected["store_id"]]
        latest = max(store_rows, key=lambda row: row["inventory_timestamp"])
        self.assertEqual(expected["as_of"], latest["inventory_timestamp"])
        self.assertEqual(expected["inventory_balance_each"], latest["inventory_level"])

    def test_space_instructions_preserve_critical_business_rules(self):
        instructions = " ".join(
            (ROOT / "genie" / "SPACE_INSTRUCTIONS.md").read_text().split()
        )
        for rule in (
            "Do not sum vintages",
            "Never sum inventory balances across dates",
            "four consecutive completed weekly periods",
            "evidence, not proven causes",
            "Never convert missing values to zero",
        ):
            self.assertIn(rule, instructions)

    def test_semantic_view_uses_one_source_and_does_not_change_teams(self):
        class FakeSpark:
            def __init__(self):
                self.statements = []

            def sql(self, statement):
                self.statements.append(" ".join(statement.split()))

        spark = FakeSpark()
        published = publish_genie_view(spark, "workspace.forecast_rca_lab")
        statement = spark.statements[0]
        self.assertEqual(published, f"workspace.forecast_rca_lab.{GENIE_VIEW}")
        self.assertIn("FROM workspace.forecast_rca_lab.vw_forecast_metrics", statement)
        self.assertNotIn(" JOIN ", statement)

        # Direct Genie does not replace or disable the future Teams application.
        host = (ROOT / "channels" / "host.py").read_text()
        teams = (ROOT / "channels" / "teams.py").read_text()
        self.assertIn("from .teams import enabled", host)
        self.assertIn("create_app(Admission", host)
        self.assertIn("TEAMS_ENABLED", teams)


if __name__ == "__main__":
    unittest.main()
