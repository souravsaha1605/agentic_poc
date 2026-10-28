"""One idempotent lab initialization/readiness job for a Databricks notebook.

Never runs during a chat request. Existing fact data is inspected and preserved.
Only a dedicated *_lab schema may be initialized. Missing certification fixtures
live separately from source data; they are never presented as enterprise facts.
"""

from datetime import datetime, timezone
from business import FEATURE_VERSION
from data_access import RecordsProvider, fingerprint, MAX_SOURCE_ROWS
from lab import (
    BRD_EXPECTED_SIGNALS,
    generate,
    certify,
    missing_fixture_rows,
    DATASET_VERSION,
)
from state import checked_table


def normalize(row):
    from datetime import date, datetime
    from decimal import Decimal

    return {
        k: v.isoformat()
        if isinstance(v, (date, datetime))
        else float(v)
        if isinstance(v, Decimal)
        else v
        for k, v in row.items()
    }


def audit(rows):
    """Grain-aware checks; duplicate dates in different stores are legitimate."""
    from data_access import as_date
    from business import number

    seen = set()
    flags = []
    for r in rows:
        grain = tuple(
            r.get(k)
            for k in ("product_id", "store_id", "date", "forecast_generated_date")
        )
        if grain in seen:
            flags.append("DUPLICATE_GRAIN")
        seen.add(grain)
        if any(
            r.get(k) is None
            for k in ("date", "product_id", "store_id", "region", "category")
        ):
            flags.append("MISSING_KEY")
        for k in ("units_sold", "demand_forecast", "inventory_level", "price"):
            if not number(r.get(k)):
                flags.append("NULL_OR_INVALID_" + k.upper())
            elif r[k] < 0:
                flags.append("NEGATIVE_" + k.upper())
        if (
            not number(r.get("discount"))
            or not 0 <= r["discount"] <= 100
            or r.get("discount_unit") != "percent"
        ):
            flags.append("INVALID_DISCOUNT")
        if not r.get("currency"):
            flags.append("MISSING_CURRENCY")
        if not r.get("unit_of_measure"):
            flags.append("MISSING_UNIT_OF_MEASURE")
        if (
            as_date(r.get("date"))
            and as_date(r["date"]) > datetime.now(timezone.utc).date()
            and r.get("units_sold") is not None
        ):
            flags.append("FUTURE_ACTUAL")
        if as_date(r.get("inventory_timestamp")) != as_date(r.get("date")):
            flags.append("INVENTORY_TIMESTAMP_CONFLICT")
        if as_date(r.get("forecast_generated_date")) and as_date(
            r["forecast_generated_date"]
        ) > as_date(r["date"]):
            flags.append("FORECAST_LEAKAGE")
    units = {r.get("unit_of_measure") for r in rows if r.get("unit_of_measure")}
    if len(units) > 1:
        flags.append("MIXED_UNIT_OF_MEASURE")
    return sorted(set(flags))


def _frame(spark, rows):
    """Explicit schema handles deliberately all-null external-signal columns."""
    from pyspark.sql.types import (
        StructType,
        StructField,
        StringType,
        DoubleType,
        LongType,
    )

    doubles = {
        "units_sold",
        "demand_forecast",
        "inventory_level",
        "price",
        "discount",
        "competitor_pricing",
    }
    integers = {"holiday_promotion", "forecast_horizon_days", "seed"}
    columns = list(rows[0])
    schema = StructType(
        [
            StructField(
                k,
                DoubleType()
                if k in doubles
                else LongType()
                if k in integers
                else StringType(),
                True,
            )
            for k in columns
        ]
    )
    return spark.createDataFrame(
        [
            tuple(
                float(r[k]) if k in doubles and r[k] is not None else r[k]
                for k in columns
            )
            for r in rows
        ],
        schema,
    )


def _validate_source_schema(schema, required):
    """Reject missing or incompatible fields before any source row is changed."""
    from pyspark.sql.types import NumericType, StringType, DateType, TimestampType

    fields = {field.name: field.dataType for field in schema.fields}
    missing = sorted(required - set(fields))
    if missing:
        raise ValueError(
            "Existing fact schema is incomplete; missing: " + ", ".join(missing)
        )
    numeric = {
        "units_sold",
        "demand_forecast",
        "inventory_level",
        "price",
        "discount",
        "competitor_pricing",
        "holiday_promotion",
        "forecast_horizon_days",
    }
    date_like = {
        "date",
        "forecast_generated_date",
        "inventory_timestamp",
        "launch_date",
        "weather_observed_at",
    }
    incompatible = []
    for name in required:
        kind = fields[name]
        valid = (
            isinstance(kind, NumericType)
            if name in numeric
            else isinstance(kind, (StringType, DateType, TimestampType))
            if name in date_like
            else isinstance(kind, StringType)
        )
        if not valid:
            incompatible.append(f"{name}:{kind.simpleString()}")
    if incompatible:
        raise ValueError(
            "Existing fact schema has incompatible types: " + ", ".join(incompatible)
        )


def _append_frame(spark, rows, target_schema):
    """Project generated fixtures to the existing schema before append."""
    from pyspark.sql import functions as F

    generated = _frame(spark, rows)
    expressions = []
    for field in target_schema.fields:
        value = F.col(field.name) if field.name in generated.columns else F.lit(None)
        expressions.append(value.cast(field.dataType).alias(field.name))
    return generated.select(*expressions)


def _catalog(rows, known_products):
    """Build the exact product/region scopes present in the staged source."""
    known = {row["product_id"]: row["product_name"] for row in known_products}
    unique = {(r["product_id"], r["region"], r["category"]) for r in rows}
    return [
        {
            "product_id": product,
            "product_name": known.get(product, product),
            "region": region,
            "category": category,
        }
        for product, region, category in sorted(unique)
    ]


def initialize(spark, database="workspace.forecast_rca_lab", _after_source_write=None):
    database = checked_table(database)
    if not database.split(".")[-1].endswith("_lab"):
        raise ValueError(
            "Synthetic initialization is restricted to a dedicated *_lab schema."
        )
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {database}")
    # Only this serial initialization job creates the initial shared counter.
    # Reruns never reset its value, including after failed/charged calls.
    ledger = f"{database}.rca_paid_call_ledger"
    spark.sql(
        f"CREATE TABLE IF NOT EXISTS {ledger} (id INT, used BIGINT, token STRING) USING DELTA TBLPROPERTIES ('delta.isolationLevel'='Serializable')"
    )
    if spark.table(ledger).count() == 0:
        spark.sql(f"INSERT INTO {ledger} VALUES (1,0,'initialized')")
    generated, products = generate()
    golden = RecordsProvider(generated, products)
    golden_registry = certify(golden)
    failures = [r for r in golden_registry if r["validation"] == "FAIL"]
    if failures:
        raise RuntimeError(
            "A supported golden fixture failed. Registry publication is blocked."
        )
    fact = f"{database}.fact_sales_forecast"
    existed = spark.catalog.tableExists(fact)
    raw = spark.table(fact).limit(MAX_SOURCE_ROWS + 1).collect() if existed else []
    if len(raw) > MAX_SOURCE_ROWS:
        raise ValueError(
            "This small lab supports at most 20000 rows; use a scoped distributed certification job for larger sources."
        )
    existing_rows = [normalize(r.asDict()) for r in raw]
    required = set(generated[0]) - {"scenario", "dataset_version", "seed"}
    if existed:
        _validate_source_schema(spark.table(fact).schema, required)
    additions = missing_fixture_rows(existing_rows, generated)
    if len(existing_rows) + len(additions) > MAX_SOURCE_ROWS:
        raise ValueError("Adding lab fixtures would exceed the 20000-row safety limit.")
    staged_rows = existing_rows + additions
    staged_products = _catalog(staged_rows, products)
    staged = RecordsProvider(staged_rows, staged_products)
    registry = certify(staged, expectations=BRD_EXPECTED_SIGNALS)
    # Comprehensive quality checks run against the staged source before writes.
    for entry in registry:
        entity_rows = [
            r
            for r in staged_rows
            if r["product_id"] == entry["product_id"] and r["region"] == entry["region"]
        ]
        flags = audit(entity_rows)
        entry["quality_flags"] = ",".join(flags)
        entry["feature_version"] = FEATURE_VERSION
        if flags and entry["capability"] != "quality" and entry["status"] == "READY":
            entry.update(status="PARTIAL", data_quality="PARTIAL")
        if any(
            flag
            in {
                "DUPLICATE_GRAIN",
                "MISSING_KEY",
                "FUTURE_ACTUAL",
                "FORECAST_LEAKAGE",
                "MISSING_UNIT_OF_MEASURE",
                "MIXED_UNIT_OF_MEASURE",
            }
            for flag in flags
        ):
            entry.update(status="BLOCKED", validation="FAIL")
    source_failures = [r for r in registry if r["validation"] == "FAIL"]
    if source_failures:
        raise RuntimeError(
            "Staged source failed expected-signal or quality certification; no source rows or readiness were published."
        )

    # Validate the immutable golden table before changing the serving source.
    fixtures = f"{database}.rca_golden_fixtures"
    if spark.catalog.tableExists(fixtures):
        fixture_rows = [
            normalize(row.asDict())
            for row in spark.table(fixtures).limit(MAX_SOURCE_ROWS + 1).collect()
        ]
        if fingerprint(fixture_rows) != fingerprint(generated):
            raise RuntimeError(
                "Golden fixture table differs from the versioned BRD fixtures; it was preserved and publication was blocked."
            )

    # Only now is it safe to create or append. Matching grains are untouched.
    if not existed:
        _frame(spark, staged_rows).write.format("delta").mode(
            "errorifexists"
        ).saveAsTable(fact)
    elif additions:
        _append_frame(spark, additions, spark.table(fact).schema).write.format(
            "delta"
        ).mode("append").saveAsTable(fact)
    # Private test seam for proving that an interrupted multi-table publication
    # is repaired by an idempotent rerun. Production callers leave this unset.
    if _after_source_write:
        _after_source_write()
    if not spark.catalog.tableExists(fixtures):
        _frame(spark, generated).write.format("delta").mode(
            "errorifexists"
        ).saveAsTable(fixtures)

    # Re-read the committed source so its fingerprint matches served data types.
    rows = [normalize(r.asDict()) for r in spark.table(fact).collect()]
    actual_products = _catalog(rows, products)
    product_table = f"{database}.dim_product"
    if not spark.catalog.tableExists(product_table):
        spark.createDataFrame(actual_products).write.format("delta").mode(
            "errorifexists"
        ).saveAsTable(product_table)
    else:
        from delta.tables import DeltaTable

        DeltaTable.forName(spark, product_table).alias("t").merge(
            spark.createDataFrame(actual_products).alias("s"),
            "t.product_id=s.product_id AND t.region=s.region AND t.category=s.category",
        ).whenNotMatchedInsertAll().execute()
    actual_products = [
        normalize(r.asDict()) for r in spark.table(product_table).collect()
    ]
    provider = RecordsProvider(rows, actual_products)
    registry = certify(provider, expectations=BRD_EXPECTED_SIGNALS)
    # Retain the already computed audit decisions with the committed fingerprint.
    audit_by_scope = {
        (r["product_id"], r["region"], r["capability"], r["store_id"]): r
        for r in staged.registry
    }
    for entry in registry:
        audited = audit_by_scope[
            (
                entry["product_id"],
                entry["region"],
                entry["capability"],
                entry["store_id"],
            )
        ]
        for name in (
            "quality_flags",
            "feature_version",
            "data_quality",
            "status",
            "validation",
        ):
            if name in audited:
                entry[name] = audited[name]
    # Keep the five governed view contracts; calculations are deterministic.
    base = f"""SELECT *, CAST(date AS DATE) AS target_date,
        demand_forecast-units_sold AS forecast_error,
        ABS(demand_forecast-units_sold) AS absolute_error,
        units_sold*price AS gross_revenue,
        CASE WHEN discount BETWEEN 0 AND 100 AND discount_unit='percent'
          THEN units_sold*price*(1-discount/100) ELSE NULL END AS net_revenue,
        CASE WHEN inventory_level<=0 THEN 1 ELSE 0 END AS stockout_flag
        FROM {fact}"""
    # Validate collisions before replacing views in the lab schema.
    derived = {
        "target_date",
        "forecast_error",
        "absolute_error",
        "gross_revenue",
        "net_revenue",
        "stockout_flag",
    }
    if derived.intersection(rows[0]):
        columns = ", ".join("`" + c + "`" for c in rows[0] if c not in derived)
        base = base.replace("SELECT *", f"SELECT {columns}", 1)
    for view in (
        "vw_forecast_metrics",
        "vw_inventory_health",
        "vw_revenue_metrics",
        "vw_forecast_history",
        "vw_forecast_rca_features",
    ):
        spark.sql(f"CREATE OR REPLACE VIEW {database}.{view} AS {base}")
    # Direct Genie is a parallel interface. It receives one explicit-grain view
    # while the Teams application retains all existing governed view contracts.
    from genie_semantic import publish_genie_view

    publish_genie_view(spark, database)
    # Empty alias table means no approved aliases. In particular P001 != P0001.
    spark.sql(f"""CREATE TABLE IF NOT EXISTS {database}.dim_entity_alias
        (entity_id STRING, alias_value STRING, entity_type STRING, match_type STRING) USING DELTA""")
    spark.sql(f"""CREATE TABLE IF NOT EXISTS {database}.dim_store USING DELTA AS
        SELECT DISTINCT store_id,region FROM {fact}""")
    spark.sql(f"""CREATE TABLE IF NOT EXISTS {database}.dim_region USING DELTA AS
        SELECT DISTINCT region FROM {fact}""")
    spark.sql(f"""CREATE TABLE IF NOT EXISTS {database}.dim_calendar USING DELTA AS
        SELECT DISTINCT CAST(date AS DATE) date, YEAR(date) calendar_year, WEEKOFYEAR(date) calendar_week FROM {fact}""")
    # A version-keyed MERGE updates validation timestamps without duplicate rows.
    registry_frame = spark.createDataFrame(registry)
    registry_table = f"{database}.rca_readiness_registry"
    if not spark.catalog.tableExists(registry_table):
        registry_frame.write.format("delta").mode("errorifexists").saveAsTable(
            registry_table
        )
    else:
        from delta.tables import DeltaTable

        DeltaTable.forName(spark, registry_table).alias("t").merge(
            registry_frame.alias("s"),
            "t.source_version=s.source_version AND t.product_id=s.product_id AND t.region=s.region "
            "AND t.capability=s.capability AND t.store_id=s.store_id",
        ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
    delta_version = spark.sql(f"DESCRIBE HISTORY {fact} LIMIT 1").first()["version"]
    manifest = [
        {
            "source_version": provider.source_version,
            "delta_version": int(delta_version),
            "published_at": datetime.now(timezone.utc).isoformat(),
            "dataset_version": DATASET_VERSION,
            "fixture_checksum": fingerprint(generated),
        }
    ]
    # Publish the source manifest last, after features, tests and readiness.
    manifest_table = f"{database}.rca_source_manifest"
    frame = spark.createDataFrame(manifest)
    if not spark.catalog.tableExists(manifest_table):
        frame.write.format("delta").mode("errorifexists").saveAsTable(manifest_table)
    else:
        from delta.tables import DeltaTable

        DeltaTable.forName(spark, manifest_table).alias("t").merge(
            frame.alias("s"), "t.source_version=s.source_version"
        ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
    return {
        "source_version": provider.source_version,
        "rows": len(rows),
        "existing_rows": len(existing_rows),
        "generated_rows": len(additions),
        "golden_failures": len(failures),
        "source_failures": len(source_failures),
        "readiness_records": len(registry),
        "source_unchanged": not additions,
    }
