# AI-103 hands-on academy

Open [MASTER_GUIDE.md](MASTER_GUIDE.md) for the ordered execution route, every code file's purpose, and the project glossary.

**Reviewed edition 1.2:** first read [the beginner guide](docs/BEGINNER_GUIDE.md), then use each lesson's RUNBOOK.md. See [review findings](REVIEW_REPORT.md), [configuration](docs/CONFIGURATION.md), and [Azure-only execution](azure_execution/README.md).

Build one skill at a time, then combine the skills into a working retail support system.
This course uses your supplied interview/certification handbook and the AI-103 blueprint
checked on 23 October 2026. Azure Databricks is the primary execution environment;
a local Python environment is also supported.

## Your first session

1. Read [Databricks setup](docs/setup/DATABRICKS.md). Create or select a learning workspace
   and a writable Unity Catalog volume; start with local-only labs.
2. Upload this ZIP to the volume. Import [the bootstrap notebook](databricks/00_BOOTSTRAP.py)
   into your Databricks Workspace as a Python source notebook, set its widgets, and run it.
3. Import only the lab 00 notebook from `databricks/labs/`, then read
   [lab 00](labs/00_environment_and_project_tour/README.md) and execute its cells.
4. Continue with lab 01. Provision only its prerequisites using the linked portal guide.
5. Stop at each checkpoint. Change one input or setting, deliberately trigger one failure,
   and explain the result before advancing.

You do not need to install every SDK or provision every service on day one. The numbered
notebooks are small launchers for readable Python files; there is no giant notebook.
The `.py` launchers use Databricks source-notebook cell markers and import through the UI.

## Choose a pace

- **First two days:** labs 00–05, then 08–12 if time permits. Establish a secure model/RAG/tool slice.
- **Steady course:** one or two labs per session, about 3–5 weeks with Azure provisioning and experiments.
- **Experienced engineer:** run the local checks, inspect the coverage map, then focus on cloud labs
  and capstones. Existing PySpark experience helps with data ingestion, but model API calls here run
  on the driver; do not accidentally broadcast credentials or create a request storm from executors.

The complete course is broader than a two-day sprint. A full end-to-end cloud implementation
requires your subscription, roles, quotas and model access; some advanced services are gated.

## Folder guide

| Folder | Purpose |
|---|---|
| `labs/00...32` | One concept group per folder: explanation, runnable code, exercises, answers |
| `databricks/` | Bootstrap and one source notebook per lab/capstone |
| `src/academy/` | Shared configuration, Azure adapters and deterministic business logic |
| `capstones/` | Four runnable projects that combine concepts |
| `docs/setup/` | Azure Portal, Databricks, identity, networking and service walkthroughs |
| `data/` | Synthetic policies, orders, images, receipt and explicitly labeled fixtures |
| `evals/` | Small starting benchmark; extend with held-out and adversarial cases |
| `tests/` | Security, state, failure and regression checks |
| `infra/` | Bicep and explicit deployment workflow |
| `requirements/` | Separate dependency sets; install only the current lesson |
| `SOURCE_HANDBOOK.docx` | Unmodified source document supplied by you |

## What “done” means

Track four different accomplishments: **explained**, **local verified**, **Azure verified**,
and **failure tested**. A fixture result does not earn Azure verified. Use
[PROGRESS.csv](PROGRESS.csv) to record dates, evidence paths and remaining questions.

Every lab includes: purpose → prerequisites → setup → run → inspect → experiment → explain.
See [coverage](docs/COVERAGE.md), [troubleshooting](docs/TROUBLESHOOTING.md),
[validation status](VALIDATION.md), and [interview practice](docs/INTERVIEW_PRACTICE.md).

## When asking for help

Send the lab ID, Databricks runtime/Python version, local/live setting, command or widget
values excluding secrets, error class/status and the relevant sanitized traceback. Tell me
which setup step succeeded last. Never paste keys, tokens, connection strings or signed URLs.
