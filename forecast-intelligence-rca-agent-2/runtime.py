"""Explicit runtime composition; synthetic data is never a production fallback."""

import os
from pathlib import Path
from business import BusinessService
from conversation import ConversationService
from state import SQLiteStateStore, DeltaStateStore, AzureBlobStateStore
from cost_control import CallBudget, BlobCallBudget, DeltaCallBudget, EvidenceSelector


def create_core(backend="lab", state_backend="sqlite", spark=None, sql_connection=None):
    if os.getenv("FACTS_PROVIDER", "deterministic") != "deterministic":
        raise ValueError("Only the deterministic facts provider is supported.")
    root = Path(
        os.getenv(
            "FORECAST_STATE_DIR", str(Path(__file__).resolve().parent / ".rca_state")
        )
    )
    database = os.getenv("FORECAST_DATABASE", "workspace.forecast_rca_lab")
    if backend == "lab":
        from lab import local_provider

        provider = local_provider()
    else:
        from data_access import GovernedProvider, SparkQuery, DatabricksSQLQuery

        if backend == "spark":
            if spark is None:
                from pyspark.sql import SparkSession

                spark = SparkSession.getActiveSession()
            if spark is None:
                raise ValueError(
                    "Create a Spark session before selecting the notebook adapter."
                )
            query = SparkQuery(spark)
        elif backend == "sql":
            if sql_connection is None:
                raise ValueError(
                    "Pass an authenticated Databricks SQL connection; no notebook session is inherited."
                )
            query = DatabricksSQLQuery(sql_connection)
        else:
            raise ValueError("Choose lab, spark or sql explicitly.")
        provider = GovernedProvider(query, database)
    if state_backend == "sqlite":
        store = SQLiteStateStore(root / "sessions.sqlite3")
        budget = CallBudget(
            root / "paid-calls.sqlite3", os.getenv("MAX_PAID_CALLS", "70")
        )
    elif state_backend == "delta":
        if spark is None:
            raise ValueError("Delta state requires a Spark session.")
        store = DeltaStateStore(
            spark,
            os.getenv("FORECAST_STATE_TABLE", f"{database}.rca_owned_sessions"),
        )
        budget = DeltaCallBudget(
            spark,
            os.getenv(
                "FORECAST_BUDGET_TABLE",
                f"{database}.rca_paid_call_ledger",
            ),
            os.getenv("MAX_PAID_CALLS", "70"),
        )
    elif state_backend == "azure":
        from azure.identity import DefaultAzureCredential
        from azure.storage.blob import BlobServiceClient

        account = os.environ["STATE_BLOB_ACCOUNT_URL"]
        client = BlobServiceClient(account, credential=DefaultAzureCredential())
        container = client.get_container_client(os.environ["STATE_BLOB_CONTAINER"])
        store = AzureBlobStateStore(container)
        budget = BlobCallBudget(
            container.get_blob_client("global-paid-call-ledger.json"),
            os.getenv("MAX_PAID_CALLS", "70"),
        )
    else:
        raise ValueError("Choose sqlite, delta or azure state.")
    selector = None
    if os.getenv("ENABLE_LLM", "false").lower() == "true":
        from client import get_client

        from client import runtime_setting

        deployment = runtime_setting("AZURE_OPENAI_DEPLOYMENT")
        if not deployment:
            raise ValueError("Configure an Azure OpenAI deployment name.")
        selector = EvidenceSelector(get_client(), deployment, budget)
    # Historical lab data is explicitly marked synthetic. All other adapters use today.
    from lab import END

    return ConversationService(
        BusinessService(provider, today=END if backend == "lab" else None),
        store,
        selector,
    )
