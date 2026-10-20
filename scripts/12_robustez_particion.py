"""Paso 12. Robustez de la partición y brecha por citación (re-ejecutable con data/final/).

(A) Sensibilidad de la partición de Louvain a los hiperparámetros de la red de
    acoplamiento (MAX_DF, MIN_SHARED) y a la resolución, medida con ARI/NMI frente a
    la partición publicada sobre los 3.012 documentos de los cinco macro-clústeres.
(B) Segunda operacionalización de la brecha, independiente del texto: cociente entre el
    peso de acoplamiento entre clústeres esperado (modelo de configuración y permutación
    de etiquetas, 500 réplicas) y el observado. Se compara con el índice léxico.
Salida: results/robustez_particion.json
"""
from pathlib import Path
import json, random
from collections import defaultdict, Counter
from itertools import combinations
import numpy as np
import networkx as nx
import networkx.algorithms.community as nx_comm
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent.parent
FIN = ROOT / 'data' / 'final'
corpus = json.load(open(FIN / 'corpus_final_metadatos.json', encoding='utf-8'))
openalex = json.load(open(FIN / 'openalex_data.json', encoding='utf-8'))
published = json.load(open(FIN / 'louvain_communities.json', encoding='utf-8'))
gap_lex = json.load(open(FIN / 'gap_analysis_v2.json', encoding='utf-8'))

doc_by_doi = {r['doi']: i for i, r in enumerate(corpus) if r.get('doi')}
ref_to_docs = defaultdict(list)
for doi, idx in doc_by_doi.items():
    oa = openalex.get(doi)
    if not oa:
        continue
    for ref in oa.get('referenced_works', []):
        ref_to_docs[ref].append(idx)


def build(max_df, min_shared):
    pw = Counter()
    for ref, docs in ref_to_docs.items():
        if len(docs) < 2 or (max_df is not None and len(docs) > max_df):
            continue
        for a, b in combinations(sorted(set(docs)), 2):
            pw[(a, b)] += 1
    G = nx.Graph(); G.add_nodes_from(range(len(corpus)))
    for (a, b), w in pw.items():
        if w >= min_shared:
            G.add_edge(a, b, weight=w)
    return G


def louvain(G, res, seed=42):
    comms = nx_comm.louvain_communities(G, weight='weight', seed=seed, resolution=res)
    comms.sort(key=len, reverse=True)
    Q = nx_comm.modularity(G, comms, weight='weight')
    lab = {}
    for i, c in enumerate(comms):
        for n in c:
            lab[n] = i
    return comms, Q, lab

# ---------- baseline ----------
G0 = build(80, 2)
comms0, Q0, lab0 = louvain(G0, 0.5)
pub_lab = {int(k): v for k, v in published['assignment'].items()}
core = [n for n in range(len(corpus)) if pub_lab.get(n, 99) < 5]
print(f'Baseline: nodes {G0.number_of_nodes()}, edges {G0.number_of_edges()}, Q={Q0:.4f}, sizes {[len(c) for c in comms0[:6]]}')
print('ARI vs published (core):', adjusted_rand_score([pub_lab[n] for n in core], [lab0[n] for n in core]))

# ---------- (A) sensitivity grid ----------
rows = []
for max_df in [40, 80, 160, None]:
    for min_shared in [1, 2, 3]:
        G = build(max_df, min_shared)
        for res in [0.5, 0.75, 1.0]:
            comms, Q, lab = louvain(G, res)
            big = [len(c) for c in comms if len(c) >= 100]
            ari = adjusted_rand_score([pub_lab[n] for n in core], [lab[n] for n in core])
            nmi = normalized_mutual_info_score([pub_lab[n] for n in core], [lab[n] for n in core])
            iso = sum(1 for n in G.nodes if G.degree(n) == 0)
            rows.append(dict(max_df=max_df, min_shared=min_shared, resolution=res, edges=G.number_of_edges(),
                             isolated=iso, Q=round(Q, 4), n_big=len(big), big_sizes=big[:8], ARI=round(ari, 3), NMI=round(nmi, 3)))
            print(rows[-1])
# seed sensitivity at baseline
seed_rows = []
for s in range(1, 11):
    comms, Q, lab = louvain(G0, 0.5, seed=s)
    seed_rows.append(dict(seed=s, Q=round(Q, 4), n_big=sum(1 for c in comms if len(c) >= 100),
                          ARI=round(adjusted_rand_score([pub_lab[n] for n in core], [lab[n] for n in core]), 3)))
print('seeds:', seed_rows)

# ---------- (B) network-based structural gap ----------
top = list(range(5))
nodes_by_c = {c: [n for n in core if pub_lab[n] == c] for c in top}
strength = dict(G0.degree(weight='weight'))
m2 = sum(strength.values())  # = 2m (weighted)
S = {c: sum(strength[n] for n in nodes_by_c[c]) for c in top}
obs = {}
for u, v, d in G0.edges(data=True):
    cu, cv = pub_lab.get(u, 99), pub_lab.get(v, 99)
    if cu < 5 and cv < 5 and cu != cv:
        key = tuple(sorted((cu, cv)))
        obs[key] = obs.get(key, 0) + d['weight']
net_gap = []
for i, j in combinations(top, 2):
    expected = S[i] * S[j] / m2  # configuration-model expectation of weight between groups
    o = obs.get((i, j), 0)
    net_gap.append(dict(pair=[i + 1, j + 1], observed=o, expected=round(expected, 1),
                        gap_net=(None if o == 0 else round(expected / o, 3))))
# permutation test: shuffle labels among core nodes preserving sizes
rng = random.Random(42)
labels_core = [pub_lab[n] for n in core]
perm_obs = {k: [] for k in combinations(top, 2)}
core_edges = [(u, v, d['weight']) for u, v, d in G0.edges(data=True) if pub_lab.get(u, 99) < 5 and pub_lab.get(v, 99) < 5]
idx_of = {n: k for k, n in enumerate(core)}
for it in range(500):
    perm = labels_core[:]
    rng.shuffle(perm)
    acc = Counter()
    for u, v, w in core_edges:
        a, b = perm[idx_of[u]], perm[idx_of[v]]
        if a != b:
            acc[tuple(sorted((a, b)))] += w
    for k in perm_obs:
        perm_obs[k].append(acc.get(k, 0))
for r in net_gap:
    k = (r['pair'][0] - 1, r['pair'][1] - 1)
    arr = np.array(perm_obs[k])
    r['perm_mean'] = round(float(arr.mean()), 1)
    r['p_lower'] = round(float((arr <= r['observed']).mean()), 4)  # prob. of observing so few links under random labelling
    r['perm_ratio'] = (None if r['observed'] == 0 else round(float(arr.mean() / r['observed']), 3))
net_gap.sort(key=lambda r: (r['gap_net'] is None, -(r['gap_net'] or 0)))
print('\nNetwork gap (configuration-model expected / observed inter-cluster coupling weight):')
for r in net_gap:
    print(r)

# compare with lexical gap
lex = {tuple(sorted(p['par'])): (np.inf if p['gap_score_inf'] else p['gap_score']) for p in gap_lex['pairs']}
pairs = [tuple(sorted((r['pair'][0], r['pair'][1]))) for r in net_gap]
x = [lex[p] for p in pairs]
y = [np.inf if r['gap_net'] is None else r['gap_net'] for r in net_gap]
yp = [np.inf if r['perm_ratio'] is None else r['perm_ratio'] for r in net_gap]
# replace inf with large value for rank correlation
xr = [1e6 if np.isinf(v) else v for v in x]; yr = [1e6 if np.isinf(v) else v for v in y]
rho, pval = spearmanr(xr, yr)
ypr = [1e6 if np.isinf(v) else v for v in yp]
rho_p, pval_p = spearmanr(xr, ypr)
print(f'\nSpearman(lexical, config-model gap) rho={rho:.3f} p={pval:.4f}; Spearman(lexical, permutation gap) rho={rho_p:.3f} p={pval_p:.4f}')
agree = sum(1 for a, b in zip(xr, yr) if (a > 1.5) == (b > 1.5))
agree_p = sum(1 for a, b in zip(xr, ypr) if (a > 1.5) == (b > 1.5))
print(f'Agreement on significance (>1.5): config {agree}/10, permutation {agree_p}/10')
rho_nulls, p_nulls = spearmanr(yr, ypr)  # concordancia entre los dos modelos nulos
print(f'Spearman(config gap, permutation gap) rho={rho_nulls:.3f} p={p_nulls:.4f}')

json.dump(dict(baseline=dict(edges=G0.number_of_edges(), Q=Q0, sizes=[len(c) for c in comms0[:6]]),
               sensitivity=rows, seeds=seed_rows, network_gap=net_gap,
               lexical_vs_network=dict(config_model=dict(spearman_rho=float(rho), p=float(pval), agreement=agree), permutation=dict(spearman_rho=float(rho_p), p=float(pval_p), agreement=agree_p), between_nulls=dict(spearman_rho=float(rho_nulls), p=float(p_nulls)))),
          open(ROOT / 'results' / 'robustez_particion.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
print('results/robustez_particion.json')
