# Build an asynchronous approval workflow

The local ledger demonstrates a complete request/decision/execution state machine with no
money movement. The cloud exercise adds workflow infrastructure. Use synthetic requests only.

1. Run lab 20 locally. Read Ledger.create, decide and execute in domain.py. The example
   threshold is 1000 INR; values are stored as integer paise. This is a learning policy, not
   a universal financial rule. Eligibility is checked before the request is accepted.
2. In Azure Portal create a Logic App in your learning group. Choose a stateful workflow
   appropriate to your plan. In the designer add **When an HTTP request is received** and use
   `extensions/approvals/request.schema.json` for the request shape.
3. Add durable storage for request ID, immutable payload/hash, owner, status=pending, expiry,
   and decision metadata. A Cosmos container is a suitable learning choice. Check whether a
   request ID already exists before inserting; reject conflicting payloads.
4. Return **202 Accepted** with request ID/status location after persistence. The caller should
   stop waiting on this HTTP connection. In a separate workflow triggered by new pending records,
   use an approval connector available to your tenant, choose the specific authorized learning
   approver, and include action, amount/currency, policy evidence and expiry.
5. Configure a rejection path and a timeout/escalation path. Persist approver identity and
   decision time from the authenticated approval mechanism. An arbitrary JSON `approver` field
   sent by the model is not evidence of authentication.
6. Add a status read endpoint/workflow that checks the request owner's authorization. On
   approval, a backend worker rechecks expiry and payload binding before the simulated action.
   Use the request ID as an idempotency key at the action boundary. Store a completed result.
7. Test approved, rejected, expired, repeated submission, altered amount and unauthorized user.
   Record run-history IDs, not callback URLs. Treat generated callback URLs containing signatures
   as secrets; do not paste them into model context or logs. Prefer authenticated endpoints with
   managed identity/Entra or your approved API gateway.
8. Return to Databricks: submit a synthetic request through an approved authenticated client,
   store the returned ID and poll status in separate invocations. Do not hold an executor or
   notebook HTTP call open for hours. The code in this course does not pretend an external
   approval was completed; cloud connector setup and authorized approvers are your environment.

The workflow design and JSON schemas are provided; connector bindings are configured in your
portal because tenant-specific connections and recipients cannot be pre-created in this ZIP.
When productionizing, add optimistic concurrency/ETags, an outbox/worker pattern and recovery for
"external action succeeded, local commit failed". SQLite alone cannot make a remote payment atomic.

Reference: https://learn.microsoft.com/en-us/azure/logic-apps/logic-apps-http-endpoint
