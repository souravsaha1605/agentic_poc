# Purpose: Translate a support question
# Learn: Track source/target language and understand how translation fits before and after reasoning.
# Run: Import databricks/labs/07_translation_and_multilingual_flow.py as a Databricks source notebook. Start live=false; read labs/07_translation_and_multilingual_flow/RUNBOOK.md.

"""Lab 07: Translation and multilingual flow. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import args,save,fixture
from academy.cloud import translate
opts=args('Translate a synthetic policy sentence and back-translate')
text='Unused products can be returned within 30 days with a receipt.'
if opts.question != 'What is the return policy?':
    text = opts.question
if opts.live:
    hindi=translate(text,'hi','en')
    result={'source':text,'hindi':hindi,'back_translation':translate(hindi,'en','hi')}
else:
    result=fixture('translation')
save('07_translation.json',result)
