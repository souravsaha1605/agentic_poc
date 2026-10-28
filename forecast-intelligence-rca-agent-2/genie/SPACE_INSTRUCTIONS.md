# Forecast Intelligence and RCA Genie Space

Use only `workspace.forecast_rca_lab.vw_genie_forecast_observations` for
business calculations. This is certified synthetic pilot data. Never describe
it as production or customer data.

## Scope and grain

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

