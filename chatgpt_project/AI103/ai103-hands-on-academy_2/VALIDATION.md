# Validation — reviewed edition 1.2

Review date: 23 October 2026. Local runtime: Python 3.12.14.

| Check | Result / scope |
|---|---|
| Unit and failure-boundary tests | 51 passed; local logic and explicit provider doubles |
| Main offline lessons/capstones | 37/37 passed |
| Default Databricks launchers | 49/49 passed with mocked DBUtils and temporary local output |
| All offline entry/variant combinations | 76/76 passed; includes the 49 default cases, not 76 additional cases |
| Local HTTP transport | Real loopback server/client/shutdown executed by the offline extension |
| Bootstrap | Actual source executed with filesystem boundaries mocked; valid extraction and unsafe ZIP rejection checked |
| Deployment ZIP | Built and extracted; isolated WSGI request returned 200 and expected fixture answer; not a deployed HTTP service |
| Code teaching headers | 132/132 files contain Purpose, Learn and Run; Python header insertion preserved ASTs |
| Static audit | 127 Python files plus JSON, optional PyYAML workflow syntax and local Markdown targets checked |
| Core dependency resolution | See dependency_check.json; no successful Azure SDK runtime validation |
| Azure service calls | Not performed |
| Real Databricks / scopes / Unity Catalog | Not performed; local mocks do not establish workspace compatibility |
| MCP protocol / native Speech / ODBC | Not performed; packages/native runtime unavailable here |
| Bicep compilation, Docker, Azure deployment | Not performed; required tools and live environment unavailable |
| Hosted CI/CD | Source reviewed; not executed on GitHub |
| Original handbook | Byte-identical to the input ZIP |
| Final archive and manifest | ZIP integrity and every listed file hash verified during packaging |

## Reproduce local checks

From the extracted project root in a Python 3.11+ terminal:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
python scripts/verify_offline.py
python scripts/verify_notebooks.py
python scripts/verify_notebooks.py --all-variants
python scripts/audit_project.py
python scripts/package_deployment.py
```

No Azure SDK install is needed for those offline checks. PyYAML is optional for workflow syntax checking;
if absent, the audit reports it as unchecked. The dependency dry-run does not prove installation or SDK
compatibility. The notebook verifier bypasses the actual package-install and restart behavior by using
live=false and a mock workspace interface.

## Your live acceptance gate

For one lesson at a time: complete its setup → install its dependencies → restart Python → run live →
inspect the actual service output/run history → trigger one expected failure → record versions/evidence →
clean up. Use RUNBOOK.md and PROGRESS.csv. Only then mark Azure verified.

Keep model/API/analyzer/index/SDK/runtime versions with the evidence. Preview availability, quotas,
roles, network policies and retirement can block execution. Mark those prerequisites blocked rather
than labeling a fixture as a live success. These checks cannot establish general safety, accuracy or
exam readiness. The small application demonstrates industry practices but still requires production
identity, durable state, operational ownership and broader tests before serving real customers.
