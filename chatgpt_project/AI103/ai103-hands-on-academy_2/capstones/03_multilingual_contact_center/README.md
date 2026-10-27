# Capstone 03 — Multilingual contact center

**Reviewed execution instructions:** start with [RUNBOOK.md](RUNBOOK.md). It lists exact widgets, secrets, variants and failure recovery.

Complete labs 04,06–07,11,27 first. This project composes the functions you have already inspected.
Keep the synthetic dataset and trusted sample identities until you implement a real authentication boundary.

## Execute in Databricks

1. Import `databricks/capstones/03_multilingual_contact_center.py` as a source notebook.
2. Set the bootstrap project_root and your persistent output_root. Run with live=false.
3. Read run.py and follow each imported function. Draw the data/permission boundary.
4. Finish the component service setup, load only the named secrets, then use live=true.
5. Compare the result and failure behavior with the local run; record cloud status separately.

Local alternative:

```bash
python capstones/03_multilingual_contact_center/run.py
python capstones/03_multilingual_contact_center/run.py --live
```

## Build and inspect

Run the text path first. Inspect whether PII disappears before translation/model use. Check the returned policy conditions in both languages. Then run lab 27 with your consented audio, pass its transcript into this pipeline, and synthesize the final reply; keep recognition/translation errors visible rather than hiding them behind the model.

## Acceptance checks

- Raw email does not reach model input.
- Translation preserves 30 days and receipt condition.
- Sources survive the language transformation.
- Sentiment changes priority, not refund permissions.
- No-match speech is not accepted as a valid request.

## Explain it in an interview

Describe the requirement, why each service is present, the first failure you observed, how the
control is enforced in code, and the evidence that the fix worked. Identify what is local demo
state and what is actually deployed. Explain a lower-complexity alternative and its trade-off.

## Further production work

Add validated user identity, service-level authorization, concurrency-safe durable state,
realistic evaluation data, retention and monitoring before using real customers. No capstone
moves money or sends messages. Review docs/CLEANUP.md when finished.

## Complete speech path (implemented)

First run lab 27 and retain its sample.wav or upload your own short WAV. In this capstone select
variant=speech, live=true, input_file=/Volumes/.../sample.wav. Add speech-key and speech-region to
the scope; use config_json {"SPEECH_LANGUAGE":"en-US"} for the English sample. The notebook installs
requirements/contact_center.txt. The pipeline transcribes, removes PII, translates as needed,
retrieves/answers, checks output and synthesizes reply.wav. Use a supported multilingual voice.
This is single-utterance interaction, not a streaming voice server. The native-VM fallback applies.
