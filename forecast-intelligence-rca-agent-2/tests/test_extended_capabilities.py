"""Certified positive and negative cases for the previously unavailable lab drivers."""

import os
import copy
import tempfile
import unittest
from datetime import date, timedelta
from unittest.mock import patch
from business import BusinessService
from lab import local_provider, GLOBAL, END
from contracts import AnalysisPlan
from conversation import ConversationService
from data_access import RecordsProvider
from state import SQLiteStateStore


class ExtendedCapabilitiesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.provider = local_provider()

    def test_certified_driver_signals_are_real_associations(self):
        service = BusinessService(self.provider, today=END)
        for product, capability in [
            ("P0084", "weather"),
            ("P0085", "competitor"),
            ("P0086", "lifecycle"),
            ("P0087", "mix"),
        ]:
            with self.subTest(capability=capability):
                result = service.execute(
                    AnalysisPlan(
                        tool="run_forecast_rca",
                        product_id=product,
                        region="North",
                        category="Dairy",
                        hypotheses=[capability],
                    ),
                    GLOBAL,
                )
                hypothesis = result["hypotheses"][0]
                self.assertEqual(hypothesis["status"], "POSSIBLE")
                self.assertEqual(hypothesis["readiness"], "READY")
                self.assertTrue(hypothesis["evidence"])
                self.assertIn("not a causal claim", hypothesis["reason"])

    def test_missing_weather_remains_explicitly_unavailable(self):
        result = BusinessService(self.provider, today=END).execute(
            AnalysisPlan(
                tool="run_forecast_rca",
                product_id="P0001",
                region="North",
                category="Dairy",
                hypotheses=["weather"],
            ),
            GLOBAL,
        )
        self.assertEqual(result["hypotheses"][0]["status"], "NOT_TESTABLE")

    def test_regional_comparison_computes_gap_and_enforces_both_scopes(self):
        plan = AnalysisPlan(
            tool="get_forecast_context",
            product_id="P0088",
            region="North",
            category="Dairy",
            comparison_region="West",
        )
        result = BusinessService(self.provider, today=END).execute(plan, GLOBAL)
        self.assertEqual(result["comparisons"]["region"]["accuracy_gap_pp"], -40)
        restricted = GLOBAL.model_copy(update={"regions": ("North",)})
        with self.assertRaises(PermissionError):
            BusinessService(self.provider, today=END).execute(plan, restricted)

    def test_fiscal_and_channel_filters_use_actual_fields(self):
        service = BusinessService(self.provider, today=END)
        fiscal = service.execute(
            AnalysisPlan(
                tool="get_forecast_context",
                product_id="P0001",
                region="North",
                category="Dairy",
                fiscal_period="FY2026-P09",
            ),
            GLOBAL,
        )
        self.assertTrue(fiscal["period"]["start"].startswith("2026-09"))
        online = service.execute(
            AnalysisPlan(
                tool="get_forecast_context",
                product_id="P0087",
                region="North",
                category="Dairy",
                channel="Online",
            ),
            GLOBAL,
        )
        self.assertEqual(online["metrics"]["actual"], 1500)

    def test_explicit_comparison_period_has_its_own_provenance(self):
        from datetime import date

        result = BusinessService(self.provider, today=END).execute(
            AnalysisPlan(
                tool="get_forecast_context",
                product_id="P0001",
                region="North",
                category="Dairy",
                start=date(2026, 8, 2),
                end=date(2026, 9, 27),
                comparison_start=date(2026, 5, 3),
                comparison_end=date(2026, 7, 26),
            ),
            GLOBAL,
        )
        reference = result["comparisons"]["period"]
        self.assertEqual(reference["period"]["start"], "2026-05-03")
        self.assertIn("source_version", reference["provenance"])

    def test_natural_language_fiscal_and_regional_requests(self):
        with tempfile.TemporaryDirectory() as folder:
            core = ConversationService(
                BusinessService(self.provider, today=END),
                SQLiteStateStore(folder + "/state.db"),
            )
            fiscal = core.handle(
                GLOBAL,
                {
                    "session_id": "session",
                    "request_id": "one",
                    "message": "Forecast P0001 in North fiscal FY2026-P09 channel Retail",
                },
            )
            self.assertNotEqual(fiscal["intent"], "CLARIFICATION")
            regional = core.handle(
                GLOBAL,
                {
                    "session_id": "session",
                    "request_id": "two",
                    "message": "Compare forecast for P0088 in North versus West",
                },
            )
            self.assertEqual(
                regional["evidence"]["comparisons"]["region"]["accuracy_gap_pp"], -40
            )

    def test_natural_relative_months_and_previous_period_comparison(self):
        with tempfile.TemporaryDirectory() as folder:
            core = ConversationService(
                BusinessService(self.provider, today=END),
                SQLiteStateStore(folder + "/state.db"),
            )
            six_months = core.handle(
                GLOBAL,
                {
                    "session_id": "relative",
                    "request_id": "six",
                    "message": "Compare forecast for P0001 in North for the last 6 months with the previous period",
                },
            )
            evidence = six_months["evidence"]
            self.assertEqual(evidence["provenance"]["requested_start"], "2026-03-28")
            self.assertEqual(evidence["provenance"]["requested_end"], "2026-09-27")
            previous = evidence["comparisons"]["period"]
            self.assertEqual(previous["provenance"]["requested_start"], "2025-09-28")
            self.assertEqual(previous["provenance"]["requested_end"], "2026-03-27")
            last_month = core.handle(
                GLOBAL,
                {
                    "session_id": "last-month",
                    "request_id": "month",
                    "message": "Forecast P0001 in North for last month",
                },
            )
            self.assertEqual(
                last_month["evidence"]["provenance"]["requested_start"],
                "2026-08-01",
            )
            self.assertEqual(
                last_month["evidence"]["provenance"]["requested_end"],
                "2026-08-31",
            )

    def test_period_boundaries_missing_periods_and_empty_primary_scope(self):
        service = BusinessService(self.provider, today=END)
        bounded = service.execute(
            AnalysisPlan(
                tool="get_forecast_context",
                product_id="P0040",
                region="North",
                category="Dairy",
                start=date(2026, 8, 23),
                end=date(2026, 9, 27),
                comparison_start=date(2026, 7, 12),
                comparison_end=date(2026, 8, 16),
            ),
            GLOBAL,
        )
        self.assertEqual(bounded["metrics"]["actual"], 900)
        self.assertEqual(bounded["comparisons"]["period"]["metrics"]["actual"], 600)
        deltas = bounded["comparisons"]["period"]["deltas"]
        self.assertEqual(deltas["actual_units"], 300)
        self.assertEqual(deltas["actual_pct"], 50)
        self.assertEqual(deltas["accuracy_gap_pp"], -33.33)
        missing = service.execute(
            AnalysisPlan(
                tool="get_forecast_context",
                product_id="P0001",
                region="North",
                category="Dairy",
                start=date(2026, 8, 2),
                end=date(2026, 9, 27),
                comparison_start=date(2020, 1, 1),
                comparison_end=date(2020, 2, 29),
            ),
            GLOBAL,
        )
        self.assertEqual(
            missing["comparisons"]["period"]["availability"], "UNAVAILABLE"
        )
        with self.assertRaises(ValueError):
            service.execute(
                AnalysisPlan(
                    tool="get_forecast_context",
                    product_id="P0001",
                    region="North",
                    category="Dairy",
                    start=date(2020, 1, 1),
                    end=date(2020, 2, 29),
                ),
                GLOBAL,
            )

    def test_inventory_trend_and_forecast_error_exposure_are_defined(self):
        result = BusinessService(self.provider, today=END).execute(
            AnalysisPlan(
                tool="get_inventory_context",
                product_id="P0020",
                region="North",
                category="Dairy",
                lookback_weeks=12,
            ),
            GLOBAL,
        )
        trend = result["inventory_trend"]
        self.assertEqual(len(trend["points"]), 12)
        self.assertEqual(trend["points"][0]["inventory"], 300)
        self.assertEqual(trend["points"][-1]["inventory"], 0)
        self.assertEqual(trend["change_pct"], -100)
        exposure = result["forecast_error_inventory_exposure"]
        self.assertEqual(exposure["absolute_error_units_at_stockout"], 480)
        self.assertEqual(exposure["signed_error_units_at_stockout"], 480)
        self.assertEqual(exposure["stockout_snapshots"], 6)
        self.assertIn("association only", exposure["definition"])

    def test_rolling_average_signals_are_numerically_correct(self):
        result = BusinessService(self.provider, today=END).execute(
            AnalysisPlan(
                tool="analyze_historical_pattern",
                product_id="P0040",
                region="North",
                category="Dairy",
                lookback_weeks=12,
            ),
            GLOBAL,
        )
        latest = result["patterns"]["rolling_4_week"][-1]
        self.assertEqual(latest["actual_4w_avg"], 150)
        self.assertEqual(latest["forecast_4w_avg"], 100)
        self.assertEqual(latest["accuracy_4w_pct"], 66.67)

    def test_category_and_store_aggregation_and_authorization(self):
        service = BusinessService(self.provider, today=END)
        category = service.execute(
            AnalysisPlan(
                tool="get_forecast_context",
                product_id="*",
                region="North",
                category="Dairy",
            ),
            GLOBAL,
        )
        self.assertEqual(category["metrics"]["actual"], 17436.82)
        self.assertEqual(category["aggregation"]["unit_of_measure"], "each")
        self.assertEqual(
            category["aggregation"]["included_products"],
            [
                "P0001",
                "P0020",
                "P0040",
                "P0050",
                "P0060",
                "P0070",
                "P0080",
                "P0081",
                "P0082",
                "P0083",
                "P0084",
                "P0085",
                "P0086",
                "P0087",
                "P0088",
            ],
        )
        store = service.execute(
            AnalysisPlan(
                tool="get_forecast_context",
                product_id="*",
                region="North",
                category="Dairy",
                store_id="S002",
            ),
            GLOBAL,
        )
        self.assertEqual(store["metrics"]["actual"], 1500)
        restricted = GLOBAL.model_copy(update={"products": ("P0001",)})
        with self.assertRaises(PermissionError):
            service.execute(
                AnalysisPlan(
                    tool="get_forecast_context",
                    product_id="*",
                    region="North",
                    category="Dairy",
                ),
                restricted,
            )
        with tempfile.TemporaryDirectory() as folder:
            core = ConversationService(
                service, SQLiteStateStore(folder + "/aggregation.db")
            )
            answer = core.handle(
                GLOBAL,
                {
                    "session_id": "aggregate",
                    "request_id": "one",
                    "message": "Forecast for Dairy category in North store S002",
                },
            )
            self.assertEqual(answer["entity"]["product_id"], "*")
            self.assertEqual(answer["entity"]["store_id"], "S002")
            self.assertEqual(
                answer["evidence"]["metrics"],
                {
                    "actual": 1500.0,
                    "forecast": 600.0,
                    "signed_error": -900.0,
                    "absolute_error": 900.0,
                    "wmape_pct": 60.0,
                    "accuracy_pct": 40.0,
                    "bias_pct": -60.0,
                    "definition": "WMAPE=sum(abs(forecast-actual))/sum(abs(actual)); accuracy=100-WMAPE; units",
                },
            )
            revenue = core.handle(
                GLOBAL,
                {
                    "session_id": "aggregate",
                    "request_id": "revenue",
                    "message": "What about revenue?",
                },
            )
            inventory = core.handle(
                GLOBAL,
                {
                    "session_id": "aggregate",
                    "request_id": "inventory",
                    "message": "What about inventory?",
                },
            )
            forecast = core.handle(
                GLOBAL,
                {
                    "session_id": "aggregate",
                    "request_id": "forecast",
                    "message": "What about the forecast?",
                },
            )
            for followup in (revenue, inventory, forecast):
                self.assertEqual(followup["scenario_id"], answer["scenario_id"])
                self.assertEqual(followup["entity"]["product_id"], "*")
                self.assertEqual(followup["entity"]["store_id"], "S002")
                self.assertEqual(
                    followup["evidence"]["aggregation"]["included_products"],
                    ["P0087"],
                )
            self.assertEqual(revenue["intent"], "REVENUE_RETRIEVAL")
            self.assertEqual(revenue["evidence"]["gross_revenue"], 15000.0)
            self.assertEqual(revenue["evidence"]["net_revenue"], 14250.0)
            self.assertEqual(revenue["evidence"]["currency"], "INR")
            self.assertEqual(revenue["evidence"]["availability"], "AVAILABLE")
            self.assertNotIn("metrics", revenue["evidence"])
            self.assertEqual(inventory["intent"], "INVENTORY_RETRIEVAL")
            self.assertEqual(inventory["evidence"]["inventory"], 300.0)
            self.assertEqual(inventory["evidence"]["availability"], "AVAILABLE")
            self.assertEqual(inventory["evidence"]["freshness"], "FRESH")
            self.assertIn("inventory_trend", inventory["evidence"])
            self.assertNotIn("metrics", inventory["evidence"])
            self.assertEqual(forecast["intent"], "FORECAST_RETRIEVAL")
            self.assertEqual(
                forecast["evidence"]["metrics"], answer["evidence"]["metrics"]
            )
            self.assertNotIn("net_revenue", forecast["evidence"])
            self.assertNotIn("inventory", forecast["evidence"])
            empty = core.handle(
                GLOBAL,
                {
                    "session_id": "empty-store",
                    "request_id": "two",
                    "message": "Forecast for Dairy category in North store S999",
                },
            )
            self.assertFalse(empty["success"])

    def test_category_aggregation_deduplicates_forecast_vintages(self):
        provider = copy.deepcopy(self.provider)
        baseline = BusinessService(provider, today=END).execute(
            AnalysisPlan(
                tool="get_forecast_context",
                product_id="*",
                region="North",
                category="Dairy",
            ),
            GLOBAL,
        )
        older = []
        for row in provider.rows:
            if row["category"] == "Dairy" and row["region"] == "North":
                item = dict(row)
                issued = __import__("datetime").date.fromisoformat(
                    item["forecast_generated_date"]
                )
                item["forecast_generated_date"] = str(issued - timedelta(days=7))
                item["demand_forecast"] = 1.0
                older.append(item)
        provider.rows.extend(older)
        repeated = BusinessService(provider, today=END).execute(
            AnalysisPlan(
                tool="get_forecast_context",
                product_id="*",
                region="North",
                category="Dairy",
            ),
            GLOBAL,
        )
        self.assertEqual(repeated["metrics"], baseline["metrics"])

    def test_aggregate_scope_rejects_missing_and_mixed_units(self):
        with self.assertRaisesRegex(ValueError, "concrete category"):
            AnalysisPlan(
                tool="get_forecast_context",
                product_id="*",
                region="North",
            )
        for value in (None, "case"):
            with self.subTest(unit=value):
                provider = copy.deepcopy(self.provider)
                next(row for row in provider.rows if row["product_id"] == "P0001")[
                    "unit_of_measure"
                ] = value
                with self.assertRaisesRegex(ValueError, "certified unit"):
                    BusinessService(provider, today=END).execute(
                        AnalysisPlan(
                            tool="get_forecast_context",
                            product_id="*",
                            region="North",
                            category="Dairy",
                        ),
                        GLOBAL,
                    )

    def test_comparison_integrity_errors_are_not_reported_as_empty(self):
        base_plan = dict(
            tool="get_forecast_context",
            product_id="P0001",
            region="North",
            category="Dairy",
            start=date(2026, 8, 2),
            end=date(2026, 9, 27),
            comparison_start=date(2026, 7, 20),
            comparison_end=date(2026, 7, 31),
        )
        duplicate = copy.deepcopy(self.provider)
        row = next(
            row
            for row in duplicate.rows
            if row["product_id"] == "P0001" and row["date"] == "2026-07-26"
        )
        duplicate.rows.append(copy.deepcopy(row))
        with self.assertRaisesRegex(ValueError, "Duplicate source grain"):
            BusinessService(duplicate, today=END).execute(
                AnalysisPlan(**base_plan), GLOBAL
            )

        invalid = copy.deepcopy(self.provider)
        for row in invalid.rows:
            if row["product_id"] == "P0001" and row["date"] == "2026-07-26":
                row["forecast_generated_date"] = "2026-07-27"
        with self.assertRaisesRegex(ValueError, "vintage is unavailable"):
            BusinessService(invalid, today=END).execute(
                AnalysisPlan(**base_plan), GLOBAL
            )

    def test_inventory_exposure_missing_and_partial_coverage(self):
        missing = copy.deepcopy(self.provider)
        for row in missing.rows:
            if row["product_id"] == "P0001":
                row["inventory_level"] = None
        unavailable = BusinessService(missing, today=END).execute(
            AnalysisPlan(
                tool="get_inventory_context",
                product_id="P0001",
                region="North",
                category="Dairy",
            ),
            GLOBAL,
        )["forecast_error_inventory_exposure"]
        self.assertEqual(unavailable["availability"], "UNAVAILABLE")
        self.assertIsNone(unavailable["absolute_error_units_at_stockout"])
        self.assertEqual(unavailable["usable_observations"], 0)

        partial = copy.deepcopy(self.provider)
        rows = [row for row in partial.rows if row["product_id"] == "P0001"][-12:]
        rows[0]["inventory_level"] = None
        usable = [row for row in rows if row["inventory_level"] is not None]
        stockouts = [row for row in usable if row["inventory_level"] <= 0]
        in_stock = [row for row in usable if row["inventory_level"] > 0]
        expected_stockout_absolute = sum(
            abs(row["demand_forecast"] - row["units_sold"]) for row in stockouts
        )
        expected_stockout_signed = sum(
            row["demand_forecast"] - row["units_sold"] for row in stockouts
        )
        expected_in_stock_absolute = sum(
            abs(row["demand_forecast"] - row["units_sold"]) for row in in_stock
        )
        exposure = BusinessService(partial, today=END).execute(
            AnalysisPlan(
                tool="get_inventory_context",
                product_id="P0001",
                region="North",
                category="Dairy",
            ),
            GLOBAL,
        )["forecast_error_inventory_exposure"]
        self.assertEqual(exposure["availability"], "PARTIAL")
        self.assertEqual(exposure["usable_observations"], 11)
        self.assertEqual(exposure["missing_observations"], 1)
        self.assertEqual(
            exposure["absolute_error_units_at_stockout"],
            expected_stockout_absolute,
        )
        self.assertEqual(
            exposure["signed_error_units_at_stockout"], expected_stockout_signed
        )
        self.assertEqual(
            exposure["absolute_error_units_with_inventory"],
            expected_in_stock_absolute,
        )
        self.assertEqual(exposure["stockout_snapshots"], len(stockouts))

    def test_rolling_windows_require_consecutive_weeks_and_handle_zero_actuals(self):
        provider = copy.deepcopy(self.provider)
        provider.rows = [
            row
            for row in provider.rows
            if not (row["product_id"] == "P0040" and row["date"] == "2026-09-06")
        ]
        result = BusinessService(provider, today=END).execute(
            AnalysisPlan(
                tool="analyze_historical_pattern",
                product_id="P0040",
                region="North",
                category="Dairy",
                lookback_weeks=12,
            ),
            GLOBAL,
        )
        rolling = result["patterns"]["rolling_4_week"]
        self.assertTrue(result["data_quality"]["gaps"])
        self.assertTrue(
            all(
                (
                    date.fromisoformat(point["week"])
                    - date.fromisoformat(point["window_start"])
                ).days
                == 21
                for point in rolling
            )
        )
        self.assertLess(len(rolling), 8)

        zero_points = [
            {
                "date": str(date(2026, 1, 5) + timedelta(weeks=i)),
                "actual": 0,
                "forecast": 10,
            }
            for i in range(8)
        ]
        zero = BusinessService.patterns(zero_points)["rolling_4_week"]
        self.assertIsNone(zero[-1]["accuracy_4w_pct"])

    def test_period_selector_conflicts_and_calendar_boundaries(self):
        from services.forecast_rca_service import shift_months

        with self.assertRaisesRegex(ValueError, "one period selector"):
            AnalysisPlan(
                tool="get_forecast_context",
                product_id="P0001",
                region="North",
                category="Dairy",
                start=date(2026, 8, 2),
                end=date(2026, 9, 27),
                lookback_months=6,
            )
        with self.assertRaisesRegex(ValueError, "either an explicit comparison"):
            AnalysisPlan(
                tool="get_forecast_context",
                product_id="P0001",
                region="North",
                category="Dairy",
                comparison_start=date(2026, 1, 1),
                comparison_end=date(2026, 1, 31),
                compare_previous_period=True,
            )
        self.assertEqual(shift_months(date(2026, 1, 31), -1), date(2025, 12, 31))
        self.assertEqual(shift_months(date(2024, 3, 31), -1), date(2024, 2, 29))

        template = next(
            row
            for row in self.provider.rows
            if row["product_id"] == "P0001" and row["region"] == "North"
        )
        boundary_rows = []
        for target, actual, forecast in (
            (date(2025, 12, 1), 80.0, 72.0),
            (date(2025, 12, 31), 120.0, 108.0),
            (date(2026, 1, 1), 100.0, 110.0),
            (date(2026, 1, 31), 200.0, 220.0),
        ):
            row = copy.deepcopy(template)
            row.update(
                date=str(target),
                forecast_generated_date=str(target - timedelta(days=7)),
                inventory_timestamp=str(target),
                weather_observed_at=str(target),
                units_sold=actual,
                demand_forecast=forecast,
            )
            boundary_rows.append(row)
        boundary_provider = RecordsProvider(
            boundary_rows,
            [
                {
                    "product_id": "P0001",
                    "product_name": "Milk 1L",
                    "region": "North",
                    "category": "Dairy",
                }
            ],
        )
        result = BusinessService(boundary_provider, today=date(2026, 1, 31)).execute(
            AnalysisPlan(
                tool="get_forecast_context",
                product_id="P0001",
                region="North",
                category="Dairy",
                start=date(2026, 1, 1),
                end=date(2026, 1, 31),
                comparison_start=date(2025, 12, 1),
                comparison_end=date(2025, 12, 31),
            ),
            GLOBAL,
        )
        comparison = result["comparisons"]["period"]
        self.assertEqual(result["period"], {"start": "2026-01-01", "end": "2026-01-31"})
        self.assertEqual(
            comparison["period"], {"start": "2025-12-01", "end": "2025-12-31"}
        )
        self.assertEqual(result["metrics"]["actual"], 300.0)
        self.assertEqual(result["metrics"]["forecast"], 330.0)
        self.assertEqual(comparison["metrics"]["actual"], 200.0)
        self.assertEqual(comparison["metrics"]["forecast"], 180.0)
        self.assertEqual(comparison["deltas"]["actual_units"], 100.0)
        self.assertEqual(comparison["deltas"]["actual_pct"], 50.0)
        self.assertEqual(comparison["deltas"]["forecast_units"], 150.0)
        self.assertEqual(comparison["deltas"]["forecast_pct"], 83.33)
        self.assertEqual(comparison["deltas"]["accuracy_gap_pp"], 0.0)

    def test_asynchronous_inventory_history_uses_fresh_carry_forward(self):
        rows = [
            {
                "product_id": "A",
                "store_id": "S1",
                "date": "2026-01-01",
                "inventory_level": 10,
            },
            {
                "product_id": "B",
                "store_id": "S1",
                "date": "2026-01-01",
                "inventory_level": 20,
            },
            {
                "product_id": "A",
                "store_id": "S1",
                "date": "2026-01-08",
                "inventory_level": 8,
            },
            {
                "product_id": "A",
                "store_id": "S1",
                "date": "2026-01-22",
                "inventory_level": 5,
            },
        ]
        trend = BusinessService.inventory_trend(
            rows, date(2026, 1, 1), date(2026, 1, 22)
        )
        self.assertEqual(trend["points"][1]["inventory"], 28)
        self.assertEqual(trend["points"][1]["availability"], "AVAILABLE")
        self.assertEqual(trend["points"][2]["inventory"], 5)
        self.assertEqual(trend["points"][2]["availability"], "PARTIAL")
        self.assertEqual(trend["points"][2]["stale_entities"], 1)
        self.assertEqual(trend["availability"], "PARTIAL")

    def test_platform_alias_bindings_are_supported_without_network_calls(self):
        from client import runtime_setting, get_client

        with patch.dict(
            os.environ,
            {
                "MY_AZURE_OPENAI_ENDPOINT": "https://example.services.ai.azure.com/openai/v1",
                "MY_AZURE_OPENAI_API_KEY": "offline-test-only",
                "MY_AZURE_OPENAI_DEPLOYMENT": "offline-deployment",
            },
            clear=True,
        ):
            self.assertEqual(
                runtime_setting("AZURE_OPENAI_DEPLOYMENT"), "offline-deployment"
            )
            get_client.cache_clear()
            client = get_client()
            self.assertEqual(client.max_retries, 0)
            client.close()
            get_client.cache_clear()


class DeploymentArtifactTests(unittest.TestCase):
    def test_web_package_contains_cloud_dependencies_and_no_state_or_keys(self):
        from deployment.build_web_package import build
        from pathlib import Path
        from zipfile import ZipFile

        with tempfile.TemporaryDirectory() as folder:
            package = build(Path(folder) / "app.zip")
            with ZipFile(package) as archive:
                names = archive.namelist()
                self.assertFalse(
                    any(
                        ".rca_state" in name
                        or ".env" in name
                        or name.endswith(".sqlite3")
                        for name in names
                    )
                )
                self.assertIn("channels/host.py", names)
                requirements = archive.read("requirements.txt").decode()
                self.assertIn("microsoft-agents-hosting-aiohttp", requirements)
                self.assertNotIn("-r requirements.txt", requirements)

    def test_resource_template_starts_disabled_and_reuses_existing_model(self):
        from pathlib import Path
        import json

        template = json.loads(
            (
                Path(__file__).resolve().parents[1] / "deployment/azuredeploy.json"
            ).read_text()
        )
        apps = [r for r in template["resources"] if r["type"] == "Microsoft.Web/sites"]
        settings = {
            item["name"]: item["value"]
            for item in apps[0]["properties"]["siteConfig"]["appSettings"]
        }
        self.assertEqual(settings["ENABLE_LLM"], "false")
        self.assertEqual(settings["TEAMS_ENABLED"], "false")
        self.assertEqual(settings["MAX_PAID_CALLS"], "70")
        self.assertFalse(
            any(
                r["type"].startswith("Microsoft.CognitiveServices")
                for r in template["resources"]
            )
        )
        self.assertNotIn("AZURE_OPENAI_API_KEY", settings)
