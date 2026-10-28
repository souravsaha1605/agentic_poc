"""Deterministic SKU/customer/budget fixtures for the isolated Genie pilot.

These records demonstrate production-shaped grains without pretending to be
business data. They are published only to a ``*_lab`` schema and remain
separate from the original Forecast RCA fixtures.
"""

from datetime import date, datetime, timedelta, timezone
import json

from data_access import fingerprint
from state import checked_table


COMMERCIAL_DATASET_VERSION = "commercial-demo-1.0"
COMMERCIAL_SEED = 73
END = date(2026, 9, 27)

TABLE_KEYS = {
    "dim_sku": ("sku_id",),
    "dim_customer": ("customer_id",),
    "dim_fiscal_period": ("country", "fiscal_period"),
    "fact_sku_forecast": (
        "region",
        "country",
        "sku_id",
        "target_date",
        "forecast_generated_date",
    ),
    "fact_customer_forecast": (
        "region",
        "country",
        "customer_id",
        "sku_id",
        "target_date",
        "forecast_generated_date",
    ),
    "fact_sku_budget": (
        "region",
        "country",
        "sku_id",
        "fiscal_period",
        "budget_version",
    ),
    "fact_sku_price": ("country", "sku_id", "price_type", "effective_from"),
    "fact_sku_promotion": (
        "region",
        "country",
        "sku_id",
        "promotion_id",
    ),
}


def generate_commercial_data():
    """Return separate, certified table fixtures at their documented grains."""
    skus = [
        {
            "sku_id": "SKU-1001",
            "sku_name": "Dairy Classic 1L",
            "category": "Dairy",
            "region": "North",
            "country": "India",
            "unit_of_measure": "each",
            "lifecycle_stage": "mature",
            "active": True,
            "dataset_version": COMMERCIAL_DATASET_VERSION,
        },
        {
            "sku_id": "SKU-1002",
            "sku_name": "Dairy Lite 1L",
            "category": "Dairy",
            "region": "North",
            "country": "India",
            "unit_of_measure": "each",
            "lifecycle_stage": "mature",
            "active": True,
            "dataset_version": COMMERCIAL_DATASET_VERSION,
        },
        {
            "sku_id": "SKU-2001",
            "sku_name": "Cola Classic 500ml",
            "category": "Beverages",
            "region": "West",
            "country": "India",
            "unit_of_measure": "each",
            "lifecycle_stage": "mature",
            "active": True,
            "dataset_version": COMMERCIAL_DATASET_VERSION,
        },
    ]
    customers = [
        {
            "customer_id": "CUST-001",
            "customer_name": "Metro Retail Demo",
            "customer_segment": "Modern Trade",
            "region": "North",
            "country": "India",
            "active": True,
            "sensitivity_class": "DEMO",
            "dataset_version": COMMERCIAL_DATASET_VERSION,
        },
        {
            "customer_id": "CUST-002",
            "customer_name": "FreshMart Demo",
            "customer_segment": "Grocery",
            "region": "North",
            "country": "India",
            "active": True,
            "sensitivity_class": "DEMO",
            "dataset_version": COMMERCIAL_DATASET_VERSION,
        },
        {
            "customer_id": "CUST-003",
            "customer_name": "Westside Stores Demo",
            "customer_segment": "Modern Trade",
            "region": "West",
            "country": "India",
            "active": True,
            "sensitivity_class": "DEMO",
            "dataset_version": COMMERCIAL_DATASET_VERSION,
        },
    ]

    sku_profiles = {
        "SKU-1001": {"region": "North", "actual": 120, "forecast": 110, "price": 60},
        "SKU-1002": {"region": "North", "actual": 80, "forecast": 84, "price": 55},
        "SKU-2001": {"region": "West", "actual": 150, "forecast": 145, "price": 40},
    }
    customer_shares = {
        ("CUST-001", "SKU-1001"): 0.60,
        ("CUST-001", "SKU-1002"): 0.50,
        ("CUST-002", "SKU-1001"): 0.40,
        ("CUST-002", "SKU-1002"): 0.50,
        ("CUST-003", "SKU-2001"): 1.00,
    }
    customer_by_id = {row["customer_id"]: row for row in customers}

    fiscal_periods = []
    for month in range(4, 10):
        period_start = date(2026, month, 1)
        period_end = date(2026, month + 1, 1) - timedelta(days=1)
        fiscal_periods.append(
            {
                "country": "India",
                "fiscal_period": f"FY2026-P{month:02d}",
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "fiscal_year": 2026,
                "period_number": month,
                "dataset_version": COMMERCIAL_DATASET_VERSION,
            }
        )

    sku_forecast, customer_forecast = [], []
    for week in range(26):
        target = END - timedelta(weeks=25 - week)
        for sku_id, profile in sku_profiles.items():
            # A small deterministic cadence makes period and trend tests useful.
            actual = profile["actual"] + (week % 4) * 5
            forecast = profile["forecast"] + (week % 3) * 3
            sku_forecast.append(
                {
                    "region": profile["region"],
                    "country": "India",
                    "sku_id": sku_id,
                    "target_date": target.isoformat(),
                    "forecast_generated_date": (target - timedelta(days=7)).isoformat(),
                    "forecast_quantity": float(forecast),
                    "actual_quantity": float(actual),
                    "unit_of_measure": "each",
                    "forecast_horizon_days": 7,
                    "dataset_version": COMMERCIAL_DATASET_VERSION,
                    "seed": COMMERCIAL_SEED,
                }
            )
            for (customer_id, mapped_sku), share in customer_shares.items():
                if mapped_sku != sku_id:
                    continue
                customer = customer_by_id[customer_id]
                customer_forecast.append(
                    {
                        "region": customer["region"],
                        "country": customer["country"],
                        "customer_id": customer_id,
                        "sku_id": sku_id,
                        "target_date": target.isoformat(),
                        "forecast_generated_date": (target - timedelta(days=7)).isoformat(),
                        "forecast_quantity": float(round(forecast * share)),
                        "actual_quantity": float(round(actual * share)),
                        "unit_of_measure": "each",
                        "forecast_horizon_days": 7,
                        "dataset_version": COMMERCIAL_DATASET_VERSION,
                        "seed": COMMERCIAL_SEED,
                    }
                )

    budgets, prices = [], []
    for month in range(4, 10):
        period = f"FY2026-P{month:02d}"
        effective_from = date(2026, month, 1)
        effective_to = (
            date(2026, month + 1, 1) - timedelta(days=1)
            if month < 12
            else date(2026, 12, 31)
        )
        for sku_id, profile in sku_profiles.items():
            budget_quantity = float(profile["actual"] * 4)
            budget_price = float(profile["price"] + (2 if month >= 8 else 0))
            budgets.append(
                {
                    "region": profile["region"],
                    "country": "India",
                    "sku_id": sku_id,
                    "fiscal_period": period,
                    "budget_version": "FY2026-V1",
                    "budget_quantity": budget_quantity,
                    "budget_revenue": budget_quantity * budget_price,
                    "currency": "INR",
                    "status": "APPROVED",
                    "approved_at": "2026-03-15T00:00:00+00:00",
                    "dataset_version": COMMERCIAL_DATASET_VERSION,
                }
            )
            prices.append(
                {
                    "country": "India",
                    "sku_id": sku_id,
                    "price_type": "LIST",
                    "price": budget_price,
                    "currency": "INR",
                    "unit_of_measure": "each",
                    "effective_from": effective_from.isoformat(),
                    "effective_to": effective_to.isoformat(),
                    "dataset_version": COMMERCIAL_DATASET_VERSION,
                }
            )

    promotions = [
        {
            "region": "North",
            "country": "India",
            "sku_id": "SKU-1001",
            "promotion_id": "PROMO-1001-AUG",
            "promotion_type": "PERCENT_DISCOUNT",
            "start_date": "2026-08-01",
            "end_date": "2026-08-31",
            "discount_value": 10.0,
            "discount_unit": "percent",
            "status": "APPROVED",
            "dataset_version": COMMERCIAL_DATASET_VERSION,
        },
        {
            "region": "West",
            "country": "India",
            "sku_id": "SKU-2001",
            "promotion_id": "PROMO-2001-SEP",
            "promotion_type": "PERCENT_DISCOUNT",
            "start_date": "2026-09-01",
            "end_date": "2026-09-30",
            "discount_value": 5.0,
            "discount_unit": "percent",
            "status": "APPROVED",
            "dataset_version": COMMERCIAL_DATASET_VERSION,
        },
    ]

    return {
        "dim_sku": skus,
        "dim_customer": customers,
        "dim_fiscal_period": fiscal_periods,
        "fact_sku_forecast": sku_forecast,
        "fact_customer_forecast": customer_forecast,
        "fact_sku_budget": budgets,
        "fact_sku_price": prices,
        "fact_sku_promotion": promotions,
    }


def _key(row, names):
    return tuple(str(row.get(name)) for name in names)


def validate_commercial_data(tables):
    """Return validation failures; an empty list is required for publication."""
    failures = []
    expected = set(TABLE_KEYS)
    if set(tables) != expected:
        failures.append("TABLE_SET_MISMATCH")
        return failures
    for table, keys in TABLE_KEYS.items():
        rows = tables[table]
        if not rows:
            failures.append(f"{table}:EMPTY")
            continue
        grains = [_key(row, keys) for row in rows]
        if len(grains) != len(set(grains)):
            failures.append(f"{table}:DUPLICATE_GRAIN")
        if any(any(row.get(name) in (None, "") for name in keys) for row in rows):
            failures.append(f"{table}:MISSING_KEY")

    sku_ids = {row["sku_id"] for row in tables["dim_sku"]}
    customer_ids = {row["customer_id"] for row in tables["dim_customer"]}
    fiscal_periods = {
        (row["country"], row["fiscal_period"])
        for row in tables["dim_fiscal_period"]
    }
    for name in (
        "fact_sku_forecast",
        "fact_customer_forecast",
        "fact_sku_budget",
        "fact_sku_price",
        "fact_sku_promotion",
    ):
        if any(row["sku_id"] not in sku_ids for row in tables[name]):
            failures.append(f"{name}:UNKNOWN_SKU")
    if any(
        row["customer_id"] not in customer_ids
        for row in tables["fact_customer_forecast"]
    ):
        failures.append("fact_customer_forecast:UNKNOWN_CUSTOMER")
    if any("customer_id" in row for row in tables["fact_sku_budget"]):
        failures.append("fact_sku_budget:CUSTOMER_BUDGET_FORBIDDEN")
    if any("customer_id" in row for row in tables["fact_sku_promotion"]):
        failures.append("fact_sku_promotion:CUSTOMER_PROMOTION_FORBIDDEN")
    if any(row["currency"] != "INR" for row in tables["fact_sku_budget"]):
        failures.append("fact_sku_budget:INVALID_CURRENCY")
    if any(row["currency"] != "INR" for row in tables["fact_sku_price"]):
        failures.append("fact_sku_price:INVALID_CURRENCY")
    if any(
        (row["country"], row["fiscal_period"]) not in fiscal_periods
        for row in tables["fact_sku_budget"]
    ):
        failures.append("fact_sku_budget:UNKNOWN_FISCAL_PERIOD")
    for country in {row["country"] for row in tables["dim_fiscal_period"]}:
        ordered_periods = sorted(
            (
                row for row in tables["dim_fiscal_period"]
                if row["country"] == country
            ),
            key=lambda row: row["period_start"],
        )
        if any(
            current["period_start"] <= previous["period_end"]
            for previous, current in zip(ordered_periods, ordered_periods[1:])
        ):
            failures.append("dim_fiscal_period:OVERLAPPING_PERIODS")
            break
    price_groups = {}
    for row in tables["fact_sku_price"]:
        group = (row["country"], row["sku_id"], row["price_type"])
        price_groups.setdefault(group, []).append(row)
    if any(
        current["effective_from"] <= previous["effective_to"]
        for rows in price_groups.values()
        for previous, current in zip(
            sorted(rows, key=lambda row: row["effective_from"]),
            sorted(rows, key=lambda row: row["effective_from"])[1:],
        )
    ):
        failures.append("fact_sku_price:OVERLAPPING_EFFECTIVE_DATES")
    return failures


def _normalized(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def publish_commercial_lab(spark, database="workspace.forecast_rca_lab"):
    """Append missing demo grains without overwriting any existing table row."""
    database = checked_table(database)
    if not database.split(".")[-1].endswith("_lab"):
        raise ValueError("Commercial demo publication is restricted to *_lab.")
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {database}")
    generated = generate_commercial_data()
    failures = validate_commercial_data(generated)
    if failures:
        raise RuntimeError("Commercial demo certification failed: " + ", ".join(failures))

    report = {}
    for table, generated_rows in generated.items():
        full_name = f"{database}.{table}"
        existing = []
        if spark.catalog.tableExists(full_name):
            existing = [
                {k: _normalized(v) for k, v in row.asDict(recursive=True).items()}
                for row in spark.table(full_name).collect()
            ]
            required = set(generated_rows[0])
            missing_columns = required - set(spark.table(full_name).columns)
            if missing_columns:
                raise ValueError(
                    f"{full_name} is missing columns: {', '.join(sorted(missing_columns))}"
                )
        existing_by_key = {
            _key(row, TABLE_KEYS[table]): row for row in existing
        }
        if len(existing_by_key) != len(existing):
            raise RuntimeError(f"{full_name} contains duplicate certified grains.")
        additions = []
        for row in generated_rows:
            key = _key(row, TABLE_KEYS[table])
            if key not in existing_by_key:
                additions.append(row)
                continue
            expected = {name: _normalized(value) for name, value in row.items()}
            actual = {name: existing_by_key[key].get(name) for name in expected}
            if actual != expected:
                raise RuntimeError(
                    f"{full_name} contains a conflicting certified demo grain {key}."
                )
        if additions:
            spark.createDataFrame(additions).write.format("delta").mode(
                "append"
            ).saveAsTable(full_name)
        report[table] = {
            "existing_rows": len(existing),
            "generated_rows": len(additions),
            "total_rows": spark.table(full_name).count(),
        }

    # Certify the actual published tables, including any pre-existing rows,
    # before a manifest makes them available to the Genie setup notebook.
    published = {
        table: [
            {k: _normalized(v) for k, v in row.asDict(recursive=True).items()}
            for row in spark.table(f"{database}.{table}").collect()
        ]
        for table in TABLE_KEYS
    }
    published_failures = validate_commercial_data(published)
    if published_failures:
        raise RuntimeError(
            "Published commercial data failed certification: "
            + ", ".join(published_failures)
        )

    source_rows = [
        {"table": table, **row}
        for table, rows in generated.items()
        for row in rows
    ]
    source_version = fingerprint(source_rows)
    manifest_name = f"{database}.rca_commercial_manifest"
    manifest = {
        "dataset_version": COMMERCIAL_DATASET_VERSION,
        "source_version": source_version,
        "published_at": datetime.now(timezone.utc).isoformat(),
        "table_counts_json": json.dumps(
            {name: len(rows) for name, rows in generated.items()}, sort_keys=True
        ),
        "validation": "PASS",
    }
    exists = spark.catalog.tableExists(manifest_name)
    already_published = (
        spark.table(manifest_name).where(f"source_version = '{source_version}'").count()
        if exists
        else 0
    )
    if not already_published:
        spark.createDataFrame([manifest]).write.format("delta").mode(
            "append"
        ).saveAsTable(manifest_name)
    return {
        "dataset_version": COMMERCIAL_DATASET_VERSION,
        "source_version": source_version,
        "validation": "PASS",
        "tables": report,
    }

