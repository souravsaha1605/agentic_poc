# Capstone 02 — Receipt and refund workflow

**Reviewed execution instructions:** start with [RUNBOOK.md](RUNBOOK.md). It lists exact widgets, secrets, variants and failure recovery.

Complete labs 12–15,20,25 first. This project composes the functions you have already inspected.
Keep the synthetic dataset and trusted sample identities until you implement a real authentication boundary.

## Execute in Databricks

1. Import `databricks/capstones/02_receipt_and_refund_workflow.py` as a source notebook.
2. Set the bootstrap project_root and your persistent output_root. Run with live=false.
3. Read run.py and follow each imported function. Draw the data/permission boundary.
4. Finish the component service setup, load only the named secrets, then use live=true.
5. Compare the result and failure behavior with the local run; record cloud status separately.

Local alternative:

```bash
python capstones/02_receipt_and_refund_workflow/run.py
python capstones/02_receipt_and_refund_workflow/run.py --live
```

## Build and inspect

The receipt is analyzed independently of order eligibility. Review its extracted amount/currency against the trusted order. The default demonstration rejects the request; variant=approve invokes a synthetic supervisor decision to exercise the happy path. This is not a real authenticated human approval. Use the Logic Apps guide to replace that fixture with durable, authenticated approval state.

## Acceptance checks

- No execution while pending or after rejection.
- Alice cannot read Bob's order.
- Duplicate execution produces one simulated effect.
- Receipt fields alone never grant authorization.
- Live extraction still requires human field review.

## Explain it in an interview

Describe the requirement, why each service is present, the first failure you observed, how the
control is enforced in code, and the evidence that the fix worked. Identify what is local demo
state and what is actually deployed. Explain a lower-complexity alternative and its trade-off.

## Further production work

Add validated user identity, service-level authorization, concurrency-safe durable state,
realistic evaluation data, retention and monitoring before using real customers. No capstone
moves money or sends messages. Review docs/CLEANUP.md when finished.
