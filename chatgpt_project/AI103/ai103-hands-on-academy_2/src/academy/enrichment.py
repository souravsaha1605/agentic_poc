# Purpose: Validate custom Search skill records
# Learn: Separate batch errors from individual record failures and preserve record IDs.
# Run: Imported by lesson code; do not run this file directly. Follow the importing lesson in MASTER_GUIDE.md.

"""Azure Search Web API skill: preserve record IDs and report per-record errors."""
import re


def enrich(payload):
    if not isinstance(payload, dict) or not isinstance(payload.get('values'), list):
        raise ValueError('Expected a values array')
    values = []
    for item in payload['values']:
        if not isinstance(item, dict) or not isinstance(item.get('recordId'), str):
            raise ValueError('Every record requires a string recordId')
        try:
            text = item['data']['text']
            if not isinstance(text, str):
                raise ValueError('text must be a string')
            values.append({'recordId':item['recordId'], 'data':{'productCodes':sorted(set(re.findall(r'\bK\d{3}\b',text)))},
                           'errors':[], 'warnings':[]})
        except (KeyError, TypeError, ValueError):
            values.append({'recordId':item['recordId'], 'data':{},
                           'errors':[{'message':'Missing/invalid text'}], 'warnings':[]})
    return {'values':values}
