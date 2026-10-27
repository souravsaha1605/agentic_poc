# generation controls

Start with [RUNBOOK.md](RUNBOOK.md).

Use the lab 02 chat deployment. Start variant=default, then temperature with
config_json={"GENERATION_TEMPERATURE":"0.2","GENERATION_MAX_TOKENS":"256"}; repeat at 0.8.
Choose a model that supports temperature. If it rejects that parameter, use default and compare
system instructions instead; do not suppress the error. For code, use variant=code and question
"Show a Python function that sums a list". Read generated code as text; never execute it automatically.
Expected: settings, answer and usage. Explain randomness versus a factual correctness guarantee.
