"""Caracteriza los 5 macro-clústeres: tamaño, año promedio, citas promedio
(via OpenAlex cited_by_count), palabras clave dominantes (TF-IDF sobre
título+resumen+keywords), y documentos representativos (mayor citación
dentro del clúster)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import json
import re
from collections import Counter
import math

with open(ROOT / 'data' / 'final' / 'corpus_final.json', encoding='utf-8') as f:
    corpus = json.load(f)
with open(ROOT / 'data' / 'final' / 'openalex_data.json', encoding='utf-8') as f:
    openalex = json.load(f)
with open(ROOT / 'data' / 'final' / 'louvain_communities.json', encoding='utf-8') as f:
    louvain = json.load(f)

assignment = {int(k): v for k, v in louvain['assignment'].items()}
sizes = Counter(assignment.values())
top5_ids = [cid for cid, _ in sizes.most_common(5)]
print('IDs de los 5 clústeres principales (por tamaño):', top5_ids)

def get_text(r):
    parts = [r.get('Title', ''), r.get('Abstract', '')]
    kw = r.get('Keywords') or r.get('Author Keywords') or ''
    kwp = r.get('Keywords-Plus') or r.get('Index Keywords') or ''
    parts.append(kw)
    parts.append(kwp)
    return ' '.join(p for p in parts if p)

STOPWORDS = set("""the a an of and or to in for on with is are be by this that
we our study paper research analysis using approach model models based results
result show shows shown between among from as at it its their they can may also
not have has had these those such more most than into which when where while
under over via using use used than into finding findings we're such other one
two three data set among however both also new methods method effect effects
significant significantly related literature review journal article articles
finance financial investment investments portfolio portfolios""".split())

def tokenize(text):
    words = re.findall(r"[a-zA-Z][a-zA-Z\-]{2,}", text.lower())
    return [w for w in words if w not in STOPWORDS]

# documento -> tokens
doc_tokens = {}
for i, r in enumerate(corpus):
    doc_tokens[i] = tokenize(get_text(r))

# DF global (para TF-IDF)
df = Counter()
for toks in doc_tokens.values():
    for t in set(toks):
        df[t] += 1
N = len(corpus)

def top_terms_for_cluster(doc_ids, k=12):
    tf = Counter()
    for i in doc_ids:
        tf.update(doc_tokens[i])
    scores = {}
    for term, freq in tf.items():
        if df[term] < 3:
            continue
        idf = math.log(N / df[term])
        scores[term] = freq * idf
    return sorted(scores.items(), key=lambda x: -x[1])[:k]

print('\n=== CARACTERIZACIÓN DE LOS 5 MACRO-CLÚSTERES ===\n')
cluster_summaries = []
for rank, cid in enumerate(top5_ids, 1):
    doc_ids = [i for i, c in assignment.items() if c == cid]
    years = [int(corpus[i]['Year']) for i in doc_ids if corpus[i].get('Year', '').isdigit()]
    cites = []
    for i in doc_ids:
        doi = corpus[i].get('_doi_norm')
        oa = openalex.get(doi) if doi else None
        if oa and oa.get('cited_by_count') is not None:
            cites.append(oa['cited_by_count'])
    avg_year = sum(years) / len(years) if years else None
    avg_cites = sum(cites) / len(cites) if cites else None
    terms = top_terms_for_cluster(doc_ids)
    # documento representativo: mayor citación dentro del clúster
    def get_cites(i):
        doi = corpus[i].get('_doi_norm')
        oa = openalex.get(doi) if doi else None
        return oa.get('cited_by_count', 0) if oa else 0
    top_docs = sorted(doc_ids, key=get_cites, reverse=True)[:3]

    summary = {
        'cluster_rank': rank, 'cluster_id': cid, 'n_docs': len(doc_ids),
        'avg_year': avg_year, 'avg_citations': avg_cites,
        'top_terms': [t for t, s in terms],
        'top_docs': [{'title': corpus[i].get('Title'), 'year': corpus[i].get('Year'),
                       'citations': get_cites(i)} for i in top_docs],
    }
    cluster_summaries.append(summary)
    print(f"C{rank} (n={len(doc_ids)}, año prom. {avg_year:.1f}, citas prom. {avg_cites:.1f})")
    print(f"  Palabras clave dominantes: {', '.join(t for t,s in terms)}")
    print(f"  Documentos representativos:")
    for i in top_docs:
        print(f"    - [{get_cites(i)} citas, {corpus[i].get('Year')}] {corpus[i].get('Title')}")
    print()

with open(ROOT / 'data' / 'final' / 'cluster_summaries.json', 'w', encoding='utf-8') as f:
    json.dump(cluster_summaries, f, ensure_ascii=False, indent=2)
