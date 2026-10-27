# Forecast Intelligence and RCA Agent, review 5

This folder contains the shared conversation core, deterministic supply-chain
services, durable user-owned state, and default-disabled cloud adapters. It uses
the review document's original FMCG examples. `P001` and `P0001` are distinct;
`Coke` has two master-data candidates. No response hard-codes 84% accuracy.

## Run locally without Azure or a key

Use Python 3.12 or newer. From **this folder**:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
python app.py --interactive --session my-investigation
```

`python app.py` runs real assertions, returns a nonzero status on failure, and
makes **zero paid model calls**. Optional SDK/Delta tests report explicit skips
when their dependencies or opt-in runtime are absent. To include the offline
Teams SDK boundary tests, install `requirements-cloud.txt` and run it again.

The interactive default uses **synthetic lab data**, not enterprise data. Local
identity comes from the OS login. State is kept in the Git-ignored `.rca_state` directory in this folder;
set `FORECAST_STATE_DIR` to an approved persistent location outside the checkout
when sharing a prepared development snapshot. Restart with the same `--session` to resume. Each cloud task
already has an isolated checkout; do not create a Git worktree unless requested.

Try the complete original journey:

```text
Analyze forecast performance for P0001 in North.
What about revenue?
Was inventory constraining sales?
What if demand is 15% higher?
We increased the promotion and accuracy improved.
Now analyze P0099 in West.
```

Inventory and revenue follow-ups reuse the active entity and period. A changed
product, region, store or category starts a separate case. An outcome stays
**user-reported and unverified**. What-if calculations create new versions and
preserve the baseline and previous versions. Price changes do not silently
predict demand. Use an owned `case_id` through the Python API, or
`/resume CASE_ID question` in Teams, to select an earlier case.

## Where the code lives

| File | Responsibility |
| --- | --- |
| `app.py` | Local validation and interactive development entry point |
| `agents/forecast_rca_agent.py` | Small channel-independent facade |
| `conversation.py` | Resolve context, decide intent/action, execute, render, commit |
| `contracts.py`, `models.py` | Trusted principal, bounded requests/plans, typed responses |
| `tool_registry.py`, `tool_executor.py`, `tools/` | Six-tool allowlist and typed dispatch |
| `services/forecast_rca_service.py` | Numerical calculations and evidence contracts |
| `data_access.py` | Synthetic records, Spark literal binding, hosted SQL parameter binding |
| `analytics.py` | Retained governed analytical DSL/compiler, with bound values and limits |
| `state.py`, `state_migration.py` | Owned SQLite/Delta/Azure Blob state and checked cutover |
| `lab.py`, `bootstrap.py` | Reproducible fixtures, actual validation, source audit/publication |
| `cost_control.py`, `client.py` | Shared paid-call ceiling and lazy, retry-free client |
| `channels/`, `genie_validation.py` | Deferred channel and synthetic comparison adapters |

Comments explain the purpose and the important business/security decisions.
Business calculations do not call a model. `business.py` is only an import
facade; the implementation remains in the `services` layer.

The old global service singletons, default shared `demand_planner` owner, and
caller-supplied comparison dictionaries have intentionally been replaced.
Notebooks in this folder use the new contracts; older notebooks in sibling
folders are outside this change and should not be mixed into this runtime.

## Metrics and evidence

- Error is forecast minus actual. WMAPE uses total absolute error divided by
  total **absolute actual**. Accuracy is `100 - WMAPE`, including negative
  accuracy when justified. Zero denominators remain unavailable.
- Select one forecast vintage per product/store/target. Explicit vintage requests
  must exist; default is latest issued at/before each target. Conflicting actuals,
  duplicate grains and forecast-time leakage are rejected.
- Net revenue requires unit price, a validated **percentage** discount and a
  single explicit currency. Missing net revenue never becomes gross revenue.
  Exposure is a signed forecast/actual revenue difference at observed prices,
  not a causal lost-sales claim. Trend compares mean observed weekly net revenue.
- Inventory uses the latest known snapshot **per store** at/before the cutoff.
  Never sum dates. Mixed ages, stale snapshots and timestamp conflicts are
  visible. Weekly zero snapshots do not establish stockout days.
- RCA returns SUPPORTED, POSSIBLE, NOT_SUPPORTED or NOT_TESTABLE. Certification
  failures are separately BLOCKED/FAIL and stale certification is STALE.
  Missing competitors, weather, lifecycle or mix evidence is not fabricated.
- All evidence includes source/version, coverage, vintage policy, feature/logic
  version and calculation timestamp. Raw source rows stay inside the backend.

Routing is deliberately conservative and deterministic. It supports exact IDs,
normalized names/approved aliases, regions, stores, categories on selected
products, ISO date windows, `last N weeks`, as-of inventory, explicit vintage selection,
`FY2026-P09`, `channel Retail/Online`, four-date period comparisons and two-region
comparisons. Ambiguous names and unsupported mapping labels ask for clarification. Category-wide ranking is available through the governed
DSL to an authorized development caller; it is not silently substituted for a
single-product investigation. The v5.2 lab certifies weather, competitor, lifecycle and store-mix associations,
explicit period/region comparisons, Retail/Online filtering and a documented
calendar-year monthly fiscal mapping. Enterprise calendars, additional seasonal
cadences and external sources still require their own approved data contracts. These are explicit capability limits.

## Cost controls

Standard Azure binding names and the platform-published `MY_AZURE_OPENAI_*`
aliases are supported without copying secrets into source files.

`ENABLE_LLM=false` is the default. The complete deterministic journey needs no
model. When enabled, a model may rank existing evidence IDs, **not write new
numbers, SQL or causal claims**. Rendering uses backend-owned facts.

Each answered turn makes at most one model HTTP request. Input is bounded by a
conservative **1500 UTF-8 byte** ceiling (including instructions), and output is
capped at **150 tokens**. There is no transcript replay and no automatic SDK
retry. Oversized evidence uses the deterministic answer. Failed requests still
consume reservations. The persistent shared ledger permits at most **70 paid
API reservations**, including optional Genie requests/polls. `MAX_PAID_CALLS`
can lower this limit, never raise it. Never delete/reset the ledger to retry.

SQLite is the single-host local ledger, Delta is the shared notebook ledger,
and Azure Blob ETags are the multi-worker ledger. During cutover, stop the old
writer and use `transfer_paid_budget` to carry spent calls to the new empty
ledger. Do not keep independent active ledgers for the same project. This ceiling
covers application model/Genie requests; storage, hosting and SQL compute have
separate platform charges, even with LLM disabled.

## Databricks notebooks

1. Run `01_data_initialization.ipynb` on an approved Delta-enabled Runtime.
   The default is the dedicated `workspace.forecast_rca_lab` schema.
2. Run `02_golden_rca_tests.ipynb`. It runs assertions and displays actual readiness.
3. Supply a verified identity map, then use `LLM Test Notebook.ipynb` as the
   shared notebook harness. It also defaults to zero paid calls.

Initialization preserves existing fact data. Incompatible source schema blocks
publication and requires an explicit lab migration. Deliberate golden fixtures
live separately. The job validates their expected signals, audits the actual
source, creates the five governed views, and publishes a source manifest last.
Reruns do not duplicate fixture data, state, readiness keys or spent calls.
`deployment/databricks.yml` defines one manually triggered readiness job; add
its schedule only after confirming source cadence and budget.

For a real local Delta integration, use compatible Spark/Delta dependencies and
set `RUN_DELTA_TESTS=true` with `DELTA_TEST_JARS` pointing to trusted, verified
matching jars. The test executes initialization twice, actual governed queries,
Delta state, budget persistence, and rejection of a changed uncertified source.
No cloud credentials are needed.

## Cloud handoff and verification

Read [AZURE_SETUP.md](AZURE_SETUP.md) for the consolidated Azure/Databricks setup,
identity linking, deployment and live release gates. Teams and Genie stay off
until configured and tested. A flag is an operator attestation, not evidence that
provisioning or tenant authentication has already succeeded.

[docs/REQUIREMENTS_MAP.md](docs/REQUIREMENTS_MAP.md) maps the review to code,
fixtures, tests and remaining source/platform decisions. The original reference
catalogue is preserved in [docs/BRD_REFERENCE_EXCERPTS.md](docs/BRD_REFERENCE_EXCERPTS.md).
The code does not change forecasts, ERP records or operational inventory.

For the reviewable deployment template, private source packaging, secure runtime
configuration and bounded live check, follow [deployment/RUN_CLOUD.md](deployment/RUN_CLOUD.md).
