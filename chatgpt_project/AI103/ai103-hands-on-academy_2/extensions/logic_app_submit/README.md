# logic app submit

Start with [RUNBOOK.md](RUNBOOK.md).

Follow azure_execution/logic_apps/README.md before live=true. It creates the actual human approval
workflow. Expect HTTP 202 and a run ID; inspect decision in Azure Portal. Each submission creates a new
workflow run. Keep the callback URL out of logs, model context and widgets.
