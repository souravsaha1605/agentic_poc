# Purpose: Protect behavior with automated regression tests
# Learn: Check async runner inside notebook loop, speech contact center composition, fabric research composition.
# Run: From project root: PYTHONPATH=src python -m unittest discover -s tests -v. Service doubles are not live Azure tests; test names describe the assertions.

"""Exercise the new composition branches with doubles; no Azure calls or native SDKs."""
import asyncio
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import runpy
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
from academy.common import ROOT, run_async

class CompositionTests(unittest.TestCase):
    def test_async_runner_inside_notebook_loop(self):
        async def work():return 'done'
        async def notebook_cell():return run_async(work())
        self.assertEqual(asyncio.run(notebook_cell()),'done')
    def test_speech_contact_center_composition(self):
        calls=[]
        def transcribe(path):calls.append('transcribe');return 'return policy'
        def synthesize(text):calls.append('synthesize');return 'reply.wav'
        source=ROOT/'capstones/03_multilingual_contact_center/run.py'
        clean={'language':'en','redacted':'return policy','pii_categories':[],'sentiment':'neutral'}
        speech=types.SimpleNamespace(transcribe=transcribe,synthesize=synthesize)
        with tempfile.TemporaryDirectory() as tmp, patch('academy.common.OUT',Path(tmp)),patch.dict(sys.modules,{'academy.speech':speech}),patch('academy.language.preprocess',return_value=clean),patch('academy.cloud.safety',return_value={'blocked':False}),patch('academy.flows.rag',return_value={'answer':'30 days','sources':['returns-v1']}),patch.object(sys,'argv',[str(source),'--live','--variant','speech','--file','synthetic.wav']),redirect_stdout(io.StringIO()):
            runpy.run_path(str(source),run_name='__main__')
            result=json.loads((Path(tmp)/'capstone03.json').read_text())
        self.assertEqual(calls,['transcribe','synthesize'])
        self.assertEqual(result['reply_audio'],'reply.wav')
    def test_fabric_research_composition(self):
        source=ROOT/'capstones/04_enterprise_research_assistant/run.py'
        response=types.SimpleNamespace(choices=[types.SimpleNamespace(message=types.SimpleNamespace(content='Evidence summary'))])
        enterprise=types.SimpleNamespace(sales=lambda:{'source':'Fabric test double','rows':[{'product_id':'K100','units':120}]})
        with tempfile.TemporaryDirectory() as tmp,patch('academy.common.OUT',Path(tmp)),patch.dict(sys.modules,{'academy.enterprise':enterprise}),patch('academy.search.search',return_value=[{'id':'warranty-v1','text':'12 months','tenant':'retail'}]),patch('academy.cloud.chat',return_value=response) as model,patch.object(sys,'argv',[str(source),'--live','--variant','fabric']),redirect_stdout(io.StringIO()):
            runpy.run_path(str(source),run_name='__main__')
            result=json.loads((Path(tmp)/'capstone04.json').read_text())
        self.assertEqual(result['evidence']['sales']['source'],'Fabric test double')
        self.assertEqual(model.call_count,2)

if __name__=='__main__':unittest.main()
