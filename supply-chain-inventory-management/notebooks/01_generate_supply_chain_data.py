"""
Supply Chain Synthetic Data Generation Pipeline
================================================

PURPOSE
-------
This script generates a comprehensive, realistic, and internally consistent
synthetic supply-chain dataset in Databricks Delta tables.  The data populates
the `workspace.forecast_db` schema and is designed to support the Agentic AI
Supply Chain Exception Management Platform described in the BRD (v1.0).

PIPELINE FLOW
-------------
    Configuration
        |
        v
    Master Data Generation   (suppliers, skus, warehouses)
        |
        v
    Transactional Data Generation  (inventory, demand_forecast,
        purchase_orders, po_lines, customer_orders, shipments)
        |
        v
    Event & Exception Data   (supplier_events, supply_chain_exceptions,
        inventory_movements)
        |
        v
    Observability Schemas    (agent_runs, agent_tool_calls, agent_decisions,
        human_approvals, action_execution)
        |
        v
    Bridge Table             (fact_sales_forecast  -- backward-compat)
        |
        v
    Analytical Views          (vw_forecast_metrics, vw_inventory_health)
        |
        v
    Data Validation           (referential integrity, non-negativity, dates)
        |
        v
    Summary Statistics        (row counts per table)

REPRODUCIBILITY
---------------
All randomness is seeded with SEED=42 so that re-running the script produces
identical data.  This is critical for scenario reproducibility and evaluation.

TABLES CREATED (all in workspace.forecast_db)
---------------------------------------------
  Master Data:     suppliers, skus, warehouses
  Transactional:   inventory, demand_forecast, purchase_orders,
                   purchase_order_lines, customer_orders, shipments
  Events:          supplier_events, supply_chain_exceptions,
                   inventory_movements
  Observability:   agent_runs, agent_tool_calls, agent_decisions,
                   human_approvals, action_execution
  Bridge:          fact_sales_forecast
  Views:           vw_forecast_metrics, vw_inventory_health

USAGE
-----
Run on Databricks serverless compute (any all-purpose cluster works too):
    python 01_generate_supply_chain_data.py

No external API calls are made.  All data is generated in-memory by Python
and persisted via Spark Delta writes.
"""

# ===========================================================================
# SECTION 1: IMPORTS
# ===========================================================================
# Standard-library imports for randomness, date arithmetic, and numerics
import random
import numpy as np
from datetime import datetime, timedelta

# PySpark imports for DataFrame creation and Delta table I/O
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, LongType,
    DoubleType, BooleanType, DateType, TimestampType
)
from pyspark.sql import functions as F

# ===========================================================================
# SECTION 2: CONFIGURATION
# ===========================================================================
# All knobs are centralised here.  Adjusting a constant changes data volumes
# or reference values without touching the generation logic below.

# --- Databricks Target -------------------------------------------------
# The Unity Catalog catalog and schema where all tables will be created.
CATALOG = "workspace"
SCHEMA = "forecast_db"
FULL_SCHEMA = f"{CATALOG}.{SCHEMA}"

# --- Reproducibility ----------------------------------------------------
SEED = 42                     # Fixed seed → identical output on every run

# --- Master Data Volumes (BRD §42.3) -----------------------------------
NUM_SUPPLIERS = 20            # BRD: "Generate at least 20 suppliers"
NUM_SKUS = 100                # BRD: "Generate at least 100 SKUs"
NUM_WAREHOUSES = 5            # BRD: "Generate at least 5 warehouses"
NUM_CUSTOMERS = 50            # Distinct customers that place orders

# --- Transactional Data Volumes (BRD §42.4) ----------------------------
NUM_PURCHASE_ORDERS = 500     # BRD: "At least 500 purchase orders"
MIN_PO_LINES = 1000          # BRD: "At least 1,000 PO lines"
NUM_CUSTOMER_ORDERS = 2000    # BRD: "At least 2,000 customer orders"
FORECAST_DAYS = 90           # BRD: "At least 90 days of demand forecasts"
NUM_SHIPMENTS = 300           # Shipment records
NUM_INVENTORY_MOVEMENTS = 500 # Inventory movement records

# --- Date Range ----------------------------------------------------------
# Master and transactional dates span the full calendar year 2024.
# The 90-day demand-forecast window starts on October 1, 2024.
DATA_START = datetime(2024, 1, 1)
DATA_END = datetime(2024, 12, 31)
FORECAST_START = datetime(2024, 10, 1)   # First day of the 90-day forecast

# --- Reference Data ------------------------------------------------------
# These lists define the categorical values used across tables.  Keeping them
# here makes it easy to extend (e.g. add a new product category) in one place.
CATEGORIES = ["Beverages", "Snacks", "Dairy", "Personal Care", "Home Care"]
REGIONS = ["North", "South", "East", "West", "Central"]
SUPPLIER_TYPES = ["Raw Material", "Component", "Finished Goods"]
WAREHOUSE_TYPES = ["Distribution", "Manufacturing", "Cross-Dock"]
CRITICALITY = ["High", "Medium", "Low"]
DEMAND_PROFILES = ["Stable", "Seasonal", "Trending", "Intermittent",
                   "New Launch", "Declining"]
WEATHER = ["Sunny", "Rainy", "Cloudy", "Snowy", "Stormy"]
ORDER_PRIORITIES = ["Critical", "High", "Medium", "Low"]
ORDER_STATUSES = ["Open", "Confirmed", "Shipped", "Delivered", "Cancelled"]
PO_STATUSES = ["Open", "Delivered", "Partially Delivered", "Delayed",
               "Cancelled"]
SHIPMENT_STATUSES = ["Planned", "In-Transit", "Delivered", "Delayed"]
EXCEPTION_TYPES = ["SUPPLIER_DELAY", "INVENTORY_SHORTAGE", "STOCKOUT_RISK",
                   "SHIPMENT_DELAY", "DEMAND_SPIKE", "WAREHOUSE_IMBALANCE"]
SEVERITY = ["HIGH", "MEDIUM", "LOW"]

# ===========================================================================
# SECTION 3: RANDOM SEED & SPARK SESSION
# ===========================================================================
# Seeding both Python's `random` and NumPy ensures every stochastic call
# (random.choice, np.random.normal, etc.) is deterministic across runs.
random.seed(SEED)
np.random.seed(SEED)

# Obtain the active Spark session.  On Databricks serverless this is
# auto-provisioned; on a cluster it is the notebook's default session.
spark = SparkSession.getActiveSession()

# ===========================================================================
# SECTION 4: SCHEMA CREATION
# ===========================================================================
# Create the Unity Catalog schema if it does not already exist.
# IF NOT EXISTS makes the script idempotent — safe to re-run.
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {FULL_SCHEMA}")
print(f"[OK] Schema '{FULL_SCHEMA}' is ready.")

# ===========================================================================
# SECTION 5: HELPER FUNCTIONS
# ===========================================================================

def write_table(df, table_name):
    """
    Persist a Spark DataFrame as a managed Delta table.

    Parameters
    ----------
    df : DataFrame
        The Spark DataFrame to write.
    table_name : str
        Logical table name (without catalog/schema prefix).

    The function:
      1. Overwrites the table if it already exists (mode='overwrite').
      2. Allows schema evolution (overwriteSchema='true') so column
         additions on re-runs do not fail.
      3. Uses Delta format for ACID transactions and time travel.
    """
    full_name = f"{FULL_SCHEMA}.{table_name}"
    (
        df.write
          .mode("overwrite")
          .option("overwriteSchema", "true")
          .format("delta")
          .saveAsTable(full_name)
    )
    print(f"  [OK] Written: {full_name}  ({df.count()} rows)")


def create_empty_table(schema, table_name):
    """
    Create an empty Delta table with an explicit schema.

    Used for observability tables that will be populated later by the
    agent orchestration layer — not by this data-generation script.
    """
    full_name = f"{FULL_SCHEMA}.{table_name}"
    spark.sql(f"DROP TABLE IF EXISTS {full_name}")
    empty_df = spark.createDataFrame([], schema)
    (
        empty_df.write
          .mode("overwrite")
          .option("overwriteSchema", "true")
          .format("delta")
          .saveAsTable(full_name)
    )
    print(f"  [OK] Created empty table: {full_name}")


def random_date(start, end):
    """Return a random datetime between `start` and `end` (inclusive)."""
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


# ===========================================================================
# SECTION 6: MASTER DATA GENERATION
# ===========================================================================
# Master data is the foundation: every transactional table references these
# IDs.  Generating them first ensures foreign-key integrity downstream.

print("\n" + "=" * 60)
print("SECTION 6: Master Data Generation")
print("=" * 60)

# ---------------------------------------------------------------------------
# 6.1  SUPPLIERS  (BRD §42.3 — at least 20)
# ---------------------------------------------------------------------------
# Each supplier has a reliability score (0.60–0.99) that influences PO delay
# probabilities later.  `approved_supplier` flags whether the supplier can
# be used for alternate-sourcing recommendations.

print("\n[6.1] Generating suppliers...")

# Supplier name prefixes paired with suffixes for realistic naming
SUPPLIER_PREFIXES = ["Global", "Prime", "Apex", "Nexus", "Vertex",
                     "Summit", "Pinnacle", "Atlas", "Zenith", "Meridian"]
SUPPLIER_SUFFIXES = ["Materials", "Components", "Supply Co", "Industries",
                     "Logistics", "Manufacturing", "Trading", "Partners"]
SUPPLIER_COUNTRIES = ["USA", "Germany", "China", "India", "Brazil",
                      "Japan", "Mexico", "UK", "Canada", "Vietnam"]

def generate_suppliers():
    """Generate a list of supplier dictionaries (20 suppliers)."""
    suppliers = []
    for i in range(1, NUM_SUPPLIERS + 1):
        # Build a realistic supplier name, e.g. "Global Materials"
        name = f"{random.choice(SUPPLIER_PREFIXES)} {random.choice(SUPPLIER_SUFFIXES)}"
        # Reliability score: higher is better; range 0.60–0.99
        reliability = round(random.uniform(0.60, 0.99), 2)
        # Lead time in days: 5–45 (shorter for domestic, longer for overseas)
        country = random.choice(SUPPLIER_COUNTRIES)
        base_lead = random.randint(5, 45)
        suppliers.append({
            "supplier_id": f"S{i:03d}",
            "supplier_name": name,
            "country": country,
            "region": random.choice(REGIONS),
            "status": random.choices(
                ["Active", "Inactive", "Under Review"],
                weights=[0.80, 0.10, 0.10]
            )[0],
            "supplier_type": random.choice(SUPPLIER_TYPES),
            "lead_time_days": base_lead,
            "reliability_score": reliability,
            "approved_supplier": random.choices([True, False],
                                                  weights=[0.75, 0.25])[0],
            "capacity_units": random.randint(5000, 50000),
            "unit_cost": round(random.uniform(0.50, 25.00), 2),
        })
    return suppliers

supplier_rows = generate_suppliers()
supplier_schema = StructType([
    StructField("supplier_id", StringType(), False),
    StructField("supplier_name", StringType(), False),
    StructField("country", StringType(), True),
    StructField("region", StringType(), True),
    StructField("status", StringType(), True),
    StructField("supplier_type", StringType(), True),
    StructField("lead_time_days", IntegerType(), True),
    StructField("reliability_score", DoubleType(), True),
    StructField("approved_supplier", BooleanType(), True),
    StructField("capacity_units", IntegerType(), True),
    StructField("unit_cost", DoubleType(), True),
])
supplier_df = spark.createDataFrame(supplier_rows, supplier_schema)
write_table(supplier_df, "suppliers")

# Extract supplier IDs for use in PO generation
supplier_ids = [s["supplier_id"] for s in supplier_rows]
supplier_lead_times = {s["supplier_id"]: s["lead_time_days"] for s in supplier_rows}

# ---------------------------------------------------------------------------
# 6.2  SKUs  (BRD §42.3 — at least 100)
# ---------------------------------------------------------------------------
# Each SKU is assigned a demand profile that controls the shape of its
# demand-forecast curve (stable, seasonal, trending, etc.).  The safety_stock
# and minimum_order_quantity fields are used by inventory and PO logic.

print("\n[6.2] Generating SKUs...")

def generate_skus():
    """Generate a list of SKU dictionaries (100 SKUs across categories)."""
    skus = []
    for i in range(1, NUM_SKUS + 1):
        cat = random.choice(CATEGORIES)
        # Base daily demand varies by criticality: High items sell more
        crit = random.choices(CRITICALITY, weights=[0.20, 0.50, 0.30])[0]
        base_demand = {"High": random.randint(400, 800),
                       "Medium": random.randint(150, 400),
                       "Low": random.randint(50, 150)}[crit]
        skus.append({
            "sku_id": f"SKU-{i:03d}",
            "sku_name": f"{cat[:3].upper()}-{i:03d} Product",
            "category": cat,
            "unit_cost": round(random.uniform(0.50, 50.00), 2),
            "standard_lead_time_days": random.randint(3, 30),
            "safety_stock": random.randint(100, 1000),
            "minimum_order_quantity": random.choice([50, 100, 200, 500]),
            "criticality": crit,
            # Store base demand for forecast generation (not persisted)
            "_base_daily_demand": base_demand,
            "_demand_profile": random.choices(
                DEMAND_PROFILES,
                weights=[0.25, 0.20, 0.15, 0.15, 0.10, 0.15]
            )[0],
        })
    return skus

sku_rows = generate_skus()
sku_schema = StructType([
    StructField("sku_id", StringType(), False),
    StructField("sku_name", StringType(), True),
    StructField("category", StringType(), True),
    StructField("unit_cost", DoubleType(), True),
    StructField("standard_lead_time_days", IntegerType(), True),
    StructField("safety_stock", IntegerType(), True),
    StructField("minimum_order_quantity", IntegerType(), True),
    StructField("criticality", StringType(), True),
])
# Only persist the schema-relevant columns (drop private _fields)
sku_persist = [{k: v for k, v in row.items() if not k.startswith("_")}
               for row in sku_rows]
sku_df = spark.createDataFrame(sku_persist, sku_schema)
write_table(sku_df, "skus")

# Keep full dicts (with _base_daily_demand and _demand_profile) for downstream use
sku_ids = [s["sku_id"] for s in sku_rows]
sku_base_demand = {s["sku_id"]: s["_base_daily_demand"] for s in sku_rows}
sku_profiles = {s["sku_id"]: s["_demand_profile"] for s in sku_rows}
sku_safety = {s["sku_id"]: s["safety_stock"] for s in sku_rows}
sku_categories = {s["sku_id"]: s["category"] for s in sku_rows}
sku_cost = {s["sku_id"]: s["unit_cost"] for s in sku_rows}

# ---------------------------------------------------------------------------
# 6.3  WAREHOUSES  (BRD §42.3 — at least 5)
# ---------------------------------------------------------------------------
# Each warehouse is assigned a region so that region-comparison queries work.
# Capacity controls how much inventory can be stored.

print("\n[6.3] Generating warehouses...")

WAREHOUSE_NAMES = [
    ("WH01", "Northgate Distribution Center", "Chicago, IL", "North"),
    ("WH02", "Southport Logistics Hub", "Atlanta, GA", "South"),
    ("WH03", "Eastbay Cross-Dock Facility", "Newark, NJ", "East"),
    ("WH04", "Westend Distribution Center", "Long Beach, CA", "West"),
    ("WH05", "Central Hub Warehouse", "Kansas City, MO", "Central"),
]

def generate_warehouses():
    """Generate a list of warehouse dictionaries (5 warehouses)."""
    warehouses = []
    for wh_id, name, loc, region in WAREHOUSE_NAMES:
        warehouses.append({
            "warehouse_id": wh_id,
            "warehouse_name": name,
            "location": loc,
            "region": region,
            "capacity": random.randint(50000, 200000),
            "warehouse_type": random.choice(WAREHOUSE_TYPES),
        })
    return warehouses

warehouse_rows = generate_warehouses()
warehouse_schema = StructType([
    StructField("warehouse_id", StringType(), False),
    StructField("warehouse_name", StringType(), True),
    StructField("location", StringType(), True),
    StructField("region", StringType(), True),
    StructField("capacity", IntegerType(), True),
    StructField("warehouse_type", StringType(), True),
])
warehouse_df = spark.createDataFrame(warehouse_rows, warehouse_schema)
write_table(warehouse_df, "warehouses")

warehouse_ids = [w["warehouse_id"] for w in warehouse_rows]
warehouse_regions = {w["warehouse_id"]: w["region"] for w in warehouse_rows}


# ===========================================================================
# SECTION 7: TRANSACTIONAL DATA GENERATION
# ===========================================================================
# Transactional data references the master data via foreign keys.
# Generation order matters: inventory and demand_forecast are produced first
# because the fact_sales_forecast bridge table depends on them.

print("\n" + "=" * 60)
print("SECTION 7: Transactional Data Generation")
print("=" * 60)

# ---------------------------------------------------------------------------
# 7.1  INVENTORY  (one record per SKU × warehouse = 500 rows)
# ---------------------------------------------------------------------------
# Inventory snapshot for every SKU/warehouse combination.
#   on_hand   = physical units currently in the warehouse
#   allocated = units reserved for existing customer orders
#   available = on_hand - allocated (must be >= 0)
#   in_transit = units on their way from a supplier
#   safety_stock = from the SKU master data

print("\n[7.1] Generating inventory snapshots...")

def generate_inventory():
    """Generate inventory records for every SKU × warehouse pair."""
    rows = []
    for sku in sku_ids:
        ss = sku_safety[sku]
        for wh in warehouse_ids:
            # On-hand: range from 0 to 5,000; ~10% of SKUs have low stock
            on_hand = random.randint(0, 5000)
            # Allocated cannot exceed on_hand
            allocated = random.randint(0, on_hand)
            available = on_hand - allocated
            # In-transit: 0–2,000
            in_transit = random.randint(0, 2000)
            rows.append({
                "warehouse_id": wh,
                "sku_id": sku,
                "on_hand": on_hand,
                "allocated": allocated,
                "available": available,
                "in_transit": in_transit,
                "safety_stock": ss,
            })
    return rows

inventory_rows = generate_inventory()
inventory_schema = StructType([
    StructField("warehouse_id", StringType(), False),
    StructField("sku_id", StringType(), False),
    StructField("on_hand", IntegerType(), True),
    StructField("allocated", IntegerType(), True),
    StructField("available", IntegerType(), True),
    StructField("in_transit", IntegerType(), True),
    StructField("safety_stock", IntegerType(), True),
])
inventory_df = spark.createDataFrame(inventory_rows, inventory_schema)
write_table(inventory_df, "inventory")

# ---------------------------------------------------------------------------
# 7.2  DEMAND FORECAST  (100 SKUs × 90 days = 9,000 rows)
# ---------------------------------------------------------------------------
# Daily demand forecast for 90 days.  Each SKU has a demand profile that
# controls the time-series shape:
#   Stable      — flat with small noise
#   Seasonal    — sine wave (weekly seasonality)
#   Trending    — linear upward trend
#   Intermittent — mostly zero with occasional spikes
#   New Launch  — starts at 0, ramps up
#   Declining   — linear downward trend
# Both `forecast_quantity` (the model prediction) and `actual_quantity`
# (ground truth) are generated.  The forecast is the actual plus bias noise,
# so forecast accuracy/bias metrics can be computed.

print("\n[7.2] Generating demand forecasts (90 days × 100 SKUs)...")

def generate_demand_forecast():
    """Generate 90 days of daily demand forecasts for all SKUs."""
    rows = []
    for sku in sku_ids:
        profile = sku_profiles[sku]
        base = sku_base_demand[sku]
        for d in range(FORECAST_DAYS):
            date = (FORECAST_START + timedelta(days=d)).date()

            # --- Actual demand based on profile ---
            if profile == "Stable":
                actual = max(0, int(np.random.normal(base, base * 0.10)))
            elif profile == "Seasonal":
                # Weekly sine wave: peak mid-week, trough weekends
                seasonal = base * (1 + 0.30 * np.sin(2 * np.pi * d / 7))
                actual = max(0, int(np.random.normal(seasonal, base * 0.15)))
            elif profile == "Trending":
                # Linear upward trend over 90 days
                trend = base + (d / FORECAST_DAYS) * base * 0.5
                actual = max(0, int(np.random.normal(trend, base * 0.10)))
            elif profile == "Intermittent":
                # Mostly zero; ~20% of days have demand
                actual = int(np.random.normal(base * 2, base * 0.30)) if random.random() < 0.20 else 0
            elif profile == "New Launch":
                # Ramp up from 0 to base over first 30 days, then stable
                ramp = min(base, base * (d / 30)) if d < 30 else base
                actual = max(0, int(np.random.normal(ramp, base * 0.15)))
            else:  # Declining
                decline = base * (1 - d / FORECAST_DAYS * 0.6)
                actual = max(0, int(np.random.normal(decline, base * 0.10)))

            # Inject demand spikes on ~3% of days (for exception scenarios)
            if random.random() < 0.03:
                actual = int(actual * random.uniform(2.5, 4.0))

            # --- Forecast = actual + bias noise ---
            # Bias is intentionally non-zero so forecast_bias metrics are
            # meaningful.  Positive bias means over-forecasting.
            bias_pct = np.random.normal(0.05, 0.15)  # mean +5% over-forecast
            forecast = max(0, int(actual * (1 + bias_pct)))

            rows.append({
                "date": date,
                "sku_id": sku,
                "forecast_quantity": forecast,
                "actual_quantity": actual,
                "demand_profile": profile,
            })
    return rows

forecast_rows = generate_demand_forecast()
forecast_schema = StructType([
    StructField("date", DateType(), False),
    StructField("sku_id", StringType(), False),
    StructField("forecast_quantity", IntegerType(), True),
    StructField("actual_quantity", IntegerType(), True),
    StructField("demand_profile", StringType(), True),
])
forecast_df = spark.createDataFrame(forecast_rows, forecast_schema)
write_table(forecast_df, "demand_forecast")

# ---------------------------------------------------------------------------
# 7.3  PURCHASE ORDERS & PO LINES  (500+ POs, 1,000+ lines)
# ---------------------------------------------------------------------------
# Each PO is linked to a supplier.  PO status determines received_quantity:
#   Delivered          → received = ordered
#   Partially Delivered → received = 50–90% of ordered
#   Delayed            → received = 0–30% of ordered
#   Open / Cancelled    → received = 0
# Each PO has 1–5 lines, each referencing a SKU.

print("\n[7.3] Generating purchase orders and PO lines...")

def generate_purchase_orders_and_lines():
    """Generate purchase orders and their line items."""
    po_rows = []
    line_rows = []
    line_counter = 0

    for i in range(1, NUM_PURCHASE_ORDERS + 1):
        po_id = f"PO-{i:05d}"
        supplier = random.choice(supplier_ids)
        lead_time = supplier_lead_times[supplier]
        status = random.choices(
            PO_STATUSES,
            weights=[0.20, 0.35, 0.15, 0.15, 0.15]
        )[0]

        # Order date: within last 120 days before DATA_END
        order_date = (DATA_END - timedelta(days=random.randint(0, 120))).date()
        # Expected delivery = order date + supplier lead time
        expected_delivery = order_date + timedelta(days=lead_time)

        # Actual delivery for delivered/delayed POs
        if status == "Delivered":
            actual_delivery = expected_delivery
        elif status == "Delayed":
            actual_delivery = expected_delivery + timedelta(
                days=random.randint(3, 10))
        elif status == "Partially Delivered":
            actual_delivery = expected_delivery + timedelta(
                days=random.randint(0, 5))
        else:
            actual_delivery = None

        po_rows.append({
            "po_id": po_id,
            "supplier_id": supplier,
            "status": status,
            "order_date": order_date,
            "expected_delivery": expected_delivery,
            "actual_delivery": actual_delivery,
        })

        # Generate 1–5 PO lines per PO
        num_lines = random.randint(1, 5)
        for j in range(1, num_lines + 1):
            line_counter += 1
            sku = random.choice(sku_ids)
            ordered = random.randint(100, 5000)
            # Received quantity depends on PO status
            if status == "Delivered":
                received = ordered
            elif status == "Partially Delivered":
                received = int(ordered * random.uniform(0.50, 0.90))
            elif status == "Delayed":
                received = int(ordered * random.uniform(0, 0.30))
            else:
                received = 0

            line_rows.append({
                "po_id": po_id,
                "line_id": j,
                "sku_id": sku,
                "ordered_quantity": ordered,
                "received_quantity": received,
                "expected_delivery": expected_delivery,
                "unit_cost": sku_cost[sku],
            })

    return po_rows, line_rows

po_rows, pol_rows = generate_purchase_orders_and_lines()
po_schema = StructType([
    StructField("po_id", StringType(), False),
    StructField("supplier_id", StringType(), True),
    StructField("status", StringType(), True),
    StructField("order_date", DateType(), True),
    StructField("expected_delivery", DateType(), True),
    StructField("actual_delivery", DateType(), True),
])
po_df = spark.createDataFrame(po_rows, po_schema)
write_table(po_df, "purchase_orders")

pol_schema = StructType([
    StructField("po_id", StringType(), False),
    StructField("line_id", IntegerType(), False),
    StructField("sku_id", StringType(), True),
    StructField("ordered_quantity", IntegerType(), True),
    StructField("received_quantity", IntegerType(), True),
    StructField("expected_delivery", DateType(), True),
    StructField("unit_cost", DoubleType(), True),
])
pol_df = spark.createDataFrame(pol_rows, pol_schema)
write_table(pol_df, "purchase_order_lines")

# ---------------------------------------------------------------------------
# 7.4  CUSTOMER ORDERS  (2,000 rows)
# ---------------------------------------------------------------------------
# Each customer order references a SKU and has a requested delivery date.
# Priority and status are weighted to produce a realistic mix.

print("\n[7.4] Generating customer orders...")

def generate_customer_orders():
    """Generate 2,000 customer orders."""
    rows = []
    for i in range(1, NUM_CUSTOMER_ORDERS + 1):
        order_date = (DATA_END - timedelta(days=random.randint(0, 180))).date()
        requested_delivery = order_date + timedelta(
            days=random.randint(3, 30))
        rows.append({
            "order_id": f"CO-{i:05d}",
            "customer_id": f"C{random.randint(1, NUM_CUSTOMERS):03d}",
            "sku_id": random.choice(sku_ids),
            "quantity": random.randint(10, 1000),
            "order_date": order_date,
            "requested_delivery_date": requested_delivery,
            "priority": random.choices(ORDER_PRIORITIES,
                                       weights=[0.05, 0.25, 0.50, 0.20])[0],
            "status": random.choices(
                ORDER_STATUSES,
                weights=[0.15, 0.25, 0.25, 0.30, 0.05]
            )[0],
        })
    return rows

co_rows = generate_customer_orders()
co_schema = StructType([
    StructField("order_id", StringType(), False),
    StructField("customer_id", StringType(), True),
    StructField("sku_id", StringType(), True),
    StructField("quantity", IntegerType(), True),
    StructField("order_date", DateType(), True),
    StructField("requested_delivery_date", DateType(), True),
    StructField("priority", StringType(), True),
    StructField("status", StringType(), True),
])
co_df = spark.createDataFrame(co_rows, co_schema)
write_table(co_df, "customer_orders")

# ---------------------------------------------------------------------------
# 7.5  SHIPMENTS  (300 rows)
# ---------------------------------------------------------------------------
# Shipments are linked to PO lines and have origin (supplier country) and
# destination (warehouse).  Status determines delivery dates.

print("\n[7.5] Generating shipments...")

def generate_shipments():
    """Generate 300 shipment records linked to purchase orders."""
    rows = []
    for i in range(1, NUM_SHIPMENTS + 1):
        # Pick a random PO that has lines
        po = random.choice(po_rows)
        po_id = po["po_id"]
        # Origin = supplier country (look up from supplier_rows)
        supplier = next(s for s in supplier_rows if s["supplier_id"] == po["supplier_id"])
        origin = supplier["country"]
        dest = random.choice(warehouse_ids)
        status = random.choices(
            SHIPMENT_STATUSES,
            weights=[0.15, 0.30, 0.40, 0.15]
        )[0]
        ship_date = (DATA_END - timedelta(days=random.randint(0, 90))).date()
        expected_arrival = ship_date + timedelta(days=random.randint(3, 20))

        if status == "Delivered":
            actual_arrival = expected_arrival
        elif status == "Delayed":
            actual_arrival = expected_arrival + timedelta(days=random.randint(2, 8))
        else:
            actual_arrival = None

        rows.append({
            "shipment_id": f"SHP-{i:04d}",
            "po_id": po_id,
            "origin": origin,
            "destination_warehouse": dest,
            "status": status,
            "ship_date": ship_date,
            "expected_arrival": expected_arrival,
            "actual_arrival": actual_arrival,
            "carrier": random.choice(["FedEx", "UPS", "DHL", "Maersk", "DB Schenker"]),
        })
    return rows

ship_rows = generate_shipments()
ship_schema = StructType([
    StructField("shipment_id", StringType(), False),
    StructField("po_id", StringType(), True),
    StructField("origin", StringType(), True),
    StructField("destination_warehouse", StringType(), True),
    StructField("status", StringType(), True),
    StructField("ship_date", DateType(), True),
    StructField("expected_arrival", DateType(), True),
    StructField("actual_arrival", DateType(), True),
    StructField("carrier", StringType(), True),
])
ship_df = spark.createDataFrame(ship_rows, ship_schema)
write_table(ship_df, "shipments")
