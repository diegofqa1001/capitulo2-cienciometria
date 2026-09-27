"""Análisis de brechas estructurales entre los cinco macro-clústeres (paso 10).

Operacionalización: cociente entre la co-ocurrencia esperada bajo
independencia y la observada para el par de palabras clave dominantes de dos
clústeres distintos. Cada clúster se representa con UNA palabra clave, la de
mayor peso TF-IDF (rank 1 en cluster_summaries.json), y se verifica que sea
exclusiva: ninguna aparece en la lista de términos dominantes de otro
clúster. Esa exclusividad evita que un término técnico compartido (p. ej.
'risk' en C2 y C3, u 'optimization' en C3 y C4) infle la co-ocurrencia
observada entre clústeres que comparten vocabulario sin compartir tema.

El índice es un cociente con umbral descriptivo de 1,5; el contraste
estadístico de cada par frente a la independencia se hace en el paso 11
(scripts/11_prueba_brechas_poisson.py)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import json
import re
from itertools import combinations

with open(ROOT / 'data' / 'final' / 'corpus_final.json', encoding='utf-8') as f:
    corpus = json.load(f)
with open(ROOT / 'data' / 'final' / 'cluster_summaries.json', encoding='utf-8') as f:
    cluster_summaries = json.load(f)

def get_text(r):
    parts = [r.get('Title', ''), r.get('Abstract', '')]
    kw = r.get('Keywords') or r.get('Author Keywords') or ''
    kwp = r.get('Keywords-Plus') or r.get('Index Keywords') or ''
    parts.append(kw)
    parts.append(kwp)
    return ' '.join(p for p in parts if p).lower()

N = len(corpus)
doc_text = [get_text(r) for r in corpus]

# palabra clave dominante y exclusiva por clúster (rank-1 TF-IDF de cada uno)
keyword = {c['cluster_rank']: c['top_terms'][0] for c in cluster_summaries}
all_terms_by_cluster = {c['cluster_rank']: set(c['top_terms']) for c in cluster_summaries}

# verificación de exclusividad: el término elegido no debe aparecer en la
# lista de términos dominantes de NINGÚN otro clúster
print('Palabra clave dominante elegida por clúster (verificación de exclusividad):')
for cid, term in keyword.items():
    others = set()
    for other_cid, terms in all_terms_by_cluster.items():
        if other_cid != cid and term in terms:
            others.add(other_cid)
    status = 'EXCLUSIVA' if not others else f'*** APARECE TAMBIÉN EN C{sorted(others)} ***'
    print(f'  C{cid}: "{term}" -> {status}')

def contains_word(text, word):
    return re.search(r'\b' + re.escape(word) + r'\b', text) is not None

presence = {cid: [1 if contains_word(t, term) else 0 for t in doc_text]
            for cid, term in keyword.items()}
f = {cid: sum(v) for cid, v in presence.items()}

print(f'\nDocumentos (de N={N}) que contienen la palabra clave dominante de cada clúster:')
for cid in sorted(f):
    print(f'  C{cid} ("{keyword[cid]}"): {f[cid]} documentos ({100*f[cid]/N:.1f}%)')

results = []
for i, j in combinations(sorted(keyword.keys()), 2):
    cooc = sum(1 for k in range(N) if presence[i][k] and presence[j][k])
    expected = f[i] * f[j] / N
    gap = float('inf') if cooc == 0 else expected / cooc
    results.append({'par': (i, j), 'kw_i': keyword[i], 'kw_j': keyword[j],
                     'f_i': f[i], 'f_j': f[j], 'cooc_ij': cooc,
                     'expected': expected, 'gap_score': gap})

results.sort(key=lambda r: r['gap_score'], reverse=True)

print(f'\n=== ÍNDICE DE BRECHA (palabra clave única y exclusiva por clúster, N={N}) ===')
print('Fórmula: gap_ij = (f_i * f_j / N) / cooc_ij  |  umbral descriptivo: >1,5\n')
for r in results:
    i, j = r['par']
    gap_str = 'inf (sin co-ocurrencia)' if r['gap_score'] == float('inf') else f"{r['gap_score']:.3f}"
    flag = ' *** SUPERA EL UMBRAL 1,5 ***' if (r['gap_score'] == float('inf') or r['gap_score'] > 1.5) else ''
    print(f"  C{i}(\"{r['kw_i']}\")-C{j}(\"{r['kw_j']}\"): f_i={r['f_i']}, f_j={r['f_j']}, "
          f"cooc={r['cooc_ij']}, esperado={r['expected']:.2f}, gap={gap_str}{flag}")

sig = [r for r in results if r['gap_score'] == float('inf') or r['gap_score'] > 1.5]
print(f'\nPares por encima del umbral (gap > 1,5): {len(sig)} de {len(results)} pares posibles')

theme_labels = {
    1: 'opciones reales / inversión corporativa bajo incertidumbre',
    2: 'aversión a la ambigüedad / elección conductual',
    3: 'optimización robusta / selección de portafolio',
    4: 'decisión multicriterio difusa (fuzzy MCDM)',
    5: 'conectividad de crisis / contagio (COVID, cripto, ESG)',
}

out = {
    'N_corpus': N, 'method': 'single_exclusive_keyword_per_cluster',
    'keyword_per_cluster': {str(k): v for k, v in keyword.items()},
    'theme_labels': theme_labels,
    'f': {str(k): v for k, v in f.items()},
    'pairs': [{'par': list(r['par']), 'kw_i': r['kw_i'], 'kw_j': r['kw_j'],
               'f_i': r['f_i'], 'f_j': r['f_j'], 'cooc_ij': r['cooc_ij'],
               'expected': r['expected'],
               'gap_score': (None if r['gap_score'] == float('inf') else r['gap_score']),
               'gap_score_inf': r['gap_score'] == float('inf')}
              for r in results],
    'n_significant': len(sig),
}
with open(ROOT / 'data' / 'final' / 'gap_analysis_v2.json', 'w', encoding='utf-8') as fh:
    json.dump(out, fh, ensure_ascii=False, indent=2)
print('\nResultados guardados en gap_analysis_v2.json')
