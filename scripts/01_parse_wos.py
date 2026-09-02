"""Parser manual para BibTeX exportado por Web of Science.
No depende de librerías externas: el formato de WoS es regular
(Campo = {valor, puede tener saltos de línea con indentación}),
separado por comas al final de cada campo, entrada delimitada por
'@article{ WOS:..., ... }' (u otros tipos: @misc, @proceedings, etc.)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import re
import glob
import json

FIELD_RE = re.compile(r'^([A-Za-z][A-Za-z0-9_-]*)\s*=\s*\{', re.MULTILINE)

def parse_bib_file(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        text = f.read()
    # dividir en entradas por '@tipo{ WOS:...,'
    entries = re.split(r'\n@(\w+)\{\s*', text)
    records = []
    # entries[0] es preámbulo vacío; luego alterna tipo, resto
    for i in range(1, len(entries), 2):
        entry_type = entries[i]
        body = entries[i + 1]
        # el ID de WoS es lo primero hasta la primera coma
        m = re.match(r'([^,]+),', body)
        wos_id = m.group(1).strip() if m else None
        rec = {'_type': entry_type, '_wos_id': wos_id}
        # parsear campos: nombre = {valor...} hasta el cierre de llave que
        # precede a una coma+salto de línea+nombre de campo, o fin de entrada
        pos = 0
        matches = list(FIELD_RE.finditer(body))
        for j, fm in enumerate(matches):
            field_name = fm.group(1)
            start = fm.end()
            end = matches[j + 1].start() if j + 1 < len(matches) else len(body)
            raw_val = body[start:end]
            # quitar el cierre '},\n' final de este campo si quedó incluido
            raw_val = re.sub(r'\}\s*,?\s*$', '', raw_val.rstrip())
            # normalizar espacios/saltos de línea de continuación
            val = re.sub(r'\s+', ' ', raw_val).strip()
            rec[field_name] = val
        records.append(rec)
    return records

def normalize_doi(doi):
    if not doi:
        return None
    d = doi.strip().lower()
    d = re.sub(r'^https?://(dx\.)?doi\.org/', '', d)
    d = d.rstrip('.')
    return d if d else None

if __name__ == '__main__':
    all_records = []
    files = sorted(glob.glob(str(ROOT / 'data' / 'raw' / 'wos_*.bib')))
    for fpath in files:
        recs = parse_bib_file(fpath)
        print(fpath, '->', len(recs), 'registros')
        all_records.extend(recs)
    print('TOTAL WoS:', len(all_records))

    with_doi = sum(1 for r in all_records if r.get('DOI'))
    print('Con DOI:', with_doi, '/', len(all_records))

    # dedup interno por WOS id y por DOI
    seen_ids = set()
    seen_dois = set()
    dup_id = 0
    dup_doi = 0
    unique = []
    for r in all_records:
        wid = r.get('_wos_id')
        doi = normalize_doi(r.get('DOI'))
        if wid and wid in seen_ids:
            dup_id += 1
            continue
        if doi and doi in seen_dois:
            dup_doi += 1
            continue
        if wid:
            seen_ids.add(wid)
        if doi:
            seen_dois.add(doi)
        unique.append(r)
    print('Duplicados internos por WOS-id:', dup_id)
    print('Duplicados internos por DOI (entre lotes):', dup_doi)
    print('WoS únicos tras dedup interno:', len(unique))

    with open(ROOT / 'data' / 'intermediate' / 'wos_parsed.json', 'w', encoding='utf-8') as f:
        json.dump(unique, f, ensure_ascii=False)

    # muestreo de tipos de documento
    from collections import Counter
    types = Counter(r.get('_type') for r in unique)
    print('Tipos de entrada BibTeX:', types)
    doctypes = Counter(r.get('Document-Type', r.get('Article-Type', 'N/A')) for r in unique)
    print('Sample fields de un registro:', list(unique[0].keys()))
