# Current analyzer modes and the exam's historical “pro mode” wording

The checked exam outline still mentions pro mode. Microsoft's current documentation says the
2025-05-01-preview pro-mode API is retired. Do not spend time trying to provision it.
Learn the historical purpose, then use the supported **agentic document workflow** in
2026-06-01-preview for the migration exercise. It is not a drop-in replacement.

1. Complete lab 26 with GA 2025-11-01 first. In Content Understanding Studio select the resource,
   open Settings, configure required model mappings/deployments, and verify a prebuilt analyzer.
2. For advanced document reasoning use the separate extension `26_agentic_analyzer.py`.
   Read its RUNBOOK; configure the supported completion model mapping and capacity before creating
   the analyzer. This preview has substantial capacity requirements; check the source below before
   provisioning and stop if the required quota is unavailable.
3. The extension creates a dedicated analyzer using `config.workflow=agentic`, then uses lab 26's
   analysis path. Use only a synthetic receipt. Compare computed fields with its visible values.
4. Record workflow/API version, latency and whether the extra reasoning improved the output.
   The current preview is for documents, one input file, and does not support extract-method fields.
5. Delete the learning analyzer through Studio when finished. Model deployments may remain billable.

For image/audio/video analysis use appropriate GA analyzers in lab 26; do not force the
agentic document workflow onto those modalities. The multimodal-ingestion extension retains
segment/page/time provenance when turning analysis results into retrieval chunks.

References (checked 22 October 2026):
- https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/concepts/agentic-mode
- https://learn.microsoft.com/en-us/azure/ai-services/content-understanding/foundry-vs-content-understanding-studio
