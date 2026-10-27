# Capstone 04 — Enterprise research assistant

**Reviewed execution instructions:** start with [RUNBOOK.md](RUNBOOK.md). It lists exact widgets, secrets, variants and failure recovery.

Complete labs 09,17–19,22–23,30 first. This project composes the functions you have already inspected.
Keep the synthetic dataset and trusted sample identities until you implement a real authentication boundary.

## Execute in Databricks

1. Import `databricks/capstones/04_enterprise_research_assistant.py` as a source notebook.
2. Set the bootstrap project_root and your persistent output_root. Run with live=false.
3. Read run.py and follow each imported function. Draw the data/permission boundary.
4. Finish the component service setup, load only the named secrets, then use live=true.
5. Compare the result and failure behavior with the local run; record cloud status separately.

Local alternative:

```bash
python capstones/04_enterprise_research_assistant/run.py
python capstones/04_enterprise_research_assistant/run.py --live
```

## Build and inspect

Compare source freshness before joining evidence. Use variant=fabric for the implemented parameterized Fabric read after lab 30 setup. A current-inventory source remains a separately designed production extension. Keep those identities and timestamps separate. This capstone uses application-orchestrated roles; lab 16 covers the distinct managed-agent service.

## Acceptance checks

- Independent reads overlap.
- The answer names historical versus current evidence.
- The reviewer flags unsupported claims without an unbounded loop.
- Cross-tenant data remains excluded.
- Actual cloud-source status is recorded rather than inferred from live model output.

## Explain it in an interview

Describe the requirement, why each service is present, the first failure you observed, how the
control is enforced in code, and the evidence that the fix worked. Identify what is local demo
state and what is actually deployed. Explain a lower-complexity alternative and its trade-off.

## Further production work

Add validated user identity, service-level authorization, concurrency-safe durable state,
realistic evaluation data, retention and monitoring before using real customers. No capstone
moves money or sends messages. Review docs/CLEANUP.md when finished.

## Complete Fabric read path (implemented)

After live lab 30 works, choose variant=fabric and live=true. Add fabric-sql-connection-string to
the scope. The notebook installs requirements/enterprise.txt; the native ODBC Driver 18 is still
required. The two independent reads now use Fabric and Azure Search. The result includes retrieval
time separately from the data's business period. Default mode retains the labeled sales fixture.
If ODBC cannot run on your compute use azure_execution/fabric or the Azure VM fallback; do not
report the default fixture as a real Fabric integration.
