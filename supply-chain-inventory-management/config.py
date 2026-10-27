"""
config.py
=========
Central configuration module for the Agentic AI Supply Chain Exception
Management Platform.

PURPOSE
-------
Loads Azure OpenAI credentials from the .env file located in the sibling
forecast-agent directory.  All environment-specific values (API keys,
endpoint URLs, model deployment names) are read from environment variables
so that NO credentials are ever hard-coded in source code.

WHY A SEPARATE CONFIG FILE?
--------------------------
Following the production-grade principle of environment-driven configuration
(BRD §38, §42.2), every other module imports from here rather than reading
os.getenv directly.  This centralises the configuration surface and makes
it trivial to swap environments (dev / staging / prod) by changing only the
.env file.

INPUT
-----
  .env file at ../forecast-agent/.env  (relative to this project folder)
    Contains:
      AZURE_OPENAI_ENDPOINT      – Azure OpenAI inference endpoint URL
      AZURE_OPENAI_API_KEY       – Secret API key for the Azure deployment
      AZURE_OPENAI_DEPLOYMENT    – Model deployment name (e.g. gpt-5.4-mini)
      AZURE_OPENAI_API_VERSION   – API version string

OUTPUT
------
  Module-level constants consumed by client.py, agents, and tools:
      AZURE_OPENAI_ENDPOINT
      AZURE_OPENAI_API_KEY
      AZURE_OPENAI_DEPLOYMENT
      AZURE_OPENAI_API_VERSION
      DATABRICKS_CATALOG         – Unity Catalog catalog name
      DATABRICKS_SCHEMA          – Schema name within the catalog
      MAX_API_CALLS              – Hard limit on LLM API calls per run
"""

import os
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Load the .env file from the sibling forecast-agent directory.
# The path is resolved relative to this file so it works regardless of the
# current working directory at runtime.
# ---------------------------------------------------------------------------
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_ENV_PATH = os.path.join(_THIS_DIR, "..", "forecast-agent", ".env")
load_dotenv(dotenv_path=_ENV_PATH)

# ---------------------------------------------------------------------------
# Azure OpenAI configuration (read from environment – never hard-coded)
# ---------------------------------------------------------------------------
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-5.4-mini")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-08-07-preview")

# ---------------------------------------------------------------------------
# Databricks configuration
# The catalog and schema names match what the data-generation scripts
# (01_generate_supply_chain_data.py, 02_generate_events_observability_views.py)
# use when creating Delta tables.
# ---------------------------------------------------------------------------
DATABRICKS_CATALOG = os.getenv("DATABRICKS_CATALOG", "workspace")
DATABRICKS_SCHEMA = os.getenv("DATABRICKS_SCHEMA", "forecast_db")

# ---------------------------------------------------------------------------
# API call budget
# The user has specified a maximum of 10 LLM API calls for any single
# end-to-end run.  This constant is enforced by the agent orchestrator.
# ---------------------------------------------------------------------------
MAX_API_CALLS = 10