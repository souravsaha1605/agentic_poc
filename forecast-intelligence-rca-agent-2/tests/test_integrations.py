"""Boundaries tested with local doubles; cloud provisioning is deliberately deferred."""

import copy
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from analytics import AnalyticalQueryCompiler, PlanValidator
from state import SQLiteStateStore
from contracts import Principal
from cost_control import CallBudget
from genie_validation import GenieValidationAdapter

USER = Principal(
    tenant="tenant",
    subject="canonical-user",
    regions=("North",),
    products=("P0001",),
    categories=("Dairy",),
)


class CompilerTests(unittest.TestCase):
    def setUp(self):
        self.plan = {
            "analysis_type": "FORECAST_PERFORMANCE",
            "grain": "SKU",
            "metrics": ["actual", "forecast"],
            "filters": [
                {"field": "REGION", "operator": "=", "value": "North' OR 1=1 --"}
            ],
            "lookback_weeks": 12,
        }

    def test_sql_values_are_bound_not_interpolated(self):
        sql = AnalyticalQueryCompiler.compile(self.plan, "2026-01-01", "2026-09-27")
        self.assertNotIn("OR 1=1", str(sql))
        self.assertEqual(sql.parameters["filter_0"], "North' OR 1=1 --")
        self.assertIn("LIMIT 100", str(sql))

    def test_unknown_identifiers_rejected_even_without_tool_layer(self):
        for field, value in [
            ("grain", "DROP TABLE"),
            ("metrics", ["password"]),
            ("analysis_type", "anything"),
        ]:
            plan = {**self.plan, field: value}
            with self.assertRaises(ValueError):
                AnalyticalQueryCompiler.compile(plan, "2026-01-01", "2026-09-27")

    def test_inventory_averaging_and_fake_stockout_days_rejected(self):
        for metric in ("inventory_level", "stockout_days"):
            self.assertFalse(
                PlanValidator.validate({**self.plan, "metrics": [metric]})["valid"]
            )

    def test_cumulative_share_includes_boundary_item(self):
        plan = {
            **self.plan,
            "metrics": ["actual"],
            "cumulative_share": {"metric": "actual", "threshold": 0.8},
        }
        sql = AnalyticalQueryCompiler.compile(plan, "2026-01-01", "2026-09-27")
        self.assertIn("(_cum_sum - actual)", sql)


class GenieTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = SQLiteStateStore(self.temp.name + "/state.db")
        self.budget = CallBudget(self.temp.name + "/budget.db")
        self.calls = []

        def request(method, path, body=None):
            self.calls.append((method, path, body))
            return (
                {"conversation_id": "conv", "message_id": "msg"}
                if method == "POST"
                else {"status": "COMPLETED", "content": "untrusted SQL and raw rows"}
            )

        self.transport = SimpleNamespace(request=request)
        self.adapter = GenieValidationAdapter(
            self.transport,
            self.store,
            self.budget,
            "lab-space",
            ("lab-space",),
            "validation",
        )

    def test_default_disabled_does_not_make_call(self):
        disabled = GenieValidationAdapter(
            self.transport, self.store, self.budget, "lab-space"
        )
        with self.assertRaises(PermissionError):
            disabled.begin(USER, "session", "request", "short question")
        self.assertEqual(self.budget.used, 0)

    def test_provider_thread_persists_and_followup_reuses_it(self):
        first = self.adapter.begin(
            USER, "session", "request-1", "Compare P0001 forecast"
        )
        self.assertEqual(first["conversation_id"], "conv")
        restored = GenieValidationAdapter(
            self.transport,
            SQLiteStateStore(self.temp.name + "/state.db"),
            self.budget,
            "lab-space",
            ("lab-space",),
            "validation",
        )
        result = restored.poll(USER, "session")
        self.assertFalse(result["authoritative"])
        self.assertNotIn("content", result)
        restored.begin(USER, "session", "request-2", "Follow-up")
        self.assertIn("/conversations/conv/messages", self.calls[-1][1])
        self.assertEqual(self.budget.used, 3)

    def test_retry_does_not_restart_provider_operation(self):
        first = self.adapter.begin(USER, "session", "same", "short question")
        second = self.adapter.begin(USER, "session", "same", "short question")
        self.assertEqual(first, second)
        self.assertEqual(len(self.calls), 1)

    def test_unknown_post_outcome_is_not_blindly_retried(self):
        def fail(*args):
            raise TimeoutError("simulated")

        self.transport.request = fail
        with self.assertRaises(TimeoutError):
            self.adapter.begin(USER, "session", "same", "short")
        result = self.adapter.begin(USER, "session", "same", "short")
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertEqual(self.budget.used, 1)

    def test_candidate_mismatch_never_changes_core_facts(self):
        expected = {"actual": 100.0}
        result = self.adapter.compare(USER, "session", {"actual": 999.0}, expected)
        self.assertFalse(result["matched"])
        self.assertEqual(expected, {"actual": 100.0})


HAS_AGENTS = importlib.util.find_spec("microsoft_agents") is not None


@unittest.skipUnless(HAS_AGENTS, "Optional Teams SDK not installed")
class ChannelTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.map = Path(self.temp.name) / "identities.json"
        self.map.write_text(
            json.dumps(
                {
                    "tenant:object": {
                        "verified": True,
                        "principal": USER.model_dump(mode="json"),
                        "session_id": "owned-session",
                    }
                }
            )
        )
        self.gates = Path(self.temp.name) / "gates.json"
        from channels.teams import REQUIRED_GATES

        self.gates.write_text(json.dumps(dict.fromkeys(REQUIRED_GATES, True)))
        self.environment = patch.dict(
            os.environ,
            {
                "CHANNEL_MODE": "teams",
                "TEAMS_ENABLED": "true",
                "TEAMS_ACCEPTANCE_REPORT": str(self.gates),
            },
        )
        self.environment.start()
        self.addCleanup(self.environment.stop)
        from microsoft_agents.activity import (
            Activity,
            ChannelAccount,
            ConversationAccount,
        )

        self.activity = Activity(
            type="message",
            channelId="msteams",
            id="activity",
            text="Analyze P0001 in North.",
            serviceUrl="https://smba.trafficmanager.net/teams/",
            from_property=ChannelAccount(id="ignored", aadObjectId="object"),
            recipient=ChannelAccount(id="bot"),
            conversation=ConversationAccount(
                id="channel-conversation",
                conversationType="personal",
                tenantId="tenant",
            ),
        )

    async def test_sdk_authentication_and_personal_scope_are_mandatory(self):
        from channels.teams import Admission, IdentityMap

        queue = SimpleNamespace(send_message=lambda message: None)
        admission = Admission(IdentityMap(self.map), queue)
        with self.assertRaises(PermissionError):
            await admission.accept(self.activity)
        self.activity.conversation.conversation_type = "groupChat"
        with self.assertRaises(PermissionError):
            await admission.accept(self.activity, authenticated=True)

    async def test_durable_queue_is_written_before_acceptance(self):
        from channels.teams import Admission, IdentityMap

        messages = []
        admission = Admission(
            IdentityMap(self.map), SimpleNamespace(send_message=messages.append)
        )
        await admission.accept(self.activity, authenticated=True)
        envelope = json.loads(messages[0])
        self.assertEqual(envelope["owner"], USER.owner)
        self.assertEqual(envelope["request"]["session_id"], "owned-session")
        self.assertNotIn("ignored", envelope["owner"])

    async def test_failed_durable_send_does_not_accept(self):
        from channels.teams import Admission, IdentityMap

        def fail(message):
            raise RuntimeError("queue unavailable")

        admission = Admission(IdentityMap(self.map), SimpleNamespace(send_message=fail))
        with self.assertRaises(RuntimeError):
            await admission.accept(self.activity, authenticated=True)

    async def test_disabled_rejects_new_admissions(self):
        from channels.teams import Admission, IdentityMap

        with patch.dict(os.environ, {"TEAMS_ENABLED": "false"}):
            with self.assertRaises(PermissionError):
                await Admission(IdentityMap(self.map), None).accept(
                    self.activity, authenticated=True
                )

    async def test_disabled_host_health_and_admission(self):
        from aiohttp.test_utils import TestClient, TestServer
        from channels.host import build_app

        with patch.dict(os.environ, {"TEAMS_ENABLED": "false"}):
            client = TestClient(TestServer(build_app()))
            await client.start_server()
            try:
                health = await client.get("/health")
                self.assertEqual(health.status, 200)
                rejected = await client.post("/api/messages", json={})
                self.assertEqual(rejected.status, 503)
            finally:
                await client.close()

    async def test_explicit_lab_backend_preserves_azure_state(self):
        from channels.host import create_facts_core

        with (
            patch.dict(os.environ, {"FACTS_BACKEND": "lab"}),
            patch("runtime.create_core", return_value="lab-core") as create_core,
        ):
            core, connection = create_facts_core()
        self.assertEqual(core, "lab-core")
        self.assertIsNone(connection)
        create_core.assert_called_once_with("lab", "azure")

    async def test_unknown_facts_backend_is_rejected(self):
        from channels.host import create_facts_core

        with patch.dict(os.environ, {"FACTS_BACKEND": "unknown"}):
            with self.assertRaisesRegex(ValueError, "sql.*lab"):
                create_facts_core()

    async def test_missing_and_malformed_jwt_rejected_without_backend(self):
        from aiohttp.test_utils import TestClient, TestServer
        from channels.teams import create_app
        from microsoft_agents.hosting.core import AgentAuthConfiguration, AuthTypes

        class NoHandler:
            def message(self):
                return lambda handler: handler

        auth = AgentAuthConfiguration(
            auth_type=AuthTypes.client_secret,
            client_id="00000000-0000-0000-0000-000000000001",
            tenant_id="00000000-0000-0000-0000-000000000002",
            client_secret="offline-test-only",
            anonymous_allowed=False,
        )
        client = TestClient(TestServer(create_app(None, None, NoHandler(), auth)))
        await client.start_server()
        try:
            for headers in ({}, {"Authorization": "not-a-bearer-token"}):
                response = await client.post("/api/messages", json={}, headers=headers)
                self.assertEqual(response.status, 401)
        finally:
            await client.close()


class MigrationTests(unittest.TestCase):
    def test_cutover_preserves_versions_owner_receipts_and_checksums(self):
        from state_migration import export_sessions, import_sessions, checksum
        from conversation import ConversationService
        from business import BusinessService
        from lab import local_provider, END

        with tempfile.TemporaryDirectory() as folder:
            source = SQLiteStateStore(folder + "/source.db")
            target = SQLiteStateStore(folder + "/target.db")
            core = ConversationService(
                BusinessService(local_provider(), today=END), source
            )
            core.handle(
                USER,
                {
                    "session_id": "cutover",
                    "request_id": "one",
                    "message": "Analyze P0001 in North.",
                },
            )
            core.handle(
                USER,
                {
                    "session_id": "cutover",
                    "request_id": "two",
                    "message": "What if demand increases by 15%?",
                },
            )
            archive = export_sessions(source, USER, ["cutover"])
            self.assertEqual(import_sessions(target, USER, archive), ["cutover"])
            self.assertEqual(
                checksum(source.load(USER.owner, "cutover")),
                checksum(target.load(USER.owner, "cutover")),
            )
            with self.assertRaises(ValueError):
                import_sessions(target, USER, archive)
            tampered = copy.deepcopy(archive)
            tampered["sessions"][0]["document"]["revision"] = 1000
            with self.assertRaises(ValueError):
                import_sessions(SQLiteStateStore(folder + "/other.db"), USER, tampered)


@unittest.skipUnless(HAS_AGENTS, "Optional Teams SDK not installed")
class WorkerTests(unittest.IsolatedAsyncioTestCase):
    async def test_queue_redelivery_reuses_saved_result_without_duplicate_notification(
        self,
    ):
        from channels.teams import Worker
        from conversation import ConversationService
        from business import BusinessService
        from lab import local_provider, END

        with tempfile.TemporaryDirectory() as folder:
            store = SQLiteStateStore(folder + "/state.db")
            core = ConversationService(
                BusinessService(local_provider(), today=END), store
            )
            envelope = {
                "tenant": "tenant",
                "subject": "object",
                "owner": USER.owner,
                "request": {
                    "session_id": "session",
                    "request_id": "stable-request",
                    "message": "Analyze P0001 in North.",
                    "channel": "teams",
                },
                "reference": {"conversation": "saved"},
            }
            message = SimpleNamespace(content=json.dumps(envelope), dequeue_count=1)
            deleted = []
            queue = SimpleNamespace(
                receive_messages=lambda **kwargs: [message],
                delete_message=deleted.append,
            )
            deliveries = []

            async def deliver(reference, text):
                deliveries.append(text)

            identities = SimpleNamespace(
                resolve=lambda tenant, subject: (USER, "session")
            )
            worker = Worker(
                core,
                identities,
                queue,
                SimpleNamespace(send_message=lambda content: None),
                deliver,
            )
            await worker.once()
            await worker.once()
            self.assertEqual(len(deliveries), 1)
            self.assertEqual(len(deleted), 2)
            self.assertEqual(len(store.load(USER.owner, "session")["turns"]), 1)

    async def test_poison_request_is_preserved_after_five_failures(self):
        from channels.teams import Worker

        message = SimpleNamespace(content="invalid-json", dequeue_count=5)
        deleted, poison = [], []
        queue = SimpleNamespace(
            receive_messages=lambda **kwargs: [message], delete_message=deleted.append
        )
        worker = Worker(
            None, None, queue, SimpleNamespace(send_message=poison.append), None
        )
        await worker.once()
        self.assertEqual(poison, ["invalid-json"])
        self.assertEqual(deleted, [message])


class BudgetCutoverTests(unittest.TestCase):
    def test_spent_calls_are_transferred_not_reset(self):
        from state_migration import transfer_paid_budget
        from cost_control import BudgetExceeded

        with tempfile.TemporaryDirectory() as folder:
            source = CallBudget(folder + "/old.db")
            target = CallBudget(folder + "/new.db")
            source.reserve()
            source.reserve()
            self.assertEqual(transfer_paid_budget(source, target), 2)
            self.assertEqual(target.used, 2)
            with self.assertRaises(BudgetExceeded):
                transfer_paid_budget(source, target)
