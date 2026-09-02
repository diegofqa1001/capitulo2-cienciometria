"""Parser del CSV exportado por Scopus."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import csv
import json
import re

def normalize_doi(doi):
    if not doi:
        return None
    d = doi.strip().lower()
    d = re.sub(r'^https?://(dx\.)?doi\.org/', '', d)
    d = d.rstrip('.')
    return d if d else None

if __name__ == '__main__':
    with open(ROOT / 'data' / 'raw' / 'scopus_raw.csv', encoding='utf-8-sig') as f:
        r = csv.DictReader(f)
        rows = list(r)
    print('Columnas disponibles:', r.fieldnames)
    print('Total filas Scopus:', len(rows))

    with_doi = sum(1 for row in rows if row.get('DOI'))
    print('Con DOI:', with_doi, '/', len(rows))

    # dedup interno por DOI y por EID (identificador único de Scopus)
    seen_doi = set()
    seen_eid = set()
    dup_doi = 0
    dup_eid = 0
    unique = []
    for row in rows:
        doi = normalize_doi(row.get('DOI'))
        eid = row.get('EID', '').strip()
        if eid and eid in seen_eid:
            dup_eid += 1
            continue
        if doi and doi in seen_doi:
            dup_doi += 1
            continue
        if eid:
            seen_eid.add(eid)
        if doi:
            seen_doi.add(doi)
        unique.append(row)
    print('Duplicados internos por EID:', dup_eid)
    print('Duplicados internos por DOI:', dup_doi)
    print('Scopus únicos tras dedup interno:', len(unique))

    with open(ROOT / 'data' / 'intermediate' / 'scopus_parsed.json', 'w', encoding='utf-8') as f:
        json.dump(unique, f, ensure_ascii=False)

    from collections import Counter
    dtypes = Counter(row.get('Document Type', 'N/A') for row in unique)
    print('Tipos de documento:', dtypes)
    years = [row.get('Year') for row in unique if row.get('Year')]
    print('Rango de años:', min(years), '-', max(years))
