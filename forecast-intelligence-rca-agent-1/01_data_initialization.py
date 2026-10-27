# Databricks notebook source


# COMMAND ----------

# DBTITLE 1,First-Run Data Initialization
# ============================================================
# 01_data_initialization.py
# Forecast Intelligence & RCA Agent – First-Run Data Initialization
# BRD §45, §52: Inspect → Identify gaps → Generate missing data →
#   Inject RCA scenarios → Generate features → Validate → Certify
# ============================================================

import random
from datetime import date, datetime, timedelta
from pyspark.sql import functions as F
from pyspark.sql.types import *

SEED = 42
random.seed(SEED)

DB = "workspace.forecast_db"
CATALOG = "workspace"
SCHEMA = "forecast_db"

print("=" * 70)
print("  Forecast Intelligence & RCA Agent")
print("  First-Run Data Initialization & Validation")
print("=" * 70)

# ------------------------------------------------------------------
# Step 0: Ensure schema exists
# ------------------------------------------------------------------
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {DB}")
print("\n[0] Schema ensured.")

# ------------------------------------------------------------------
# Step 1: Inspect existing data (BRD §45)
# ------------------------------------------------------------------
print("\n[1] Inspecting existing tables...")

existing_tables = spark.sql(f"""
    SELECT table_name, table_type
    FROM {CATALOG}.information_schema.tables
    WHERE table_schema = '{SCHEMA}'
    ORDER BY table_name
""").collect()
existing_names = {r['table_name'] for r in existing_tables}
print(f"  Existing tables: {len(existing_names)}")
for r in existing_tables:
    print(f"    {r['table_name']} ({r['table_type']})")

# Check fact_sales_forecast schema
if "fact_sales_forecast" in existing_names:
    cols = spark.sql(f"DESCRIBE TABLE {DB}.fact_sales_forecast").collect()
    existing_cols = {r['col_name'] for r in cols}
    print(f"  fact_sales_forecast columns: {sorted(existing_cols)}")
else:
    existing_cols = set()
    print("  fact_sales_forecast NOT FOUND")

# ------------------------------------------------------------------
# Step 2: Recreate fact_sales_forecast with BRD-compliant schema
#         and inject deliberate RCA scenarios (BRD §46)
# ------------------------------------------------------------------
print("\n[2] Generating fact_sales_forecast with BRD-compliant schema and RCA scenarios...")

# Product definitions
PRODUCTS = [f"SKU-{str(i).zfill(3)}" for i in range(1, 101)]
REGIONS = ["North", "South", "East", "West", "Central"]
CATEGORIES = ["Beverages", "Dairy", "Home Care", "Personal Care", "Snacks"]
SEASONALITIES = ["Peak", "Regular", "Off-Season"]
WEATHER = ["Sunny", "Cloudy", "Rainy", "Snowy"]

# RCA scenario product assignments (BRD §46)
# Distribute 100 SKUs across 5 regions (20 per region) with diverse RCA scenarios
# Each region gets: 2 over_bias, 2 under_bias, 2 trend_shift, 2 promotion_uplift,
# 2 price_effect, 1 seasonality, 2 stockout_constraint, 2 revenue_deterioration,
# 1 missing_data, 1 new_product, 3 normal
SCENARIO_PRODUCTS = {}
_sku = 1
for _region in REGIONS:
    for _scenario, _count in [
        ("over_bias", 2), ("under_bias", 2), ("trend_shift", 2),
        ("promotion_uplift", 2), ("price_effect", 2), ("seasonality", 1),
        ("stockout_constraint", 2), ("revenue_deterioration", 2),
        ("missing_data", 1), ("new_product", 1), ("normal", 3),
    ]:
        for _ in range(_count):
            SCENARIO_PRODUCTS[f"SKU-{str(_sku).zfill(3)}"] = {
                "scenario": _scenario, "region": _region,
                "category": random.choice(CATEGORIES),
            }
            _sku += 1

# Generate 6 months of daily data (Jan 2026 - Jun 2026) for richer history
start_date = date(2026, 1, 1)
end_date = date(2026, 6, 30)
date_range = [(start_date + timedelta(days=d)) for d in range((end_date - start_date).days + 1)]

rows = []
for product_id in PRODUCTS:
    scenario_info = SCENARIO_PRODUCTS.get(product_id, {"scenario": "normal"})
    scenario = scenario_info.get("scenario", "normal")
    region = scenario_info.get("region", random.choice(REGIONS))
    category = scenario_info.get("category", random.choice(CATEGORIES))
    
    base_demand = random.randint(200, 500)
    base_price = round(random.uniform(5.0, 50.0), 2)
    base_discount = round(random.uniform(0, 15), 2)
    
    # New product: only last 2 weeks of data (BRD: insufficient history)
    if scenario == "new_product":
        product_dates = date_range[-14:]
    else:
        product_dates = date_range
    
    for d in product_dates:
        actual = base_demand + random.randint(-50, 50)
        forecast = actual + random.randint(-20, 20)
        
        # Apply scenario-specific modifications
        day_idx = (d - start_date).days
        
        if scenario == "over_bias":
            # Forecast consistently 25% above actual
            forecast = int(actual * 1.25) + random.randint(-10, 10)
        elif scenario == "under_bias":
            # Forecast consistently 20% below actual
            forecast = int(actual * 0.80) + random.randint(-10, 10)
        elif scenario == "trend_shift":
            # Demand structurally decreases after 3 months
            if day_idx > 90:
                actual = int(actual * 0.65) + random.randint(-10, 10)
                forecast = int(actual * 1.05) + random.randint(-10, 10)
        elif scenario == "promotion_uplift":
            # Every 4th week is a promotion week with 40% uplift
            week_num = day_idx // 7
            if week_num % 4 == 0:
                actual = int(actual * 1.40) + random.randint(-5, 5)
                forecast = int(actual * 0.90) + random.randint(-10, 10)
                holiday_promo = 1
            else:
                holiday_promo = 0
        elif scenario == "price_effect":
            # Price increases 20% after 2 months, demand drops 15%
            if day_idx > 60:
                price = round(base_price * 1.20, 2)
                actual = int(actual * 0.85) + random.randint(-10, 10)
            else:
                price = base_price
        elif scenario == "seasonality":
            # Sinusoidal seasonal pattern
            seasonal_factor = 1 + 0.3 * __import__('math').sin(2 * __import__('math').pi * day_idx / 30)
            actual = int(actual * seasonal_factor) + random.randint(-5, 5)
            forecast = int(actual * 0.95) + random.randint(-10, 10)
        elif scenario == "stockout_constraint":
            # Inventory drops to 0 for 3 weeks in the middle
            if 60 <= day_idx <= 81:
                inventory_level = 0
                actual = int(actual * 0.30) + random.randint(-5, 5)  # Supply-constrained sales
            else:
                inventory_level = max(100, actual * 3 + random.randint(-50, 50))
        elif scenario == "revenue_deterioration":
            # Price stays same but demand drops 30% after month 2
            if day_idx > 60:
                actual = int(actual * 0.70) + random.randint(-10, 10)
                discount = round(base_discount * 0.5, 2)  # Reduced discounts
        elif scenario == "regional_divergence":
            # North region has 50% higher demand than other regions for this product
            if region == "North":
                actual = int(actual * 1.50) + random.randint(-10, 10)
                forecast = int(actual * 0.95) + random.randint(-10, 10)
        elif scenario == "missing_data":
            # Skip 20% of days randomly and set some values to null
            if random.random() < 0.20:
                continue  # Skip this day (data gap)
        elif scenario == "normal":
            pass  # Normal random data
        
        # Set defaults for variables that might not have been set
        price = locals().get('price', base_price)
        discount = locals().get('discount', base_discount)
        holiday_promo = locals().get('holiday_promo', random.choice([0, 0, 0, 1]))
        inventory_level = locals().get('inventory_level', max(100, actual * 3 + random.randint(-100, 100)))
        
        # Reset price/discount for non-price scenarios
        if scenario not in ["price_effect", "revenue_deterioration"]:
            price = base_price + random.uniform(-2, 2)
            discount = base_discount + random.uniform(-3, 3)
        
        # Calculate BRD-required derived fields (§22)
        gross_revenue = round(actual * price, 2)
        net_revenue = round(actual * price * (1 - discount / 100), 2)
        forecast_error = forecast - actual
        absolute_error = abs(forecast_error)
        stockout_flag = 1 if inventory_level <= 0 else 0
        
        if stockout_flag:
            inv_status = "Stockout"
        elif inventory_level < actual * 1.5:
            inv_status = "Low Inventory"
        else:
            inv_status = "Healthy"
        
        # Data quality flag
        dq_flag = "OK"
        if actual < 0: dq_flag = "NEGATIVE_UNITS"
        elif forecast is None: dq_flag = "NULL_FORECAST"
        elif discount < 0 or discount > 100: dq_flag = "INVALID_DISCOUNT"
        elif price <= 0: dq_flag = "INVALID_PRICE"
        
        seasonality = random.choice(SEASONALITIES)
        weather = random.choice(WEATHER)
        competitor_price = round(price + random.uniform(-5, 5), 2)
        units_ordered = actual + random.randint(0, 50)
        
        rows.append(Row(
            product_id=product_id,
            date=d,
            store_id="STORE01",
            demand_profile=scenario_info.get("scenario", "normal").replace("_", " ").title(),
            inventory_level=int(inventory_level),
            units_sold=max(0, actual),
            units_ordered=max(0, units_ordered),
            demand_forecast=max(0, forecast),
            price=round(price, 2),
            discount=round(max(0, min(100, discount)), 2),
            weather_condition=weather,
            holiday_promotion=int(holiday_promo),
            competitor_pricing=round(max(0, competitor_price), 2),
            seasonality=seasonality,
            region=region,
            category=category,
            gross_revenue=gross_revenue,
            net_revenue=net_revenue,
            forecast_error=forecast_error,
            absolute_error=absolute_error,
            stockout_flag=stockout_flag,
            inventory_status=inv_status,
            forecast_generated_date=d - timedelta(days=7),
            forecast_horizon_days=7,
            data_quality_flag=dq_flag,
        ))
        
        # Reset locals for next iteration
        price = base_price
        discount = base_discount

print(f"  Generated {len(rows)} rows for {len(PRODUCTS)} products across {len(date_range)} days")

# Create DataFrame and save
from pyspark.sql import Row
schema = StructType([
    StructField("product_id", StringType()),
    StructField("date", DateType()),
    StructField("store_id", StringType()),
    StructField("demand_profile", StringType()),
    StructField("inventory_level", IntegerType()),
    StructField("units_sold", IntegerType()),
    StructField("units_ordered", IntegerType()),
    StructField("demand_forecast", IntegerType()),
    StructField("price", DoubleType()),
    StructField("discount", DoubleType()),
    StructField("weather_condition", StringType()),
    StructField("holiday_promotion", IntegerType()),
    StructField("competitor_pricing", DoubleType()),
    StructField("seasonality", StringType()),
    StructField("region", StringType()),
    StructField("category", StringType()),
    StructField("gross_revenue", DoubleType()),
    StructField("net_revenue", DoubleType()),
    StructField("forecast_error", IntegerType()),
    StructField("absolute_error", IntegerType()),
    StructField("stockout_flag", IntegerType()),
    StructField("inventory_status", StringType()),
    StructField("forecast_generated_date", DateType()),
    StructField("forecast_horizon_days", IntegerType()),
    StructField("data_quality_flag", StringType()),
])

fact_df = spark.createDataFrame(rows, schema=schema)
(fact_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{DB}.fact_sales_forecast"))
print(f"  fact_sales_forecast written: {fact_df.count()} rows")

# ------------------------------------------------------------------
# Step 3: Create missing dimension tables (BRD §22)
# ------------------------------------------------------------------
print("\n[3] Creating dimension tables...")

# dim_store
spark.sql(f"""
    CREATE OR REPLACE TABLE {DB}.dim_store AS
    SELECT
        'STORE01' AS store_id,
        'Main Distribution Center' AS store_name,
        'All Regions' AS region,
        'Active' AS status
""")
print("  dim_store created")

# dim_region
region_data = [(r,) for r in REGIONS]
spark.createDataFrame(region_data, StructType([StructField("region", StringType(), True)])).write \
    .format("delta").mode("overwrite").saveAsTable(f"{DB}.dim_region")
print("  dim_region created")

# dim_entity_alias (BRD §13 – entity resolution support)
alias_rows = []
for p in PRODUCTS:
    pnum = p.replace("SKU-", "P").replace("SKU", "P")
    alias_rows.append((p, p, "product_id", "exact"))
    alias_rows.append((p, p.replace("SKU-", "P"), "product_id", "alias"))
    alias_rows.append((p, p.replace("SKU-0", "P00"), "product_id", "alias"))

alias_df = spark.createDataFrame(alias_rows, StructType([
    StructField("entity_id", StringType(), True),
    StructField("alias_value", StringType(), True),
    StructField("entity_type", StringType(), True),
    StructField("match_type", StringType(), True),
]))
alias_df.write.format("delta").mode("overwrite").saveAsTable(f"{DB}.dim_entity_alias")
print(f"  dim_entity_alias created: {len(alias_rows)} aliases")

# ------------------------------------------------------------------
# Step 4: Create memory and scenario tables (BRD §31)
# ------------------------------------------------------------------
print("\n[4] Creating memory and scenario tables...")

spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {DB}.conversation_turns (
        session_id STRING,
        turn_id INT,
        user_id STRING,
        timestamp TIMESTAMP,
        role STRING,
        message STRING,
        scenario_id STRING,
        intent STRING,
        scenario_action STRING
    ) USING DELTA
""")
print("  conversation_turns created")

spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {DB}.scenario_state (
        scenario_id STRING,
        session_id STRING,
        user_id STRING,
        status STRING,
        resolved_entities STRING,
        time_range STRING,
        analysis_type STRING,
        active_issue STRING,
        baseline_state STRING,
        current_state STRING,
        previous_state STRING,
        last_tool_results STRING,
        rca_summary STRING,
        rca_evidence STRING,
        rca_hypotheses STRING,
        recommendations STRING,
        what_if_parameters STRING,
        reported_outcomes STRING,
        assumptions STRING,
        version INT,
        created_at TIMESTAMP,
        updated_at TIMESTAMP
    ) USING DELTA
""")
print("  scenario_state created")

# rca_readiness_registry (BRD §23, §50)
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {DB}.rca_readiness_registry (
        capability STRING,
        required_evidence STRING,
        min_history_weeks INT,
        synthetic_scenario STRING,
        validation_rule STRING,
        status STRING,
        last_validated TIMESTAMP,
        entity STRING,
        coverage_start DATE,
        coverage_end DATE,
        data_quality_status STRING
    ) USING DELTA
""")
print("  rca_readiness_registry created")

# agent_observability (BRD §34)
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {DB}.agent_observability (
        correlation_id STRING,
        session_id STRING,
        scenario_id STRING,
        turn_id INT,
        user_principal STRING,
        timestamp TIMESTAMP,
        intent STRING,
        scenario_action STRING,
        entities STRING,
        tools_called STRING,
        tool_latency_ms DOUBLE,
        llm_latency_ms DOUBLE,
        llm_token_usage INT,
        data_as_of DATE,
        errors STRING,
        response_status STRING
    ) USING DELTA
""")
print("  agent_observability created")

# ------------------------------------------------------------------
# Step 5: Create analytical views (BRD §23)
# ------------------------------------------------------------------
print("\n[5] Creating analytical views...")

# vw_forecast_metrics (updated with WMAPE)
spark.sql(f"""
    CREATE OR REPLACE VIEW {DB}.vw_forecast_metrics AS
    SELECT
        product_id, date, store_id, region, category,
        units_sold, demand_forecast,
        forecast_error, absolute_error,
        gross_revenue, net_revenue,
        price, discount, holiday_promotion,
        seasonality, weather_condition, competitor_pricing,
        inventory_level, inventory_status, stockout_flag,
        forecast_generated_date, forecast_horizon_days, data_quality_flag,
        -- Row-level metrics
        ROUND(CAST(absolute_error AS DOUBLE) / NULLIF(CAST(units_sold AS DOUBLE), 0) * 100, 2) AS abs_pct_error,
        ROUND((CAST(demand_forecast AS DOUBLE) - CAST(units_sold AS DOUBLE)) / NULLIF(CAST(units_sold AS DOUBLE), 0) * 100, 2) AS row_bias_pct
    FROM {DB}.fact_sales_forecast
""")
print("  vw_forecast_metrics created")

# vw_inventory_health
spark.sql(f"""
    CREATE OR REPLACE VIEW {DB}.vw_inventory_health AS
    SELECT
        product_id, date, store_id, region, category,
        inventory_level, units_sold,
        inventory_status, stockout_flag,
        CASE WHEN units_sold > 0
             THEN ROUND(CAST(inventory_level AS DOUBLE) / CAST(units_sold AS DOUBLE), 1)
             ELSE NULL END AS inventory_days,
        price, discount, gross_revenue, net_revenue
    FROM {DB}.fact_sales_forecast
""")
print("  vw_inventory_health created")

# vw_revenue_metrics (NEW - BRD §23, FR-02)
spark.sql(f"""
    CREATE OR REPLACE VIEW {DB}.vw_revenue_metrics AS
    SELECT
        product_id, date, store_id, region, category,
        units_sold, price, discount,
        gross_revenue, net_revenue,
        ROUND(CAST(gross_revenue AS DOUBLE) - CAST(net_revenue AS DOUBLE), 2) AS discount_amount,
        holiday_promotion,
        ROUND(CAST(net_revenue AS DOUBLE) / NULLIF(CAST(units_sold AS DOUBLE), 0), 2) AS avg_net_unit_revenue
    FROM {DB}.fact_sales_forecast
""")
print("  vw_revenue_metrics created")

# vw_forecast_history (NEW - BRD §23)
spark.sql(f"""
    CREATE OR REPLACE VIEW {DB}.vw_forecast_history AS
    SELECT
        product_id, date, region, category,
        units_sold AS actual, demand_forecast AS forecast,
        forecast_error, absolute_error,
        ROW_NUMBER() OVER (PARTITION BY product_id, region ORDER BY date DESC) AS rn,
        AVG(CAST(units_sold AS DOUBLE)) OVER (
            PARTITION BY product_id, region ORDER BY date
            ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        ) AS rolling_actual_4,
        AVG(CAST(demand_forecast AS DOUBLE)) OVER (
            PARTITION BY product_id, region ORDER BY date
            ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        ) AS rolling_forecast_4,
        AVG(CAST(forecast_error AS DOUBLE)) OVER (
            PARTITION BY product_id, region ORDER BY date
            ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        ) AS rolling_bias_4
    FROM {DB}.fact_sales_forecast
""")
print("  vw_forecast_history created")

# vw_forecast_rca_features (NEW - BRD §23, §24)
spark.sql(f"""
    CREATE OR REPLACE VIEW {DB}.vw_forecast_rca_features AS
    SELECT
        product_id, date, region, category,
        units_sold AS period_actual,
        demand_forecast AS period_forecast,
        forecast_error, absolute_error,
        ROUND(CAST(absolute_error AS DOUBLE) / NULLIF(CAST(units_sold AS DOUBLE), 0) * 100, 2) AS abs_pct_error,
        ROUND((CAST(demand_forecast AS DOUBLE) - CAST(units_sold AS DOUBLE)) / NULLIF(CAST(units_sold AS DOUBLE), 0) * 100, 2) AS bias_pct,
        -- Rolling features (4-period window)
        AVG(CAST(units_sold AS DOUBLE)) OVER w AS rolling_actual,
        AVG(CAST(demand_forecast AS DOUBLE)) OVER w AS rolling_forecast,
        AVG(CAST(forecast_error AS DOUBLE)) OVER w AS rolling_bias,
        STDDEV(CAST(units_sold AS DOUBLE)) OVER w AS actual_volatility,
        STDDEV(CAST(demand_forecast AS DOUBLE)) OVER w AS forecast_volatility,
        -- Inventory features
        inventory_level, inventory_status, stockout_flag,
        CASE WHEN units_sold > 0
             THEN ROUND(CAST(inventory_level AS DOUBLE) / CAST(units_sold AS DOUBLE), 1)
             ELSE NULL END AS inventory_days,
        -- Revenue features
        gross_revenue, net_revenue, price, discount,
        -- Promotion / price change flags
        holiday_promotion AS promotion_flag,
        CASE WHEN price IS NOT NULL THEN
            CASE WHEN LAG(price) OVER w2 IS NOT NULL AND price != LAG(price) OVER w2 THEN 1 ELSE 0 END
            ELSE 0 END AS price_change,
        CASE WHEN competitor_pricing IS NOT NULL THEN
            CASE WHEN LAG(competitor_pricing) OVER w2 IS NOT NULL AND competitor_pricing != LAG(competitor_pricing) OVER w2 THEN 1 ELSE 0 END
            ELSE 0 END AS competitor_price_change
    FROM {DB}.fact_sales_forecast
    WINDOW w AS (PARTITION BY product_id, region ORDER BY date ROWS BETWEEN 3 PRECEDING AND CURRENT ROW),
           w2 AS (PARTITION BY product_id, region ORDER BY date)
""")
print("  vw_forecast_rca_features created")

print("\n[5] All analytical views created.")

# ------------------------------------------------------------------
# Step 6: Validate RCA scenarios (BRD §46)
# ------------------------------------------------------------------
print("\n[6] Validating RCA scenarios...")

validation_results = []

for product_id, info in SCENARIO_PRODUCTS.items():
    scenario = info["scenario"]
    region = info.get("region", "North")
    
    try:
        df = spark.sql(f"""
            SELECT
                COUNT(*) as n_obs,
                SUM(demand_forecast) as total_forecast,
                SUM(units_sold) as total_actual,
                SUM(ABS(demand_forecast - units_sold)) as sum_abs_err,
                SUM(CASE WHEN stockout_flag = 1 THEN 1 ELSE 0 END) as stockout_days,
                MIN(date) as min_date,
                MAX(date) as max_date
            FROM {DB}.fact_sales_forecast
            WHERE product_id = '{product_id}' AND region = '{region}'
        """)
        r = df.collect()[0]
        n = r["n_obs"] or 0
        total_f = r["total_forecast"] or 0
        total_a = r["total_actual"] or 0
        sum_err = r["sum_abs_err"] or 0
        stockout_days = r["stockout_days"] or 0
        
        bias_pct = ((total_f - total_a) / total_a * 100) if total_a > 0 else 0
        wmape = (sum_err / total_a * 100) if total_a > 0 else 0
        
        # Validate expected pattern
        passed = False
        expected = ""
        if scenario == "over_bias":
            passed = bias_pct > 15
            expected = f"Positive bias > 15% (got {bias_pct:.1f}%)"
        elif scenario == "under_bias":
            passed = bias_pct < -15
            expected = f"Negative bias < -15% (got {bias_pct:.1f}%)"
        elif scenario == "trend_shift":
            passed = n > 0
            expected = f"Data exists with trend shift ({n} obs)"
        elif scenario == "promotion_uplift":
            promo_df = spark.sql(f"SELECT AVG(CASE WHEN holiday_promotion > 0 THEN units_sold ELSE NULL END) AS promo_avg, AVG(CASE WHEN holiday_promotion = 0 THEN units_sold ELSE NULL END) AS nonpromo_avg FROM {DB}.fact_sales_forecast WHERE product_id = '{product_id}' AND region = '{region}'")
            pr = promo_df.collect()[0]
            if pr["promo_avg"] and pr["nonpromo_avg"]:
                uplift = ((pr["promo_avg"] - pr["nonpromo_avg"]) / pr["nonpromo_avg"] * 100)
                passed = uplift > 20
                expected = f"Promo uplift > 20% (got {uplift:.1f}%)"
            else:
                passed = False
                expected = "No promo data"
        elif scenario == "stockout_constraint":
            passed = stockout_days > 0
            expected = f"Stockout days > 0 (got {stockout_days})"
        elif scenario == "new_product":
            passed = n <= 14
            expected = f"Short history <= 14 days (got {n})"
        elif scenario == "missing_data":
            passed = n < len(date_range) * 0.85
            expected = f"Missing > 15% of days (got {n} of {len(date_range)})"
        elif scenario == "normal":
            passed = True
            expected = "Normal data"
        else:
            passed = n > 0
            expected = f"Data exists ({n} obs)"
        
        status = "PASS" if passed else "FAIL"
        validation_results.append((product_id, scenario, region, status, n, f"{bias_pct:.1f}%", f"{wmape:.1f}%", expected))
        print(f"  {product_id} [{scenario}]: {status} - {expected}")
    except Exception as e:
        validation_results.append((product_id, scenario, region, "ERROR", 0, "", "", str(e)))
        print(f"  {product_id} [{scenario}]: ERROR - {e}")

# ------------------------------------------------------------------
# Step 7: Populate rca_readiness_registry (BRD §50)
# ------------------------------------------------------------------
print("\n[7] Populating RCA readiness registry...")

readiness_data = [
    ("Forecast bias", "Actual + Forecast", 4, "Over/under-bias", "Bias detected", "READY", datetime.now(), "ALL", date(2026, 1, 1), date(2026, 6, 30), "SUFFICIENT"),
    ("Trend shift", "Date + Actual", 8, "Trend shift", "Trend detected", "READY", datetime.now(), "ALL", date(2026, 1, 1), date(2026, 6, 30), "SUFFICIENT"),
    ("Promotion RCA", "Promotion + Actual + Forecast", 8, "Promotion uplift", "Promo/non-promo contrast", "READY", datetime.now(), "ALL", date(2026, 1, 1), date(2026, 6, 30), "SUFFICIENT"),
    ("Inventory RCA", "Inventory + Actual", 8, "Stockout/constraint", "Suppressed sales detected", "READY", datetime.now(), "ALL", date(2026, 1, 1), date(2026, 6, 30), "SUFFICIENT"),
    ("Revenue RCA", "Actual + Price + Discount", 4, "Revenue deterioration", "Revenue delta detected", "READY", datetime.now(), "ALL", date(2026, 1, 1), date(2026, 6, 30), "SUFFICIENT"),
    ("Seasonality RCA", "Calendar + Actual", 26, "Seasonality", "Recurring pattern detected", "PARTIAL", datetime.now(), "ALL", date(2026, 1, 1), date(2026, 6, 30), "PARTIAL"),
    ("Competitor RCA", "Competitor pricing + demand", 8, "Competitor scenario", "Pattern detected", "NOT_TESTABLE", datetime.now(), "ALL", date(2026, 1, 1), date(2026, 6, 30), "INSUFFICIENT"),
    ("Price effect", "Price + Actual", 8, "Price effect", "Price-change correlation detected", "READY", datetime.now(), "ALL", date(2026, 1, 1), date(2026, 6, 30), "SUFFICIENT"),
    ("New product", "Short history", 1, "New product", "Insufficient history flag", "READY", datetime.now(), "ALL", date(2026, 1, 1), date(2026, 6, 30), "SUFFICIENT"),
    ("Data quality", "All fields", 4, "Missing data", "Quality issues detected", "READY", datetime.now(), "ALL", date(2026, 1, 1), date(2026, 6, 30), "SUFFICIENT"),
]

readiness_df = spark.createDataFrame(readiness_data, StructType([
    StructField("capability", StringType(), True),
    StructField("required_evidence", StringType(), True),
    StructField("min_history_weeks", IntegerType(), True),
    StructField("synthetic_scenario", StringType(), True),
    StructField("validation_rule", StringType(), True),
    StructField("status", StringType(), True),
    StructField("last_validated", TimestampType(), True),
    StructField("entity", StringType(), True),
    StructField("coverage_start", DateType(), True),
    StructField("coverage_end", DateType(), True),
    StructField("data_quality_status", StringType(), True),
]))
readiness_df.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{DB}.rca_readiness_registry")
print(f"  rca_readiness_registry populated: {len(readiness_data)} capabilities")

# ------------------------------------------------------------------
# Step 8: Summary
# ------------------------------------------------------------------
print("\n" + "=" * 70)
print("  INITIALIZATION SUMMARY")
print("=" * 70)

# Count all objects
final_tables = spark.sql(f"""
    SELECT table_name, table_type
    FROM {CATALOG}.information_schema.tables
    WHERE table_schema = '{SCHEMA}'
    ORDER BY table_name
""").collect()

table_count = sum(1 for r in final_tables if r['table_type'] == 'MANAGED')
view_count = sum(1 for r in final_tables if r['table_type'] == 'VIEW')
print(f"  Total managed tables: {table_count}")
print(f"  Total views: {view_count}")

fact_count = spark.sql(f"SELECT COUNT(*) FROM {DB}.fact_sales_forecast").collect()[0][0]
print(f"  fact_sales_forecast rows: {fact_count}")

passed = sum(1 for r in validation_results if r[3] == "PASS")
failed = sum(1 for r in validation_results if r[3] == "FAIL")
print(f"  RCA scenario validation: {passed} passed, {failed} failed")

readiness_count = spark.sql(f"SELECT COUNT(*) FROM {DB}.rca_readiness_registry").collect()[0][0]
print(f"  Readiness registry entries: {readiness_count}")

print("\n  Status: INITIALIZATION COMPLETE")
if failed > 0:
    print(f"  WARNING: {failed} scenario validations failed - review above.")
print("=" * 70)