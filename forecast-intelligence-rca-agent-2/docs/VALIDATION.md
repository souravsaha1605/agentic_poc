# Validation performed

## Latest verified local results

The following results were produced during the final test-hardening pass after
the Increment 1 and Increment 2 correctness changes.

| Check | Latest verified result |
| --- | --- |
| Default offline suite | 95 discovered; 90 passed; 5 optional Spark/Delta tests skipped |
| Separately enabled local Spark 4.2.0 / Delta 4.4.1 suite | 5 passed in 79.925 seconds |
| Focused hardening tests | 3 passed: aggregate follow-ups, partial inventory exposure and calendar-boundary comparison |
| Focused Python lint and syntax checks | Passed |
| `git diff --check` | Passed |
| Persistent application paid-call ledger | `used = 2`; SQLite integrity check `ok` |

No hosted Databricks validation is represented by these local results.

## Historical validation record

The results below were recorded earlier on 27 October 2026 with Python 3.12.14
and OpenJDK 21. They are retained as historical evidence and are not the current
suite counts.

| Check | Observed result |
| --- | --- |
| `python app.py` with cloud dependencies installed | 78 discovered, 77 passed, 1 explicitly skipped local Delta opt-in |
| Real local Spark 4.2.0 / Delta 4.4.1 integration | 1 integration test passed separately, including repeat initialization, query metrics, Delta state, budget and source-change rejection |
| Default interactive CLI and separate-process restart | Forecast/revenue/what-if completed; restarted process reused P0001/North for inventory |
| Application ledger after the first live probe | 1 reserved attempt; request blocked at network proxy |
| Successful live Azure OpenAI / Genie calls | 0; endpoint egress is pending publication |
| Teams package generation | Personal manifest plus original 192px color / 32px outline icons created and inspected locally |
| Focused Python lint and syntax checks | Passed |
| `git diff --check` | Passed |

The offline suite includes simulated model/Genie failures and budgets, real local
SQLite transactions, two-user/tenant isolation, request receipts/conflicts,
immutable versions, source edge cases, source certification, missing/malformed
JWT rejection, queue-first admission, worker redelivery/poison handling and
checksummed state/budget cutover. Budget tests reserve simulated calls; they do
not contact paid endpoints. Optional cloud packages were installed for the SDK
boundary tests. Delta artifacts used for local integration were downloaded over
verified TLS and checked against the Maven repository's SHA-512 digests.

Local Delta initialization was run twice without duplicating or overwriting the
source, and the spent-call ledger retained its simulated reservation. A changed
Delta source version was then rejected until readiness could be refreshed.

Actual Azure deployment, valid cloud channel authentication, tenant installation,
cloud OAuth/managed identity, live Blob/Queue persistence and proactive replies
remain unrun until the setup in `AZURE_SETUP.md`. Local mocks and negative-token
tests are not evidence that those live operations work. The cloud acceptance
report therefore defaults to all false, and Teams/Genie remain disabled.

## Follow-up cloud validation and v5.2 capabilities

The published credentials were found under MY_AZURE_OPENAI_* and the client now
supports those bindings. One compact model request was attempted with retries
disabled. It raised APIConnectionError; an unauthenticated reachability probe
confirmed a tunnel-level HTTP 403 from the environment proxy. No provider token
usage was returned. The failed attempt remains in the persistent ledger.

The exact hostname was saved in the environment network draft. The draft was
still unpublished at the last configuration check. No unchanged model retry was
performed. Azure Resource Manager authentication was tested and unavailable;
subscription target and Databricks authentication were not present. No paid
cloud resources were created and no live channel check is marked passed.

New synthetic weather, competitor, lifecycle and mix signals, regional/period
comparisons and fiscal/channel filters pass positive and negative tests. The
1154-row lab has 468 scoped readiness records and no failed expected fixtures.
The real local Spark/Delta integration passed again after these schema changes.
The ARM JSON/source-package invariants were tested locally; Azure-side template
validation and what-if remain unrun until authenticated deployment access exists.
