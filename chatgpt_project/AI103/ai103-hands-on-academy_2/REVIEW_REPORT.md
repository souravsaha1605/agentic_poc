# Tutor review — edition 1.2, 23 October 2026

This pass resumed from the saved edition 1.1 ZIP. It fixes additional defects found during
code review and expanded execution checks, and adds an ordered teaching guide.
Start with [MASTER_GUIDE](MASTER_GUIDE.md); it links every notebook, implementation and RUNBOOK.

## Corrections found in this pass

| Finding | Correction and evidence |
|---|---|
| A supervisor in another tenant could decide a refund | Store the request tenant; require the same tenant when approving. Cross-tenant regression passes. |
| The same user name in another tenant could execute an approved refund | Require owner AND tenant on execution. Verify no effect is inserted for the denied caller. |
| Unknown roles inherited search-tool permission | Explicit role allowlist; unknown roles have no tools. Test verifies the backend is not reached. |
| A cache key omitted the principal role | Include role alongside tenant, user, version and query. Verify a changed role cannot reuse the entry. |
| Launcher left runtime output/dotenv settings behind | Restore their prior values in finally, on both successful and failed execution. Credentials still clear. |
| Incomplete or traversal-containing volume paths passed string checks | Reject incomplete volume names, placeholders and traversal in launcher and bootstrap. These are format checks, not a live permission or mount check. |
| Offline custom-document variant requested a cloud model ID | Read DOCUMENT_MODEL_ID only in the live custom branch. Found by running every offline variant. |
| A non-ASCII invalid API token could raise TypeError before auth rejection | Compare UTF-8 bytes and return 401; regression test covers the malformed token. |
| Per-file learning intent and route were inconsistent | Added Purpose, Learn and Run headers to all 132 code files; Python header insertion preserved ASTs. |
| Learners needed one ordered reference | MASTER_GUIDE covers 49 learning entrypoints, code glossary, prerequisites, variants, execution locations and terms. |

## Completed pending local checks

- 51 unit/boundary checks passed, including real bootstrap code with filesystem boundaries mocked.
- 37 main offline lesson/capstone scripts passed.
- 49 default notebook launchers passed with mocked DBUtils.
- 76/76 offline entry/variant combinations passed; this includes all defaults plus nondefault variants.
- App Service ZIP was built, integrity-checked, extracted into an isolated directory and exercised through
  a WSGI request with the expected synthetic answer. This does not test Gunicorn, Docker or Azure hosting.
- Python/JSON/YAML syntax and local documentation links were checked. Every code file has teaching headers.
- Updated package integrity manifest and retained the original handbook byte-for-byte.

## Upgrade instructions

1. Download this ZIP and preserve your existing personal experiments and evidence separately.
2. Upload the new ZIP to your Databricks volume and rerun the reviewed bootstrap.
3. Reimport the updated lesson notebook into Workspace: updating the ZIP does not replace already imported notebooks.
4. Run lab 00 with live=false, then resume your lesson using MASTER_GUIDE and its RUNBOOK.
5. No new secrets are required for these fixes. New output runs still get unique folders.
6. If you customized the SQLite refund example to persist requests, old records without a tenant now fail closed.
   Use a new teaching ledger/request ID and re-run the synthetic example. Do not alter real business records to bypass authorization.
7. Rebuild your app deployment ZIP if you deployed the previous API so the authorization fix reaches that application.

## Still requires your environment

No Azure credentials or Databricks workspace were used. Live SDK imports/calls, real secret scopes/volumes,
MCP protocol execution, Speech/ODBC native dependencies, Bicep compilation, Docker build and hosted CI/CD
remain unverified. The dependency-resolution retry result is saved in review_evidence/dependency_check.json.
See [VALIDATION](VALIDATION.md) for exact scope and the one-lesson-at-a-time live acceptance gate.

The official AI-103 study guide was rechecked on 23 October 2026 and still identifies the April 16, 2026
skills outline. Existing objective mappings remain the course reference; portal exercises and preview
prerequisites must be completed as described, not counted as complete from offline output alone.
Source: https://learn.microsoft.com/en-us/credentials/certifications/resources/study-guides/ai-103

---

## Historical review: edition 1.1

The following records the earlier corrections. Current validation counts are those above and in VALIDATION.

### Earlier pass — 22 October 2026

The saved ZIP was retrieved and reviewed as the source of this edition. The original supplied
handbook is preserved unchanged. The review checked project inventory, Python source, notebook
launchers, configuration branches, service contracts, documentation, setup dependencies and
coverage. This report distinguishes corrected local behavior from unverified cloud integration.

## Material corrections

| Finding | Correction |
|---|---|
| Old video jobs API and invalid reference dimensions | Sora 2 v1 submit/resume/remix flow; correctly sized synthetic reference; persisted job ID |
| Notebook environment could retain settings/credentials | One shared runner resets config, loads only branch secrets and clears credentials afterward |
| Keyless switch removed keys required by image/evaluator paths | Those adapters explicitly reject unsupported auth selection; video supports the implemented Entra path |
| Missing live variants failed late | Dropdowns and early validation; exact variant-specific run cards |
| Outputs could overwrite or look like an earlier successful run | Unique run folders, run_status.json and recorded package versions |
| Nested output paths could fail | Parent directory creation and output path containment |
| MCP subprocess could lose the source package path | Explicit server environment PYTHONPATH |
| Native Speech wrote directly to volume paths | Driver-local WAV staging followed by completed-file copy |
| Retrieval happened before input checks in some compositions | RAG now checks/redacts before invoking a supplied retriever |
| Order authorization checked only user | Tenant and owner are both enforced |
| Approval state check and update could race | SQLite immediate transaction around local transition; boolean decisions validated |
| Non-object API JSON produced an upstream-style error | Invalid input now receives 400 |
| “Agentic retrieval” required learner wiring | Implemented Azure Search tool backend variant |
| Some objectives had only suggested experiments | Added generation controls, domain extraction, visual evidence, multimodal ingestion and app-output evaluation |
| Advanced capstones required code assembly | Implemented speech input/reply and Fabric analytical-read variants |
| Portal-only/hosted work was scattered | Separate azure_execution directory with execution locations and step sequences |
| Historical pro-mode wording could send learners to retired API | Current migration explanation and separate agentic-analyzer exercise |
| Dense one-line suites were hard to learn from | Expanded code, added function docstrings, source comments, code map and per-lesson RUNBOOK files |

## How to use the reviewed edition

1. Read START_HERE.md and docs/BEGINNER_GUIDE.md.
2. Upload this ZIP to the Databricks volume, replacing the older course ZIP only after saving
   any personal experiments separately. Import the reviewed bootstrap notebook and run it.
3. Import the reviewed notebook for the lesson you are doing. Old imported notebooks are not
   automatically updated when the ZIP changes; reimport/replace them through Workspace.
4. Open that lesson's RUNBOOK.md. It is the execution authority for widgets, secrets, variants
   and prerequisites. README adds concept explanations/experiments; instructor notes help reflection.
5. Use the unique result folder printed by the runner. Do not infer success from a previous run.

## What this review does not certify

There is no honest guarantee of zero failures across subscriptions, future SDK releases,
private-network configurations, model access/retirement, quotas and Databricks runtimes.
No Azure credentials or real Databricks workspace were available for live validation here.
Package-distribution access was unavailable, so SDK dependency installation could not be verified.
Bicep compilation, actual deployments, GitHub Actions, native Speech/ODBC and real MCP transport
must be validated in the documented environment. VALIDATION.md records the exact completed checks.

The course uses industry patterns in a small teaching implementation. It is not a security-audited
production system. Synthetic identities, local SQLite, tiny evaluation sets and the hosted demo
Bearer token are explicitly scoped simplifications. Keep them out of real customer workflows.
The source handbook's historical wording is not edited; current corrections are in the course docs.
