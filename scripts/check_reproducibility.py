#!/usr/bin/env python3
"""Compara una re-ejecución de los pasos 06/08/09 contra los resultados
publicados en data/final/, para que cualquier lector pueda verificar qué
tan exactamente reproducen las cifras congeladas del Capítulo 2.

Uso:
    python3 scripts/06_build_network_coupling.py   # regenera en un directorio de prueba
    python3 scripts/08_tree_of_science.py
    python3 scripts/09_tos_classify.py
    python3 scripts/check_reproducibility.py <ruta_a_los_json_regenerados> data/final

Nota de reproducibilidad conocida: el corte tronco/hojas del Árbol de la
Ciencia depende de una centralidad de intermediación (betweenness)
APROXIMADA (muestreo k=800, semilla fija=42, ver 08_tree_of_science.py).
El muestreo aleatorio, aun con semilla fija, puede depender del orden de
iteración interno de NetworkX sobre el grafo, que a su vez puede variar
levemente entre entornos/versiones. En pruebas propias, esto reclasificó
~9% de los nodos en el margen del percentil de corte (40 de 465 nodos de
"tronco") entre tronco y hojas, SIN alterar los conteos agregados
(n_roots, n_trunk, n_leaves) ni ninguna cifra reportada en la Figura 2.5
o en el texto del capítulo. No es un defecto: es una propiedad conocida
de los algoritmos de centralidad aproximada sobre grafos grandes, y se
documenta aquí en vez de silenciarse.
"""
import json
import sys
from pathlib import Path


def load(p):
    with open(p, encoding='utf-8') as f:
        return json.load(f)


def compare(name, a, b):
    if a == b:
        print(f'  [EXACTO]     {name}')
        return
    if isinstance(a, dict) and isinstance(b, dict) and set(a) == set(b):
        diffs = sum(1 for k in a if a[k] != b[k])
        print(f'  [DIFERENCIA] {name}: {diffs}/{len(a)} claves distintas')
    elif isinstance(a, list) and isinstance(b, list):
        sa, sb = set(map(str, a)), set(map(str, b))
        print(f'  [DIFERENCIA] {name}: {len(sa - sb)} solo en nuevo, {len(sb - sa)} solo en publicado')
    else:
        print(f'  [DIFERENCIA] {name}: valores distintos ({a!r} vs {b!r})')


if __name__ == '__main__':
    new_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('data/final')
    ref_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('data/final')

    print('louvain_communities.json:')
    a, b = load(new_dir / 'louvain_communities.json'), load(ref_dir / 'louvain_communities.json')
    compare('modularity', a['modularity'], b['modularity'])
    compare('assignment', a['assignment'], b['assignment'])

    print('tos_classification.json:')
    a, b = load(new_dir / 'tos_classification.json'), load(ref_dir / 'tos_classification.json')
    for k in ('n_roots', 'n_trunk', 'n_leaves', 'total_network'):
        compare(k, a[k], b[k])
    compare('roots (conjunto)', sorted(a['roots']), sorted(b['roots']))
    compare('trunk (conjunto)', sorted(a['trunk']), sorted(b['trunk']))
