# Purpose: Synthesize, transcribe and translate speech
# Learn: Use file audio without a microphone, inspect recognition outcomes and understand custom endpoints.
# Run: Import databricks/labs/27_speech_transcription_synthesis_translation.py as a Databricks source notebook. Start live=false; read labs/27_speech_transcription_synthesis_translation/RUNBOOK.md.

"""Lab 27: Speech transcription synthesis translation. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import args,env,save,OUT,fixture
opts=args('Synthesize speech, transcribe it, or translate speech')
if not opts.live:
    save('27_speech.json',fixture('speech'))
else:
    import azure.cognitiveservices.speech as speech
    OUT.mkdir(parents=True, exist_ok=True)
    config=speech.SpeechConfig(subscription=env('SPEECH_KEY'),region=env('SPEECH_REGION'))
    config.speech_synthesis_voice_name=env('SPEECH_VOICE','en-US-AvaMultilingualNeural')
    config.speech_recognition_language=env('SPEECH_LANGUAGE','en-US')
    if opts.variant=='custom':
        config.endpoint_id=env('SPEECH_CUSTOM_ENDPOINT_ID')
    import tempfile, shutil
    from pathlib import Path
    workspace = tempfile.TemporaryDirectory(prefix='ai103-speech-')
    path = opts.file or Path(workspace.name) / 'sample.wav'
    if opts.file is None:
        output=speech.audio.AudioOutputConfig(filename=str(path))
        synth=speech.SpeechSynthesizer(speech_config=config,audio_config=output)
        ssml='<speak version="1.0" xml:lang="en-US"><voice name="'+config.speech_synthesis_voice_name+'"><prosody rate="slow">Please check order one thousand and one.</prosody></voice></speak>'
        result=synth.speak_ssml_async(ssml).get()
        if result.reason!=speech.ResultReason.SynthesizingAudioCompleted:
            raise RuntimeError('Speech synthesis failed')
    audio=speech.audio.AudioConfig(filename=str(path))
    if opts.variant=='translate':
        cfg=speech.translation.SpeechTranslationConfig(subscription=env('SPEECH_KEY'),region=env('SPEECH_REGION'))
        cfg.speech_recognition_language=env('SPEECH_LANGUAGE','en-US')
        cfg.add_target_language('hi')
        recognizer=speech.translation.TranslationRecognizer(translation_config=cfg,audio_config=audio)
        result=recognizer.recognize_once_async().get()
        if result.reason!=speech.ResultReason.TranslatedSpeech:
            raise RuntimeError('Speech translation failed or no speech recognized')
        value={'text':result.text,'translations':dict(result.translations)}
    else:
        config.output_format=speech.OutputFormat.Detailed
        result=speech.SpeechRecognizer(speech_config=config,audio_config=audio).recognize_once_async().get()
        if result.reason!=speech.ResultReason.RecognizedSpeech:
            raise RuntimeError('No recognized speech; inspect file/language/resource')
        value={'text':result.text,'details':result.json,'audio':str(path)}
    if opts.file is None:
        shutil.copyfile(path, OUT / 'sample.wav')
        value['audio'] = str(OUT / 'sample.wav')
    workspace.cleanup()
    save('27_speech.json',value)
