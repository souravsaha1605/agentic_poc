"""
client.py -- Azure OpenAI client factory (singleton).
============================================================================

PURPOSE
-------
Creates exactly one OpenAI Python-client instance configured for Azure
OpenAI and exposes it as the module-level ``client`` variable.  Every
other module imports it:  from client import client

DESIGN RATIONALE
----------------
- Singleton pattern: the client is stateless and thread-safe; no benefit
  to creating multiple instances.
- Fail-fast: if credentials are missing the import raises RuntimeError,
  so misconfiguration is caught at startup, not during the first request.
- Secrets from .env: credentials are loaded by config.py via python-dotenv
  and never appear in source code (BRD SS33).

BRD REFERENCES: SS33 (Security -- secrets management).
"""

# Third-party imports
from openai import OpenAI

# Project imports -- config.py loads .env and exposes the credential constants
from config import (
    AZURE_OPENAI_ENDPOINT,    # Azure OpenAI endpoint URL
    AZURE_OPENAI_API_KEY,     # API key (secret -- never log or expose)
    AZURE_OPENAI_API_VERSION, # API version string (e.g. "2025-08-07-preview")
)


def _build_client() -> OpenAI:
    """
    Construct and return the Azure OpenAI client.

    The base_url is the endpoint with a trailing slash appended.  No
    api-version query parameter is sent — the Azure AI Foundry endpoint
    (*.services.ai.azure.com) does not require or accept it, unlike the
    legacy *.openai.azure.com endpoint.

    Returns:
        OpenAI: A configured client instance ready for responses.create().

    Raises:
        RuntimeError: If AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_API_KEY
            is not set (i.e. .env is missing or not loaded).
    """
    # Fail-fast guard -- prevent silent misconfiguration
    if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_API_KEY:
        raise RuntimeError(
            "Azure OpenAI credentials not found. "
            "Populate .env with AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY."
        )

    # Construct the client with sensible defaults:
    #   timeout=60s   -- generous enough for LLM inference
    #   max_retries=2 -- automatic retry on transient HTTP errors
    #
    # NOTE: The trailing slash on the endpoint is required so httpx
    # URL.join() preserves the full path (e.g. '/openai/v1/') when
    # appending relative paths like 'responses', 'chat/completions', etc.
    # No api-version query param is sent — the Azure AI Foundry endpoint
    # (*.services.ai.azure.com) rejects it with 400 "API version not supported".
    return OpenAI(
        base_url=f"{AZURE_OPENAI_ENDPOINT}/",
        api_key=AZURE_OPENAI_API_KEY,
        timeout=60,
        max_retries=2,
    )


# ------------------------------------------------------------------
# Module-level singleton -- created once at import time.
# All other modules should do:  from client import client
# ------------------------------------------------------------------
client = _build_client()