# Purpose: Analyze language and remove PII
# Learn: Inspect entities, sentiment and summaries while minimizing sensitive text sent downstream.
# Run: Import databricks/labs/06_language_and_pii_preprocessing.py as a Databricks source notebook. Start live=false; read labs/06_language_and_pii_preprocessing/RUNBOOK.md.

"""Lab 06: Language and PII preprocessing. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import args,save,fixture
from academy.language import preprocess
opts=args('Analyze a synthetic support message')
text='My name is Alex Example. Contact alex@example.test. My kettle is broken and I am unhappy.'
if opts.question != 'What is the return policy?':
    text = opts.question
save('06_language.json',preprocess(text) if opts.live else fixture('language'))
