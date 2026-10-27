# Purpose: Screen model input and output
# Learn: Apply Content Safety checks on both sides of generation and interpret blocked results.
# Run: Import databricks/labs/04_content_safety_input_and_output.py as a Databricks source notebook. Start live=false; read labs/04_content_safety_input_and_output/RUNBOOK.md.

"""Lab 04: Content Safety input and output. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import args,save
from academy.cloud import safety,chat
opts=args('Apply independent input and output safety gates')
if opts.live:
    inp=safety(opts.question)
    if inp['blocked']:
        result={'stage':'input','allowed':False,'analysis':inp}
    else:
        text=chat([{'role':'user','content':opts.question}]).choices[0].message.content or ''
        out=safety(text)
        result={'stage':'output','allowed':not out['blocked'],'answer':text if not out['blocked'] else 'Response withheld.', 'analysis':out}
else:
    result={'mode':'policy calculation with synthetic scores','scale':[0,2,4,6],
            'decisions':[{'severity':s,'blocked':s>=4} for s in (0,2,4,6)]}
save('04_safety.json',result)
