"""Lazy Azure OpenAI client: importing offline modules never needs a key."""

from functools import lru_cache
import os
from urllib.parse import urlsplit


def runtime_setting(name, default=None):
    """Support the platform's non-reserved MY_ bindings without copying secrets."""
    return os.getenv(name) or os.getenv("MY_" + name) or default


@lru_cache(maxsize=1)
def get_client():
    from dotenv import load_dotenv
    from openai import OpenAI

    load_dotenv()
    endpoint = runtime_setting("AZURE_OPENAI_ENDPOINT", "").rstrip("/") + "/"
    key = runtime_setting("AZURE_OPENAI_API_KEY")
    parsed = urlsplit(endpoint)
    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.query
        or parsed.fragment
    ):
        raise ValueError(
            "Configure an HTTPS Azure OpenAI base URL without credentials or query parameters."
        )
    if not parsed.path.endswith("/openai/v1/"):
        raise ValueError("AZURE_OPENAI_ENDPOINT must include /openai/v1/.")
    if not key:
        raise ValueError(
            "Configure AZURE_OPENAI_API_KEY securely in environment settings."
        )
    # Automatic retries would make an invisible extra paid request. The app ledger
    # reserves each explicit HTTP attempt, including attempts that fail.
    return OpenAI(base_url=endpoint, api_key=key, timeout=30, max_retries=0)
