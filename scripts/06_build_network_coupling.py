"""Red de acoplamiento bibliográfico (bibliographic coupling): dos documentos
del corpus se conectan si citan referencias en común (sin exigir que esas
referencias estén dentro del corpus). Es más robusta que la co-citación pura
para un corpus con muchos documentos recientes que aún no acumulan citas
entrantes -- y es el estándar de facto en cienciometría para este escenario.
Referencias 'ubicuas' (citadas por muchísimos documentos del corpus, p.ej.
Markowitz 1952) se excluyen del cómputo de pesos porque no discriminan
temáticamente -- mismo principio que max_df en TF-IDF."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import json
import networkx as nx
from collections import defaultdict, Counter
from itertools import combinations

with open(ROOT / 'data' / 'final' / 'corpus_final_metadatos.json', encoding='utf-8') as f:
    corpus = json.load(f)
with open(ROOT / 'data' / 'final' / 'openalex_data.json', encoding='utf-8') as f:
    openalex = json.load(f)

doc_by_doi = {r['doi']: i for i, r in enumerate(corpus) if r.get('doi')}

# índice invertido: referencia (OpenAlex ID citado) -> lista de docs del corpus que la citan
ref_to_docs = defaultdict(list)
for doi, idx in doc_by_doi.items():
    oa = openalex.get(doi)
    if not oa:
        continue
    for ref in oa.get('referenced_works', []):
        ref_to_docs[ref].append(idx)

print(f'Referencias distintas citadas por el corpus: {len(ref_to_docs)}')
ref_doc_counts = Counter({r: len(d) for r, d in ref_to_docs.items()})
print('Top 10 referencias más citadas dentro del corpus:')
for ref, n in ref_doc_counts.most_common(10):
    print(f'  {n} docs citan {ref}')

MAX_DF = 80  # excluir referencias citadas por más de 80 documentos del corpus (ubicuas)
MIN_SHARED = 2  # peso mínimo de arista para conservarla (reduce ruido)

pair_weight = Counter()
n_refs_used = 0
for ref, docs in ref_to_docs.items():
    if len(docs) < 2 or len(docs) > MAX_DF:
        continue
    n_refs_used += 1
    uniq = sorted(set(docs))
    for a, b in combinations(uniq, 2):
        pair_weight[(a, b)] += 1

print(f'Referencias usadas para acoplamiento (2 <= n_docs <= {MAX_DF}): {n_refs_used}')
print(f'Pares candidatos (antes de umbral de peso): {len(pair_weight)}')

G = nx.Graph()
G.add_nodes_from(range(len(corpus)))
for (a, b), w in pair_weight.items():
    if w >= MIN_SHARED:
        G.add_edge(a, b, weight=w)

print(f'Nodos: {G.number_of_nodes()}, Aristas (peso >= {MIN_SHARED}): {G.number_of_edges()}')
n_isolated = sum(1 for n in G.nodes() if G.degree(n) == 0)
print(f'Nodos aislados: {n_isolated} ({100*n_isolated/G.number_of_nodes():.1f}%)')

components = sorted(nx.connected_components(G), key=len, reverse=True)
print(f'Componentes conexas: {len(components)}; top 5 tamaños: {[len(c) for c in components[:5]]}')

import networkx.algorithms.community as nx_comm
RESOLUTION = 0.5  # calibrado para granularidad macro-tematica (decision con Diego, 2026-08-22)
communities = nx_comm.louvain_communities(G, weight='weight', seed=42, resolution=RESOLUTION)
communities.sort(key=len, reverse=True)
modularity = nx_comm.modularity(G, communities, weight='weight')

print(f'\n=== RESULTADO LOUVAIN (acoplamiento bibliográfico) ===')
print(f'Comunidades detectadas: {len(communities)}')
print(f'Modularidad Q: {modularity:.4f}')
for i, comm in enumerate(communities[:15]):
    years = [int(corpus[idx].get('Year')) for idx in comm if corpus[idx].get('Year', '').isdigit()]
    avg_year = sum(years) / len(years) if years else None
    print(f'  Comunidad {i+1}: {len(comm)} documentos' + (f', año prom. {avg_year:.1f}' if avg_year else ''))

assignment = {int(idx): i for i, comm in enumerate(communities) for idx in comm}
with open(ROOT / 'data' / 'final' / 'louvain_communities.json', 'w', encoding='utf-8') as f:
    json.dump({'assignment': assignment, 'modularity': modularity,
               'n_communities': len(communities),
               'community_sizes': [len(c) for c in communities],
               'method': 'bibliographic_coupling', 'max_df': MAX_DF, 'min_shared': MIN_SHARED,
               'resolution': RESOLUTION}, f)
