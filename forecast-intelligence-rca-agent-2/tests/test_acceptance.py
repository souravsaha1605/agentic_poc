"""Offline acceptance tests. Any accidental external connection fails the suite."""

import copy
import socket
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import patch

from contracts import Principal, AnalysisPlan
from conversation import ConversationService
from business import BusinessService
from lab import (
    BRD_EXPECTED_SIGNALS,
    FIXTURE_GRAIN,
    generate,
    local_provider,
    certify,
    missing_fixture_rows,
    END,
)
from state import SQLiteStateStore, ConflictError
from cost_control import CallBudget, BudgetExceeded, EvidenceSelector
from tool_executor import ToolExecutor

ALICE = Principal(
    tenant="tenant-a",
    subject="alice",
    regions=("*",),
    products=("*",),
    categories=("*",),
)
BOB = Principal(
    tenant="tenant-a", subject="bob", regions=("*",), products=("*",), categories=("*",)
)


class AcceptanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.network_guard = patch.object(
            socket,
            "create_connection",
            side_effect=AssertionError("No network allowed in offline acceptance"),
        )
        cls.network_guard.start()
        cls.template = local_provider()

    @classmethod
    def tearDownClass(cls):
        cls.network_guard.stop()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.provider = copy.deepcopy(self.template)
        self.store = SQLiteStateStore(self.temp.name + "/state.db")
        self.core = ConversationService(
            BusinessService(self.provider, today=END), self.store
        )
        self.n = 0

    def turn(self, message, owner=ALICE, **extra):
        self.n += 1
        return self.core.handle(
            owner,
            {
                "session_id": "session-a",
                "request_id": str(self.n),
                "message": message,
                **extra,
            },
        )

    def plan(
        self, tool="get_forecast_context", product="P0001", region="North", **kwargs
    ):
        return AnalysisPlan(
            tool=tool, product_id=product, region=region, category="Dairy", **kwargs
        )

    def test_01_forecast_retrieval_is_scoped(self):
        answer = self.turn("What is the forecast for P0001?")
        self.assertEqual(answer["entity"]["product_id"], "P0001")
        metrics = answer["evidence"]["metrics"]
        self.assertEqual(metrics["forecast"], 1200)
        self.assertEqual(metrics["actual"], 1350)
        self.assertEqual(metrics["accuracy_pct"], 88.89)
        self.assertIn("period", answer["evidence"])

    def test_02_inventory_followup_reuses_context(self):
        first = self.turn("Analyze P0001 in North.")
        follow = self.turn("What about inventory?")
        self.assertEqual(first["scenario_id"], follow["scenario_id"])
        self.assertEqual(follow["evidence"]["inventory"], 300)
        self.assertEqual(follow["evidence"]["stockout_days"], None)

    def test_03_promotion_continues_rca(self):
        first = self.turn("Why is forecast accuracy deteriorating for P0001?")
        follow = self.turn("Was promotion a contributor?")
        self.assertEqual(first["scenario_id"], follow["scenario_id"])
        self.assertEqual(
            [h["cause"] for h in follow["evidence"]["hypotheses"]], ["promotion"]
        )
        self.assertEqual(follow["evidence"]["hypotheses"][0]["status"], "SUPPORTED")

    def test_04_new_entity_preserves_prior_case(self):
        first = self.turn("Analyze P0001 in North.")
        second = self.turn("Now analyze P0099 in West.")
        self.assertNotEqual(first["scenario_id"], second["scenario_id"])
        doc = self.store.load(ALICE.owner, "session-a")
        self.assertEqual(len(doc["cases"]), 2)
        self.assertEqual(
            doc["cases"][first["scenario_id"]]["entity"]["product_id"], "P0001"
        )

    def test_05_outcome_is_persisted_unverified(self):
        first = self.turn("Accuracy is poor for P0001.")
        outcome = self.turn("We changed the promotion last week and accuracy improved.")
        doc = self.store.load(ALICE.owner, "session-a")
        item = doc["cases"][first["scenario_id"]]["outcomes"][0]
        self.assertEqual(outcome["intent"], "OUTCOME_UPDATE")
        self.assertEqual(item["provenance"], "USER_REPORTED")
        self.assertFalse(item["verified"])

    def test_06_what_if_clones_and_keeps_baseline(self):
        first = self.turn("Analyze P0001 in North.")
        before = self.store.load(ALICE.owner, "session-a")["cases"][
            first["scenario_id"]
        ]
        result = self.turn("What if demand increases by 15%?")
        after = self.store.load(ALICE.owner, "session-a")["cases"][first["scenario_id"]]
        self.assertEqual(after["baseline"], before["baseline"])
        self.assertEqual(after["previous"], before["current"])
        self.assertEqual(after["versions"][0], before["versions"][0])
        self.assertEqual(result["evidence"]["current"]["demand"], 1552.5)
        evidence, _ = ConversationService.what_if(
            "What if demand increases by 15%?",
            {"baseline": {"demand": 100}, "current": {"demand": 100}},
        )
        self.assertEqual(evidence["current"]["demand"], 115)

    def test_07_ambiguous_coke_uses_master_candidates(self):
        result = self.turn("Analyze Coke.")
        self.assertEqual(result["intent"], "CLARIFICATION")
        self.assertIn("P0030/North", result["response"])
        self.assertIn("P0031/South", result["response"])
        self.assertEqual(len(self.store.load(ALICE.owner, "session-a")["cases"]), 0)

    def test_08_new_product_discloses_insufficient_history(self):
        result = self.turn("Perform RCA for New product.")
        self.assertTrue(
            all(
                h["status"] == "NOT_TESTABLE"
                for h in result["evidence"]["hypotheses"]
                if h["cause"] != "quality"
            )
        )
        self.assertEqual(result["evidence"]["data_quality"]["weeks"], 2)

    def test_09_stockout_distortion_is_qualified(self):
        result = self.turn(
            "Could inventory have caused the drop in sales for P0020 in North?"
        )
        hyp = result["evidence"]["hypotheses"][0]
        self.assertEqual(hyp["status"], "SUPPORTED")
        self.assertIn("inventory-censored", result["response"])
        self.assertEqual(hyp["evidence"]["metric"]["stockout_snapshots"], 6)

    def test_10_new_revenue_topic_creates_case(self):
        first = self.turn("Analyze P0001 in North.")
        second = self.turn("What is the revenue for P0099 in West?")
        self.assertNotEqual(first["scenario_id"], second["scenario_id"])
        self.assertEqual(second["intent"], "REVENUE_RETRIEVAL")

    def test_restart_resumes_owned_case_and_period(self):
        first = self.turn("Analyze P0001 in North from 2026-08-02 to 2026-09-27.")
        self.core = ConversationService(
            BusinessService(self.provider, today=END),
            SQLiteStateStore(self.temp.name + "/state.db"),
        )
        second = self.turn("What about revenue?")
        self.assertEqual(first["scenario_id"], second["scenario_id"])
        self.assertEqual(second["evidence"]["period"]["start"], "2026-08-02")

    def test_other_user_cannot_load_or_append_session(self):
        self.turn("Analyze P0001 in North.")
        with self.assertRaises(PermissionError):
            self.turn("What about inventory?", owner=BOB)
        with self.assertRaises(PermissionError):
            self.store.delete(BOB.owner, "session-a")

    def test_other_tenant_is_isolated(self):
        self.turn("Analyze P0001 in North.")
        stranger = ALICE.model_copy(update={"tenant": "tenant-b"})
        with self.assertRaises(PermissionError):
            self.turn("What about inventory?", owner=stranger)

    def test_entitlements_apply_before_retrieval(self):
        restricted = ALICE.model_copy(update={"regions": ("South",)})
        result = self.turn("Analyze P0001 in North.", owner=restricted)
        self.assertEqual(result["intent"], "CLARIFICATION")
        self.assertNotIn("metrics", result)

    def test_revoked_entitlements_prevent_receipt_replay(self):
        self.turn("Analyze P0001 in North.")
        restricted = ALICE.model_copy(update={"regions": ("South",)})
        with self.assertRaises(PermissionError):
            self.core.handle(
                restricted,
                {
                    "session_id": "session-a",
                    "request_id": "1",
                    "message": "Analyze P0001 in North.",
                },
            )

    def test_duplicate_request_is_idempotent(self):
        request = {
            "session_id": "dup",
            "request_id": "same",
            "message": "Analyze P0001 in North.",
        }
        first = self.core.handle(ALICE, request)
        second = self.core.handle(ALICE, request)
        self.assertEqual(first, second)
        self.assertEqual(len(self.store.load(ALICE.owner, "dup")["turns"]), 1)
        with self.assertRaises(ValueError):
            self.core.handle(ALICE, {**request, "message": "Different prompt"})

    def test_optimistic_conflict_does_not_lose_versions(self):
        doc = self.store.load(ALICE.owner, "new")
        self.store.commit(ALICE.owner, "new", 0, doc)
        with self.assertRaises(ConflictError):
            self.store.commit(ALICE.owner, "new", 0, doc)
        self.assertEqual(self.store.load(ALICE.owner, "new")["revision"], 1)

    def test_expected_version_checked(self):
        self.turn("Analyze P0001 in North.")
        with self.assertRaises(ConflictError):
            self.turn("What about revenue?", expected_version=0)

    def test_resume_selected_owned_case(self):
        first = self.turn("Analyze P0001 in North.")
        self.turn("Analyze P0099 in West.")
        resumed = self.turn("What about inventory?", case_id=first["scenario_id"])
        self.assertEqual(resumed["scenario_id"], first["scenario_id"])
        with self.assertRaises(PermissionError):
            self.turn("hello", case_id="SCN-does-not-exist")

    def test_changed_region_starts_new_case_without_magic_phrase(self):
        # Add a real master/data scope; do not infer a region from an arbitrary row.
        rows = [
            {**r, "region": "South"}
            for r in self.provider.rows
            if r["product_id"] == "P0001"
        ]
        self.provider.rows += rows
        self.provider.products.append(
            {
                "product_id": "P0001",
                "product_name": "Dairy regular",
                "region": "South",
                "category": "Dairy",
            }
        )
        first = self.turn("Analyze P0001 in North.")
        second = self.turn("Analyze P0001 in South.")
        self.assertNotEqual(first["scenario_id"], second["scenario_id"])

    def test_distinct_p001_not_normalized(self):
        result = self.turn("Analyze P001 in South.")
        self.assertEqual(result["entity"]["product_id"], "P001")
        self.assertEqual(result["evidence"]["metrics"]["accuracy_pct"], 100)

    def test_unknown_id_cannot_inherit_previous_product(self):
        self.turn("Analyze P0001 in North.")
        result = self.turn("Analyze P9999 in North.")
        self.assertEqual(result["intent"], "CLARIFICATION")

    def test_inventory_historical_cutoff_never_uses_future_snapshot(self):
        result = self.core.business.execute(
            self.plan(
                "get_inventory_context", product="P0020", as_of=date(2026, 7, 26)
            ),
            ALICE,
        )
        self.assertEqual(result["inventory"], 300)
        self.assertEqual(result["snapshot_dates"], ["2026-07-26"])

    def test_inventory_staleness_and_timestamp_conflict(self):
        rows = [r for r in self.provider.rows if r["product_id"] == "P0001"]
        for r in rows:
            r["inventory_timestamp"] = "2020-01-01"
        result = self.core.business.execute(
            self.plan("get_inventory_context", as_of=END), ALICE
        )
        self.assertEqual(result["freshness"], "CONFLICT")

    def test_inventory_null_is_unavailable_not_zero(self):
        for r in self.provider.rows:
            if r["product_id"] == "P0001":
                r["inventory_level"] = None
        result = self.core.business.execute(
            self.plan("get_inventory_context", as_of=END), ALICE
        )
        self.assertIsNone(result["inventory"])
        self.assertEqual(result["availability"], "UNAVAILABLE")

    def test_revenue_discount_is_percent_and_gross_is_not_net_fallback(self):
        result = self.core.business.execute(self.plan("get_revenue_context"), ALICE)
        self.assertEqual(result["gross_revenue"], 13500)
        self.assertEqual(result["net_revenue"], 12825)
        for r in self.provider.rows:
            if r["product_id"] == "P0001":
                r["discount"] = None
        missing = self.core.business.execute(self.plan("get_revenue_context"), ALICE)
        self.assertIsNone(missing["net_revenue"])
        self.assertIsNone(missing["primary_revenue"])
        self.assertEqual(missing["gross_revenue"], 13500)

    def test_mixed_currencies_are_not_added(self):
        self.provider.rows[0]["currency"] = "USD"
        plan = self.plan("get_revenue_context", lookback_weeks=60)
        self.assertIsNone(self.core.business.execute(plan, ALICE)["net_revenue"])

    def test_multiple_vintages_do_not_double_count_actuals(self):
        rows = [
            {
                **r,
                "forecast_generated_date": str(
                    date.fromisoformat(r["date"]) - timedelta(days=14)
                ),
                "demand_forecast": 50.0,
            }
            for r in self.provider.rows
            if r["product_id"] == "P0001"
        ]
        self.provider.rows += rows
        result = self.core.business.execute(self.plan(), ALICE)
        self.assertEqual(result["metrics"]["actual"], 1350)
        self.assertEqual(result["metrics"]["forecast"], 1200)

    def test_duplicate_grain_rejected(self):
        self.provider.rows.append(
            copy.deepcopy(
                [r for r in self.provider.rows if r["product_id"] == "P0001"][-1]
            )
        )
        result = self.turn("Analyze P0001 in North.")
        self.assertFalse(result["success"])
        self.assertEqual(result["error_code"], "DATA_UNAVAILABLE")

    def test_zero_actuals_do_not_invent_accuracy(self):
        metrics = BusinessService.forecast([{"units_sold": 0, "demand_forecast": 100}])
        self.assertIsNone(metrics["wmape_pct"])
        self.assertIsNone(metrics["accuracy_pct"])
        self.assertEqual(metrics["forecast"], 100)

    def test_negative_accuracy_is_not_clamped(self):
        self.assertEqual(
            BusinessService.forecast([{"units_sold": 10, "demand_forecast": 100}])[
                "accuracy_pct"
            ],
            -800,
        )

    def test_returns_use_absolute_actual_denominator(self):
        result = BusinessService.forecast(
            [
                {"units_sold": -10, "demand_forecast": 10},
                {"units_sold": 20, "demand_forecast": 20},
            ]
        )
        self.assertEqual(result["wmape_pct"], 66.67)

    def test_not_testable_external_driver_is_explicit(self):
        answer = self.turn("Was competitor pricing a contributor for P0001 in North?")
        self.assertEqual(answer["evidence"]["hypotheses"][0]["status"], "NOT_TESTABLE")

    def test_failed_readiness_is_blocked_not_ready(self):
        for r in self.provider.registry:
            if r["product_id"] == "P0001" and r["capability"] == "promotion":
                r["validation"] = "FAIL"
        answer = self.turn("Was promotion a contributor for P0001 in North?")
        hyp = answer["evidence"]["hypotheses"][0]
        self.assertEqual(hyp["readiness"], "BLOCKED")
        self.assertEqual(hyp["status"], "NOT_TESTABLE")

    def test_stale_readiness_requires_refresh(self):
        for r in self.provider.registry:
            r["validated_at"] = "2020-01-01T00:00:00+00:00"
        result = self.turn("Was promotion a contributor for P0001 in North?")
        self.assertEqual(result["evidence"]["hypotheses"][0]["readiness"], "STALE")

    def test_source_version_mismatch_not_certified(self):
        self.provider.source_version = "new-uncertified-version"
        result = self.turn("Was promotion a contributor for P0001 in North?")
        self.assertEqual(
            result["evidence"]["hypotheses"][0]["readiness"], "NOT_TESTABLE"
        )

    def test_golden_certification_observes_signals_and_is_repeatable(self):
        self.assertFalse(any(r["validation"] == "FAIL" for r in self.provider.registry))
        before = copy.deepcopy(self.provider.rows)
        certify(self.provider)
        self.assertEqual(self.provider.rows, before)
        broken = certify(self.provider, expectations={("P001", "bias"): "SUPPORTED"})
        self.assertTrue(
            any(r["status"] == "BLOCKED" and r["validation"] == "FAIL" for r in broken)
        )

    def test_brd_signal_contract_and_missing_rows_preserve_existing_grains(self):
        generated, _ = generate()
        existing = copy.deepcopy(generated[:-5])
        existing[0]["units_sold"] = 999.0
        additions = missing_fixture_rows(existing, generated)
        self.assertEqual(len(additions), 5)
        self.assertEqual(existing[0]["units_sold"], 999.0)
        self.assertEqual(
            len({tuple(str(r.get(k)) for k in FIXTURE_GRAIN) for r in generated}),
            len(generated),
        )
        self.assertEqual(BRD_EXPECTED_SIGNALS[("P0001", "promotion")], "SUPPORTED")
        self.assertEqual(BRD_EXPECTED_SIGNALS[("P0020", "inventory")], "SUPPORTED")

    def test_all_required_patterns_have_meaningful_outputs(self):
        result = self.core.business.execute(
            self.plan("analyze_historical_pattern", product="P0040"), ALICE
        )
        self.assertEqual(result["patterns"]["trend"], "up")
        intermittent = self.core.business.execute(
            self.plan("analyze_historical_pattern", product="P0082"), ALICE
        )
        self.assertGreater(intermittent["patterns"]["intermittency_ratio"], 0.5)
        seasonal = self.core.business.execute(
            self.plan(
                "run_forecast_rca",
                product="P0060",
                lookback_weeks=60,
                hypotheses=["seasonality"],
            ),
            ALICE,
        )
        self.assertEqual(seasonal["hypotheses"][0]["status"], "SUPPORTED")

    def test_arbitrary_tools_and_fields_are_rejected(self):
        executor = ToolExecutor(self.core.business, ALICE, max_tool_calls=1)
        with self.assertRaises(ValueError):
            executor.execute("execute_sql", {"sql": "DROP TABLE fact"})
        with self.assertRaises(ValueError):
            executor.execute(
                "get_forecast_context",
                {"product_id": "P0001", "region": "North", "sql": "SELECT *"},
            )

    def test_message_and_window_bounds(self):
        with self.assertRaises(ValueError):
            self.turn("x" * 2001)
        with self.assertRaises(ValueError):
            self.plan(lookback_weeks=10000)
        with self.assertRaises(ValueError):
            self.plan(start=date(2026, 9, 1), end=date(2026, 8, 1))

    def test_original_what_if_price_and_inventory(self):
        self.turn("Analyze P0001 in North.")
        self.turn("What about revenue?")
        self.turn("What about inventory?")
        price = self.turn("What if price increases by 5%?")
        self.assertEqual(price["evidence"]["current"]["price"], 10.5)
        inventory = self.turn("What if inventory decreases by 20%?")
        self.assertEqual(inventory["evidence"]["current"]["inventory"], 240)
        # Arithmetic price change must not silently recalculate demand.
        self.assertEqual(price["evidence"]["current"]["demand"], 1350)

    def test_retrieving_facts_does_not_erase_what_if_assumptions(self):
        first = self.turn("Analyze P0001 in North.")
        self.turn("What about revenue?")
        self.turn("What if price increases by 5%?")
        self.turn("What about revenue?")
        case = self.store.load(ALICE.owner, "session-a")["cases"][first["scenario_id"]]
        self.assertEqual(case["current"]["price"], 10.5)
        self.assertEqual(case["facts"]["price"], 10.0)
        self.assertEqual(case["assumptions"]["price"]["change_pct"], 5.0)

    def test_unknown_what_if_assumptions_clarify(self):
        self.turn("Analyze P0001 in North.")
        result = self.turn("What if price increases by 5%?")
        self.assertEqual(result["intent"], "CLARIFICATION")

    def test_model_is_optional_and_cannot_invent_facts(self):
        self.core.selector = SimpleNamespace(select=lambda facts: ["does-not-exist"])
        # The selector normally validates IDs. The renderer also treats a bad
        # selector implementation as untrusted rather than using unknown values.
        result = self.turn("Analyze P0001 in North.")
        self.assertEqual(result["evidence"]["metrics"]["forecast"], 1200)
        self.assertNotIn("does-not-exist", result["response"])


class CostTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def test_persistent_ceiling_is_seventy_even_after_restart(self):
        path = self.temp.name + "/budget.db"
        budget = CallBudget(path, limit=999)
        for _ in range(70):
            budget.reserve()
        self.assertEqual(budget.used, 70)
        with self.assertRaises(BudgetExceeded):
            CallBudget(path).reserve()

    def test_concurrent_reservations_cannot_overspend(self):
        path = self.temp.name + "/budget.db"
        budget = CallBudget(path, limit=7)

        def reserve(_):
            try:
                budget.reserve()
                return True
            except BudgetExceeded:
                return False

        with ThreadPoolExecutor(max_workers=8) as pool:
            self.assertEqual(sum(pool.map(reserve, range(30))), 7)
        self.assertEqual(budget.used, 7)

    def test_failure_consumes_one_reservation_and_no_retry(self):
        budget = CallBudget(self.temp.name + "/budget.db")
        calls = []

        def fail(**kwargs):
            calls.append(kwargs)
            raise RuntimeError("simulated network failure")

        selector = EvidenceSelector(
            SimpleNamespace(responses=SimpleNamespace(create=fail)), "test", budget
        )
        with self.assertRaises(RuntimeError):
            selector.select({"metric": "forecast 100"})
        self.assertEqual(budget.used, 1)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["max_output_tokens"], 150)

    def test_oversized_prompts_do_not_make_a_call(self):
        budget = CallBudget(self.temp.name + "/budget.db")
        selector = EvidenceSelector(None, "test", budget)
        with self.assertRaises(ValueError):
            selector.select({"data": "words " * 5000})
        self.assertEqual(budget.used, 0)

    def test_hallucinated_fact_ids_are_rejected(self):
        budget = CallBudget(self.temp.name + "/budget.db")
        client = SimpleNamespace(
            responses=SimpleNamespace(
                create=lambda **kw: SimpleNamespace(output_text='{"ids":["invented"]}')
            )
        )
        with self.assertRaises(ValueError):
            EvidenceSelector(client, "test", budget).select({"metrics": "100"})


if __name__ == "__main__":
    unittest.main()
