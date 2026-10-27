# Configuration: what you must change

You do not edit shared Python files to enter credentials. In Databricks create the named Key Vault
secrets, then set widgets. `.env.example` is only for the optional terminal/VM route.

| Widget | Required value | Example / meaning |
|---|---|---|
| project_root | Bootstrap's printed local folder | /local_disk0/tmp/ai103-course/ai103-hands-on-academy |
| output_root | Your writable UC volume directory | /Volumes/training/default/ai103_lab/ai103-output |
| secret_scope | Existing scope backed by your learning vault | ai103-lab |
| live | false first; true only after setup | true may call paid Azure APIs; MCP true starts real local protocol |
| variant | Select from notebook dropdown | See each RUNBOOK; unknown variants are rejected |
| question | Synthetic question | Some fixed-fixture lessons explain in source when they use a fixed input |
| input_file | Blank unless lesson needs your file | Full /Volumes/... path; staged temporarily to driver |
| config_json | Non-secret JSON object | {"SEARCH_INDEX":"ai103-media-v1"} |

Allowed overrides are listed in `src/academy/notebook.py` DEFAULTS/OPTIONAL. Common examples:

- MODEL_AUTH: key or entra. Lab 23 evaluator and lab 28 image adapter require key.
- SEARCH_INDEX: default ai103-policies-v1; choose ai103-media-v1 for multimodal ingestion.
- CU_ANALYZER/CU_API_VERSION: GA default prebuilt-invoice / 2025-11-01; preview extension has its own values.
- DOCUMENT_MODEL_ID: custom trained Document Intelligence model ID.
- SPEECH_LANGUAGE/SPEECH_VOICE: supported recognition language/voice.
- COSMOS_DATABASE/COSMOS_CONTAINER: default ai103 / memory; vector extension uses ai103-vectors.
- VIDEO_ID/VIDEO_SIZE/VIDEO_SECONDS: resume/remix ID and supported Sora 2 controls.
- FOUNDRY_AGENT_NAME: dedicated learning agent name; use a personal suffix in shared resources.
- GENERATION_TEMPERATURE/GENERATION_MAX_TOKENS: generation-controls extension only.

All values in config_json are quoted strings. Every run resets these settings to defaults before
applying your overrides; a prior lesson's analyzer or identity cannot leak into the next run.
Secrets are loaded only for live branches and removed from the process environment afterward.
Never pass secrets to Spark workers. The secret map includes capstones/extensions and branch additions.

Each run writes output_root/lesson-name/UTC-timestamp-randomsuffix/. This prevents overwrite and
makes failures visible through run_status.json. environment.json records installed packages.
Keep only synthetic data until you add your organization's identity, retention and access controls.

## Edition 1.2 execution notes

The launcher restores its prior ACADEMY_OUTPUT_DIR and ACADEMY_SKIP_DOTENV settings when it finishes
(success or failure), while clearing loaded service credentials. Output paths require a complete
/Volumes/catalog/schema/volume path and reject traversal. Scope permissions and volume write access
are still checked by your actual workspace, not by this local path validation.
