"""Optional development-only Genie comparison; never an authoritative fact tool.

The core does not import this module. Operators must approve a synthetic-only
space. Each HTTP request (including polls) uses the same paid-call budget as the
optional model. Pending provider IDs are saved for restart-safe polling.
"""

import copy
import re
import time
from urllib.parse import urlsplit
from state import ConflictError


class GenieHTTP:
    def __init__(self, host, auth_headers):
        parsed = urlsplit(host)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.path not in ("", "/")
            or parsed.username
            or parsed.query
            or parsed.fragment
        ):
            raise ValueError("Use an HTTPS Databricks workspace host.")
        self.host = host.rstrip("/")
        self.auth_headers = auth_headers

    def request(self, method, path, body=None):
        import requests

        # requests has no automatic status retries. TLS verification stays on.
        response = requests.request(
            method, self.host + path, headers=self.auth_headers(), json=body, timeout=15
        )
        response.raise_for_status()
        return response.json()


class GenieValidationAdapter:
    def __init__(
        self, transport, store, budget, space_id, approved_spaces=(), mode="off"
    ):
        if not re.fullmatch(r"[A-Za-z0-9_-]+", space_id):
            raise ValueError("Invalid Genie space ID.")
        self.transport, self.store, self.budget = transport, store, budget
        self.space_id, self.enabled = (
            space_id,
            mode == "validation" and space_id in approved_spaces,
        )

    def begin(self, principal, session_id, request_id, question):
        if not self.enabled:
            raise PermissionError(
                "Genie validation is disabled or its lab space is not approved."
            )
        if len(question.encode()) > 1000:
            raise ValueError("Use a short synthetic-data validation question.")
        doc = self.store.load(principal.owner, session_id)
        key = "genie:" + self.space_id
        mapping = doc["providers"].get(key, {})
        import hashlib

        signature = hashlib.sha256(question.encode()).hexdigest()
        if mapping.get("request_id") == request_id:
            if mapping.get("signature") != signature:
                raise ValueError(
                    "Provider request ID was reused with different content."
                )
            # UNKNOWN initiation is deliberately not resubmitted: the previous
            # POST may have succeeded even when its network response was lost.
            return mapping
        if mapping.get("status") in ("PENDING", "INITIATING", "UNKNOWN"):
            raise ConflictError(
                "Finish/recover the pending provider operation before sending another question."
            )
        old_conversation = mapping.get("conversation_id")
        pending = {
            "request_id": request_id,
            "signature": signature,
            "status": "INITIATING",
            "conversation_id": old_conversation,
        }
        doc["providers"][key] = pending
        self.store.commit(principal.owner, session_id, doc["revision"], doc)
        prefix = f"/api/2.0/genie/spaces/{self.space_id}"
        path = (
            f"{prefix}/conversations/{old_conversation}/messages"
            if old_conversation
            else f"{prefix}/start-conversation"
        )
        try:
            self.budget.reserve()
            response = self.transport.request("POST", path, {"content": question})
            pending.update(
                status="PENDING",
                conversation_id=response.get("conversation_id", old_conversation),
                message_id=response["message_id"],
            )
            if not pending["conversation_id"]:
                raise ValueError("Provider response did not include conversation ID.")
            if any(
                not re.fullmatch(r"[A-Za-z0-9_-]+", value)
                for value in (pending["conversation_id"], pending["message_id"])
            ):
                raise ValueError("Invalid provider operation identifier.")
        except Exception:
            pending["status"] = "UNKNOWN"
            self._save(principal, session_id, key, pending)
            raise
        self._save(principal, session_id, key, pending)
        return copy.deepcopy(pending)

    def poll(self, principal, session_id, max_polls=3, seconds=20):
        if not self.enabled:
            raise PermissionError("Genie validation is disabled.")
        key = "genie:" + self.space_id
        mapping = self.store.load(principal.owner, session_id)["providers"].get(key)
        if not mapping or not mapping.get("message_id"):
            raise ValueError("No recoverable provider message ID.")
        start = time.monotonic()
        for _ in range(min(5, max(0, max_polls))):
            if time.monotonic() - start >= min(30, seconds):
                break
            self.budget.reserve()
            path = f"/api/2.0/genie/spaces/{self.space_id}/conversations/{mapping['conversation_id']}/messages/{mapping['message_id']}"
            response = self.transport.request("GET", path)
            status = response.get("status", "UNKNOWN")
            mapping["status"] = status
            # Candidate text/SQL and raw query rows are deliberately not copied
            # into core state, model context, or business evidence.
            mapping["candidate_available"] = status == "COMPLETED"
            self._save(principal, session_id, key, mapping)
            if status in ("COMPLETED", "FAILED", "CANCELLED"):
                break
            time.sleep(0.2)
        return {
            **mapping,
            "authoritative": False,
            "scope": "approved synthetic validation only",
        }

    def compare(self, principal, session_id, candidate_metrics, deterministic_metrics):
        """Compare an operator-selected aggregate candidate, never replace facts."""
        if not self.enabled:
            raise PermissionError("Genie validation is disabled.")
        self.store.load(principal.owner, session_id)
        allowed = {"actual", "forecast", "wmape_pct", "accuracy_pct", "bias_pct"}
        if not candidate_metrics:
            raise ValueError("At least one actual candidate metric is required.")
        if set(candidate_metrics) - allowed:
            raise ValueError("Only approved aggregate metrics may be compared.")
        from business import number

        differences = {
            k: round(v - deterministic_metrics[k], 4)
            for k, v in candidate_metrics.items()
            if number(v)
            and number(deterministic_metrics.get(k))
            and abs(v - deterministic_metrics[k]) > 0.01
        }
        missing = [
            k
            for k in candidate_metrics
            if not number(candidate_metrics[k])
            or not number(deterministic_metrics.get(k))
        ]
        return {
            "matched": not differences and not missing,
            "differences": differences,
            "unavailable": missing,
            "authoritative": False,
        }

    def _save(self, principal, session_id, key, mapping):
        doc = self.store.load(principal.owner, session_id)
        if doc["providers"].get(key, {}).get("request_id") != mapping["request_id"]:
            raise ConflictError(
                "Provider request changed; do not overwrite its progress."
            )
        doc["providers"][key] = copy.deepcopy(mapping)
        self.store.commit(principal.owner, session_id, doc["revision"], doc)
