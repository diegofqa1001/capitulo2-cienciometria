"""Estratifica la red en raíces/tronco/hojas usando las MISMAS proporciones
que reporta el artículo original (54/343/2745 sobre 3142 = 1,7%/10,9%/87,4%),
aplicadas como percentiles sobre esta red nueva -- mantiene continuidad
metodológica con el análisis ya defendido, en vez de inventar cortes nuevos."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import json

with open(ROOT / 'data' / 'final' / 'corpus_final_metadatos.json', encoding='utf-8') as f:
    corpus = json.load(f)
with open(ROOT / 'data' / 'final' / 'openalex_data.json', encoding='utf-8') as f:
    openalex = json.load(f)
with open(ROOT / 'data' / 'final' / 'tos_centralities.json', encoding='utf-8') as f:
    cent = json.load(f)

out_deg = cent['out_deg']
in_deg = cent['in_deg']
closeness = cent['closeness']
betweenness = cent['betweenness']

all_nodes = list(out_deg.keys())
N = len(all_nodes)
print(f'Total nodos de red: {N}')

# normalizar out-degree y closeness a [0,1] para combinarlos
def normalize(d):
    vals = list(d.values())
    lo, hi = min(vals), max(vals)
    rng = hi - lo if hi > lo else 1
    return {k: (v - lo) / rng for k, v in d.items()}

out_deg_n = normalize(out_deg)
closeness_n = normalize(closeness)
root_score = {n: out_deg_n[n] + closeness_n[n] for n in all_nodes}

# Proporciones del artículo original
P_ROOTS = 54 / 3142
P_TRUNK = 343 / 3142
n_roots = round(P_ROOTS * N)
n_trunk = round(P_TRUNK * N)
n_leaves = N - n_roots - n_trunk
print(f'Cortes aplicados: raíces={n_roots} ({100*P_ROOTS:.2f}%), tronco={n_trunk} ({100*P_TRUNK:.2f}%), hojas={n_leaves}')

ranked_by_root = sorted(all_nodes, key=lambda n: -root_score[n])
roots = set(ranked_by_root[:n_roots])
remaining = [n for n in all_nodes if n not in roots]
ranked_by_betw = sorted(remaining, key=lambda n: -betweenness[n])
trunk = set(ranked_by_betw[:n_trunk])
leaves = set(remaining) - trunk

def get_year_and_title(node_key):
    kind, ident = node_key.split(':', 1)
    if kind == 'doc':
        r = corpus[int(ident)]
        # nota: el metadato publicado no incluye Título (dato con licencia
        # de Clarivate/Elsevier); se usa el DOI como identificador legible
        return r.get('year'), r.get('doi')
    return None, None  # nodos externos: no tenemos año/DOI de OpenAlex cargado aquí

def avg_year(nodeset):
    years = []
    for n in nodeset:
        y, _ = get_year_and_title(n)
        if y and y.isdigit():
            years.append(int(y))
    return sum(years) / len(years) if years else None

print(f'\n=== ESTRATIFICACIÓN TREE OF SCIENCE (corpus nuevo, 21-ago-2026) ===')
for name, nodeset in [('Raíces', roots), ('Tronco', trunk), ('Hojas', leaves)]:
    ay = avg_year(nodeset)
    n_ext = sum(1 for n in nodeset if n.startswith('ext:'))
    n_doc = len(nodeset) - n_ext
    print(f'{name}: {len(nodeset)} nodos ({n_doc} del corpus, {n_ext} externos)' +
          (f', año prom. {ay:.1f}' if ay else ''))

print('\nTop 10 raíces por score (título si es documento del corpus, ID OpenAlex si es externo):')
for n in ranked_by_root[:10]:
    y, t = get_year_and_title(n)
    if t:
        print(f'  [{y}] {t[:90]}')
    else:
        print(f'  [externo] {n}')

with open(ROOT / 'data' / 'final' / 'tos_classification.json', 'w', encoding='utf-8') as f:
    json.dump({
        'roots': list(roots), 'trunk': list(trunk), 'leaves': list(leaves),
        'n_roots': len(roots), 'n_trunk': len(trunk), 'n_leaves': len(leaves),
        'total_network': N,
    }, f)
