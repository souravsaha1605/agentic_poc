# Purpose: Adapt language-analysis service operations
# Learn: Inspect supported analysis tasks and how service results become application evidence.
# Run: Imported by lesson code; do not run this file directly. Follow the importing lesson in MASTER_GUIDE.md.

from .common import env

def preprocess(text):
    """Detect language, redact PII, then extract limited support-message signals."""
    from azure.ai.textanalytics import TextAnalyticsClient
    from azure.core.credentials import AzureKeyCredential
    client=TextAnalyticsClient(env('LANGUAGE_ENDPOINT'),AzureKeyCredential(env('LANGUAGE_KEY')))
    def one(results):
        result=results[0]
        if result.is_error:
            raise RuntimeError('Language service document error; inspect language support/input size')
        return result
    lang=one(client.detect_language([text])).primary_language.iso6391_name
    pii=one(client.recognize_pii_entities([text],language=lang))
    clean=pii.redacted_text
    entities=one(client.recognize_entities([clean],language=lang))
    phrases=one(client.extract_key_phrases([clean],language=lang))
    sentiment=one(client.analyze_sentiment([clean],language=lang))
    return {'language':lang,'redacted':clean,'pii_categories':[e.category for e in pii.entities],
            'entities':[{'category':e.category,'confidence':e.confidence_score} for e in entities.entities],
            'key_phrases':phrases.key_phrases,'sentiment':sentiment.sentiment}
