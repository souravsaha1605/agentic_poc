# Purpose: Serve the local synthetic policy HTTP endpoint
# Learn: Inspect route handling and JSON HTTP response construction.
# Run: Prefer databricks/extensions/12_rest_transport.py, which manages start and stop. Standalone: PYTHONPATH=src python extensions/rest_tools/server.py; blocks until Ctrl+C.

"""Local loopback teaching API. Only synthetic public data, no production auth claims."""
import json
from http.server import BaseHTTPRequestHandler,HTTPServer
from academy.domain import retrieve
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path!='/policy':
            self.send_error(404)
            return
        body=json.dumps(retrieve('return policy')).encode()
        self.send_response(200)
        self.send_header('Content-Type','application/json')
        self.send_header('Content-Length',str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self,*args):
        pass
if __name__=='__main__':
    HTTPServer(('127.0.0.1',8765),Handler).serve_forever()
