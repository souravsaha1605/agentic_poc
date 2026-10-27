"""Reproducible FMCG lab fixtures and honest capability certification.

No random enterprise evidence is invented. These deliberately small fixtures
keep the BRD IDs (including distinct P001/P0001), and declare their seed/version.
Run certification at initialization or maintenance, never for every chat turn.
"""

import copy
import json
import math
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from business import BusinessService, MIN_WEEKS
from contracts import AnalysisPlan, Principal
from data_access import RecordsProvider

DATASET_VERSION = "brd-lab-5.2"
SEED = 42
END = date(2026, 9, 27)
# A fixture row is unique at the forecast-vintage grain. Initialization uses this
# key to add absent lab rows without replacing an existing business observation.
FIXTURE_GRAIN = (
    "product_id",
    "store_id",
    "region",
    "date",
    "forecast_generated_date",
)

# These are the original BRD examples plus the explicitly added review-5 lab
# capabilities. Keeping the contract outside ``certify`` lets initialization
# apply the same expectations to an existing, compatible lab fact table.
BRD_EXPECTED_SIGNALS = {
    ("P0001", "promotion"): "SUPPORTED",
    ("P0099", "bias"): "SUPPORTED",
    ("P0020", "inventory"): "SUPPORTED",
    ("P0040", "trend"): "SUPPORTED",
    ("P0050", "price"): "POSSIBLE",
    ("P0060", "seasonality"): "SUPPORTED",
    ("P0070", "revenue"): "SUPPORTED",
    ("P0080", "quality"): "SUPPORTED",
    ("P0083", "bias"): "SUPPORTED",
    ("P001", "bias"): "NOT_SUPPORTED",
    ("P0084", "weather"): "POSSIBLE",
    ("P0085", "competitor"): "POSSIBLE",
    ("P0086", "lifecycle"): "POSSIBLE",
    ("P0087", "mix"): "POSSIBLE",
}
GLOBAL = Principal(
    tenant="lab",
    subject="certification",
    regions=("*",),
    products=("*",),
    categories=("*",),
)


def generate():
    definitions = [
        ("P0001", "Dairy regular", "North", "Dairy", "promotion"),
        ("P0099", "Dairy West", "West", "Dairy", "under_bias"),
        ("P0020", "Dairy constrained", "North", "Dairy", "inventory"),
        ("P001", "Dairy distinct", "South", "Dairy", "normal"),
        ("P0030", "Coke", "North", "Beverages", "normal"),
        ("P0031", "Coke", "South", "Beverages", "normal"),
        ("P0040", "Dairy trend", "North", "Dairy", "trend"),
        ("P0050", "Dairy price", "North", "Dairy", "price"),
        ("P0060", "Dairy seasonal", "North", "Dairy", "seasonality"),
        ("P0070", "Dairy revenue", "North", "Dairy", "revenue"),
        ("P0080", "Dairy missing", "North", "Dairy", "quality"),
        ("P0081", "New product", "North", "Dairy", "new_product"),
        ("P0082", "Dairy intermittent", "North", "Dairy", "intermittent"),
        ("P0083", "Dairy over forecast", "North", "Dairy", "over_bias"),
        ("P0084", "Dairy weather", "North", "Dairy", "weather"),
        ("P0085", "Dairy competitor", "North", "Dairy", "competitor"),
        ("P0086", "Dairy launch", "North", "Dairy", "lifecycle"),
        ("P0087", "Dairy store mix", "North", "Dairy", "mix"),
        ("P0088", "Dairy regional", "North", "Dairy", "regional_divergence"),
        ("P0088", "Dairy regional", "West", "Dairy", "normal"),
    ]
    rows, products = [], []
    for product, name, region, category, scenario in definitions:
        products.append(
            {
                "product_id": product,
                "product_name": name,
                "region": region,
                "category": category,
            }
        )
        for week in range(60):
            if scenario == "new_product" and week < 58:
                continue
            if scenario == "lifecycle" and week < 48:
                continue
            day = END - timedelta(weeks=59 - week)
            actual, forecast, inventory, price, promo = 100.0, 100.0, 300.0, 10.0, 0
            if scenario == "promotion":
                promo = int(week % 4 == 0)
                actual = 150.0 if promo else 100.0
            elif scenario == "under_bias":
                forecast = 80.0
            elif scenario == "over_bias":
                forecast = 140.0
            elif scenario == "trend":
                actual = 150.0 if week >= 54 else 100.0
            elif scenario == "inventory" and week >= 54:
                actual, inventory = 20.0, 0.0
            elif scenario == "price" and week >= 54:
                actual, price = 75.0, 12.0
            elif scenario == "seasonality":
                actual = 100 + 40 * math.sin(2 * math.pi * week / 26)
            elif scenario == "revenue" and week >= 54:
                price = 5.0
            elif scenario == "intermittent":
                actual = 0.0 if week % 3 else 100.0
            elif scenario == "weather":
                actual = 70.0 if week % 2 else 100.0
            elif scenario == "competitor":
                actual = 70.0 if week % 4 < 2 else 100.0
            elif scenario == "lifecycle":
                actual = 50.0 + 10 * (week - 48)
            elif scenario == "mix":
                actual = 50.0 if week >= 54 else 200.0
                forecast = 200.0
            elif scenario == "regional_divergence":
                forecast = 140.0
            row = {
                "product_id": product,
                "store_id": "S001",
                "region": region,
                "category": category,
                "date": day.isoformat(),
                "units_sold": actual,
                "demand_forecast": forecast,
                "inventory_level": inventory,
                "price": price,
                "discount": 5.0,
                "discount_unit": "percent",
                "currency": "INR",
                "unit_of_measure": "each",
                "holiday_promotion": promo,
                "weather_condition": None,
                "seasonality": "synthetic_26_week"
                if scenario == "seasonality"
                else None,
                "competitor_pricing": None,
                "forecast_generated_date": (day - timedelta(days=7)).isoformat(),
                "forecast_horizon_days": 7,
                "inventory_timestamp": day.isoformat(),
                "scenario": scenario,
                "dataset_version": DATASET_VERSION,
                "seed": SEED,
                "launch_date": (
                    END
                    - timedelta(
                        weeks=11
                        if scenario == "lifecycle"
                        else 1
                        if scenario == "new_product"
                        else 59
                    )
                ).isoformat(),
                "lifecycle_stage": "launch"
                if scenario in ("lifecycle", "new_product")
                else "mature",
                "channel": "Retail",
                "fiscal_period": f"FY{day.year}-P{day.month:02d}",
                "fiscal_calendar_policy": "LAB_ONLY: calendar year starts January; monthly periods",
                "weather_observed_at": day.isoformat()
                if scenario == "weather"
                else None,
            }
            if scenario == "weather":
                row["weather_condition"] = "Rainy" if week % 2 else "Sunny"
            if scenario == "competitor":
                row["competitor_pricing"] = 8.0 if week % 4 < 2 else 12.0
            if scenario == "quality" and week >= 58:
                row["demand_forecast"] = None
                row["discount"] = None
            rows.append(row)
            if scenario == "mix":
                rows.append(
                    {
                        **row,
                        "store_id": "S002",
                        "channel": "Online",
                        "units_sold": 200.0 if week >= 54 else 50.0,
                        "demand_forecast": 50.0,
                    }
                )
    return rows, products


def fixture_key(row):
    """Return the stable lab grain, normalizing Spark date-like values."""
    return tuple(
        str(row.get(name))[:10] if name == "date" else str(row.get(name))
        for name in FIXTURE_GRAIN
    )


def missing_fixture_rows(existing, generated):
    """Find absent fixture grains; matching existing rows are never replaced."""
    existing_keys = {fixture_key(row) for row in existing}
    return [
        copy.deepcopy(row) for row in generated if fixture_key(row) not in existing_keys
    ]


def certify(provider, expectations=None):
    """Validate actual signals, then publish a separate scoped registry.

    FAIL is BLOCKED, not NOT_TESTABLE. Unknown external drivers remain explicit.
    A provisional registry exists only inside this certification function.
    """
    expected = BRD_EXPECTED_SIGNALS
    if expectations is not None:
        expected = expectations
    provisional = copy.copy(provider)
    provisional.registry = []
    service = BusinessService(provisional)
    registry = []
    for item in provider.catalog():
        entity_rows = [
            r
            for r in provider.rows
            if r["product_id"] == item["product_id"] and r["region"] == item["region"]
        ]
        if not entity_rows:
            continue
        for capability in MIN_WEEKS:
            entry = {
                "product_id": item["product_id"],
                "region": item["region"],
                "category": item["category"],
                "store_id": "*",
                "capability": capability,
                "source_version": provider.source_version,
                "coverage_start": min(r["date"] for r in entity_rows),
                "coverage_end": max(r["date"] for r in entity_rows),
                "validated_at": datetime.now(timezone.utc).isoformat(),
                "status": "READY",
                "validation": "PASS",
                "required_weeks": MIN_WEEKS[capability],
                "dataset_version": DATASET_VERSION,
                "feature_version": "weekly-5.2",
            }
            provisional.registry = [entry]
            plan = AnalysisPlan(
                tool="run_forecast_rca",
                product_id=item["product_id"],
                region=item["region"],
                category=item["category"],
                lookback_weeks=60 if capability == "seasonality" else 12,
                hypotheses=[capability],
            )
            try:
                result = service.execute(plan, GLOBAL)
                status = result["hypotheses"][0]["status"]
                entry["data_quality"] = result["data_quality"]["status"]
                if status == "NOT_TESTABLE":
                    entry.update(status="NOT_TESTABLE", validation="NOT_RUN")
                expectation = expected.get((item["product_id"], capability))
                if expectation and status != expectation:
                    entry.update(status="BLOCKED", validation="FAIL")
                entry["observed"] = status
                entry["expected"] = expectation or "contract/coverage validation"
            except (ValueError, TypeError) as exc:
                entry.update(
                    status="BLOCKED",
                    validation="FAIL",
                    observed=type(exc).__name__,
                    data_quality="INSUFFICIENT",
                )
            registry.append(entry)
            # This lab has exactly one store per entity. The same certification
            # therefore also applies to that exact store, without broadening scope.
            stores = {r["store_id"] for r in entity_rows}
            if len(stores) == 1:
                registry.append({**entry, "store_id": next(iter(stores))})
    provider.registry = registry
    return registry


def local_provider():
    rows, products = generate()
    provider = RecordsProvider(rows, products)
    certify(provider)
    return provider


def save_report(provider, path):
    report = {
        "dataset_version": DATASET_VERSION,
        "seed": SEED,
        "source_version": provider.source_version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "rows": len(provider.rows),
        "registry": provider.registry,
    }
    Path(path).write_text(json.dumps(report, indent=2))
    if any(r["validation"] == "FAIL" for r in provider.registry):
        raise RuntimeError("Certification failed; readiness publication is blocked.")
    return report
