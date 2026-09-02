"""Clasificación Tree of Science (Robledo et al., 2014): raíces (literatura
fundacional), tronco (conectores estructurales) y hojas (frontera activa).

Convención de dirección: arista CITADO -> CITANTE (el flujo de influencia
va del trabajo antiguo hacia el que lo usa), consistente con la definición
del artículo: raíces = alto out-degree + closeness (muchas obras influidas,
posición central) y hojas = alto in-degree (construyen sobre mucho trabajo
previo). Se agregan como nodos externos las referencias citadas por al
menos 15 documentos del corpus (umbral elegido para mantener una proporción
red-total/corpus similar a la del análisis original: ~1.17x)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import json
import networkx as nx
from collections import Counter

with open(ROOT / 'data' / 'final' / 'corpus_final_metadatos.json', encoding='utf-8') as f:
    corpus = json.load(f)
with open(ROOT / 'data' / 'final' / 'openalex_data.json', encoding='utf-8') as f:
    openalex = json.load(f)

doc_by_doi = {r['doi']: i for i, r in enumerate(corpus) if r.get('doi')}
oaid_to_idx = {}
for doi, idx in doc_by_doi.items():
    oa = openalex.get(doi)
    if oa and oa.get('openalex_id'):
        oaid_to_idx[oa['openalex_id']] = idx

THRESHOLD = 15
ext_ref_count = Counter()
for doi, oa in openalex.items():
    for ref in oa.get('referenced_works', []):
        if ref not in oaid_to_idx:
            ext_ref_count[ref] += 1
external_nodes = {ref for ref, c in ext_ref_count.items() if c >= THRESHOLD}
print(f'Nodos externos (citados por >= {THRESHOLD} docs del corpus): {len(external_nodes)}')

# construir grafo dirigido: CITADO -> CITANTE
G = nx.DiGraph()
for i in range(len(corpus)):
    G.add_node(('doc', i))
for ext in external_nodes:
    G.add_node(('ext', ext))

for doi, oa in openalex.items():
    idx = doc_by_doi.get(doi)
    if idx is None:
        continue
    citing_node = ('doc', idx)
    for ref in oa.get('referenced_works', []):
        if ref in oaid_to_idx:
            cited_node = ('doc', oaid_to_idx[ref])
        elif ref in external_nodes:
            cited_node = ('ext', ref)
        else:
            continue
        G.add_edge(cited_node, citing_node)  # CITADO -> CITANTE

print(f'Nodos totales de la red: {G.number_of_nodes()} (corpus {len(corpus)} + externos {len(external_nodes)})')
print(f'Proporción red/corpus: {G.number_of_nodes()/len(corpus):.3f}x')
print(f'Aristas: {G.number_of_edges()}')

# Se usa la red COMPLETA (no solo la componente gigante), igual que describe
# el artículo ('la red completa asciende a...'); networkx calcula closeness y
# betweenness correctamente sobre grafos con componentes desconectadas.
out_deg = dict(G.out_degree())
in_deg = dict(G.in_degree())
print('Calculando closeness centrality (puede tardar)...')
# OJO: nx.closeness_centrality en grafos dirigidos usa por defecto distancia
# ENTRANTE (qué tan cerca le queda a otros llegar a X). Para 'raices' con
# arista CITADO->CITANTE necesitamos distancia SALIENTE (qué tan bien X
# alcanza, via la cadena de citas, a todo lo que vino despues) -- eso exige
# invertir el grafo antes de calcular closeness, tal como indica la propia
# documentacion de networkx ('To use outward distance, act on G.reverse()').
closeness = nx.closeness_centrality(G.reverse())
print('Calculando betweenness centrality aproximada (muestreo k=800)...')
betweenness = nx.betweenness_centrality(G, k=min(800, len(G)), seed=42, normalized=True)

with open(ROOT / 'data' / 'final' / 'tos_centralities.json', 'w', encoding='utf-8') as f:
    json.dump({
        'out_deg': {f'{k[0]}:{k[1]}': v for k, v in out_deg.items()},
        'in_deg': {f'{k[0]}:{k[1]}': v for k, v in in_deg.items()},
        'closeness': {f'{k[0]}:{k[1]}': v for k, v in closeness.items()},
        'betweenness': {f'{k[0]}:{k[1]}': v for k, v in betweenness.items()},
    }, f)
print('Centralidades guardadas.')
