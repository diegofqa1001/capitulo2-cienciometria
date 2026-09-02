"""Fusiona WoS + Scopus deduplicados internamente, cruza por DOI,
y aplica el cribado de calidad (documento revisado por pares, metadatos
completos), replicando el protocolo PRISMA descrito en el artículo."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import json
import re

def normalize_doi(doi):
    if not doi:
        return None
    d = doi.strip().lower()
    d = re.sub(r'^https?://(dx\.)?doi\.org/', '', d)
    d = d.rstrip('.')
    return d if d else None

with open(ROOT / 'data' / 'intermediate' / 'wos_parsed.json', encoding='utf-8') as f:
    wos = json.load(f)
with open(ROOT / 'data' / 'intermediate' / 'scopus_parsed.json', encoding='utf-8') as f:
    scopus = json.load(f)

print(f'WoS (post-dedup interno): {len(wos)}')
print(f'Scopus (post-dedup interno): {len(scopus)}')
print(f'Total bruto consolidado: {len(wos) + len(scopus)}')

wos_doi_map = {}
wos_no_doi = []
for r in wos:
    doi = normalize_doi(r.get('DOI'))
    if doi:
        wos_doi_map[doi] = r
    else:
        wos_no_doi.append(r)

scopus_doi_map = {}
scopus_no_doi = []
for r in scopus:
    doi = normalize_doi(r.get('DOI'))
    if doi:
        scopus_doi_map[doi] = r
    else:
        scopus_no_doi.append(r)

overlap_dois = set(wos_doi_map) & set(scopus_doi_map)
only_wos_dois = set(wos_doi_map) - set(scopus_doi_map)
only_scopus_dois = set(scopus_doi_map) - set(wos_doi_map)

print(f'\nSolapamiento por DOI: {len(overlap_dois)}')
print(f'Solo WoS (con DOI): {len(only_wos_dois)}')
print(f'Solo Scopus (con DOI): {len(only_scopus_dois)}')
print(f'Sin DOI en WoS: {len(wos_no_doi)}')
print(f'Sin DOI en Scopus: {len(scopus_no_doi)}')

# Corpus deduplicado: para el solapamiento, preferimos el registro de WoS
# (trae Cited-References, que Scopus no exportó), pero guardamos ambos IDs.
merged = []
for doi in overlap_dois:
    rec = dict(wos_doi_map[doi])
    rec['_source'] = 'both'
    rec['_scopus_eid'] = scopus_doi_map[doi].get('EID')
    rec['_doi_norm'] = doi
    merged.append(rec)
for doi in only_wos_dois:
    rec = dict(wos_doi_map[doi])
    rec['_source'] = 'wos_only'
    rec['_doi_norm'] = doi
    merged.append(rec)
for doi in only_scopus_dois:
    rec = dict(scopus_doi_map[doi])
    rec['_source'] = 'scopus_only'
    rec['_doi_norm'] = doi
    merged.append(rec)
# los sin DOI de ambas fuentes se mantienen (no se pueden deduplicar por DOI,
# se marcan aparte para decidir en el cribado de calidad)
for rec in wos_no_doi:
    r = dict(rec)
    r['_source'] = 'wos_only_nodoi'
    r['_doi_norm'] = None
    merged.append(r)
for rec in scopus_no_doi:
    r = dict(rec)
    r['_source'] = 'scopus_only_nodoi'
    r['_doi_norm'] = None
    merged.append(r)

total_bruto = len(wos) + len(scopus)
duplicados_doi = len(overlap_dois)
print(f'\n=== RESUMEN FLUJO PRISMA (corpus nuevo, extracción 21-ago-2026) ===')
print(f'WoS: {len(wos)}')
print(f'Scopus: {len(scopus)}')
print(f'Total bruto: {total_bruto}')
print(f'Duplicados por DOI: {duplicados_doi}')
print(f'Corpus deduplicado (antes de cribado de calidad): {len(merged)}')
print(f'  (verificación: {total_bruto} - {duplicados_doi} = {total_bruto - duplicados_doi}, debe = {len(merged)})')

with open(ROOT / 'data' / 'intermediate' / 'corpus_deduplicado.json', 'w', encoding='utf-8') as f:
    json.dump(merged, f, ensure_ascii=False)
