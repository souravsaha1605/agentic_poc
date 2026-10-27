# Purpose: Chunk text and compare embeddings
# Learn: Explain overlap, vector dimensions and why similarity does not establish factual truth.
# Run: Import databricks/labs/08_embeddings_and_chunking.py as a Databricks source notebook. Start live=false; read labs/08_embeddings_and_chunking/RUNBOOK.md.

"""Lab 08: Embeddings and chunking. Read README.md before using --live."""

# Tutor: start with this folder's RUNBOOK.md. Read the offline branch before enabling live calls.
# Inputs come from notebook widgets via args(); secrets come from the scope, never this file.
# save() writes a JSON checkpoint; a fixture is not proof that Azure was called.
from academy.common import args,read,save
from academy.domain import cosine,chunk
from academy.cloud import embed
opts=args('Inspect chunking and cosine similarity')
texts=[r['text'] for r in read('data/policies.json')[:3]]
if opts.live:
    vectors=embed([opts.question]+texts)
    scores=[cosine(vectors[0],v) for v in vectors[1:]]
    result={'embedding_dimensions':len(vectors[0]),'similarities':list(zip(texts,scores))}
else:
    result={'mode':'hand-built vectors, NOT model embeddings','same_direction':cosine([1,0],[2,0]),'orthogonal':cosine([1,0],[0,1])}
result['chunks']=chunk(' '.join(texts),size=12,overlap=3)
save('08_embeddings.json',result)
