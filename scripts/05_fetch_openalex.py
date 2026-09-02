"""Consulta OpenAlex (base de datos científica abierta, gratuita, y sí
redistribuible) para obtener, por DOI, el registro completo con sus
referencias citadas y su conteo de citas recibidas. Esto sustituye la
necesidad de las 'Cited References' de WoS/Scopus (que no se pueden
republicar) y nos da cobertura de citación PAREJA para todo el corpus
(WoS-only, Scopus-only, y ambos), no solo para el 72% que ya traía CR de WoS.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import json
import time
import urllib.request
import urllib.parse
import urllib.error

MAILTO = 'tu-email@ejemplo.com'  # reemplaza por tu correo: OpenAlex prioriza ("polite pool") las solicitudes con contacto identificado
BATCH_SIZE = 50
BASE_URL = 'https://api.openalex.org/works'

with open(ROOT / 'data' / 'final' / 'corpus_final_metadatos.json', encoding='utf-8') as f:
    corpus = json.load(f)

dois = [r['doi'] for r in corpus if r.get('doi')]
print(f'DOIs a consultar: {len(dois)}')

results = {}
errors = []

def fetch_batch(batch_dois, attempt=1):
    filt = '|'.join(urllib.parse.quote(d, safe='') for d in batch_dois)
    url = f'{BASE_URL}?filter=doi:{filt}&per_page=100&mailto={MAILTO}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': f'mailto:{MAILTO}'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        return data.get('results', [])
    except urllib.error.HTTPError as e:
        if e.code == 429 and attempt <= 5:
            wait = 3 * attempt
            print(f'  429, esperando {wait}s (intento {attempt})...')
            time.sleep(wait)
            return fetch_batch(batch_dois, attempt + 1)
        errors.append((batch_dois, str(e)))
        return []
    except Exception as e:
        if attempt <= 3:
            time.sleep(2 * attempt)
            return fetch_batch(batch_dois, attempt + 1)
        errors.append((batch_dois, str(e)))
        return []

n_batches = (len(dois) + BATCH_SIZE - 1) // BATCH_SIZE
for i in range(0, len(dois), BATCH_SIZE):
    batch = dois[i:i + BATCH_SIZE]
    batch_num = i // BATCH_SIZE + 1
    recs = fetch_batch(batch)
    for rec in recs:
        doi_norm = (rec.get('doi') or '').replace('https://doi.org/', '').lower()
        if doi_norm:
            results[doi_norm] = rec
    print(f'Lote {batch_num}/{n_batches}: {len(recs)}/{len(batch)} encontrados (acumulado: {len(results)})')
    time.sleep(0.15)

print(f'\nTotal encontrados en OpenAlex: {len(results)} / {len(dois)}')
print(f'Errores de lote: {len(errors)}')

# guardamos solo los campos que necesitamos para no inflar el archivo:
# id, doi, referenced_works (lista de IDs OpenAlex citados), cited_by_count,
# concepts/topics (para triangulación temática opcional)
slim = {}
for doi, rec in results.items():
    slim[doi] = {
        'openalex_id': rec.get('id'),
        'referenced_works': rec.get('referenced_works', []),
        'cited_by_count': rec.get('cited_by_count'),
        'publication_year': rec.get('publication_year'),
        'title': rec.get('display_name'),
    }

with open(ROOT / 'data' / 'final' / 'openalex_data.json', 'w', encoding='utf-8') as f:
    json.dump(slim, f, ensure_ascii=False)

with_refs = sum(1 for v in slim.values() if v['referenced_works'])
print(f'Con referenced_works no vacío: {with_refs} / {len(slim)}')
