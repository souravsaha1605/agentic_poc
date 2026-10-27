# Purpose: Run a bounded agent discussion
# Learn: Track speaker turns and terminate a discussion instead of allowing an unbounded autonomous loop.
# Run: Import databricks/extensions/19_group_discussion.py as a Databricks source notebook. Start live=false; read labs/19_multi_agent_orchestration_and_reflection/RUNBOOK.md.

"""Bounded group discussion: fixed speaker policy, shared state, two rounds maximum."""
from academy.common import args,save
from academy.cloud import chat
opts=args('Run a bounded group discussion')
shared=[{'role':'user','content':'Evidence: unused items may be returned within 30 days with receipt. Question: '+opts.question}]
events=[]
for round_id in range(2):
    for name,instruction in [('policy','Identify the applicable evidence only.'),('review','Flag unsupported claims or missing evidence.')]:
        if opts.live:
            text=chat([{'role':'system','content':instruction+' Give a concise finding; no action execution.'}]+shared).choices[0].message.content
        else:
            text='Check unused condition, receipt and delivery date.'
        events.append({'round':round_id+1,'speaker':name,'finding':text})
        shared.append({'role':'assistant','content':name+': '+text})
save('19_group_chat.json',{'events':events,'stop':'fixed two-round limit','mode':'real model calls' if opts.live else 'scripted findings'})
