"""Paso 13. Estabilidad por consenso (co-asociación) de los cinco macro-clústeres frente a
20 semillas de Louvain, cinco configuraciones vecinas de hiperparámetros y la rejilla
completa de 36 configuraciones. Para cada par de clústeres publicados (Ci, Cj) se reporta
la probabilidad media de que un documento de Ci y uno de Cj queden en la misma comunidad
en una corrida alternativa; la diagonal mide la cohesión interna. Incluye la conectividad
de cada comunidad publicada. Salida: results/consenso_estabilidad.json"""
from pathlib import Path
import json, itertools
import numpy as np
import networkx as nx
import networkx.algorithms.community as nx_comm
from collections import Counter, defaultdict
from itertools import combinations
from sklearn.metrics import adjusted_rand_score

ROOT = Path(__file__).resolve().parent.parent
FIN = ROOT / 'data' / 'final'
corpus = json.load(open(FIN / 'corpus_final_metadatos.json', encoding='utf-8'))
openalex = json.load(open(FIN / 'openalex_data.json', encoding='utf-8'))
published = json.load(open(FIN / 'louvain_communities.json', encoding='utf-8'))
pub_lab = {int(k): v for k, v in published['assignment'].items()}
core = np.array([n for n in range(len(corpus)) if pub_lab.get(n, 99) < 5])
core_lab = np.array([pub_lab[n] for n in core])

doc_by_doi = {r['doi']: i for i, r in enumerate(corpus) if r.get('doi')}
ref_to_docs = defaultdict(list)
for doi, idx in doc_by_doi.items():
    oa = openalex.get(doi)
    if oa:
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

def run(G, res, seed):
    comms = nx_comm.louvain_communities(G, weight='weight', seed=seed, resolution=res)
    lab = {}
    for i, c in enumerate(sorted(comms, key=len, reverse=True)):
        for n in c:
            lab[n] = i
    return lab

def coassoc(labs):
    """mean co-association between published clusters over a list of label dicts"""
    M = np.zeros((5, 5)); cnt = 0
    for lab in labs:
        alt = np.array([lab[n] for n in core])
        # co-membership matrix via one-hot
        k = alt.max() + 1
        A = np.zeros((len(core), k)); A[np.arange(len(core)), alt] = 1
        B = np.zeros((len(core), 5)); B[np.arange(len(core)), core_lab] = 1
        cross = B.T @ A              # 5 x k : counts of Ci docs in alt community a
        sizes = B.sum(0)
        same = cross @ cross.T       # pairs (with self) co-placed
        M += same / np.outer(sizes, sizes); cnt += 1
    return M / cnt

def merges(lab):
    """for an alternative run, map each published cluster to its majority community and list merges"""
    maj = {}
    for c in range(5):
        alt = [lab[n] for n in core[core_lab == c]]
        top, n = Counter(alt).most_common(1)[0]
        maj[c] = (top, round(n / len(alt), 2))
    groups = defaultdict(list)
    for c, (t, share) in maj.items():
        groups[t].append(f'C{c+1}({share:.0%})')
    return ['+'.join(v) for v in groups.values() if len(v) > 1] or ['none'], maj

out = {}
G0 = build(80, 2)
# (1) seeds at baseline
labs = [run(G0, 0.5, s) for s in range(1, 21)]
M = coassoc(labs)
out['seeds_baseline'] = dict(coassociation=M.round(3).tolist(), merges=[merges(l)[0] for l in labs],
                             ARI=[round(adjusted_rand_score(core_lab, [l[n] for n in core]), 3) for l in labs],
                             n_big=[sum(1 for v in Counter(l.values()).values() if v >= 100) for l in labs])
print('Co-association across 20 seeds (baseline):\n', M.round(2))
print('merges per seed:', out['seeds_baseline']['merges'])
# (2) neighbouring hyper-parameters (seed 42), resolution 0.5
alt = []
for max_df, ms in [(40, 2), (160, 2), (80, 1), (80, 3), (None, 2)]:
    G = build(max_df, ms)
    lab = run(G, 0.5, 42)
    alt.append(lab)
    m, maj = merges(lab)
    print(f'max_df={max_df} min_shared={ms}: merges={m}; majority shares={ {f"C{c+1}": v[1] for c, v in maj.items()} }')
    out.setdefault('hyperparams', []).append(dict(max_df=max_df, min_shared=ms, merges=m,
                                                   majority_share={f'C{c+1}': v[1] for c, v in maj.items()}))
M2 = coassoc(alt)
out['hyperparams_coassociation'] = M2.round(3).tolist()
print('Co-association across 5 hyper-parameter settings:\n', M2.round(2))
# (3) resolution 1.0 at baseline (10 communities) : which published clusters split
lab = run(G0, 1.0, 42)
splits = {}
for c in range(5):
    cnt = Counter(lab[n] for n in core[core_lab == c])
    splits[f'C{c+1}'] = [round(v / (core_lab == c).sum(), 2) for _, v in cnt.most_common(4)]
out['resolution_1_splits'] = splits
print('resolution 1.0 – share of each published cluster in its largest sub-communities:', splits)
json.dump(out, open(ROOT / 'results' / 'consenso_estabilidad.json', 'w'), indent=2)

# (4) full 36-setting grid: co-association of C1 with each theoretical cluster, and community connectivity
grid_rows = []
for max_df in [40, 80, 160, None]:
    for ms in [1, 2, 3]:
        G = build(max_df, ms)
        for res in [0.5, 0.75, 1.0]:
            lab = run(G, res, 42)
            Mg = coassoc([lab])
            big = sum(1 for c in Counter(lab.values()).values() if c >= 100)
            grid_rows.append(dict(max_df=max_df, min_shared=ms, resolution=res, n_big=big,
                                  C1_C2=round(Mg[0, 1], 3), C1_C3=round(Mg[0, 2], 3), C1_C4=round(Mg[0, 3], 3),
                                  C1_C5=round(Mg[0, 4], 3), C3_C4=round(Mg[2, 3], 3), C2_C3=round(Mg[1, 2], 3)))
            print(grid_rows[-1])
out['grid_coassociation'] = grid_rows
# connectivity of the five published communities inside the baseline network
conn = {}
for c in range(5):
    sub = G0.subgraph([int(n) for n in core[core_lab == c]])
    conn[f'C{c+1}'] = dict(connected=nx.is_connected(sub), n_components=nx.number_connected_components(sub),
                          largest_component_share=round(max(len(x) for x in nx.connected_components(sub)) / sub.number_of_nodes(), 3))
out['community_connectivity'] = conn
print(conn)
json.dump(out, open(ROOT / 'results' / 'consenso_estabilidad.json', 'w'), indent=2)
