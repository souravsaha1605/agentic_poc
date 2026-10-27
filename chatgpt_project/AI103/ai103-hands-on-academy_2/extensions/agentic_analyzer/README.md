# agentic analyzer

Start with [RUNBOOK.md](RUNBOOK.md).

Complete GA lab 26 first and read azure_execution/content_understanding/README.md.
In CU Studio configure the current supported completion-model mapping and adequate quota.
Set config_json={"CU_API_VERSION":"2026-06-01-preview","CU_ANALYZER":"ai103-receipt-review","CU_COMPLETION_MODEL":"gpt-5.2"}
only if gpt-5.2 is a currently supported mapped model in your resource; otherwise use the supported
model family name from its settings. Run live=true variant=create once, then variant=default.
Create retains the analyzer; default analyzes receipt.png. Inspect ArithmeticReview against the
receipt. If quota/preview access is unavailable, record blocked; the historical pro API is retired.
