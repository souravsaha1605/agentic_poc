# SKU, Customer Forecast and SKU Budget Demo

This optional extension adds deterministic synthetic data for demonstrating
entity routing in the existing Forecast Intelligence and RCA Genie Agent. It
does not modify `workspace.forecast_db`, call Azure OpenAI, or change Teams.

## Supported capabilities

| Request | Supported source |
| --- | --- |
| SKU forecast | `vw_genie_sku_forecast` |
| Customer or customer-SKU forecast | `vw_genie_customer_forecast` |
| SKU budget | `vw_genie_sku_budget` |
| SKU price | `vw_genie_sku_price` |
| SKU promotion | `vw_genie_sku_promotion` |
| Entity name/type lookup | `vw_genie_entity_lookup` |

Customer budgets, customer prices and customer promotions are deliberately
unsupported. All customer names contain `Demo`, and every row carries dataset
version `commercial-demo-1.0`.

## Assumptions

- Country: India
- Currency: INR
- Forecast cadence: weekly
- Forecast vintage: seven days before target date
- Budget cadence: monthly fiscal periods `FY2026-P04` through `FY2026-P09`
- Budget version: `FY2026-V1`
- Unit: `each`
- Customer forecast grain: region, country, customer, SKU, target date, vintage
- Price and promotion grain: SKU only

## Publish in Databricks

Pull the feature branch and run `04_commercial_genie_setup.py` using Serverless
compute. A successful run prints `Commercial Genie demo is ready` and these six
view names. Rerunning is idempotent; matching certified grains are preserved and
conflicts block publication.

In the existing Genie Agent, add only the six printed views. Do not add the raw
dimensions or facts. Replace the Agent instructions with the complete current
`genie/SPACE_INSTRUCTIONS.md`.

## Controlled tests

Use `genie/commercial_benchmark_questions.json` as the complete oracle. Start
with:

```text
Show forecast performance for SKU-1001 in North, India from 2026-04-05 through
2026-09-27.
```

Expected actual is 3,305 each, forecast is 2,935 each, WMAPE is approximately
11.1952%, accuracy is 88.8048%, and bias is -11.1952%.

Then test customer routing:

```text
Show the SKU-1001 forecast for Metro Retail Demo in North, India from
2026-04-05 through 2026-09-27.
```

Expected actual is 1,983 each and forecast is 1,766 each.

Test the business boundary:

```text
Show the budget for Metro Retail Demo.
```

The Agent must state that customer budget is unsupported and ask for an SKU. It
must not allocate or infer a customer budget.

Finally test SKU budget and commercial evidence:

```text
Show the approved budget for SKU-1001 for FY2026-P08.
```

Expected budget is 480 each and ₹29,760 under approved version `FY2026-V1`.

```text
Show the price and approved promotion for SKU-1001 in August 2026.
```

Expected list price is ₹62 per each and promotion `PROMO-1001-AUG` is a 10%
discount.

## Production boundary

This demonstrates the schema, routing, certification and calculations. Real
customer forecasts and budgets require approved source tables, customer
entitlements, country mappings, freshness rules and row-level security. Do not
describe these demo identities or values as business data.

