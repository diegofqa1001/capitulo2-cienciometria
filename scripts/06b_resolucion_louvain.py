"""Sensibilidad de la partición de Louvain a la resolución (Cap. 2, §2.2).

Reconstruye la red de acoplamiento bibliográfico con los mismos parámetros del
paso 06 (MAX_DF = 80, MIN_SHARED = 2), ejecuta louvain_communities de NetworkX
(Blondel et al., 2008; implementación estándar, semilla 42) con resolución
0,5 y 1,0, verifica que la partición con 0,5 coincide con la publicada en
data/final/louvain_communities.json y publica la partición con resolución 1,0
en data/final/louvain_communities_gamma1.json, junto con un resumen en
results/resolucion_louvain.json.
"""
from pathlib import Path
import json
from collections import defaultdict, Counter
from itertools import combinations
import networkx as nx
import networkx.algorithms.community as nx_comm

ROOT = Path(__file__).resolve().parent.parent
MAX_DF, MIN_SHARED, SEED = 80, 2, 42

corpus = json.load(open(ROOT / 'data' / 'final' / 'corpus_final_metadatos.json', encoding='utf-8'))
openalex = json.load(open(ROOT / 'data' / 'final' / 'openalex_data.json', encoding='utf-8'))
doc_by_doi = {r['doi']: i for i, r in enumerate(corpus) if r.get('doi')}
ref_to_docs = defaultdict(list)
for doi, idx in doc_by_doi.items():
    oa = openalex.get(doi)
    if oa:
        for ref in oa.get('referenced_works', []):
            ref_to_docs[ref].append(idx)
pair_weight = Counter()
for ref, docs in ref_to_docs.items():
    if 2 <= len(docs) <= MAX_DF:
        for a, b in combinations(sorted(set(docs)), 2):
            pair_weight[(a, b)] += 1
G = nx.Graph()
G.add_nodes_from(range(len(corpus)))
for (a, b), w in pair_weight.items():
    if w >= MIN_SHARED:
        G.add_edge(a, b, weight=w)
conectados = sum(1 for n in G.nodes() if G.degree(n) > 0)

def particion(gamma):
    comms = nx_comm.louvain_communities(G, weight='weight', seed=SEED, resolution=gamma)
    comms.sort(key=len, reverse=True)
    q = nx_comm.modularity(G, comms, weight='weight')
    return comms, q

resumen = {'networkx': nx.__version__, 'semilla': SEED, 'nodos': G.number_of_nodes(),
           'documentos_conectados': conectados, 'aristas': G.number_of_edges(), 'resoluciones': {}}
publicada = json.load(open(ROOT / 'data' / 'final' / 'louvain_communities.json'))
for gamma in (0.5, 1.0):
    comms, q = particion(gamma)
    sizes = [len(c) for c in comms]
    no_triviales = [s for s in sizes if s >= 10]
    resumen['resoluciones'][str(gamma)] = {
        'modularidad': round(q, 4), 'n_comunidades_total': len(comms),
        'n_comunidades_10_o_mas_docs': len(no_triviales), 'tamanos_10_o_mas': no_triviales,
        'docs_en_comunidades_10_o_mas': sum(no_triviales),
        'pct_corpus': round(100 * sum(no_triviales) / len(corpus), 2),
        'pct_conectados': round(100 * sum(no_triviales) / conectados, 2)}
    if gamma == 0.5:
        resumen['resoluciones']['0.5']['coincide_con_publicada'] = sizes == publicada['community_sizes']
    else:
        assignment = {int(i): k for k, c in enumerate(comms) for i in c}
        json.dump({'assignment': assignment, 'modularity': q, 'n_communities': len(comms),
                   'community_sizes': sizes, 'method': 'bibliographic_coupling',
                   'max_df': MAX_DF, 'min_shared': MIN_SHARED, 'resolution': gamma},
                  open(ROOT / 'data' / 'final' / 'louvain_communities_gamma1.json', 'w', encoding='utf-8'))
(ROOT / 'results').mkdir(exist_ok=True)
json.dump(resumen, open(ROOT / 'results' / 'resolucion_louvain.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=2)
print(json.dumps(resumen, ensure_ascii=False, indent=2))
