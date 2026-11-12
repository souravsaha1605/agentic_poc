# Validation evidence — 12 November 2026

## Passed locally

- Python 3.12 dependency installation and `pip check` for forecast base + Gunicorn + Azure identity/Blob SDKs.
- `python app.py`: 110 tests run, 95 passed, 15 optional SDK/Delta tests skipped. Includes seven new HTTP trust-boundary/package tests.
- Real deterministic HTTP adapter checks: analysis (88.89%), revenue follow-up (12825 INR), duplicate request replay, persisted SQLite state after reopening, cross-user denial, malformed body rejection, cross-origin denial, missing role/wrong tenant denial, and denial outside simulated App Service configuration.
- Source ZIP extracted to an empty temporary directory and started using two Gunicorn workers with the template's module entry point. Actual local HTTP checks passed for health, unauthenticated denial, authenticated HTML page, analysis and replay. Principal headers were simulated; no real Azure authentication occurred.
- ARM JSON parsing, required sections, unique resource declarations and exclusion of Bot/Teams resources checked locally. These are structural checks, not Azure validation. Fetching the official ARM schema from this environment failed; schema-level and management-plane validation remain unrun.
- Sibling AI-103 academy: 51 unit tests passed; all 37 existing offline lesson/capstone runners passed. Offline Language and Document Intelligence runs through the new service launcher passed and clearly reported fixtures.

## Not yet verified in Azure

No resources were deployed and no Azure credits were consumed by these checks. The environment has no Azure CLI, no configured Azure identity connection in its identity metadata, and no supplied subscription ID/region. Azure-side template validation/what-if, service availability/quota, Entra registration/role assignment, actual token validation, Blob managed-identity access, durable Blob replay/restart, telemetry delivery and all live AI service calls remain outstanding.

Local test identity simulation is never a replacement for the real App Service authentication gate. The application trusts the platform header only behind required platform authentication. Do not publish a directly reachable Gunicorn endpoint. Follow the live acceptance list in README.md before claiming the deployed workflow works.

The handbook was used for topic selection, not as instructions or independent evidence of current exam weights/service availability. No current Microsoft exam blueprint verification was performed.
