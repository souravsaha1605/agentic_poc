"""
app.py
======
Entry point for the Agentic AI Supply Chain Exception Management Platform.

PURPOSE
-------
This script demonstrates the end-to-end exception management workflow:
  1. Initialise the ExceptionAgent (loads .env, creates OpenAI client,
     tool executor, and policy engine)
  2. Present demo scenarios to the user
  3. Run the agent on a selected scenario
  4. Display the structured response

DEMO SCENARIOS (BRD §42.6)
--------------------------
The app includes three ready-to-run demo scenarios that exercise different
exception types and agent capabilities:
  1. Supplier Delay + Stockout Risk  (BRD Scenario 1)
  2. Inventory Shortage              (BRD Scenario 2)
  3. Warehouse Imbalance             (BRD Scenario 5)

API CALL BUDGET
---------------
Each demo scenario uses 1-3 LLM API calls (tool-calling round trips).
The total across all three demos stays well within the 10-call limit.

HOW TO RUN
----------
  # In a Databricks notebook (recommended — Spark is available):
  %cd /Workspace/Users/sourav.saha26-10@iimv.ac.in/agentic_poc/supply-chain-inventory-management
  %run app.py

  # Or as a standalone script:
  python app.py

INPUT
-----
  User selects a demo scenario (1, 2, or 3) or types a custom query.
  The .env file in ../forecast-agent/ provides Azure OpenAI credentials.

OUTPUT
------
  Structured text response from the agent including:
    - What happened (exception summary)
    - Why it matters (business impact)
    - What was investigated (data sources)
    - Options considered (with cost/impact)
    - Recommendation + rationale
    - Whether human approval is required
"""

import sys
import os

# Ensure the project root is on sys.path so imports work regardless of CWD
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.exception_agent import ExceptionAgent
from config import MAX_API_CALLS


# ===========================================================================
# DEMO SCENARIOS (BRD §42.6 — Mandatory Test Scenarios)
# ===========================================================================

DEMO_SCENARIOS = {
    "1": {
        "title": "Supplier Delay + Stockout Risk (BRD Scenario 1)",
        "prompt": (
            "Supplier S001 has reported a delivery delay. "
            "Investigate the impact: check inventory for SKU-001, "
            "find open purchase orders, identify affected customer orders, "
            "review demand forecast, and suggest resolution options. "
            "Evaluate each option against the business policy."
        ),
    },
    "2": {
        "title": "Inventory Shortage (BRD Scenario 2)",
        "prompt": (
            "We suspect an inventory shortage for SKU-050. "
            "Check the current inventory across all warehouses, "
            "compare against demand forecast, identify impacted customer "
            "orders, and generate replenishment or transfer options. "
            "Evaluate policy compliance for each option."
        ),
    },
    "3": {
        "title": "Warehouse Imbalance (BRD Scenario 5)",
        "prompt": (
            "Check inventory for SKU-025 across all warehouses. "
            "We suspect an imbalance — one warehouse may have excess "
            "while another is running low. Identify the imbalance, "
            "evaluate an inventory transfer option, and check if it "
            "requires human approval under the current policy."
        ),
    },
}


# ===========================================================================
# MAIN ENTRY POINT
# ===========================================================================

def main():
    """
    Main entry point — runs the exception management demo.

    In a Databricks notebook, this runs inline.  In a terminal, it
    presents an interactive menu.
    """
    print("=" * 70)
    print("  Agentic AI Supply Chain Exception Management Platform")
    print("  Agentic POC — Databricks + Azure OpenAI")
    print("=" * 70)
    print(f"\n  API Call Budget: {MAX_API_CALLS} per session")
    print(f"  Data Source:     workspace.forecast_db (Databricks Delta tables)")
    print(f"  LLM:             Azure OpenAI (gpt-5.4-mini)")
    print()

    # --- Initialise the agent ---
    agent = ExceptionAgent()

    # --- Check if running in a notebook (no stdin) or terminal ---
    if not sys.stdin or not sys.stdin.isatty():
        # Non-interactive: run Demo Scenario 1 by default
        print("\n[INFO] Non-interactive mode detected. Running Demo Scenario 1.\n")
        scenario = DEMO_SCENARIOS["1"]
        _run_scenario(agent, scenario)
        return

    # --- Interactive menu ---
    while True:
        print("\n" + "-" * 70)
        print("Available Demo Scenarios:")
        for key, sc in DEMO_SCENARIOS.items():
            print(f"  [{key}] {sc['title']}")
        print(f"  [q] Quit")
        print("-" * 70)

        choice = input("\nSelect a scenario (1-3) or type a custom query: ").strip()

        if choice.lower() in ["q", "quit", "exit"]:
            print("\nGoodbye!")
            break

        if choice in DEMO_SCENARIOS:
            scenario = DEMO_SCENARIOS[choice]
            _run_scenario(agent, scenario)
        else:
            # Treat as custom query
            print(f"\n{'='*70}")
            print(f"Running custom query")
            print(f"{'='*70}")
            print(f"\nYou: {choice}\n")
            response = agent.run(choice)
            print(f"\nAssistant:\n{response}")

        # Reset API call counter for the next query
        agent.reset()


def _run_scenario(agent, scenario):
    """Run a single demo scenario and display results."""
    print(f"\n{'='*70}")
    print(f"  {scenario['title']}")
    print(f"{'='*70}")
    print(f"\nPrompt: {scenario['prompt']}")
    print()

    response = agent.run(scenario["prompt"], verbose=True)

    print(f"\n{'='*70}")
    print(f"  AGENT RESPONSE")
    print(f"{'='*70}")
    print(f"\n{response}")
    print(f"\n  API calls used: {agent.api_call_count}/{MAX_API_CALLS}")


if __name__ == "__main__":
    main()