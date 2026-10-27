"""One App Service process: authenticated endpoint plus a serial queue worker.

Run `python -m channels.host`. With default flags it exposes health and rejects
Teams admissions, without connecting to Azure. Configure and test the real
channel before setting the enablement flags described in AZURE_SETUP.md.
"""

import asyncio
import os
import logging
from pathlib import Path
from aiohttp import web
from .teams import enabled, IdentityMap, Admission, Worker, create_app


def add_policy_routes(app):
    async def notice(request):
        name = (
            "PRIVACY_NOTICE_FILE" if request.path == "/privacy" else "TERMS_NOTICE_FILE"
        )
        path = os.getenv(name)
        if not path or not Path(path).is_file():
            return web.Response(
                status=503,
                text="The organization must configure its reviewed app notice before release.",
            )
        return web.Response(text=Path(path).read_text(), content_type="text/plain")

    app.router.add_get("/privacy", notice)
    app.router.add_get("/terms", notice)
    return app


def build_app():
    if not enabled():
        app = web.Application()

        async def health(request):
            return web.json_response({"status": "running", "teams_enabled": False})

        async def disabled(request):
            return web.Response(status=503, text="Teams is disabled.")

        app.router.add_get("/health", health)
        app.router.add_post("/api/messages", disabled)
        return add_policy_routes(app)
    from azure.identity import DefaultAzureCredential
    from azure.storage.queue import QueueClient
    from microsoft_agents.activity import Activity, ConversationReference
    from microsoft_agents.hosting.core import (
        AgentApplication,
        ApplicationOptions,
        AgentAuthConfiguration,
        AuthTypes,
    )
    from microsoft_agents.hosting.aiohttp import CloudAdapter
    from microsoft_agents.authentication.msal import MsalConnectionManager
    from databricks import sql
    from databricks.sdk.core import Config
    from runtime import create_core

    bot_id = os.environ["BOT_CLIENT_ID"]
    auth = AgentAuthConfiguration(
        auth_type=AuthTypes(os.getenv("BOT_AUTH_TYPE", "UserManagedIdentity")),
        client_id=bot_id,
        tenant_id=os.environ["BOT_TENANT_ID"],
        client_secret=os.getenv("BOT_CLIENT_SECRET"),
        anonymous_allowed=False,
        validate_issuer=True,
    )
    connections = MsalConnectionManager({"SERVICE_CONNECTION": auth})
    adapter = CloudAdapter(connection_manager=connections)
    agent = AgentApplication(
        options=ApplicationOptions(
            adapter=adapter, bot_app_id=bot_id, start_typing_timer=False
        ),
        connection_manager=connections,
    )
    credential = DefaultAzureCredential()
    queue = QueueClient(
        os.environ["QUEUE_ACCOUNT_URL"], os.environ["QUEUE_NAME"], credential=credential
    )
    poison = QueueClient(
        os.environ["QUEUE_ACCOUNT_URL"],
        os.environ["POISON_QUEUE_NAME"],
        credential=credential,
    )
    identities = IdentityMap(os.environ["IDENTITY_MAP_FILE"])
    config = Config()  # Supported Databricks unified authentication; no embedded PAT.
    connection = sql.connect(
        server_hostname=os.environ["DATABRICKS_SERVER_HOSTNAME"],
        http_path=os.environ["DATABRICKS_HTTP_PATH"],
        credentials_provider=lambda: config.authenticate,
        socket_timeout=30,
    )
    core = create_core("sql", "azure", sql_connection=connection)

    async def deliver(reference, text):
        saved = ConversationReference.model_validate(reference)
        activity = Activity(
            type="event", name="continueConversation"
        ).apply_conversation_reference(saved, is_incoming=True)

        async def send(context):
            for start in range(0, len(text), 5000):
                await context.send_activity(text[start : start + 5000])

        await adapter.continue_conversation(bot_id, activity, send)

    app = create_app(Admission(identities, queue), adapter, agent, auth)
    worker = Worker(core, identities, queue, poison, deliver)

    async def lifetime(app):
        async def work():
            while True:
                try:
                    await worker.once()
                except Exception as exc:
                    # A temporary Queue receive failure must not kill the only
                    # worker task. Log type only; service bodies can contain secrets.
                    logging.getLogger(__name__).warning(
                        "queue_receive_failed kind=%s", type(exc).__name__
                    )
                await asyncio.sleep(1)

        task = asyncio.create_task(work())
        yield
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        connection.close()
        queue.close()
        poison.close()
        credential.close()

    app.cleanup_ctx.append(lifetime)
    return add_policy_routes(app)


if __name__ == "__main__":
    web.run_app(build_app(), host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
