"""Cribado de calidad sobre el corpus deduplicado: replica el criterio
declarado en el artículo/tesis ('documentos no revisados por pares o con
metadatos incompletos'). Reglas explícitas y auditables (nada implícito):

1) Metadatos incompletos: falta título, o falta año, o falta resumen (abstract).
2) Tipo de documento no elegible: excluye lo que no sea Article/Review
   (filtra erratas, editoriales mal indexados, etc. que se cuelen).
3) Idioma distinto de inglés (por si algo se escapó del filtro de plataforma).
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import json
from collections import Counter

with open(ROOT / 'data' / 'intermediate' / 'corpus_deduplicado.json', encoding='utf-8') as f:
    corpus = json.load(f)

def get_title(r):
    return (r.get('Title') or '').strip()

def get_year(r):
    return (r.get('Year') or '').strip()

def get_abstract(r):
    return (r.get('Abstract') or '').strip()

def get_doctype(r):
    # WoS usa 'Type' (Article, Review, etc.); Scopus usa 'Document Type'
    return (r.get('Type') or r.get('Document Type') or '').strip()

def get_language(r):
    return (r.get('Language') or r.get('Language of Original Document') or '').strip().lower()

reasons = Counter()
kept = []
excluded = []

for r in corpus:
    excl_reasons = []
    if not get_title(r):
        excl_reasons.append('sin_titulo')
    if not get_year(r):
        excl_reasons.append('sin_anio')
    if not get_abstract(r):
        excl_reasons.append('sin_resumen')
    dtype = get_doctype(r).lower()
    # Instrucción de Diego (2026-08-22): no excluir por co-clasificación
    # (Proceedings Paper, Book Chapter conviven con 'Article'/'Review' sin
    # problema -- se mantiene la publicación completa). Solo se excluye lo
    # formalmente retractado: mantener una publicación retractada como
    # literatura válida sería un error de exactitud, no un criterio de
    # cribado editorial.
    if dtype and 'retracted' in dtype:
        excl_reasons.append(f'retractado:{dtype}')
    lang = get_language(r)
    if lang and lang not in ('english', 'en'):
        excl_reasons.append(f'idioma:{lang}')

    if excl_reasons:
        for reason in excl_reasons:
            reasons[reason.split(':')[0]] += 1
        r['_exclusion_reasons'] = excl_reasons
        excluded.append(r)
    else:
        kept.append(r)

print('=== CRIBADO DE CALIDAD ===')
print(f'Corpus deduplicado de entrada: {len(corpus)}')
print(f'Excluidos: {len(excluded)}')
for reason, n in reasons.most_common():
    print(f'  - {reason}: {n}')
print(f'Corpus final (elegible): {len(kept)}')

with open(ROOT / 'data' / 'final' / 'corpus_final.json', 'w', encoding='utf-8') as f:
    json.dump(kept, f, ensure_ascii=False)
with open(ROOT / 'data' / 'intermediate' / 'corpus_excluidos_RAW_NO_PUBLICAR.json', 'w', encoding='utf-8') as f:
    json.dump(excluded, f, ensure_ascii=False)

# muestreo de los distintos 'tipo_no_elegible' para revisión manual rápida
tipo_excl = [r for r in excluded if any('tipo_no_elegible' in x for x in r['_exclusion_reasons'])]
print(f'\nMuestra de exclusiones por tipo no elegible ({len(tipo_excl)} total):')
for r in tipo_excl[:10]:
    print(' -', get_doctype(r), '|', get_title(r)[:80])
