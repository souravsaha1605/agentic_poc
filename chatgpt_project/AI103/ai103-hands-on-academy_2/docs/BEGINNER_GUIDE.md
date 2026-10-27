# Before your first agent

You know Python and Databricks; the new part is how probabilistic model outputs interact with
ordinary software. Learn those boundaries in small steps.

An **LLM** predicts output from supplied messages. A **prompt** is the instructions and input you
send. A **deployment** is the Azure endpoint configuration serving a particular model/version.
An **agent** repeats a bounded loop: ask a model → receive a tool request → validate and run the
permitted function → give the result back → stop. The model proposes; Python enforces permissions.

**RAG** retrieves evidence before answering. An **embedding** is a numerical vector used for
similarity; it is not a database lookup or a truth score. A **tool** is a callable interface such as
order_status. Its JSON schema describes arguments, while backend code enforces ownership.
**Memory** is state the application stores and supplies on later calls. **MCP** is a protocol for
exposing/discovering tools, not an authorization system. **Evaluation** checks observed outputs
against expected behavior; an LLM judge can be wrong too.

## Your first successful session

1. Extract the ZIP on Windows (right-click → Extract All). Keep its top-level folder intact.
   Open Markdown in a reader such as VS Code, or a text editor if unavailable.
2. Read START_HERE, then docs/setup/DATABRICKS. You need a workspace, usable compute and writable
   UC volume. No Azure AI service key is needed for the first offline lesson.
3. Upload the ZIP to the volume. Import only databricks/00_BOOTSTRAP.py and lab 00, not the whole source package
   as a single notebook. The source package stays inside the extracted driver folder.
4. A notebook **cell** is one executable block. Run from top to bottom. After live package installs,
   restart Python once and continue to the final cell. A Python restart differs from a compute restart.
5. Inspect the JSON report. Locate run_status.json in the printed folder. This is your evidence.
6. Lab 01 introduces identity. Lab 02 makes the first model call. Do not provision image/video,
   Fabric or Redis yet. Complete one working path before adding another service.

## Read code in this order

Open the lab run.py first. `opts=args(...)` reads widget-generated command arguments. The `if opts.live`
branch makes real calls; the `else` branch demonstrates a fixture or local rule. `save(...)` records
what happened. Follow only the shared function imported by that lesson; you need not read all src at once.
The launcher's runpy call executes the file as if it were a command-line program on the driver.

## Experiments that build understanding

For each lesson: run baseline → change one input → predict output → run → explain the difference.
Then deliberately use a harmless invalid input or denied action. A correctly blocked action is a
successful control test. A wrong endpoint is a configuration problem, not a model-quality result.
Record both in PROGRESS.csv. Never turn off a control just to make an experiment turn green.

## Industry practices versus this teaching implementation

The layout separates service adapters, business rules, configuration, tests and orchestration.
It demonstrates narrow tools, input validation, tenant filters, bounded calls, safe retries,
idempotency, observability and versioned evidence. SQLite, synthetic identities, small datasets,
shared demo API token and unpinned dependency ranges are deliberate learning simplifications.
Before real customers, implement validated end-user identity, managed workload credentials,
concurrency-safe durable state, secret rotation, networking, representative evaluation, deployment
approvals and operational ownership. This course is a reference to learn from, not an audited
production platform or a guarantee of passing an exam.
