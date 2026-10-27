"""Personal-chat admission and durable worker, disabled until acceptance gates.

The Microsoft 365 Agents SDK authenticates inbound activity before this adapter
reads tenant/object IDs. An operator-controlled identity map supplies canonical
ownership and business grants. Display names and chat user_id fields are ignored.
"""

import asyncio
import hashlib
import json
import os
from pathlib import Path
from contracts import Principal, TurnRequest

REQUIRED_GATES = (
    "core_acceptance",
    "valid_token",
    "invalid_token",
    "personal_chat",
    "owner_isolation",
    "restart_recovery",
    "async_delivery",
    "state_cutover",
)


def enabled():
    if (
        os.getenv("TEAMS_ENABLED", "false").lower() != "true"
        or os.getenv("CHANNEL_MODE", "development") != "teams"
    ):
        return False
    path = os.getenv("TEAMS_ACCEPTANCE_REPORT")
    if not path:
        return False
    try:
        report = json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return False
    return isinstance(report, dict) and all(
        report.get(gate) is True for gate in REQUIRED_GATES
    )


class IdentityMap:
    """Read a trusted deployment file; never accept mappings from a chat message."""

    def __init__(self, path):
        self.path = path

    def resolve(self, tenant, object_id):
        mapping = json.loads(Path(self.path).read_text()).get(tenant + ":" + object_id)
        if not mapping or mapping.get("verified") is not True:
            raise PermissionError("A verified identity mapping is required.")
        principal = Principal.model_validate(mapping["principal"])
        if tenant != "databricks" and principal.tenant != tenant:
            raise PermissionError(
                "A channel identity cannot cross the canonical tenant boundary."
            )
        # Explicit mapping may join Databricks and Entra subjects to one internal
        # subject. Tenant separation is retained by the canonical principal.
        session = (
            mapping.get("session_id")
            or "teams-" + hashlib.sha256(principal.owner.encode()).hexdigest()[:32]
        )
        return principal, session


class Admission:
    def __init__(self, identity_map, queue):
        self.identities, self.queue = identity_map, queue

    async def accept(self, activity, authenticated=False):
        if not authenticated:
            raise PermissionError("SDK-authenticated activity is required.")
        if not enabled():
            raise PermissionError("Teams admissions are disabled.")
        if (
            str(activity.channel_id) != "msteams"
            or activity.conversation.conversation_type != "personal"
        ):
            raise PermissionError("Only approved Teams personal chats are supported.")
        tenant = activity.conversation.tenant_id
        subject = activity.from_property.aad_object_id
        # Authentication validates the channel token; the trusted Teams activity
        # supplies the Entra subject. We still require the reviewed allowlist.
        if not tenant or not subject:
            raise PermissionError("Missing authenticated Teams identity.")
        principal, session = self.identities.resolve(tenant, subject)
        request_id = hashlib.sha256(
            f"{tenant}:{activity.conversation.id}:{activity.id}".encode()
        ).hexdigest()
        if not activity.id:
            raise ValueError("A stable channel activity ID is required.")
        message = activity.text or ""
        case_id = None
        if message.startswith("/resume "):
            parts = message.split(" ", 2)
            if len(parts) != 3:
                raise ValueError("Use /resume CASE_ID question")
            case_id, message = parts[1:]
        request = TurnRequest(
            session_id=session,
            request_id=request_id,
            message=message,
            case_id=case_id,
            channel="teams",
        )
        envelope = {
            "tenant": tenant,
            "subject": subject,
            "owner": principal.owner,
            "request": request.model_dump(mode="json"),
            "reference": activity.get_conversation_reference().model_dump(
                mode="json", by_alias=True
            ),
        }
        # Completion of this durable send is the acceptance boundary. A crash
        # before it completes must not result in a user acknowledgement.
        await asyncio.to_thread(self.queue.send_message, json.dumps(envelope))
        return request_id


class Worker:
    def __init__(self, core, identities, queue, poison, deliver):
        self.core, self.identities, self.queue, self.poison, self.deliver = (
            core,
            identities,
            queue,
            poison,
            deliver,
        )

    async def once(self):
        messages = await asyncio.to_thread(
            lambda: list(
                self.queue.receive_messages(
                    messages_per_page=1, max_messages=1, visibility_timeout=180
                )
            )
        )
        for message in messages:
            try:
                envelope = json.loads(message.content)
                principal, session = self.identities.resolve(
                    envelope["tenant"], envelope["subject"]
                )
                if (
                    principal.owner != envelope["owner"]
                    or session != envelope["request"]["session_id"]
                ):
                    raise PermissionError(
                        "Identity mapping changed; operator recovery is required."
                    )
                answer = await asyncio.to_thread(
                    self.core.handle, principal, envelope["request"]
                )
                # The core durably saved the result before any outgoing notification.
                doc = self.core.store.load(principal.owner, session)
                request_id = envelope["request"]["request_id"]
                notified = doc.get("notifications", {}).get(request_id)
                if not notified:
                    await self.deliver(envelope["reference"], answer["response"])
                    doc = self.core.store.load(principal.owner, session)
                    doc.setdefault("notifications", {})[request_id] = "SENT"
                    self.core.store.commit(
                        principal.owner, session, doc["revision"], doc
                    )
                await asyncio.to_thread(self.queue.delete_message, message)
            except Exception:
                # Five failed deliveries move to an operator-owned poison queue.
                # Never silently delete accepted work. A successful send followed
                # by a failed notification commit can cause a duplicate reply.
                if message.dequeue_count >= 5:
                    await asyncio.to_thread(self.poison.send_message, message.content)
                    await asyncio.to_thread(self.queue.delete_message, message)


def create_app(admission, adapter, agent, auth_config):
    from aiohttp import web
    from microsoft_agents.hosting.aiohttp import (
        jwt_authorization_middleware,
        start_agent_process,
    )

    @web.middleware
    async def authentication(request, handler):
        if request.path != "/api/messages":
            return await handler(request)
        if not enabled():
            return web.Response(status=503, text="Teams is disabled.")
        return await jwt_authorization_middleware(request, handler)

    app = web.Application(middlewares=[authentication], client_max_size=65536)
    app["agent_configuration"] = auth_config

    @agent.message()
    async def message(context, state):
        # This handler is reached only through the SDK adapter after JWT checks.
        await admission.accept(context.activity, authenticated=True)
        await context.send_activity(
            "Accepted. I will reply when the saved investigation is complete."
        )

    async def messages(request):
        return await start_agent_process(request, agent, adapter)

    app.router.add_post("/api/messages", messages)
    app.router.add_get(
        "/health",
        lambda request: web.json_response(
            {"status": "running", "teams_enabled": enabled()}
        ),
    )
    return app
