"""Contraste estadístico de las brechas estructurales (paso 11).

El índice de brecha de `10_gap_analysis.py` es un cociente esperado/observado
con un umbral fijo de 1,5; por sí solo no es una prueba de hipótesis. Este
script contrasta, para cada uno de los diez pares de clústeres, la
co-ocurrencia observada de las dos palabras clave dominantes frente a la
esperada bajo independencia, con dos pruebas:

1. Poisson (prueba principal): X ~ Poisson(lambda = f_i * f_j / N).
   - Para pares con observada < esperada (brecha), p = P(X <= observada),
     cola inferior unilateral.
   - Para pares con observada > esperada (integración), p = P(X >= observada),
     cola superior unilateral.
2. Hipergeométrica (prueba exacta condicionada a los márgenes f_i, f_j y N,
   equivalente a la prueba exacta de Fisher unilateral sobre la tabla 2x2).

Se añade la corrección de Holm sobre las diez comparaciones para la prueba de
Poisson. Entrada: data/final/gap_analysis_v2.json (salida publicada del paso
10). Salida: results/prueba_brechas.csv.
"""

import csv
import json
from pathlib import Path

from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
ALPHA = 0.05
UMBRAL_GAP = 1.5

with open(ROOT / 'data' / 'final' / 'gap_analysis_v2.json', encoding='utf-8') as fh:
    gap = json.load(fh)

N = gap['N_corpus']
rows = []
for p in gap['pairs']:
    i, j = p['par']
    obs, lam = p['cooc_ij'], p['expected']
    fi, fj = p['f_i'], p['f_j']
    if obs <= lam:
        direccion = 'brecha'
        p_pois = stats.poisson.cdf(obs, lam)
        p_hyper = stats.hypergeom.cdf(obs, N, fi, fj)
    else:
        direccion = 'integracion'
        p_pois = stats.poisson.sf(obs - 1, lam)
        p_hyper = stats.hypergeom.sf(obs - 1, N, fi, fj)
    g = p['gap_score']
    rows.append({
        'par': f'C{i}-C{j}', 'kw_i': p['kw_i'], 'kw_j': p['kw_j'],
        'f_i': fi, 'f_j': fj, 'observada': obs, 'esperada': round(lam, 3),
        'gap_score': 'inf' if p['gap_score_inf'] else round(g, 3),
        'supera_umbral_1_5': bool(p['gap_score_inf'] or (g is not None and g > UMBRAL_GAP)),
        'direccion': direccion,
        'p_poisson': p_pois, 'p_hipergeometrica': p_hyper,
    })

# Holm sobre p_poisson
orden = sorted(range(len(rows)), key=lambda k: rows[k]['p_poisson'])
m = len(rows)
max_adj = 0.0
for rank, k in enumerate(orden):
    adj = min(1.0, (m - rank) * rows[k]['p_poisson'])
    max_adj = max(max_adj, adj)
    rows[k]['p_poisson_holm'] = max_adj
for r in rows:
    r['significativa_5pct'] = r['p_poisson'] < ALPHA
    r['significativa_holm_5pct'] = r['p_poisson_holm'] < ALPHA

out = ROOT / 'results' / 'prueba_brechas.csv'
out.parent.mkdir(exist_ok=True)
campos = ['par', 'kw_i', 'kw_j', 'f_i', 'f_j', 'observada', 'esperada', 'gap_score',
          'supera_umbral_1_5', 'direccion', 'p_poisson', 'p_poisson_holm',
          'p_hipergeometrica', 'significativa_5pct', 'significativa_holm_5pct']
with open(out, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=campos)
    w.writeheader()
    for r in rows:
        w.writerow({k: (f'{r[k]:.6g}' if isinstance(r[k], float) and k.startswith('p_') else r[k])
                    for k in campos})

print(f'N = {N}')
for r in rows:
    print(f"{r['par']:6s} obs={r['observada']:4d} esp={r['esperada']:7.2f} gap={r['gap_score']!s:>6} "
          f"{r['direccion']:11s} p_pois={r['p_poisson']:.4g} p_holm={r['p_poisson_holm']:.4g} "
          f"p_hiper={r['p_hipergeometrica']:.4g}")
print(f'Guardado en {out.relative_to(ROOT)}')
