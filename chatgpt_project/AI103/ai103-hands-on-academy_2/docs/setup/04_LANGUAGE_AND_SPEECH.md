# Language Translator and Speech setup

## Language and PII

In Azure Portal search **Language** and create a resource for the learning group. Choose a
supported region and tier, then copy its root endpoint and key into LANGUAGE_ENDPOINT and
LANGUAGE_KEY. Run lab 06 on the synthetic message before adding other languages. Inspect each
operation's supported languages and document limits if one stage fails. The sample checks
per-document error objects, not just HTTP status. Outputs contain synthetic data only.

## Translator

Create a Translator resource. Store TRANSLATOR_KEY and TRANSLATOR_REGION; the introductory
script uses the global API endpoint by default. For regional/custom/private endpoints use the
appropriate supported endpoint and route from the service documentation rather than blindly
reusing the global path. Run lab 07, compare the Hindi translation and back-translation, then
try Bengali. Check numbers, units, product IDs and conditions manually.

## Speech

Create a Speech resource in Azure Portal; record key and region as SPEECH_KEY/SPEECH_REGION.
Use Speech Studio to confirm synthesis and recognition work for your chosen language/voice.
Install requirements/speech.txt in the lesson notebook. A supported classic driver with
native SDK dependencies is required. The lab creates a WAV using SSML, then recognizes it.
`--variant translate` (Databricks variant=translate) runs speech translation to Hindi.
For your own input use a short supported WAV and the input_file widget; the launcher stages it
on the driver. Single-utterance recognition is deliberately small; use continuous/batch APIs
for longer recordings.

Inspect detailed recognition output when available. A canceled/no-match result is not a valid
empty transcript. Compare real audio to synthetic TTS; only real representative recordings
can establish recognition accuracy. Store consented/synthetic recordings and a retention policy.

## Custom Speech exercise

Open Speech Studio → Custom Speech → new project. Choose language and matching resource.
Upload a small consented dataset and reference transcripts; keep held-out recordings separate.
Run a baseline recognition test first. Train only when the measured errors justify it, compare
word error rate on the held-out set, and deploy the custom model to an endpoint if available.
Set SPEECH_CUSTOM_ENDPOINT_ID and use variant=custom. Record extra hosting/training charges
and delete the endpoint after the exercise. Some languages/training options have limited support.

For audio reasoning, use lab 26 with an audio-capable Content Understanding analyzer to inspect
speaker/segment evidence, then supply that evidence to the RAG flow. Transcription alone may
lose nonverbal context; record that limitation.

References:
- https://learn.microsoft.com/en-us/azure/ai-services/language-service/
- https://learn.microsoft.com/en-us/azure/ai-services/translator/text-translation/quickstart/rest-api
- https://learn.microsoft.com/en-us/azure/ai-services/speech-service/how-to-translate-speech
