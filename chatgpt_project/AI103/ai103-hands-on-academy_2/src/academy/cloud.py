# Purpose: Adapt model, safety and translation service calls
# Learn: Inspect credential selection, HTTP contracts and bounded error handling at a service boundary.
# Run: Imported by lesson code; do not run this file directly. Follow the importing lesson in MASTER_GUIDE.md.

"""Azure boundary. Never silently fall back to fixture output on a live failure."""
import json
import time
from urllib.parse import urlsplit, quote
from .common import env

def request(method, url, *, headers=None, body=None, data=None, files=None, safe_retry=False, timeout=60):
    """Make a bounded HTTPS call; only explicitly safe operations receive status retries."""
    import requests
    if urlsplit(url).scheme != 'https':
        raise ValueError('Cloud endpoints must use HTTPS')
    for attempt in range(3 if safe_retry else 1):
        try:
            r=requests.request(method,url,headers=headers,json=body,data=data,files=files,
                               timeout=timeout,allow_redirects=False)
        except requests.RequestException:
            raise RuntimeError('Network/timeout failure. For a write, check its state before retrying.') from None
        if 200 <= r.status_code < 300:
            return r
        if safe_retry and r.status_code in (429,502,503,504) and attempt < 2:
            delay=r.headers.get('Retry-After','')
            if delay:
                from email.utils import parsedate_to_datetime
                from datetime import datetime, timezone
                try:
                    wait = float(delay)
                except ValueError:
                    wait = max(0, (parsedate_to_datetime(delay) - datetime.now(timezone.utc)).total_seconds())
            else:
                wait = 2**attempt
            if wait > 30:
                raise RuntimeError('Server requested a longer wait; retry later, do not override Retry-After')
            time.sleep(max(0, wait))
            continue
        # Do not leak request headers, signed URLs or raw provider response bodies.
        raise RuntimeError(f'Azure HTTP {r.status_code}; see docs/TROUBLESHOOTING.md')

def cognitive_headers(prefix):
    return {'Ocp-Apim-Subscription-Key':env(prefix+'_KEY'),'Content-Type':'application/json'}

def model_client():
    """Build the Azure v1 client using a service key or Entra token provider."""
    from openai import OpenAI
    endpoint = env('AZURE_OPENAI_ENDPOINT').rstrip('/')
    parts = urlsplit(endpoint)
    if parts.scheme != 'https' or not parts.netloc or parts.path or parts.query:
        raise ValueError('AZURE_OPENAI_ENDPOINT must be the HTTPS resource root, without API paths or query strings')
    base = endpoint + '/openai/v1/'
    if env('MODEL_AUTH','key') == 'entra':
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
        key=get_bearer_token_provider(DefaultAzureCredential(),'https://ai.azure.com/.default')
    else:
        key=env('AZURE_OPENAI_API_KEY')
    return OpenAI(base_url=base,api_key=key,timeout=60,max_retries=0)

def chat(messages, *, deployment='MODEL_SMALL', **kwargs):
    """Call a configured chat deployment; reject filtered, truncated or refused output."""
    client=model_client()
    result=client.chat.completions.create(model=env(deployment),messages=messages,**kwargs)
    if not result.choices or result.choices[0].finish_reason in ('content_filter', 'length'):
        raise RuntimeError('Model returned no usable answer or content was filtered')
    if getattr(result.choices[0].message, 'refusal', None):
        raise RuntimeError('Model refused this request; revise the input or route to human review')
    return result

def embed(texts):
    """Request one embedding per input and preserve input order."""
    result=model_client().embeddings.create(model=env('MODEL_EMBEDDING'),input=texts)
    if len(result.data) != len(texts):
        raise RuntimeError('Embedding response count mismatch; no records were indexed')
    return [x.embedding for x in sorted(result.data,key=lambda x:x.index)]

def safety(text):
    """Apply the teaching block threshold to Azure Content Safety category scores."""
    url=env('SAFETY_ENDPOINT').rstrip('/')+'/contentsafety/text:analyze?api-version=2024-09-01'
    result=request('POST',url,headers=cognitive_headers('SAFETY'),body={
        'text':text,'outputType':'FourSeverityLevels'}).json()
    blocked=any(x['severity'] >= 4 for x in result['categoriesAnalysis'])
    return {'blocked':blocked,'categories':result['categoriesAnalysis'],'threshold':4,'scale':'0,2,4,6'}

def shield(prompt, documents):
    """Inspect direct user and indirect document prompt attacks."""
    url=env('SAFETY_ENDPOINT').rstrip('/')+'/contentsafety/text:shieldPrompt?api-version=2024-09-01'
    return request('POST',url,headers=cognitive_headers('SAFETY'),body={
        'userPrompt':prompt,'documents':documents}).json()

def translate(text,to='hi',source=None):
    """Translate one string with the configured Translator resource."""
    url=env('TRANSLATOR_ENDPOINT','https://api.cognitive.microsofttranslator.com').rstrip('/')
    url+='/translate?api-version=3.0&to='+quote(to,safe='')
    if source:
        url+='&from='+quote(source,safe='')
    h=cognitive_headers('TRANSLATOR')
    h['Ocp-Apim-Subscription-Region']=env('TRANSLATOR_REGION')
    return request('POST',url,headers=h,body=[{'text':text}]).json()[0]['translations'][0]['text']

def poll_operation(url, endpoint, prefix, limit=120):
    """Poll only the original service host so credentials cannot be redirected."""
    if urlsplit(url).netloc != urlsplit(endpoint).netloc:
        raise RuntimeError('Unexpected polling host; credentials were not forwarded')
    for _ in range(limit):
        r=request('GET',url,headers=cognitive_headers(prefix),safe_retry=True).json()
        status=r.get('status','').lower()
        if status == 'succeeded':
            return r
        if status in ('failed','canceled','cancelled'):
            raise RuntimeError('Analysis job failed; inspect the job in Azure')
        time.sleep(2)
    raise TimeoutError('Polling deadline exceeded; retain operation ID and inspect in Azure before resubmitting')
