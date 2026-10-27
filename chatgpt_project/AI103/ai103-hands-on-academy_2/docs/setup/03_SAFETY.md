# Configure guardrails and Content Safety

1. In Azure Portal create an **Azure AI Content Safety** resource in a supported region.
   Open **Keys and Endpoint**. Store SAFETY_ENDPOINT and SAFETY_KEY in the learning secret
   scope. Use the resource's root endpoint, without an operation path.
2. Open the Content Safety playground/Foundry tools surface and test benign text. Review the
   hate, sexual, violence and self-harm categories. Lab 04 uses FourSeverityLevels (0/2/4/6)
   and a sample block threshold of 4. EightSeverityLevels uses 0–7; do not mix thresholds.
3. Run lab 04 live. It checks input before a model call and output before returning text.
   A moderation service error aborts this sample. Decide a documented degraded-mode policy
   for a real application instead of silently allowing unscanned content.
4. In Foundry, locate **Guardrails and controls** or your model deployment's content-filter
   settings. Create a named lab configuration. Configure input/output categories and supported
   prompt-attack controls. Review whether each control BLOCKS or only ANNOTATES.
5. Attach the configuration to the intended model deployment or agent, save it, and verify the
   assignment on that deployment. Merely creating a policy does not apply it everywhere.
   Capture the policy name/version and a blocked/allowed test. Controls vary by model/service.
6. Run lab 05 with Prompt Shields to inspect direct and document attack detection. Then test
   the same attack through the actual RAG path, not just the standalone detection endpoint.
7. For visual input, lab 24 calls image moderation before vision. Embedded text can still carry
   instructions. Consider OCR/text screening, source restrictions and isolated untrusted-content
   processing; no detector eliminates the need for tool authorization.
8. Extend `data/attacks.json` with benign controls and scoped attacks. Use Foundry's automated
   red-teaming evaluation surface where available; select your own deployed target, risk categories
   and run budget, then review successful attacks and regressions. This course's four-case harness
   is custom testing, not a claim that the full PyRIT package was executed.

Never treat an LLM's self-declared confidence as a moderation or authorization decision.
For each failure record the boundary crossed, the actual effect, the fix and the regression test.

References:
- https://learn.microsoft.com/azure/foundry/guardrails/how-to-create-guardrails
- https://learn.microsoft.com/en-us/azure/ai-services/content-safety/quickstart-jailbreak
- https://learn.microsoft.com/en-us/rest/api/contentsafety/text-operations/shield-prompt?view=rest-contentsafety-2024-09-01
