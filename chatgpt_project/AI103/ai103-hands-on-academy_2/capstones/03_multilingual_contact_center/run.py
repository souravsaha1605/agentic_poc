# Purpose: Build a multilingual contact-center flow
# Learn: Follow PII handling, translation, RAG and output safety; add speech only after the text path works.
# Run: Import databricks/capstones/03_multilingual_contact_center.py as a Databricks source notebook. Start live=false; read capstones/03_multilingual_contact_center/RUNBOOK.md.

"""Language/PII -> translation -> grounded answer -> translated output safety."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import args,save
from academy.language import preprocess
from academy.cloud import translate,safety
from academy.search import search
from academy.flows import rag
opts=args('Multilingual support capstone')
source='मेरा ईमेल alex@example.test है। वापसी की नीति क्या है?'
if opts.question != 'What is the return policy?':
    source = opts.question
if opts.live and opts.variant == 'speech':
    if opts.file is None:
        raise ValueError('Speech variant requires input_file: a short WAV. Start with lab 27 sample.wav.')
    from academy.speech import transcribe
    source = transcribe(opts.file)
if opts.live:
    cleaned=preprocess(source)
    language=cleaned['language']
    query=translate(cleaned['redacted'],'en',language) if language!='en' else cleaned['redacted']
    answer=rag(query,True,retriever=search)
    final=translate(answer['answer'],language,'en') if language!='en' else answer['answer']
    if safety(final)['blocked']:
        final='Response needs human review.'
    result={'language':language,'pii_categories':cleaned['pii_categories'],'sentiment':cleaned['sentiment'],
            'sources':answer['sources'],'answer':final,'human_priority':cleaned['sentiment']=='negative'}
else:
    result={'mode':'local workflow fixture','stages':['detect language','redact PII','translate query','retrieve','answer','translate back','check output'],
            'answer':rag('return policy'),'human_priority':'sentiment can prioritize but cannot authorize'}
if opts.live and opts.variant == 'speech':
    from academy.speech import synthesize
    result['reply_audio'] = synthesize(result['answer'])
save('capstone03.json',result)
