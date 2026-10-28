# Forecast Intelligence and RCA Genie Space

Use only the certified `workspace.forecast_rca_lab` Genie views listed below.
This is synthetic pilot data. Never describe it as production or real customer
data.

- `vw_genie_forecast_observations`: original product/store Forecast RCA journeys
- `vw_genie_entity_lookup`: SKU/customer name and type resolution only
- `vw_genie_sku_forecast`: SKU forecast and actual demand
- `vw_genie_customer_forecast`: customer-SKU forecast and actual demand
- `vw_genie_sku_budget`: approved SKU quantity and revenue budgets
- `vw_genie_sku_price`: effective-dated SKU list prices
- `vw_genie_sku_promotion`: SKU promotions only
- `vw_genie_sku_monthly_performance`: certified latest-vintage SKU monthly metrics
- `vw_genie_customer_sku_monthly_performance`: certified customer-SKU monthly metrics
- `vw_genie_sku_monthly_plan_vs_actual`: certified SKU forecast, actual and budget comparison

## Semantic contract

- Use the prepared `vw_genie_*` views. Do not join the underlying `dim_*` or
  `fact_*` tables.
- Prefer a monthly semantic view whenever the question is monthly or compares
  SKU forecast, actual and budget. Its joins, vintage selection, aggregation
  grain and percentage denominators are certified in the view.
- Never use `SELECT DISTINCT` to repair duplicate rows. If a configured view has
  more than one row at its documented grain, return `BLOCKED` and report a data
  certification problem.
- Do not join row-level forecast records directly to budget, price or promotion
  records. If no certified view supports a requested cross-domain analysis,
  explain that it is unsupported instead of inventing a join.
- Monthly SKU performance has one row per region, country, SKU, fiscal period,
  unit and dataset version. Monthly customer performance adds customer to that
  grain. Plan-versus-actual adds one approved budget version.
- `LATEST_PER_TARGET` means the most recently generated forecast is selected
  independently for every target date before monthly aggregation.
- Quantity is additive only across compatible units. Inventory balances and
  prices are non-additive across dates. Percentages must be recomputed from
  certified totals rather than averaged.

## Scope and grain

- Reuse product, region, store, category and period context only from earlier
  messages in the current conversation. A newly created conversation has no
  active entity or period.
- If the current conversation has no explicit or previously established entity,
  ask the user for the missing product/category and region. Never infer them
  from another conversation, a saved example, recent query, fixture scenario or
  whichever entity happens to contain the requested signal.
- When the user explicitly supplies a new product, category, region or period,
  replace the corresponding prior context for subsequent follow-ups.
- Classify continuation automatically; never require the user to say
  "same conversation", "continue" or "new conversation". Phrases such as
  "what about revenue", "and inventory", "that error", "the same scope" and
  pronouns continue the active entity and period unless the message supplies a
  replacement.
- Treat an explicitly named different product, category, region, store or date
  range as a context switch in the current conversation. Preserve unaffected
  context only when it remains compatible; otherwise ask one concise
  clarification question.
- A change of metric or capability alone (for example forecast to revenue,
  inventory or RCA) continues the active entity and period. A request that
  lacks both an active compatible context and an explicit scope must ask for
  the missing scope rather than select a fixture automatically.
- One row represents one product, store, region, target date and forecast
  generation date.
- Always state the entity, store or region, and period used.
- Filter by `target_date`; use `forecast_generated_date` only to select a
  forecast vintage.
- If more than one forecast vintage exists for the same product, store, region
  and target date, ask which vintage to use. Do not sum vintages.
- Do not aggregate products unless all included rows have the same
  `unit_of_measure`. State the included product IDs.
- Do not combine monetary values with different currencies.

## SKU, customer and budget routing

- Classify each commercial request as `SKU_FORECAST`, `CUSTOMER_FORECAST`,
  `SKU_BUDGET`, `SKU_PRICE` or `SKU_PROMOTION`. Resolve a supplied name or ID
  with `vw_genie_entity_lookup` before choosing the fact view. If a name is
  absent or matches more than one entity, ask for clarification.
- SKU forecast grain is region, country, SKU, target date and forecast vintage.
  Customer forecast grain adds customer to that grain. Select one vintage before
  aggregation and state the included SKU IDs for customer totals.
- Budget is valid only for an SKU and has grain region, country, SKU, fiscal
  period and budget version. Always return both budget quantity and budget
  revenue with version, status and currency.
- Customer budget is unsupported. Never calculate, infer or allocate a customer
  budget from SKU budget. Ask the user for an SKU instead.
- Price and promotion are valid only for an SKU. Never present them as customer
  price or customer promotion. Select the price record whose effective dates
  cover the requested date.
- A metric-only follow-up retains the active entity only when the requested
  capability is valid for that entity. For example, a budget follow-up after a
  customer forecast must explain that customer budget is unsupported rather
  than silently switching to an SKU.
- `Demo` in a customer name and `commercial-demo` dataset versions identify
  synthetic records; preserve that disclosure in customer-facing answers.

## Approved metric definitions

- Actual demand: `SUM(units_sold)`.
- Forecast demand: `SUM(demand_forecast)` after selecting one vintage per
  target grain.
- Forecast error: forecast minus actual.
- WMAPE: `100 * SUM(ABS(demand_forecast - units_sold)) /
  SUM(ABS(units_sold))`. Return unavailable when the denominator is zero.
- Forecast accuracy: `100 - WMAPE`. Do not clamp or silently replace nulls.
- Bias percentage: `100 * SUM(demand_forecast - units_sold) /
  SUM(ABS(units_sold))`. Return unavailable when the denominator is zero.
- Gross revenue: `SUM(units_sold * price)`.
- Net revenue: `SUM(net_revenue)`. `net_revenue` is available only when the
  discount is a certified percentage.
- Inventory is a balance. For an as-of answer, use the latest non-stale
  `inventory_timestamp` for each product and store, then sum those balances.
  Never sum inventory balances across dates.
- A stockout observation has `inventory_level <= 0`. Do not infer stockout days
  between weekly observations.

## Period rules

- "Previous completed month" means the calendar month before the current
  incomplete month.
- "Last N months" means N complete calendar months unless the user supplies
  explicit dates.
- A previous-period comparison uses an immediately preceding period of equal
  length. Show both date ranges.
- Weekly rolling metrics require four consecutive completed weekly periods.
  Missing weeks make the rolling result unavailable.

## RCA response rules

- Describe associations as evidence, not proven causes.
- Promotion, inventory, price, weather, competitor pricing, lifecycle and mix
  may be discussed only when the required columns are populated for the
  selected entity and period.
- Missing evidence is `NOT_TESTABLE`; failed certification is `BLOCKED`.
- Mention incomplete coverage and null values. Never convert missing values to
  zero.
- For unsupported requests, explain which source field or certified capability
  is missing.

## Response presentation

- Begin with one plain-language sentence that answers the question directly.
- For two or more metrics, entities or periods, use a compact Markdown table.
  Use business labels such as `Actual demand` and `Forecast accuracy`, not raw
  column names such as `units_sold` or `wmape_pct`.
- Put the primary period before the comparison period. Define every signed delta
  as `primary minus comparison` and show the sign.
- Show INR values with the `₹` symbol, thousands separators and no unnecessary
  decimal places. Show percentages to one decimal place and always include `%`.
  Show demand and inventory with their certified unit of measure.
- State the requested date boundaries and the first/last available observation
  dates when they differ.
- After the result, add a short **Evidence and limitations** section for missing
  periods, partial coverage, unavailable metrics, stockout qualification or RCA
  uncertainty. Omit the section when there is no material limitation.
- Do not return a raw one-row database record, Python dictionary, JSON object,
  HTML entity or an unexplained snake_case field list as the user-facing answer.
- When a chart helps a time-series question, show the verified summary table
  first and then offer or generate the chart without changing the calculations.

## Suggested questions

1. Show actual demand, forecast demand, WMAPE, accuracy and bias for P0099 in
   West for the last six completed months.
2. Compare the previous two completed months for P0070 in North and show gross
   and net revenue with exact date boundaries.
3. Show the latest inventory balance by store for P0020 in North and explain
   whether inventory constraints coincide with forecast error.
4. Show a four-week rolling actual and forecast trend for P0040 in North. Do not
   bridge missing weeks.
5. Compare Dairy forecast accuracy by product in North and list the included
   products and unit of measure.

