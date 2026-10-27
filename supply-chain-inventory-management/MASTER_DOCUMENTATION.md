# Supply Chain Inventory Management — Master Documentation

## Agentic AI Supply Chain Exception Management Platform
### Synthetic Data Generation Pipeline

---

## Table of Contents

1. [Overview](#1-overview)
2. [Architecture & Code Execution Flow](#2-architecture--code-execution-flow)
3. [Main Components](#3-main-components)
4. [Input and Output](#4-input-and-output)
5. [Data Model & Table Schemas](#5-data-model--table-schemas)
6. [Data Validation Rules](#6-data-validation-rules)
7. [Reproducibility](#7-reproducibility)
8. [How to Run](#8-how-to-run)
9. [Key Design Decisions](#9-key-design-decisions)
10. [Glossary](#10-glossary)

---

## 1. Overview

### Purpose

This project generates a **comprehensive, realistic, and internally consistent** synthetic supply-chain dataset stored as **Databricks Delta tables** in the `workspace.forecast_db` schema. The dataset is designed to support the **Agentic AI Supply Chain Exception Management Platform** described in the BRD (Business Requirements Document v1.0).

The data enables:
- **Demand forecasting** analysis with forecast accuracy and bias metrics
- **Inventory health** monitoring across multiple warehouses
- **Exception detection** and root-cause investigation workflows
- **Scenario testing** for supply-chain disruptions (supplier delays, stockouts, demand spikes)
- **Agent observability** tracking (tool calls, decisions, approvals, actions)

### What Makes This Production-Grade

| Feature | Implementation |
| --- | --- |
| **Reproducibility** | Fixed random seed (SEED=42) — re-running produces identical data |
| **Referential Integrity** | All foreign keys validated post-load |
| **Business Rule Compliance** | PO received ≤ ordered, inventory ≥ 0, etc. |
| **Modular Architecture** | Two-part pipeline: master/transactional data, then events/views/validation |
| **Backward Compatibility** | Bridge table (`fact_sales_forecast`) preserves existing forecast-agent compatibility |
| **Observability Schema** | Pre-created empty tables for agent-run tracking |
| **Explicit Spark Schemas** | Every DataFrame uses a declared `StructType` — no schema inference errors |

---

## 2. Architecture & Code Execution Flow

### High-Level Pipeline

```
Configuration (SEED=42, volumes, dates)
        |
        v
+--------------------------------------------------+
|  SCRIPT 1: 01_generate_supply_chain_data.py       |
|                                                  |
|  Section 6:  Master Data                          |
|    6.1  suppliers     (20 rows)                   |
|    6.2  skus           (100 rows)                 |
|    6.3  warehouses     (5 rows)                   |
|                                                  |
|  Section 7:  Transactional Data                   |
|    7.1  inventory       (500 rows)                |
|    7.2  demand_forecast  (9,000 rows)             |
|    7.3  purchase_orders  (500 rows)               |
|         purchase_order_lines (1,458 rows)         |
|    7.4  customer_orders  (2,000 rows)             |
|    7.5  shipments       (300 rows)                |
+--------------------------------------------------+
        |
        v
+--------------------------------------------------+
|  SCRIPT 2: 02_generate_events_observability_views |
|                                                  |
|  Section 8:  Event & Exception Data               |
|    8.1  supplier_events     (30 rows)            |
|    8.2  supply_chain_exceptions (10 rows)         |
|    8.3  inventory_movements (500 rows)            |
|                                                  |
|  Section 9:  Observability Tables (empty schemas) |
|    9.1  agent_runs                                |
|    9.2  agent_tool_calls                          |
|    9.3  agent_decisions                           |
|    9.4  human_approvals                           |
|    9.5  action_execution                          |
|                                                  |
|  Section 10: Bridge Table                         |
|    fact_sales_forecast (9,000 rows)               |
|                                                  |
|  Section 11: Analytical Views                     |
|    vw_forecast_metrics                            |
|    vw_inventory_health                            |
|                                                  |
|  Section 12: Data Validation                      |
|    (6 integrity & business-rule checks)           |
|                                                  |
|  Section 13: Summary Statistics                   |
|    (row counts for all 22 tables/views)           |
+--------------------------------------------------+
```

### Execution Order (Critical)

**Script 1 MUST run before Script 2.** Script 2 loads tables created by Script 1 to generate events, build the bridge table, and validate referential integrity.

---

## 3. Main Components

### 3.1 Configuration Block (Section 2)

All configuration is centralized at the top of each script:

| Parameter | Value | Purpose |
| --- | --- | --- |
| `CATALOG` | `"workspace"` | Unity Catalog catalog name |
| `SCHEMA` | `"forecast_db"` | Schema within the catalog |
| `SEED` | `42` | Fixed random seed for reproducibility |
| `NUM_SUPPLIERS` | `20` | Minimum per BRD §42.3 |
| `NUM_SKUS` | `100` | Minimum per BRD §42.3 |
| `NUM_WAREHOUSES` | `5` | Minimum per BRD §42.3 |
| `NUM_PURCHASE_ORDERS` | `500` | Minimum per BRD §42.4 |
| `NUM_CUSTOMER_ORDERS` | `2000` | Minimum per BRD §42.4 |
| `FORECAST_DAYS` | `90` | Minimum per BRD §42.4 |

### 3.2 Master Data Generators (Section 6)

#### 6.1 Suppliers (`generate_suppliers`)
- **Input**: Configuration constants (NUM_SUPPLIERS, reference lists)
- **Output**: List of 20 supplier dictionaries with 11 fields each
- **Key Logic**: Supplier names are built from prefix+suffix pairs (e.g. "Global Materials"). Reliability scores range 0.60–0.99. Lead times vary 5–45 days. 75% are approved suppliers.
- **Persists to**: `workspace.forecast_db.suppliers`

#### 6.2 SKUs (`generate_skus`)
- **Input**: Configuration constants, CATEGORIES list
- **Output**: List of 100 SKU dictionaries with 8 persisted fields (plus 2 private fields for downstream use)
- **Key Logic**: Each SKU is assigned a demand profile (Stable, Seasonal, Trending, Intermittent, New Launch, Declining) and a criticality level (High/Medium/Low) that determines base daily demand. Private fields (`_base_daily_demand`, `_demand_profile`) are used by the demand-forecast generator but not persisted to the table.
- **Persists to**: `workspace.forecast_db.skus`

#### 6.3 Warehouses (`generate_warehouses`)
- **Input**: Hardcoded warehouse definitions (5 warehouses with fixed names and locations)
- **Output**: List of 5 warehouse dictionaries with 6 fields each
- **Key Logic**: Warehouses are spread across all 5 regions (North, South, East, West, Central) with realistic city locations. Capacity ranges 50,000–200,000 units.
- **Persists to**: `workspace.forecast_db.warehouses`

### 3.3 Transactional Data Generators (Section 7)

#### 7.1 Inventory (`generate_inventory`)
- **Input**: SKU IDs, warehouse IDs, safety stock from SKU master
- **Output**: 500 rows (100 SKUs × 5 warehouses), 7 columns
- **Key Logic**: `on_hand` ranges 0–5,000. `allocated` is always ≤ `on_hand`. `available = on_hand - allocated` (always ≥ 0). `in_transit` ranges 0–2,000. `safety_stock` comes from the SKU master data.

#### 7.2 Demand Forecast (`generate_demand_forecast`)
- **Input**: SKU IDs, demand profiles, base daily demand, FORECAST_START date
- **Output**: 9,000 rows (100 SKUs × 90 days), 5 columns
- **Key Logic**: Each SKU's demand curve is shaped by its demand profile:
  - **Stable**: Flat baseline with ±10% noise
  - **Seasonal**: Weekly sine wave (peak mid-week) with ±15% noise
  - **Trending**: Linear upward trend over 90 days
  - **Intermittent**: ~20% of days have demand; rest are zero
  - **New Launch**: Ramps up from 0 to base over first 30 days
  - **Declining**: Linear downward trend to 40% of baseline
  
  Demand spikes (2.5–4× normal) are injected on ~3% of days to simulate real-world disruptions.
  
  The forecast is generated as `actual × (1 + bias_noise)` where bias noise has mean +5% (systematic over-forecasting) — this ensures forecast accuracy and bias metrics are meaningful and non-trivial.

#### 7.3 Purchase Orders & PO Lines (`generate_purchase_orders_and_lines`)
- **Input**: Supplier IDs, supplier lead times, SKU IDs, SKU costs
- **Output**: 500 PO rows (6 columns) + 1,458 PO line rows (7 columns)
- **Key Logic**: PO status determines received quantity:
  - **Delivered**: received = ordered
  - **Partially Delivered**: received = 50–90% of ordered
  - **Delayed**: received = 0–30% of ordered
  - **Open/Cancelled**: received = 0
  
  Each PO has 1–5 line items, each referencing a SKU. Expected delivery = order date + supplier lead time.

#### 7.4 Customer Orders (`generate_customer_orders`)
- **Input**: SKU IDs, date range
- **Output**: 2,000 rows, 8 columns
- **Key Logic**: 50 distinct customers. Priority distribution: 5% Critical, 25% High, 50% Medium, 20% Low. Status: 15% Open, 25% Confirmed, 25% Shipped, 30% Delivered, 5% Cancelled.

#### 7.5 Shipments (`generate_shipments`)
- **Input**: PO rows, supplier countries, warehouse IDs
- **Output**: 300 rows, 9 columns
- **Key Logic**: Each shipment links to a PO. Origin = supplier's country. Destination = a random warehouse. Status determines actual arrival date: Delivered = on-time, Delayed = 2–8 days late, Planned/In-Transit = null actual arrival.

### 3.4 Event & Exception Generators (Section 8)

#### 8.1 Supplier Events (`generate_supplier_events`)
- **Output**: 30 rows, 7 columns
- **Purpose**: Simulates ERP/WMS/TMS events (delivery delays, capacity constraints, quality issues, force majeure, price changes) that would trigger the exception-detection agent.

#### 8.2 Supply Chain Exceptions (`generate_exceptions`)
- **Output**: 10 rows, 8 columns
- **Purpose**: Pre-seeded exceptions matching the 10 mandatory BRD test scenarios (§42.6): supplier delay, inventory shortage, demand spike, shipment delay, warehouse imbalance, alternate supplier, simultaneous exceptions, no resolution, autonomous action, human approval required.

#### 8.3 Inventory Movements (`generate_inventory_movements`)
- **Output**: 500 rows, 7 columns
- **Purpose**: Audit trail of inventory flowing in/out/transfer between warehouses. Each movement references the originating PO or customer order.

### 3.5 Observability Tables (Section 9)

Five empty tables with pre-defined schemas for the agent orchestration layer:

| Table | Purpose | Key Columns |
| --- | --- | --- |
| `agent_runs` | One row per agent execution | run_id, exception_id, agent_name, started_at, completed_at, status, latency_ms, model_name |
| `agent_tool_calls` | One row per tool invocation | tool_call_id, run_id, tool_name, input, output_reference, status, latency_ms |
| `agent_decisions` | One row per agent decision | decision_id, exception_id, decision_type, recommendation, confidence, evidence_references, policy_result |
| `human_approvals` | One row per approval request | approval_id, exception_id, approver, decision, comments |
| `action_execution` | One row per executed action | action_id, action_type, requested_at, executed_at, status, result_reference |

### 3.6 Bridge Table (Section 10)

#### `fact_sales_forecast`
- **Input**: `demand_forecast` table + `inventory` table (both from Part 1)
- **Output**: 9,000 rows, 15 columns
- **Purpose**: Bridges the new supply-chain data model with the existing forecast-agent's service layer. The existing agent (`supply_chain_service.py`) queries `vw_forecast_metrics` and `vw_inventory_health`, which are built on this table.
- **Key Logic**: Joins demand_forecast with max(inventory.on_hand) per SKU. Adds enrichment columns (price, discount, weather_condition, holiday_promotion, competitor_pricing, seasonality) using Spark's seeded `rand()` for determinism.

### 3.7 Analytical Views (Section 11)

#### `vw_forecast_metrics`
- **Input**: `fact_sales_forecast`
- **Output**: All columns from fact_sales_forecast + two computed columns:
  - `forecast_accuracy = (1 - |units_sold - demand_forecast| / units_sold) × 100`
  - `forecast_bias = ((demand_forecast - units_sold) / units_sold) × 100`
- **Interpretation**: 100% accuracy = perfect prediction. Positive bias = over-forecasting.

#### `vw_inventory_health`
- **Input**: `fact_sales_forecast`
- **Output**: All columns + `inventory_status`:
  - `'Stockout Risk'` when `inventory_level < units_sold`
  - `'Low Inventory'` when `inventory_level < 1.5 × units_sold`
  - `'Healthy'` otherwise

### 3.8 Data Validation (Section 12)

Six validation checks are run after all data is loaded:

| # | Check | Rule | Result |
| --- | --- | --- | --- |
| 12.1 | Referential integrity | PO.supplier_id must exist in suppliers | PASS |
| 12.2 | Referential integrity | PO Line.sku_id must exist in skus | PASS |
| 12.3 | Referential integrity | Customer Order.sku_id must exist in skus | PASS |
| 12.4 | Business rule | PO Line.received_quantity ≤ ordered_quantity | PASS |
| 12.5 | Business rule | Inventory.available ≥ 0 | PASS |
| 12.6 | Non-negativity | All inventory quantities ≥ 0 | PASS |

---

## 4. Input and Output

### Input

| Input | Source | Description |
| --- | --- | --- |
| Configuration constants | Hardcoded in script | Data volumes, dates, catalog/schema names |
| Random seed | `SEED = 42` | Ensures reproducibility |
| BRD requirements | Business Requirements Document | Defines minimum data volumes and table schemas |
| `.env` file | `forecast-agent/.env` | Azure OpenAI credentials (NOT used during data generation — only needed for agent execution later) |

### Output

All output is persisted as **Delta tables** in `workspace.forecast_db`:

| Table/View | Rows | Type |
| --- | --- | --- |
| `suppliers` | 20 | Delta table (master data) |
| `skus` | 100 | Delta table (master data) |
| `warehouses` | 5 | Delta table (master data) |
| `inventory` | 500 | Delta table (transactional) |
| `demand_forecast` | 9,000 | Delta table (transactional) |
| `purchase_orders` | 500 | Delta table (transactional) |
| `purchase_order_lines` | 1,458 | Delta table (transactional) |
| `customer_orders` | 2,000 | Delta table (transactional) |
| `shipments` | 300 | Delta table (transactional) |
| `supplier_events` | 30 | Delta table (events) |
| `supply_chain_exceptions` | 10 | Delta table (events) |
| `inventory_movements` | 500 | Delta table (events) |
| `agent_runs` | 0 | Delta table (observability — empty schema) |
| `agent_tool_calls` | 0 | Delta table (observability — empty schema) |
| `agent_decisions` | 0 | Delta table (observability — empty schema) |
| `human_approvals` | 0 | Delta table (observability — empty schema) |
| `action_execution` | 0 | Delta table (observability — empty schema) |
| `fact_sales_forecast` | 9,000 | Delta table (bridge) |
| `vw_forecast_metrics` | 9,000 | View (analytical) |
| `vw_inventory_health` | 9,000 | View (analytical) |

**Total: 18 Delta tables + 2 views = 20 objects**

---

## 5. Data Model & Table Schemas

### Entity Relationship Overview

```
suppliers  1----*  purchase_orders  1----*  purchase_order_lines  *----1  skus
                                                                        |
                                                                  *-----1 |
                                                                        1
inventory  *----1  warehouses                                      customer_orders
                                                                        |
shipments  *----1  purchase_orders                                *----1
                                                                        |
supplier_events  *----1  suppliers                              (50 customers)
supply_chain_exceptions  *----1  supplier_events
inventory_movements  *----1  warehouses, skus
```

### Detailed Schemas

#### `suppliers`
| Column | Type | Nullable | Description |
| --- | --- | --- | --- |
| supplier_id | STRING | No | Primary key (S001–S020) |
| supplier_name | STRING | Yes | E.g. "Global Materials" |
| country | STRING | Yes | Country of origin |
| region | STRING | Yes | North/South/East/West/Central |
| status | STRING | Yes | Active/Inactive/Under Review |
| supplier_type | STRING | Yes | Raw Material/Component/Finished Goods |
| lead_time_days | INT | Yes | 5–45 days |
| reliability_score | DOUBLE | Yes | 0.60–0.99 |
| approved_supplier | BOOLEAN | Yes | True = can be used for alternate sourcing |
| capacity_units | INT | Yes | 5,000–50,000 |
| unit_cost | DOUBLE | Yes | $0.50–$25.00 |

#### `skus`
| Column | Type | Nullable | Description |
| --- | --- | --- | --- |
| sku_id | STRING | No | Primary key (SKU-001–SKU-100) |
| sku_name | STRING | Yes | E.g. "BEV-001 Product" |
| category | STRING | Yes | Beverages/Snacks/Dairy/Personal Care/Home Care |
| unit_cost | DOUBLE | Yes | $0.50–$50.00 |
| standard_lead_time_days | INT | Yes | 3–30 days |
| safety_stock | INT | Yes | 100–1,000 units |
| minimum_order_quantity | INT | Yes | 50/100/200/500 |
| criticality | STRING | Yes | High/Medium/Low |

#### `warehouses`
| Column | Type | Nullable | Description |
| --- | --- | --- | --- |
| warehouse_id | STRING | No | Primary key (WH01–WH05) |
| warehouse_name | STRING | Yes | E.g. "Northgate Distribution Center" |
| location | STRING | Yes | City, State |
| region | STRING | Yes | North/South/East/West/Central |
| capacity | INT | Yes | 50,000–200,000 units |
| warehouse_type | STRING | Yes | Distribution/Manufacturing/Cross-Dock |

#### `inventory`
| Column | Type | Nullable | Description |
| --- | --- | --- | --- |
| warehouse_id | STRING | No | FK → warehouses |
| sku_id | STRING | No | FK → skus |
| on_hand | INT | Yes | Physical units in warehouse |
| allocated | INT | Yes | Units reserved for orders |
| available | INT | Yes | on_hand − allocated (always ≥ 0) |
| in_transit | INT | Yes | Units en route from supplier |
| safety_stock | INT | Yes | From SKU master data |

#### `demand_forecast`
| Column | Type | Nullable | Description |
| --- | --- | --- | --- |
| date | DATE | No | Forecast date (Oct 1 – Dec 29, 2024) |
| sku_id | STRING | No | FK → skus |
| forecast_quantity | INT | Yes | Model-predicted demand |
| actual_quantity | INT | Yes | Actual (ground-truth) demand |
| demand_profile | STRING | Yes | Stable/Seasonal/Trending/Intermittent/New Launch/Declining |

#### `purchase_orders`
| Column | Type | Nullable | Description |
| --- | --- | --- | --- |
| po_id | STRING | No | Primary key (PO-00001–PO-00500) |
| supplier_id | STRING | Yes | FK → suppliers |
| status | STRING | Yes | Open/Delivered/Partially Delivered/Delayed/Cancelled |
| order_date | DATE | Yes | When the PO was placed |
| expected_delivery | DATE | Yes | order_date + supplier lead_time_days |
| actual_delivery | DATE | Yes | Null if not yet delivered |

#### `purchase_order_lines`
| Column | Type | Nullable | Description |
| --- | --- | --- | --- |
| po_id | STRING | No | FK → purchase_orders |
| line_id | INT | No | Line number within PO (1–5) |
| sku_id | STRING | Yes | FK → skus |
| ordered_quantity | INT | Yes | Units ordered |
| received_quantity | INT | Yes | Units received (always ≤ ordered_quantity) |
| expected_delivery | DATE | Yes | From PO header |
| unit_cost | DOUBLE | Yes | From SKU master |

#### `customer_orders`
| Column | Type | Nullable | Description |
| --- | --- | --- | --- |
| order_id | STRING | No | Primary key (CO-00001–CO-02000) |
| customer_id | STRING | Yes | C001–C050 |
| sku_id | STRING | Yes | FK → skus |
| quantity | INT | Yes | Units ordered (10–1,000) |
| order_date | DATE | Yes | When the order was placed |
| requested_delivery_date | DATE | Yes | Customer's required delivery date |
| priority | STRING | Yes | Critical/High/Medium/Low |
| status | STRING | Yes | Open/Confirmed/Shipped/Delivered/Cancelled |

#### `shipments`
| Column | Type | Nullable | Description |
| --- | --- | --- | --- |
| shipment_id | STRING | No | Primary key (SHP-0001–SHP-0300) |
| po_id | STRING | Yes | FK → purchase_orders |
| origin | STRING | Yes | Supplier country |
| destination_warehouse | STRING | Yes | FK → warehouses |
| status | STRING | Yes | Planned/In-Transit/Delivered/Delayed |
| ship_date | DATE | Yes | When the shipment departed |
| expected_arrival | DATE | Yes | ship_date + transit time |
| actual_arrival | DATE | Yes | Null if not yet arrived |
| carrier | STRING | Yes | FedEx/UPS/DHL/Maersk/DB Schenker |

#### `supplier_events`
| Column | Type | Nullable | Description |
| --- | --- | --- | --- |
| event_id | STRING | No | Primary key (EVT-0001–EVT-0030) |
| supplier_id | STRING | Yes | FK → suppliers |
| po_id | STRING | Yes | FK → purchase_orders |
| event_type | STRING | Yes | DELIVERY_DELAY/CAPACITY_CONSTRAINT/QUALITY_ISSUE/FORCE_MAJEURE/PRICE_CHANGE |
| event_date | DATE | Yes | When the event was reported |
| description | STRING | Yes | Human-readable event description |
| severity | STRING | Yes | HIGH/MEDIUM/LOW |

#### `supply_chain_exceptions`
| Column | Type | Nullable | Description |
| --- | --- | --- | --- |
| exception_id | STRING | No | Primary key (EXC-001–EXC-010) |
| exception_type | STRING | Yes | SUPPLIER_DELAY/INVENTORY_SHORTAGE/STOCKOUT_RISK/SHIPMENT_DELAY/DEMAND_SPIKE/WAREHOUSE_IMBALANCE |
| severity | STRING | Yes | HIGH/MEDIUM/LOW |
| status | STRING | Yes | DETECTED/CLASSIFIED/INVESTIGATING/RESOLVED/AWAITING_APPROVAL |
| source_event_id | STRING | Yes | FK → supplier_events |
| description | STRING | Yes | Human-readable exception description |
| created_at | DATE | Yes | When the exception was created |
| updated_at | DATE | Yes | Last update timestamp |

#### `inventory_movements`
| Column | Type | Nullable | Description |
| --- | --- | --- | --- |
| movement_id | STRING | No | Primary key (MOV-00001–MOV-00500) |
| warehouse_id | STRING | Yes | FK → warehouses |
| sku_id | STRING | Yes | FK → skus |
| movement_type | STRING | Yes | Inbound/Outbound/Transfer |
| quantity | INT | Yes | Units moved (50–2,000) |
| movement_date | DATE | Yes | When the movement occurred |
| reference | STRING | Yes | PO-ID (inbound) or CO-ID (outbound) |

#### `fact_sales_forecast` (Bridge Table)
| Column | Type | Description |
| --- | --- | --- |
| date | DATE | Forecast date |
| store_id | STRING | Always "STORE01" (representative) |
| product_id | STRING | SKU ID |
| demand_profile | STRING | Demand profile from SKU |
| inventory_level | INT | Max on_hand across warehouses |
| units_sold | INT | Actual demand |
| units_ordered | INT | Forecast quantity |
| demand_forecast | INT | Same as units_ordered |
| price | DOUBLE | Seeded random $5–$55 |
| discount | DOUBLE | Seeded random $0–$20 |
| weather_condition | STRING | Sunny/Rainy/Cloudy/Snowy/Stormy |
| holiday_promotion | INT | 1 (15% chance) or 0 |
| competitor_pricing | DOUBLE | Seeded random $5–$55 |
| seasonality | STRING | Regular/Peak/Off-Season |
| region | STRING | Derived from warehouse region |

#### Observability Tables (all empty, schema only)

See [Section 3.5](#35-observability-tables-section-9) above for column details.

---

## 6. Data Validation Rules

The validation framework (Section 12) enforces BRD §42.10 requirements:

| Rule | BRD Reference | Implementation |
| --- | --- | --- |
| Customer order quantities must not be negative | §42.10 | Random generation uses `randint(10, 1000)` |
| Inventory quantities must not be negative | §42.10 | `on_hand`, `allocated`, `in_transit`, `safety_stock` all ≥ 0; validated post-load |
| PO quantities must be ≥ received quantities | §42.10 | `received_quantity` is always ≤ `ordered_quantity` by construction; validated post-load |
| Customer orders must reference valid SKUs | §42.10 | `sku_id` chosen from `sku_ids` list; left-anti join validates |
| Inventory must reference valid warehouses and SKUs | §42.10 | `warehouse_id` and `sku_id` from master data lists |
| Supplier references must exist | §42.10 | `supplier_id` chosen from `supplier_ids` list; left-anti join validates |
| Dates must be logically consistent | §42.10 | `order_date < expected_delivery`, `ship_date < expected_arrival` |

---

## 7. Reproducibility

All randomness in the pipeline is controlled by a single seed:

```python
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
```

**What this means:**
- Re-running both scripts produces **byte-for-byte identical** data
- Scenario tests are reproducible across environments
- The Spark `rand()` calls in the bridge table use `seed=SEED`, `seed=SEED+1`, etc. for deterministic enrichment columns
- Changing `SEED` to any other integer produces a different but equally valid dataset

---

## 8. How to Run

### Prerequisites
- Databricks workspace with Unity Catalog enabled
- `workspace` catalog and permission to create schemas/tables
- Serverless compute or any all-purpose cluster

### Execution Steps

```bash
# Step 1: Generate master + transactional data
python 01_generate_supply_chain_data.py

# Step 2: Generate events, observability, views, and validate
python 02_generate_events_observability_views.py
```

Or in a Databricks notebook:
```python
%run "./01_generate_supply_chain_data"
%run "./02_generate_events_observability_views"
```

### No API Calls
The data generation pipeline makes **zero external API calls**. All data is generated in-memory by Python and persisted via Spark Delta writes. The `.env` file (Azure OpenAI credentials) is only needed for the agent execution layer, not for data generation.

---

## 9. Key Design Decisions

### Why Two Scripts Instead of One?
The pipeline is split into two scripts for **modularity and re-executability**:
- Script 1 generates the foundation (master + transactional data). This is the expensive part — 9,000+ demand forecast rows.
- Script 2 generates lightweight event data, observability schemas, and the bridge table. It can be re-run independently if views or validation logic changes without regenerating all transactional data.

### Why a Bridge Table (`fact_sales_forecast`)?
The existing forecast-agent's service layer (`supply_chain_service.py`) queries `vw_forecast_metrics` and `vw_inventory_health`, which expect specific column names (`units_sold`, `demand_forecast`, `inventory_level`, etc.). The bridge table maps the new supply-chain data model to this expected schema, ensuring **backward compatibility** without modifying the agent code.

### Why Demand Profiles?
Each SKU is assigned a demand profile (Stable, Seasonal, Trending, etc.) that shapes its 90-day demand curve. This creates a **realistic and diverse** dataset where different products exhibit different forecasting challenges — critical for testing agent intelligence across scenarios.

### Why Inject Demand Spikes?
~3% of forecast days have demand spikes (2.5–4× normal). These simulate real-world disruptions (promotions, weather events, viral demand) and provide the raw material for the DEMAND_SPIKE exception scenario (BRD §42.6 Scenario 3).

### Why Empty Observability Tables?
The agent orchestration layer (not part of this data-generation pipeline) will populate these tables at runtime. Pre-creating the schemas ensures the agent code can simply `INSERT INTO` without needing DDL, and enables immediate querying of the (empty) tables for testing.

---

## 10. Glossary

| Term | Definition |
| --- | --- |
| **BRD** | Business Requirements Document — the source-of-truth specification for this platform |
| **Delta table** | Databricks' ACID-compliant storage format with time travel support |
| **Unity Catalog** | Databricks' unified governance layer for data assets |
| **Schema** | A namespace within a Unity Catalog catalog (equivalent to a database) |
| **SKU** | Stock Keeping Unit — a unique product identifier |
| **PO** | Purchase Order — an order placed with a supplier |
| **FK** | Foreign Key — a column referencing another table's primary key |
| **Demand Profile** | The time-series pattern of a SKU's demand (stable, seasonal, etc.) |
| **Forecast Accuracy** | (1 − |actual − forecast| / actual) × 100; 100% = perfect prediction |
| **Forecast Bias** | ((forecast − actual) / actual) × 100; positive = over-forecasting |
| **Safety Stock** | Minimum inventory level to avoid stockouts |
| **Bridge Table** | A table that maps one data model's schema to another's for compatibility |
| **Observability** | The ability to track and analyze agent execution behavior |

---

---

## 11. Agent Platform Architecture

### 11.1 Overview

The Agentic AI Supply Chain Exception Management Platform is built on top of the data generation pipeline (Sections 1-10 above). It implements the BRD vision of an autonomous exception management system that moves from Event-to-Alert to Event-to-Understand-to-Investigate-to-Assess-Impact-to-Generate-Options-to-Evaluate-to-Recommend-to-Verify-to-Learn.

The platform consists of 12 source files organised into a clean, layered architecture:

```
supply-chain-inventory-management/
|-- config.py              <-- Environment configuration (.env loader)
|-- client.py              <-- Azure OpenAI client singleton
|-- models.py              <-- Pydantic typed models (request + response schemas)
|-- prompts.py             <-- System prompt for the exception management agent
|-- tool_registry.py       <-- Tool definitions exposed to the LLM
|-- tool_executor.py       <-- Routes LLM tool calls to Python functions
|-- policy_engine.py       <-- Deterministic business rules (external to LLM)
|-- app.py                 <-- Entry point with demo scenarios
|-- requirements.txt       <-- Python dependencies
|-- agents/
|   |-- __init__.py
|   +-- exception_agent.py <-- Main agent orchestration loop (LLM + tools)
|-- services/
|   |-- __init__.py
|   +-- exception_service.py <-- Data access layer (Spark to Databricks tables)
|-- tools/
|   |-- __init__.py
|   +-- exception_tools.py   <-- Tool functions wrapping service calls
+-- notebooks/
    |-- 01_generate_supply_chain_data.py  <-- (existing) Data generation Part 1
    +-- 02_generate_events_observability_views.py <-- (existing) Part 2
```

### 11.2 Agent Platform Execution Flow

```
User Query (natural language)
    |
    v
app.py  -->  ExceptionAgent.run(query)
                |
                +-->  Build conversation: [system_prompt, user_query]
                |
                +-->  LOOP (max 10 API calls):
                |       |
                |       +-->  client.responses.create(model, input, tools)
                |       |       (Azure OpenAI - 1 API call per iteration)
                |       |
                |       +-->  Extract function_call items from response
                |       |
                |       +-->  If NO tool calls: return response.output_text
                |       |       (final answer - loop exits)
                |       |
                |       +-->  For each tool call:
                |       |       |
                |       |       +-->  ToolExecutor.execute(name, arguments)
                |       |       |       |   (validates args with Pydantic)
                |       |       |       |
                |       |       |       +-->  tools/exception_tools.py
                |       |       |       |       |
                |       |       |       |       +--> services/exception_service.py
                |       |       |       |       |       |
                |       |       |       |       |       +--> Spark SQL on
                |       |       |       |       |       |   workspace.forecast_db.*
                |       |       |       |       |       |
                |       |       |       |       +-->  Returns dict/list
                |       |       |       |
                |       |       +-->  Append tool_call + output to conversation
                |       |
                |       +-->  Continue LOOP (LLM sees tool results)
                |
                +-->  Return final structured response
```

### 11.3 Main Components

#### config.py - Configuration Loader
- **Input**: .env file from ../forecast-agent/.env
- **Output**: Module-level constants (AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT, DATABRICKS_CATALOG, DATABRICKS_SCHEMA, MAX_API_CALLS)
- **Purpose**: Centralises all environment-specific configuration. No credentials are ever hard-coded (BRD section 38, 42.2).

#### client.py - OpenAI Client
- **Input**: config.AZURE_OPENAI_ENDPOINT, config.AZURE_OPENAI_API_KEY
- **Output**: client - an openai.OpenAI instance configured for Azure
- **Purpose**: Single shared LLM client used by all agent calls.

#### models.py - Typed Data Models
- **Input**: N/A (definitions only)
- **Output**: 20+ Pydantic models organised into:
  - Request models (tool input schemas): InventoryRequest, PurchaseOrderRequest, CustomerOrderRequest, SupplierRequest, AlternateSupplierRequest, DemandForecastRequest, ShipmentRequest, WarehouseInventoryRequest, ExceptionRequest, ExceptionListRequest, SupplierEventRequest
  - Response models (tool output schemas): InventoryInfo, SupplierInfo, PurchaseOrderInfo, CustomerOrderInfo, ShipmentInfo, DemandForecastInfo, ExceptionInfo, SupplierEventInfo
  - Business models: ImpactAnalysis, ResolutionOption, PolicyResult, AgentResponse
- **Purpose**: End-to-end type safety from LLM JSON tool-call arguments to Spark query results (BRD section 21, 24).

#### prompts.py - System Prompt
- **Input**: N/A (definition only)
- **Output**: EXCEPTION_AGENT_INSTRUCTIONS - comprehensive system prompt
- **Purpose**: Defines the agent role, capabilities, investigation workflow, tool-usage rules, output format, and guardrails (BRD section 24, 26, 27).

#### tool_registry.py - Tool Definitions
- **Input**: Pydantic models from models.py
- **Output**: TOOLS - a JSON array of 11 tool definitions passed to the LLM
- **Purpose**: Tells the LLM what tools are available, when to use them, and what parameters they accept. The JSON schema is auto-generated from Pydantic models.

#### tool_executor.py - Tool Execution Router
- **Input**: Tool name (str) + arguments (dict) from the LLM
- **Output**: Tool result (dict or list)
- **Purpose**: Validates arguments against Pydantic models, then routes to the correct function. Prevents arbitrary function execution (security guardrail).

#### policy_engine.py - Business Rules Engine
- **Input**: ResolutionOption from the LLM + context flags
- **Output**: PolicyResult with autonomous_execution_allowed, human_approval_required, policy_violations
- **Purpose**: Enforces business rules DETERMINISTICALLY - the LLM cannot override these (BRD section 15, 16). Policies include:
  - Financial: actions over $1,000 require human approval
  - Strategic customer: any action affecting strategic customers requires approval
  - Supplier change: changing suppliers requires procurement approval
  - Stockout risk: high stockout risk requires human review

#### services/exception_service.py - Data Access Layer
- **Input**: Typed parameters (sku_id, supplier_id, etc.)
- **Output**: Python dicts/lists matching Pydantic models
- **Purpose**: The SINGLE point of contact between the agent and Databricks. Encapsulates all Spark SQL queries so agents never construct ad-hoc SQL (BRD section 42.16). Provides 11 methods:
  1. get_inventory(sku_id, warehouse_id)
  2. get_open_purchase_orders(sku_id)
  3. get_customer_orders(sku_id)
  4. get_supplier(supplier_id)
  5. get_alternate_suppliers(sku_id)
  6. get_demand_forecast(sku_id)
  7. get_shipments(sku_id)
  8. get_warehouse_inventory(sku_id)
  9. get_exception(exception_id)
  10. list_exceptions(status)
  11. get_supplier_events(supplier_id)

#### tools/exception_tools.py - Tool Functions
- **Input**: Pydantic request models
- **Output**: Dict/list from service layer
- **Purpose**: Thin wrappers that the tool executor calls. No business logic, no LLM calls, no Spark queries - pure pass-through (separation of concerns).

#### agents/exception_agent.py - Agent Orchestrator
- **Input**: User query (str)
- **Output**: Agent response (str)
- **Purpose**: Implements the main agentic loop - calls Azure OpenAI, extracts tool calls, executes them, feeds results back, and enforces the MAX_API_CALLS=10 budget. Provides verbose tracing for observability (BRD section 28).

#### app.py - Entry Point
- **Input**: User selection (demo scenario 1-3 or custom query)
- **Output**: Structured agent response printed to console/notebook
- **Purpose**: Demonstrates the end-to-end workflow with 3 pre-built demo scenarios. Handles both interactive (terminal) and non-interactive (notebook) modes.

### 11.4 Agent Platform Input and Output

#### Input

| Input | Source | Description |
| --- | --- | --- |
| User query | User (planner/manager) | Natural language exception description or investigation request |
| .env file | ../forecast-agent/.env | Azure OpenAI credentials (endpoint, API key, deployment name) |
| Databricks tables | workspace.forecast_db.* | 18 Delta tables + 2 views generated by the data pipeline |
| System prompt | prompts.py | Agent role, capabilities, rules, output format |
| Business policies | policy_engine.py | Configurable cost threshold, approval rules |

#### Output

| Output | Format | Description |
| --- | --- | --- |
| Agent response | Text (str) | Structured analysis: what happened, why it matters, investigation, options, recommendation, approval requirement |
| Tool traces | Console logs | Each API call and tool execution is logged for observability |
| Policy results | PolicyResult objects | Deterministic evaluation of each resolution option |

### 11.5 Demo Scenarios (BRD section 42.6)

| # | Scenario | Exception Type | Description |
| --- | --- | --- | --- |
| 1 | Supplier Delay + Stockout Risk | SUPPLIER_DELAY | Supplier S001 reports delayed delivery; agent investigates impact on SKU-001 |
| 2 | Inventory Shortage | INVENTORY_SHORTAGE | Agent checks SKU-050 inventory vs demand, finds shortage, proposes replenishment |
| 3 | Warehouse Imbalance | WAREHOUSE_IMBALANCE | Agent detects uneven distribution of SKU-025 across warehouses, proposes transfer |

Each scenario uses 1-3 LLM API calls (tool-calling round trips). The total across all three demos stays within the 10-call budget.

### 11.6 How to Run the Agent Platform

#### Prerequisites
1. Data generation scripts (01 and 02) have been run - Databricks tables exist in workspace.forecast_db
2. .env file exists at ../forecast-agent/.env with Azure OpenAI credentials
3. openai, pydantic, and python-dotenv packages are installed

#### Running in a Databricks Notebook
```python
# Install dependencies
%pip install openai pydantic python-dotenv

# Navigate to the project folder
import sys, os
sys.path.insert(0, "/Workspace/Users/sourav.saha26-10@iimv.ac.in/agentic_poc/supply-chain-inventory-management")

# Run the app
exec(open("/Workspace/Users/sourav.saha26-10@iimv.ac.in/agentic_poc/supply-chain-inventory-management/app.py").read())
```

#### Running as a Standalone Script
```bash
cd supply-chain-inventory-management
python app.py
```

### 11.7 API Call Budget Management

The platform enforces a strict API call budget of **10 calls per session** (MAX_API_CALLS = 10 in config.py):
- Each call to client.responses.create() increments the counter
- If the budget is exhausted, the agent returns the best partial response with a guardrail message
- The counter can be reset between queries via agent.reset()
- Tool calls (Spark queries) do NOT count against the budget - only LLM calls do

### 11.8 BRD Compliance Summary

| BRD Section | Requirement | Implementation |
| --- | --- | --- |
| 9 | Event ingestion | get_supplier_events tool retrieves trigger events |
| 10 | Exception detection | get_exception_details, list_exceptions tools |
| 11 | Exception classification | LLM classifies in system prompt; types match BRD list |
| 12 | Impact analysis | LLM uses tool data to assess inventory, customer, supply, logistics impact |
| 13 | Root cause investigation | LLM investigates using tool evidence; distinguishes facts from inferences |
| 14 | Resolution planning | LLM generates options (transfer, expedite, alternate supplier, reallocation) |
| 15 | Decision evaluation | LLM evaluates options; policy engine enforces constraints |
| 16 | Policy engine | policy_engine.py - externalized, configurable, LLM cannot override |
| 17 | Human-in-the-loop | Policy engine determines human_approval_required per option |
| 20 | Agent architecture | Orchestrated loop with tool calling (single agent, multiple capabilities) |
| 21 | Tool layer | 11 typed tools with input/output schemas, validation, audit logging |
| 24 | LLM requirements | LLM reasons over tool results; no direct data access |
| 26 | Guardrails | API call limit, tool validation, financial thresholds, approved suppliers only |
| 27 | Explainability | Output format: what happened, why, investigation, options, recommendation |
| 28 | Observability | Verbose mode prints each API call, tool call, and result |
| 42.16 | Databricks integration | Agents access data only through controlled tools, never direct SQL |
| 42.17 | POC-to-production | Tool interface separates agent from data source; swap service layer for real APIs |

---

*Document Version: 2.0*  
*Last Updated: September 2025*  
*Project: Supply Chain Inventory Management - Agentic AI Platform*  
*Sections 1-10: Data Generation Pipeline*  
*Section 11: Agent Platform Architecture*