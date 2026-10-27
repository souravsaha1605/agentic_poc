"""
client.py
=========
Azure OpenAI client singleton.

PURPOSE
-------
Creates a single, reusable OpenAI SDK client configured to talk to the
Azure OpenAI inference endpoint.  All agents import this `client` object
rather than constructing their own — this mirrors the forecast-agent
pattern and ensures that connection pooling, timeouts, and credentials
are managed in exactly one place.

WHY AZURE OPENAI AND NOT DATABRICKS AI GATEWAY?
----------------------------------------------
The existing forecast-agent project already uses Azure OpenAI (gpt-5.4-mini)
via the Responses API.  To keep the two projects compatible and share the
same .env credentials file, we reuse the same client configuration.

INPUT
-----
  config.AZURE_OPENAI_ENDPOINT – base URL for the Azure deployment
  config.AZURE_OPENAI_API_KEY  – secret key

OUTPUT
------
  `client` – an openai.OpenAI instance ready for client.responses.create()
"""

from openai import OpenAI

from config import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY

# ---------------------------------------------------------------------------
# Build the OpenAI-compatible client pointing at the Azure endpoint.
# Azure OpenAI exposes an OpenAI-compatible REST surface, so we can use
# the standard `openai` Python SDK by overriding the base_url.
# ---------------------------------------------------------------------------
client = OpenAI(
    base_url=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
)