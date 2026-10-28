# Genie Code Runbook — Forecast Intelligence and RCA

Use this document as the operating contract when Genie Code diagnoses or fixes
the Databricks pilot. The BRD remains the business requirements authority. This
runbook explains how to work safely in the current repository.

## Copyable Genie Code instruction

```text
Read docs/GENIE_CODE_RUNBOOK.md completely before executing or changing code.
Treat its safety boundaries, data invariants, execution order and acceptance
checks as mandatory. Work only in forecast-intelligence-rca-agent-2 on branch
forecast-rca-review. Diagnose the exact failure before proposing a fix. Prefer
the smallest reversible code change and run the prescribed regression checks.
Do not weaken certification, overwrite data, reset the paid-call ledger, call a
paid API, change cloud resources, or alter the Teams path. If a required action
is prohibited or needs an administrator, stop and report the blocker.
```

## Project purpose

The project provides governed forecast, revenue, inventory, historical-pattern
and evidence-qualified root-cause analysis. The current business-user pilot is
a Databricks Genie Space backed by one certified semantic view.

The delivery paths coexist:

```text
Direct pilot:
Business user -> Genie Space -> Serverless SQL -> certified Genie view

Future Teams path:
Teams -> Azure Bot -> App Service -> Queue worker -> governed analytical views
```

Direct Genie does not replace or disable Teams. Application setting
`GENIE_MODE=off` disables only the optional application-side Genie comparison
adapter. It does not disable a direct Genie Space.

## Authoritative sources

Read these before changing business behavior:

1. `docs/BRD_REFERENCE_EXCERPTS.md` — authoritative business requirements.
2. `docs/REQUIREMENTS_MAP.md` — requirement-to-code coverage and limitations.
3. `docs/VALIDATION.md` — historical and latest verified test evidence.
4. `genie/SPACE_INSTRUCTIONS.md` — metric and answer rules for the Genie Space.
5. `genie/benchmark_questions.json` — offline numerical answer oracle.

Do not reinterpret an illustrative BRD example as permission to change fixture
IDs, formulas, source grain or business semantics.

## Environment and scope

- Git branch: `forecast-rca-review`.
- Project folder: `forecast-intelligence-rca-agent-2`.
- Pilot catalog/schema: `workspace.forecast_rca_lab`.
- Existing `workspace.forecast_db` is outside this initializer's scope.
- The supplied initializer rejects schemas whose name does not end in `_lab`.
- Databricks Free Edition/Serverless is suitable for this pilot but is not proof
  of Azure Databricks production hosting or service-level guarantees.
- Use Serverless compute already available in the workspace. Do not provision a
  workspace, warehouse, cluster, job schedule or other cloud resource.

Never drop, truncate, overwrite, rename or migrate an unrelated schema. Never
copy lab fixtures into `workspace.forecast_db`.

## Key data objects

| Object | Purpose | Write policy |
| --- | --- | --- |
| `fact_sales_forecast` | Preserved lab source and versioned BRD fixtures | Append missing fixture grains only |
| `rca_golden_fixtures` | Immutable expected scenarios | Create once; mismatch blocks publication |
| `dim_product` | Product/region/category catalogue | Insert missing catalogue scopes |
| `rca_readiness_registry` | Capability certification by source version | Version-keyed merge |
| `rca_source_manifest` | Published source and Delta version | Publish last, after successful certification |
| `rca_paid_call_ledger` | Durable paid-call reservations | Preserve; never reset or delete |
| `vw_forecast_metrics` | Governed application source | Replaceable view after certification |
| `vw_genie_forecast_observations` | Original product/store Genie source | Replaceable single-grain view |
| Commercial demo dimensions/facts | Separate SKU, customer, forecast, budget, price and promotion grains | Append missing certified demo grains only |
| `rca_commercial_manifest` | Certified commercial demo version and counts | Append one record per source version |

Fixture grain:

```text
product_id, store_id, region, date, forecast_generated_date
```

Matching source rows must remain unchanged. Missing fixture grains may be
appended. Duplicate grains, incompatible units and invalid forecast vintages
must block publication.

## Mandatory execution sequence

Run from the pulled Databricks Git folder in this order:

1. `01_data_initialization.ipynb`
2. `02_golden_rca_tests.ipynb`
3. `03_genie_space_setup.py` as a Databricks source-format notebook
4. `04_commercial_genie_setup.py` when the separate SKU/customer/budget demo is
   in scope

Do not create or extend the Genie Space until the applicable steps pass.

Initialization is designed to recover from an interruption and to be
idempotent. A rerun must preserve existing matching rows, table grain, source
certification and the paid-call ledger.

## Required success evidence

Record the following values after execution:

- `source_version`
- current fact-table Delta version
- `rows`, `existing_rows` and `generated_rows`
- `golden_failures` and `source_failures`
- readiness record count
- failed or blocked readiness count
- paid-call ledger value before and after
- Genie semantic-view row count
- duplicate fixture-grain count

Required conditions:

```text
golden_failures == 0
source_failures == 0
failed readiness records == 0
blocked readiness records == 0
manifest source_version == readiness source_version
manifest delta_version == current fact Delta version
duplicate fixture grains == 0
Genie semantic-view rows > 0
paid-call ledger after == paid-call ledger before
```

A clean v5.2 fixture-only initialization normally has 1,154 fact rows and 468
readiness records. Existing compatible lab data can change those totals, so the
certification conditions above are authoritative.

## Business invariants

Do not change these rules to make a test or generated answer pass:

- WMAPE is `100 * sum(abs(forecast - actual)) / sum(abs(actual))`.
- Forecast accuracy is `100 - WMAPE`; it is not silently clamped.
- Bias is forecast minus actual and uses absolute actual as its percentage
  denominator.
- Zero actual demand makes percentage metrics unavailable.
- Forecast vintages are selected before aggregation. Never sum vintages.
- Inventory is a balance. Select the latest valid balance per product/store at
  or before the cutoff; never sum inventory across dates.
- Missing inventory is unavailable rather than zero. Partial coverage must be
  disclosed.
- Product aggregation requires a concrete category and homogeneous certified
  units. Currency aggregation requires one currency.
- Four-week rolling results require four consecutive completed weeks.
- Missing comparison data is different from duplicate-grain, schema,
  certification and data-integrity errors.
- Missing evidence is `NOT_TESTABLE`; certification failure is `BLOCKED`.
- Associations are evidence, not proof of causality.

## Known Serverless compatibility rule

Databricks Serverless rejects Spark writer mode `errorifexists`. Production code
uses `mode("append")` only after an explicit table-absence check in the serial
initializer. Do not restore `errorifexists`, and do not replace this with
`overwrite`.

If an append/create operation fails:

1. Check whether the target table already exists.
2. Check schema compatibility without writing.
3. Check whether a previous run stopped after source append.
4. Rerun the initializer when the existing schema and grain are compatible.
5. Stop and report an incompatible schema; do not force a migration.

## Error triage

### Project root or import error

Symptoms include `Set FORECAST_PROJECT_DIR` or `ModuleNotFoundError` for a
project module.

- Run the notebook from the repository folder.
- Set `FORECAST_PROJECT_DIR` to the exact
  `forecast-intelligence-rca-agent-2` directory if required.
- Add that directory to `sys.path`; do not copy modules into another folder.

### Missing table or view

- If the schema is absent, run initialization.
- If the fact exists but readiness/manifest is absent, treat it as an
  incomplete initialization and rerun.
- If certification exists but the Genie view is absent, pull the latest branch,
  rerun initialization, then run `03_genie_space_setup.py`.
- Do not create an empty placeholder table to bypass a check.

### Schema incompatibility

- Report the exact missing or incompatible columns and types.
- Preserve the table unchanged.
- Propose an isolated versioned lab migration for human review.
- Do not cast identifiers or business measures merely to silence validation.

### Expected-signal or readiness failure

- Identify the product, region, capability, source version and quality flags.
- Compare the source observation with the BRD expected signal.
- Correct a clear generation/calculation defect only with a focused regression
  test.
- Do not change an expected status from supported to unavailable to make it pass.
- Do not publish a manifest after a failed certification.

### Source/manifest Delta-version mismatch

- Another write occurred after certification.
- Do not update only the manifest.
- Rerun complete certification so views, readiness and manifest refer to the
  same source version.

### Duplicate grain or forecast vintage

- Display the duplicate key and counts.
- Determine whether it is a repeated identical row or a legitimate different
  forecast vintage.
- Preserve legitimate vintages and select one before aggregation.
- Do not apply `DISTINCT` as a general repair because it can hide source defects.

### Genie answer differs from benchmark

- Inspect generated SQL and selected date boundaries.
- Confirm the Space uses only the certified views documented in
  `genie/SPACE_INSTRUCTIONS.md`, never the underlying raw facts.
- Confirm one vintage per target grain and correct units/currency.
- Compare with `genie/benchmark_questions.json` and deterministic service output.
- Improve Space instructions or the semantic view only when the deterministic
  oracle proves the issue. Do not change expected numbers to match Genie.

### Permission or warehouse error

The business user needs workspace access, Genie Space `Can use`, warehouse
`CAN USE`, catalog `USE CATALOG`, schema `USE SCHEMA`, and view `SELECT`.
Report the missing permission. Do not grant administrator or broad wildcard
access as a shortcut.

## Permitted focused fixes

Genie Code may propose a change when all of these are true:

- The failure is reproduced and its exact source is identified.
- The change stays inside this project and isolated lab contract.
- Existing business semantics and fixture IDs are preserved.
- A regression test fails before and passes after the change.
- Relevant focused tests and the default offline suite pass.
- The diff contains no credentials, private identity mappings or unrelated files.

Prefer fixing a shared helper or deterministic calculation over editing notebook
output. Keep comments simple enough for a new developer to follow.

## Prohibited actions

Do not:

- Drop, truncate, overwrite or reset tables to make initialization pass.
- Modify `workspace.forecast_db` or production data.
- Reset, delete or lower the recorded value in `rca_paid_call_ledger`.
- Call Azure OpenAI, a Genie conversation API or another paid model API.
- Enable `ENABLE_LLM`, application `GENIE_MODE`, or Teams release flags.
- Provision, deploy or change Azure/Databricks resources.
- Create a scheduled job or leave compute deliberately running.
- Commit, push or merge without explicit user instruction.
- Weaken assertions, suppress errors or relabel failures as unavailable.
- Remove or replace Teams integration while implementing direct Genie.
- Put secrets, tenant IDs, tokens, personal mappings or credentials in Git.

## Offline validation

Run from `forecast-intelligence-rca-agent-2`:

```bash
python -m unittest discover -s tests
python -m py_compile 03_genie_space_setup.py 04_commercial_genie_setup.py genie_semantic.py commercial_lab.py
python -m json.tool genie/benchmark_questions.json
python -m json.tool genie/commercial_benchmark_questions.json
git diff --check
```

Optional Spark/Delta and Teams SDK tests may skip when their runtimes are not
installed. Report skips explicitly; do not claim hosted validation from local
doubles.

## Genie Space configuration

- Space name: `Forecast Intelligence and RCA`.
- Add `workspace.forecast_rca_lab.vw_genie_forecast_observations`. When the
  commercial demo is enabled, also add only the six views printed by
  `04_commercial_genie_setup.py`; never add their raw fact tables.
- Paste the complete `genie/SPACE_INSTRUCTIONS.md` into Space instructions.
- Use the smallest approved Serverless SQL warehouse with auto-stop.
- Grant business users `Can use`, not edit, unless they are approved builders.
- Validate with the exact questions and results in
  `genie/benchmark_questions.json` and, when enabled,
  `genie/commercial_benchmark_questions.json` before sharing broadly.

## Completion report template

```text
Scope:
Failure reproduced:
Root cause:
Files changed:
Data objects read:
Data objects written:
Source version:
Delta version:
Initialization report:
Readiness failures/blocks:
Duplicate grains:
Paid-call ledger before/after:
Focused tests:
Full offline tests and skips:
Hosted Databricks checks actually run:
Remaining limitations:
Cloud/model calls made: none
Cloud resources changed: none
```

