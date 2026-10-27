# Execute a real human approval in Azure

This beginner workflow exercises a real approval connector and a durable Logic App run.
It does **not** implement a production refund ledger, user-facing status API or payment.
Lab 20 separately tests authorization, expiry and idempotency in deterministic code.
Complete both exercises; do not confuse an email approval with payment execution.

## Prerequisites

Use a dedicated learning Logic App and a Microsoft 365 account that can use the Office 365
Outlook connector. You need an approver you are authorized to contact; use your own mailbox
for this learning exercise. If your tenant blocks the connector, mark this integration blocked
and use the local state-machine tests. Do not substitute a model-generated approval.

## Build in Azure Portal

1. Create **Logic App (Consumption)** in the learning resource group. Open its designer.
2. Add trigger **When an HTTP request is received**, method POST. Paste
   `extensions/approvals/request.schema.json` into the request schema field.
3. Add **Response** with status code 202. Set body to the object below. In the Expression editor
   use `workflow().run.name` for request_id. Place this response BEFORE the slow approval step.

```json
{"request_id":"<workflow().run.name expression>","state":"pending","review_location":"Azure Portal: this workflow run history"}
```

4. Add Office 365 Outlook **Send approval email**. Sign in through the connector, choose your
   approved learning recipient, set options `Approve, Reject`, and subject `AI103 synthetic approval`.
   Include the trigger body request_id/order_id/amount/currency fields available from your schema,
   plus the text: `Learning only. No money will move.` Do not use prompt text as the recipient.
5. Set a bounded action timeout if supported (for example PT15M). Add a **Condition** using the
   approval action's **SelectedOption** dynamic output: equals `Approve`.
6. True branch: add **Compose** object `{"decision":"approved","effect":"simulated only"}`.
   False branch: Compose `{"decision":"rejected","effect":"none"}`.
   Add a separate Compose action configured with **Run after → timed out / failed** on the approval
   action; set `decision=expired-or-failed`, `effect=none`. Do not treat failed approvals as approved.
7. Save. Copy the trigger's generated callback URL to Key Vault secret `logic-app-trigger-url`.
   It contains a signature: treat it as a credential. Restrict the workflow to synthetic input.
8. Submit using the Databricks extension `20_logic_app_submit.py` (live=true). It sends once,
   expects 202, and saves the request ID. Do not rerun just because approval is still pending.
9. Open your email and choose Reject on the first run. In Portal → Run history inspect Response,
   connector output and rejection Compose. Repeat once with Approve; verify no payment action exists.
10. Let a third request expire and inspect the timeout branch. Save run IDs, not callback URLs.

## What to add before a real system

The Logic App run is durable but repeat submissions create distinct runs. Use the payload-bound
idempotency ledger, authenticated callers/approvers, ETag transitions, request-owner status reads,
expiry rechecks and action-boundary deduplication described in
[the advanced design](../../docs/setup/07_APPROVALS_LOGIC_APPS.md). The supplied local ledger
is a reference for these rules; it does not automatically persist this cloud workflow.

Delete the workflow and connector connection when done; remove the callback secret.
Reference: https://learn.microsoft.com/en-us/azure/connectors/connectors-create-api-office365-outlook
