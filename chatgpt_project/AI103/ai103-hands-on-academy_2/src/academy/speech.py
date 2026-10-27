# Purpose: Adapt file-based speech operations
# Learn: Follow transcription/synthesis, result checks and temporary local audio handling.
# Run: Imported by lesson code; do not run this file directly. Follow the importing lesson in MASTER_GUIDE.md.

"""Short-utterance speech adapters; stage all native output on local driver disk."""
from pathlib import Path
import shutil
import tempfile
from .common import env, OUT


def transcribe(path):
    import azure.cognitiveservices.speech as sdk
    config = sdk.SpeechConfig(subscription=env('SPEECH_KEY'), region=env('SPEECH_REGION'))
    config.speech_recognition_language = env('SPEECH_LANGUAGE','en-US')
    result = sdk.SpeechRecognizer(speech_config=config,
                                 audio_config=sdk.audio.AudioConfig(filename=str(path))).recognize_once_async().get()
    if result.reason != sdk.ResultReason.RecognizedSpeech:
        raise RuntimeError('Speech returned no usable transcript; inspect input WAV, language and resource')
    return result.text


def synthesize(text):
    import azure.cognitiveservices.speech as sdk
    config = sdk.SpeechConfig(subscription=env('SPEECH_KEY'), region=env('SPEECH_REGION'))
    config.speech_synthesis_voice_name = env('SPEECH_VOICE','en-US-AvaMultilingualNeural')
    OUT.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='ai103-reply-') as stage:
        local = Path(stage)/'reply.wav'
        result = sdk.SpeechSynthesizer(speech_config=config,
                     audio_config=sdk.audio.AudioOutputConfig(filename=str(local))).speak_text_async(text).get()
        if result.reason != sdk.ResultReason.SynthesizingAudioCompleted:
            raise RuntimeError('Speech synthesis failed; inspect supported voice/resource')
        target = OUT/'reply.wav'
        shutil.copyfile(local,target)
    return str(target)
