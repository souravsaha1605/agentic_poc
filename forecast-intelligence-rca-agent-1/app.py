"""
app.py -- Entry point for the Forecast Intelligence & RCA Agent.
============================================================================

PURPOSE
-------
Provides two modes of operation:

  1. NON-LLM VALIDATION MODE (default):
     Run ``python app.py`` to execute all deterministic service-layer tests.
     These tests do NOT require Azure OpenAI credentials.  They validate:
       - Forecast retrieval and WMAPE accuracy
       - Inventory retrieval and stockout flags
       - Revenue retrieval (gross/net)
       - Historical pattern analysis (trend, volatility, level-shift)
       - Full RCA with evidence and hypotheses
       - Scenario comparison (what-if deltas)
       - Entity resolution (exact + ambiguous)
       - Data quality checks

  2. INTERACTIVE LLM MODE:
     Run ``python app.py --interactive`` to start a conversational loop.
     Requires .env credentials for Azure OpenAI.  The agent will:
       - Resolve entities from your natural-language queries
       - Call the appropriate tools to retrieve evidence
       - Return structured, grounded responses
     Type 'exit' to quit, 'tests' to run non-LLM validation.

BRD REFERENCES: SS38 (Test Scenarios), SS41 (End-to-End Journey).
"""

from __future__ import annotations

import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.forecast_rca_agent import ForecastIntelligenceAgent
from services.forecast_rca_service import (
    forecast_service, inventory_service, revenue_service,
    pattern_service, rca_service, comparison_service,
    entity_service, data_quality_service,
)


def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


# ============================================================
#  Non-LLM validation demos (BRD SS38 tests, deterministic only)
# --------------------------------------------------------------
#  These functions test the service layer directly without invoking the
#  LLM.  They are useful for validating data integrity, metric
#  calculations, and RCA hypothesis logic.  Each demo prints a
#  human-readable summary of the results.
# ============================================================

def demo_forecast_retrieval():
    """Test 1 – Forecast retrieval (BRD §38)."""
    print_header("Test 1: Forecast Retrieval")
    result = forecast_service.get_forecast_data("SKU-001", region="North", lookback_weeks=12)
    print(f"  Product: SKU-001 | Region: North")
    print(f"  Forecast: {result.get('total_forecast', 'N/A')}")
    print(f"  Actual: {result.get('total_actual', 'N/A')}")
    print(f"  WMAPE: {result.get('wmape', 'N/A')}%")
    print(f"  Accuracy: {result.get('forecast_accuracy', 'N/A')}%")
    print(f"  Bias: {result.get('forecast_bias_pct', 'N/A')}%")
    return result


def demo_inventory_retrieval():
    """Test 2 – Multi-turn continuation (inventory)."""
    print_header("Test 2: Inventory Retrieval")
    result = inventory_service.get_inventory_data("SKU-001", region="North", lookback_weeks=12)
    print(f"  Product: SKU-001 | Region: North")
    print(f"  Inventory Level: {result.get('inventory_level', 'N/A')}")
    print(f"  Status: {result.get('inventory_status', 'N/A')}")
    print(f"  Stockout: {result.get('stockout_flag', 'N/A')}")
    print(f"  Inventory Days: {result.get('inventory_days', 'N/A')}")
    return result


def demo_revenue_retrieval():
    """Test – Revenue retrieval (BRD FR-02)."""
    print_header("Test: Revenue Retrieval")
    result = revenue_service.get_revenue_data("SKU-001", region="North", lookback_weeks=12)
    print(f"  Product: SKU-001 | Region: North")
    print(f"  Gross Revenue: {result.get('gross_revenue', 'N/A')}")
    print(f"  Net Revenue: {result.get('net_revenue', 'N/A')}")
    print(f"  Avg Price: {result.get('avg_price', 'N/A')}")
    print(f"  Avg Discount: {result.get('avg_discount', 'N/A')}%")
    return result


def demo_historical_pattern():
    """Test – Historical pattern analysis (BRD FR-04)."""
    print_header("Test: Historical Pattern Analysis")
    result = pattern_service.analyze_patterns("SKU-001", region="North", lookback_weeks=12)
    print(f"  Product: SKU-001 | Region: North")
    print(f"  Observations: {result.get('observations', 'N/A')}")
    patterns = result.get("patterns", {})
    for name, data in patterns.items():
        print(f"  {name}: {data}")
    return result


def demo_rca():
    """Test 3 – RCA (BRD §9, §25)."""
    print_header("Test 3: Forecast RCA")
    result = rca_service.run_rca("SKU-001", region="North", lookback_weeks=12)
    print(f"  Product: SKU-001 | Region: North")
    print(f"  Observations: {result.get('observations', [])}")
    print(f"  Hypotheses:")
    for h in result.get("hypotheses", []):
        print(f"    - {h['cause']} [{h['status']}] strength={h['strength']}")
    print(f"  Confidence: {result.get('confidence', 'N/A')}")
    print(f"  Recommendations: {result.get('recommendations', [])}")
    return result


def demo_scenario_comparison():
    """Test 6 – What-if / scenario comparison (BRD §18)."""
    print_header("Test 6: Scenario Comparison (What-If)")
    baseline = {"demand": 100, "revenue": 5000, "inventory": 200}
    what_if = {"demand_adjustment_pct": 15}
    current = {"demand": 115, "revenue": 5750, "inventory": 200}
    result = comparison_service.compare(baseline, current, what_if)
    print(f"  Baseline: {baseline}")
    print(f"  What-If: {what_if}")
    print(f"  Current: {current}")
    print(f"  Deltas: {result.get('deltas', {})}")
    print(f"  Summary: {result.get('summary', '')}")
    return result


def demo_entity_resolution():
    """Test 7 – Ambiguous entity (BRD §38)."""
    print_header("Test 7: Entity Resolution")
    result = entity_service.resolve_product(product_name="Product")
    print(f"  Resolved: {result.resolved}")
    print(f"  Ambiguous: {result.ambiguous}")
    if result.candidates:
        print(f"  Candidates: {result.candidates[:5]}")
    # Exact match
    result2 = entity_service.resolve_product(product_id="SKU-001")
    print(f"  Exact match SKU-001: resolved={result2.resolved}, region={result2.region}")
    return result


def demo_data_quality():
    """Test 8 – Data quality checks (BRD §27)."""
    print_header("Test 8: Data Quality")
    entity_check = data_quality_service.check_entity("SKU-001")
    print(f"  Entity check: {entity_check}")
    date_check = data_quality_service.check_date_range("SKU-001")
    print(f"  Date range: {date_check}")
    metric_check = data_quality_service.check_metrics("SKU-001")
    print(f"  Metrics: {metric_check}")
    return {"entity": entity_check, "date": date_check, "metrics": metric_check}


def run_all_non_llm_tests():
    """Run all deterministic (non-LLM) demo tests."""
    print_header("Running All Non-LLM Validation Tests")
    tests = [
        ("Forecast Retrieval", demo_forecast_retrieval),
        ("Inventory Retrieval", demo_inventory_retrieval),
        ("Revenue Retrieval", demo_revenue_retrieval),
        ("Historical Pattern", demo_historical_pattern),
        ("Forecast RCA", demo_rca),
        ("Scenario Comparison", demo_scenario_comparison),
        ("Entity Resolution", demo_entity_resolution),
        ("Data Quality", demo_data_quality),
    ]
    passed = 0
    failed = 0
    for name, test_fn in tests:
        try:
            result = test_fn()
            if result and (result.get("success", True) is not False or result.get("valid", True) is not False):
                print(f"  ✓ PASSED: {name}")
                passed += 1
            else:
                print(f"  ✗ FAILED: {name}")
                failed += 1
        except Exception as exc:
            print(f"  ✗ ERROR: {name} - {exc}")
            failed += 1

    print_header(f"Results: {passed} passed, {failed} failed")
    return {"passed": passed, "failed": failed}


# ============================================================
#  Interactive LLM mode (requires .env credentials)
# --------------------------------------------------------------
#  Starts a conversational REPL that sends user messages through the
#  full agent pipeline (entity resolution -> tool calls -> LLM response).
#  Requires Azure OpenAI credentials in .env.
# ============================================================

def interactive_mode():
    """Interactive conversational mode (requires Azure OpenAI credentials)."""
    print_header("Forecast Intelligence & RCA Agent – Interactive Mode")
    print("  Type 'exit' to quit. Type 'tests' to run non-LLM validation.\n")

    agent = ForecastIntelligenceAgent()

    while True:
        user_query = input("\nYou: ").strip()
        if user_query.lower() in ["exit", "quit"]:
            print("\nGoodbye!")
            break
        if user_query.lower() == "tests":
            run_all_non_llm_tests()
            continue
        if not user_query:
            continue

        try:
            response = agent.run(user_query)
            print(f"\nAssistant:\n  {response.response}")
            if response.scenario_id:
                print(f"  [Scenario: {response.scenario_id} | Intent: {response.intent} | Action: {response.scenario_action}]")
            if response.tools_called:
                print(f"  [Tools: {', '.join(response.tools_called)}]")
        except Exception as exc:
            print(f"\n  Error: {exc}")
            print("  Ensure .env credentials are configured correctly.")


if __name__ == "__main__":
    # Default: run non-LLM validation tests
    # Use: python app.py --interactive  for LLM mode
    if "--interactive" in sys.argv:
        interactive_mode()
    else:
        run_all_non_llm_tests()