"""Certified positive and negative cases for the previously unavailable lab drivers."""

import os
import tempfile
import unittest
from unittest.mock import patch
from business import BusinessService
from lab import local_provider, GLOBAL, END
from contracts import AnalysisPlan
from conversation import ConversationService
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
