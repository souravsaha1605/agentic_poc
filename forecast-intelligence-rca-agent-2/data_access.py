"""Governed read adapters. SQL values are bound parameters, not interpolation.

Raw rows stay inside the deterministic backend. The LLM only sees the compact
evidence returned by business.py. A notebook Spark session and a hosted SQL
connection implement the same small query interface.
"""

import copy
import hashlib
import json
from datetime import date
from state import checked_table

MAX_SOURCE_ROWS = 20000


def fingerprint(records):
    # Spark partition order can change between runs; source identity must not.
    canonical = sorted(json.dumps(row, default=str, sort_keys=True) for row in records)
    return hashlib.sha256(json.dumps(canonical).encode()).hexdigest()


class RecordsProvider:
    """Explicit synthetic/test provider. Never silently used for enterprise data."""

    def __init__(self, rows, products, aliases=None, registry=None):
        self.rows = copy.deepcopy(rows)
        self.products = copy.deepcopy(products)
        self.aliases = aliases or {}
        self.registry = registry or []
        self.source_version = fingerprint(rows)
        self.source = "synthetic-lab/fact_sales_forecast"

    def catalog(self):
        return self.products

    def resolve_alias(self, text):
        return self.aliases.get(text.casefold(), [])

    def fetch(self, plan):
        selected = [
            r
            for r in self.rows
            if r["product_id"] == plan.product_id
            and r["region"] == plan.region
            and (not plan.store_id or r["store_id"] == plan.store_id)
            and (not plan.category or r["category"] == plan.category)
            and (not plan.channel or r.get("channel") == plan.channel)
            and (not plan.fiscal_period or r.get("fiscal_period") == plan.fiscal_period)
        ]
        if len(selected) > MAX_SOURCE_ROWS:
            raise ValueError("Source row limit exceeded; select a narrower scope.")
        return copy.deepcopy(selected)


class SparkQuery:
    def __init__(self, spark):
        self.spark = spark

    def query(self, sql, parameters=None):
        # Some Spark/Delta combinations lose named markers while expanding a
        # governed view. Bind values as DataFrame literals in a one-row relation
        # instead. SQL contains only references to these typed scalar values.
        # Each call has its own temporary view, so concurrent scopes cannot mix.
        import re
        import uuid
        from pyspark.sql import functions as F

        values = parameters or {}
        if not values:
            return [r.asDict(recursive=True) for r in self.spark.sql(sql).collect()]
        relation = "rca_parameters_" + uuid.uuid4().hex
        if any(not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key) for key in values):
            raise ValueError("Invalid parameter identifier.")
        frame = self.spark.range(1).select(
            *[F.lit(value).alias(key) for key, value in values.items()]
        )
        frame.createOrReplaceTempView(relation)
        try:

            def marker(match):
                key = match[1]
                if key not in values:
                    raise ValueError("Missing query parameter.")
                return f"(SELECT `{key}` FROM {relation})"

            bound = re.sub(r":([A-Za-z_][A-Za-z0-9_]*)", marker, sql)
            return [r.asDict(recursive=True) for r in self.spark.sql(bound).collect()]
        finally:
            self.spark.catalog.dropTempView(relation)


class DatabricksSQLQuery:
    """Pass a databricks.sql connection configured by the trusted host.

    Configure socket_timeout and the warehouse statement timeout at deployment.
    No Spark session or notebook-global variables are needed in an Azure worker.
    """

    def __init__(self, connection):
        self.connection = connection

    def query(self, sql, parameters=None):
        with self.connection.cursor() as cursor:
            cursor.execute(sql, parameters or {})
            names = [column[0] for column in cursor.description]
            rows = cursor.fetchmany(MAX_SOURCE_ROWS + 1)
            if len(rows) > MAX_SOURCE_ROWS:
                raise ValueError("Source row limit exceeded; narrow the scope.")
            return [dict(zip(names, row)) for row in rows]


class GovernedProvider:
    def __init__(self, query, database):
        self.query = query
        self.database = checked_table(database)
        # A published manifest is mandatory; it must change with the data/views.
        manifest = query.query(
            f"SELECT source_version, delta_version FROM {database}.rca_source_manifest "
            "ORDER BY published_at DESC LIMIT 1"
        )
        if not manifest:
            raise ValueError(
                "Publish a certified source manifest before serving requests."
            )
        self.source_version = manifest[0]["source_version"]
        self.delta_version = int(manifest[0]["delta_version"])
        self.source = f"{database}.vw_forecast_metrics"
        self.registry = query.query(
            f"SELECT * FROM {database}.rca_readiness_registry LIMIT 20000"
        )
        self.products = query.query(
            f"SELECT product_id, product_name, region, category "
            f"FROM {database}.dim_product LIMIT 10001"
        )
        if len(self.products) > 10000:
            raise ValueError(
                "Master catalogue too large; configure a scoped catalogue adapter."
            )

    def catalog(self):
        return self.products

    def resolve_alias(self, text):
        rows = self.query.query(
            f"SELECT entity_id FROM {self.database}.dim_entity_alias "
            "WHERE LOWER(alias_value)=:alias AND entity_type='product_id' LIMIT 10",
            {"alias": text.casefold()},
        )
        return [r["entity_id"] for r in rows]

    def fetch(self, plan):
        # Read only approved columns, always scope in SQL before collecting.
        # Period filtering is done here as well as in the analytical layer.
        self.check_source_version()
        clauses = ["product_id=:product", "region=:region"]
        args = {"product": plan.product_id, "region": plan.region}
        for column, value in [
            ("store_id", plan.store_id),
            ("category", plan.category),
            ("channel", plan.channel),
            ("fiscal_period", plan.fiscal_period),
        ]:
            if value:
                clauses.append(f"{column}=:{column}")
                args[column] = value
        if plan.tool == "get_inventory_context" and (plan.as_of or plan.end):
            clauses.append("date<=:inventory_cutoff")
            args["inventory_cutoff"] = plan.as_of or plan.end
        elif plan.start:
            clauses.append("date BETWEEN :start AND :end")
            args.update(start=plan.start, end=plan.end)
        elif plan.as_of:
            clauses.append("date<=:as_of")
            args["as_of"] = plan.as_of
        rows = self.query.query(
            f"""SELECT product_id, region, category, store_id, date,
            units_sold, demand_forecast, inventory_level, price, discount,
            holiday_promotion, competitor_pricing, weather_condition, seasonality,
            forecast_generated_date, forecast_horizon_days, currency, discount_unit,
            inventory_timestamp, launch_date, lifecycle_stage, channel, fiscal_period,
            fiscal_calendar_policy, weather_observed_at FROM {self.source}
            WHERE {" AND ".join(clauses)} ORDER BY date LIMIT {MAX_SOURCE_ROWS + 1}""",
            args,
        )
        if len(rows) > MAX_SOURCE_ROWS:
            raise ValueError("Source row limit exceeded; narrow the period/store.")
        self.check_source_version()
        from bootstrap import normalize

        return [normalize(r) for r in rows]

    def check_source_version(self):
        current = self.query.query(
            f"DESCRIBE HISTORY {self.database}.fact_sales_forecast LIMIT 1"
        )
        if not current or int(current[0]["version"]) != self.delta_version:
            raise ValueError(
                "Source changed after certification; refresh readiness before analysis."
            )


def as_date(value):
    if value is None:
        return None
    return date.fromisoformat(str(value)[:10])
