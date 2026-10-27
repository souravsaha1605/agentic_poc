# Review-to-code map and fixture audit

Baseline: review 5 / BRD 1.1, 27 October 2026. The supplied folder was found on
`agent-creation` at `4da5388d9c736694470468f46908555fdd8a2d62`; it was absent from
`main`. Changes are isolated to `forecast-intelligence-rca-agent-2`.

## Repository findings before changes

- The default non-LLM entry imported an eagerly initialized credential client.
- Delta scenario loads omitted saved baseline/current/previous, evidence,
  assumptions, outcomes and period fields. Reads did not enforce a trusted owner.
- A shared default user and session-only lookups could reuse another user's state.
- The model loop allowed ten round-trips plus implicit SDK retries, with a large
  system prompt and unbounded full results.
- The analytical compiler interpolated filter values and omitted a default LIMIT.
- Inventory selected one arbitrary row across stores; missing values became zero.
- Initialization overwrote source tables, substituted SKU examples and populated
  illustrative readiness independently of failed scenario assertions.
- Golden tests checked retrieval instead of actual conversation/outcome behavior;
  their success logic could hide a failing result.

## Functional coverage

| Requirement | Changed code / evidence | Boundary |
| --- | --- | --- |
| FR01 forecast | Typed plan; deterministic WMAPE/bias; vintage/grain handling; original Test 1; exact windows | Fiscal/channel mappings use explicit source fields; unsupported labels/grains ask clarification |
| FR02 revenue | Percent discount/currency validation; gross/net; weekly change and defined signed exposure | No gross-for-net fallback or inferred price elasticity |
| FR03 inventory | Latest per store at/before cutoff; freshness/conflict flags; historical tests | Snapshots do not certify stockout days |
| FR04 history | Weekly trend/level shift, volatility, bias drift, deterioration, divergence, spikes/drops/intermittency; cycle tests | Seasonal cadence must be validated; absent external drivers NOT_TESTABLE |
| FR05 initiation | Entity resolution precedes intent/action; explicit/implicit RCA; selective follow-ups | Conservative supported language; no unrestricted model agent |
| FR06 evidence | Six governed tools, bounded typed plan, versions/provenance and paired-data quality | Raw rows stay in backend; no raw SQL model tool |
| FR07 hypotheses | Per-capability readiness, evidence status and conservative confidence | Correlation is not causation; Certified lab lifecycle/mix/weather/competitor associations; no causal inference |
| FR08 memory | Atomic owned document with transcript, request receipts and restart/resume tests | Host must authenticate; SDK display names are never authority |
| FR09 scenario | Immutable versions, baseline/current/previous, outcomes and assumptions | Arithmetic what-if only; state cutover requires paused writers |

## BRD sections and amendments

| Source coverage | Implementation / acceptance evidence |
| --- | --- |
| Sections 1–7 | README scope/non-goals; existing governed-data architecture retained |
| Sections 8–12 | Deterministic numerical services; null/returns/vintage/stockout tests |
| Sections 13–19 | Context resolution, separate intent/action, owner state and ten original journeys |
| Sections 20–25 | Six-tool contracts, typed plans, governed read adapters, evidence/provenance |
| Sections 26–30 | Readiness/quality, explicit errors, parameter/literal binding, token/call ceilings |
| Sections 31–37 | SQLite/Delta/Blob adapters, identity mapping, audit turns, deterministic grounding |
| Sections 38–43 | Actual conversation assertions, complete journey, beginner-facing entry points |
| Section 44, amendments 1–6 | Preserving initializer; dedicated fixtures; observed certification; versioned registry |
| Section 44, amendments 7–9 | Validated plans, deterministic query boundaries, small evidence-only model input |
| Section 44, amendments 10–12 | Mandatory resolution, durable owned memory, immutable scenarios |
| Section 44, amendments 13–15 | Purposeful signals, golden failures block readiness, honest NOT_TESTABLE |
| Section 44, amendments 16–18 | Grain/null/gap/discount/future/timestamp audit, provenance, deterministic seed/version |
| Section 44, amendments 19–22 | Safe notebooks, one shared core, default-disabled hosted adapters, reviewed runtime sequence |
| Sections 45–47 | First-run notebook and single maintained Databricks readiness job |
| Sections 48–50 | Typed bounded plans, minimum exposure, source/capability publication |
| Sections 51–55 | Shared harness, documented release gates, cloud setup handoff |

These rows map responsibility and implemented boundaries, not a claim that
unrun cloud integrations or all possible business-data contracts are certified.
Original source examples and both matrices are retained in
`BRD_REFERENCE_EXCERPTS.md`. Original illustrative READY cells remain examples.

## Fixture audit and certification

The old notebook generated `SKU-001` … `SKU-100` and overwrote data in
`workspace.forecast_db`. Its synthetic scenarios and aliases were not proof of
the original P0001/P0099/Coke examples. That code is replaced by an initializer
restricted to a separate `*_lab` schema; existing source facts are preserved.

The deterministic lab uses seed 42 and dataset `brd-lab-5.2`, with 1154 weekly
records. It includes P0001/North promotion, P0099/West under-bias,
P0020/North inventory constraint, distinct P001/South normal demand, two Coke
master candidates, trend, price, 26-week seasonality, revenue deterioration,
missing-data, new-product, intermittency and over-bias fixtures. There are 468
entity/capability/store-scope readiness records. Certification observes the
actual signal and marks failures BLOCKED/FAIL rather than relabelling them as
unavailable. No record is certified merely because generation completed.

The v5.2 lab adds observed weather contrasts (P0084), competitor-relative price
contrasts (P0085), a launch ramp (P0086), a two-store share shift (P0087), and
North/West divergence for P0088. Expected associations are POSSIBLE, not causal
proof. The fiscal mapping explicitly uses calendar-year monthly lab periods;
Retail/Online are source fields. Negative fixtures still return NOT_TESTABLE
when a particular entity lacks evidence or history. Real enterprise data needs
its own approved drivers, calendar, aliases and source-version publication.

## Verified versus deferred

- Local acceptance: real assertions for ten original journeys, restart, ownership,
  request retries/conflicts, what-if immutability, metric edge cases, certification,
  call budgets, SQL binding, Genie isolation, and Teams boundary/worker behavior.
- Real local Spark/Delta: initializer executed twice, source row count/version
  preserved, governed query metrics verified, shared budget preserved, state
  recovered, owner/conflict checks enforced, changed source rejected.
- Actual Azure OpenAI and Genie invocations: zero. Budget tests use local doubles.
- Live Azure Bot tokens, tenant installation, outbound replies, cloud SQL OAuth,
  deployed managed identity and Blob/Queue endpoints: require the later setup in
  `AZURE_SETUP.md`. Local doubles do not certify these cloud operations.
- Data-source gaps above remain explicit unsupported/not-testable capabilities;
  turning a flag on cannot create the missing evidence.
