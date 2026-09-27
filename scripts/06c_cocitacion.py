"""Red de co-citación estricta entre documentos del corpus (paso 6c).

Alternativa descartada en la §2.2 de la tesis: dos documentos del corpus se
vinculan solo si un tercer documento del propio corpus cita a ambos. El
script cuenta los nodos aislados de esa red sobre los 3.643 documentos del
corpus, con los datos abiertos de OpenAlex publicados en data/final/, y
escribe results/cocitacion.json.
"""

import json
from itertools import combinations
from pathlib import Path

import networkx as nx

ROOT = Path(__file__).resolve().parent.parent
with open(ROOT / 'data' / 'final' / 'corpus_final_metadatos.json', encoding='utf-8') as f:
    corpus = json.load(f)
with open(ROOT / 'data' / 'final' / 'openalex_data.json', encoding='utf-8') as f:
    openalex = json.load(f)

N = len(corpus)
# OpenAlex ID -> índice del documento del corpus
oa_to_idx = {}
for i, r in enumerate(corpus):
    oa = openalex.get(r.get('doi')) if r.get('doi') else None
    if oa and oa.get('openalex_id'):
        oa_to_idx[oa['openalex_id']] = i


def refs(oa):
    rw = oa.get('referenced_works', [])
    if isinstance(rw, str):  # algunas entradas se serializaron como texto de lista
        import ast
        rw = ast.literal_eval(rw) if rw.strip() else []
    return rw


G = nx.Graph()
G.add_nodes_from(range(N))
for r in corpus:
    oa = openalex.get(r.get('doi')) if r.get('doi') else None
    if not oa:
        continue
    cited_in_corpus = sorted({oa_to_idx[w] for w in refs(oa) if w in oa_to_idx})
    for a, b in combinations(cited_in_corpus, 2):
        G.add_edge(a, b)

aislados = sum(1 for n in G if G.degree(n) == 0)
out = {'N_corpus': N, 'documentos_con_openalex_id': len(oa_to_idx),
       'aristas': G.number_of_edges(), 'nodos_aislados': aislados,
       'porcentaje_aislados': round(100 * aislados / N, 2),
       'networkx': nx.__version__}
(ROOT / 'results').mkdir(exist_ok=True)
with open(ROOT / 'results' / 'cocitacion.json', 'w', encoding='utf-8') as fh:
    json.dump(out, fh, ensure_ascii=False, indent=2)
print(json.dumps(out, ensure_ascii=False, indent=2))
