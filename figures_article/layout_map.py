"""Document-level science map: spring layout of the bibliographic-coupling network (five macro-clusters)."""
from pathlib import Path
import json, time
from collections import defaultdict, Counter
from itertools import combinations
import numpy as np, networkx as nx
ROOT = Path(__file__).resolve().parent.parent; FIN = ROOT/'data'/'final'
corpus = json.load(open(FIN/'corpus_final_metadatos.json', encoding='utf-8'))
openalex = json.load(open(FIN/'openalex_data.json', encoding='utf-8'))
pub = {int(k): v for k, v in json.load(open(FIN/'louvain_communities.json'))['assignment'].items()}
doc_by_doi = {r['doi']: i for i, r in enumerate(corpus) if r.get('doi')}
ref_to_docs = defaultdict(list)
for doi, idx in doc_by_doi.items():
    oa = openalex.get(doi)
    if oa:
        for ref in oa.get('referenced_works', []): ref_to_docs[ref].append(idx)
pw = Counter()
for ref, docs in ref_to_docs.items():
    if 2 <= len(docs) <= 80:
        for a, b in combinations(sorted(set(docs)), 2): pw[(a, b)] += 1
G = nx.Graph()
for (a, b), w in pw.items():
    if w >= 2 and pub.get(a, 99) < 5 and pub.get(b, 99) < 5: G.add_edge(a, b, weight=w)
print(G.number_of_nodes(), G.number_of_edges())
t = time.time()
pos = nx.spring_layout(G, weight='weight', k=0.08, iterations=80, seed=42)
print('layout s', round(time.time()-t))
json.dump({str(n): [float(x), float(y)] for n, (x, y) in pos.items()}, open(FIN/'layout_coupling_spring.json', 'w'))
