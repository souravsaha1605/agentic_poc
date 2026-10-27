# Purpose: Expose the learning RAG and custom-skill HTTP API
# Learn: Inspect bearer-token checks, bounded request bodies, safe errors and the public health route.
# Run: For deployment follow azure_execution/app_service/README.md. For optional local development use PYTHONPATH=src python -m academy.api from the project root; it blocks until Ctrl+C.

"""Small WSGI learning API; public synthetic corpus only, no refund endpoints."""
import hmac,json,os
from .common import load_env
from .flows import rag

def application(environ,start_response):
    load_env()
    def respond(status,value):
        body=json.dumps(value).encode()
        start_response(status,[('Content-Type','application/json'),('Content-Length',str(len(body)))])
        return [body]
    if environ.get('PATH_INFO')=='/health':
        return respond('200 OK',{'status':'ok','version':'1.2.0'})
    if environ.get('PATH_INFO') not in ('/ask','/skill') or environ.get('REQUEST_METHOD')!='POST':
        return respond('404 Not Found',{'error':'not found'})
    expected=os.getenv('API_DEMO_TOKEN','')
    supplied=environ.get('HTTP_AUTHORIZATION','')
    if not expected or not hmac.compare_digest(supplied.encode('utf-8'),('Bearer '+expected).encode('utf-8')):
        return respond('401 Unauthorized',{'error':'valid demo token required'})
    try:
        length=int(environ.get('CONTENT_LENGTH','0'))
        if not 0<length<=16000:
            raise ValueError('size')
        body=json.loads(environ['wsgi.input'].read(length))
        if not isinstance(body, dict):
            raise ValueError('Expected a JSON object')
        if environ.get('PATH_INFO') == '/skill':
            from .enrichment import enrich
            if not isinstance(body.get('values'), list):
                raise ValueError('Expected values array')
            return respond('200 OK', enrich(body))
        question=body['question']
        if not isinstance(question,str):
            raise ValueError('type')
        result=rag(question,live=os.getenv('API_LIVE','false').lower()=='true')
        return respond('200 OK',result)
    except (ValueError,KeyError):
        return respond('400 Bad Request',{'error':'expected JSON question string, bounded length'})
    except Exception:
        return respond('502 Bad Gateway',{'error':'upstream failure; inspect sanitized telemetry'})

if __name__=='__main__':
    from wsgiref.simple_server import make_server
    print('Local development only: http://127.0.0.1:8000')
    make_server('127.0.0.1',8000,application).serve_forever()
