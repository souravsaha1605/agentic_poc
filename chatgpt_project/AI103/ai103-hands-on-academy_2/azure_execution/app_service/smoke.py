# Purpose: Check the deployed application health and ask endpoint
# Learn: Verify reachable deployment and token-protected inference without echoing the token.
# Run: Run python azure_execution/app_service/smoke.py in Azure Cloud Shell after app deployment; enter the HTTPS app URL and hidden demo token.

"""Cloud Shell client: getpass keeps the demo token out of shell history/output."""
import getpass
import json
import urllib.request
url = input('App root HTTPS URL: ').strip().rstrip('/')
if not url.startswith('https://'):
    raise ValueError('Use the HTTPS App Service URL')
token = getpass.getpass('API_DEMO_TOKEN (hidden): ')
with urllib.request.urlopen(url+'/health', timeout=30) as response:
    print('Health:', response.status)
request = urllib.request.Request(url+'/ask', data=json.dumps({'question':'return policy'}).encode(),
    headers={'Authorization':'Bearer '+token,'Content-Type':'application/json'}, method='POST')
with urllib.request.urlopen(request, timeout=60) as response:
    result = json.load(response)
    print('Ask:', response.status, '| sources:', result.get('sources'))
