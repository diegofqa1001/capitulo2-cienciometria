# Cartografía cienciométrica del Capítulo 2 — brecha teoría-práctica

Código y datos de reproducibilidad para la cartografía cienciométrica del
Capítulo 2 de la tesis doctoral *"Modelo adaptativo de recomendación para el
diseño de portafolios de inversión en renta variable bajo incertidumbre,
mediante el operador OWA y perfiles conductuales de riesgo"*: la revisión que
identifica cinco macro-clústeres temáticos en la literatura sobre selección de
portafolios bajo incertidumbre, calcula sus brechas estructurales (Burt, 1992)
y documenta la brecha teoría-práctica entre la investigación aplicada y el
núcleo teórico del campo.

**Este repositorio no es el mismo que
[`prisma-repo`](https://github.com/diegofqa1001/prisma-repo).** `prisma-repo`
documenta una revisión PRISMA distinta y más pequeña (727 → 560 registros)
que sustenta la taxonomía difusa-OWA de perfiles de riesgo conductual del
Capítulo 3. Este repositorio documenta un corpus distinto y mucho mayor
(5.188 → 3.643 registros) que sustenta la cartografía cienciométrica del
Capítulo 2. Comparten protocolo metodológico (PRISMA
2020, Web of Science + Scopus) pero no comparten corpus ni resultados.

## Qué encuentra aquí un lector, jurado o par evaluador

- El pipeline completo, en diez pasos numerados, desde el export crudo de
  Web of Science/Scopus hasta la cartografía de clústeres y brechas.
- Los datos derivados que sustentan cada cifra, tabla y figura del capítulo.
- Las seis figuras del Capítulo 2 (más la Figura 1.4 del Capítulo 1, que se
  construye sobre este mismo corpus) y los scripts que las generan.
- Un script de verificación (`scripts/check_reproducibility.py`) que compara
  una re-ejecución contra los resultados publicados.

## Qué NO se publica, y por qué

Los registros crudos de Web of Science y Scopus (título, resumen, palabras
clave, referencias citadas, afiliaciones) **no se redistribuyen** en este
repositorio: su licenciamiento (Clarivate Analytics y Elsevier,
respectivamente) prohíbe la redistribución de exports masivos, incluso con
fines académicos de reproducibilidad. Esta es una restricción legal, no una
elección de conveniencia.

En su lugar se publican los **datos derivados**: identificadores DOI, año,
fuente, asignación de clúster y estrato Tree-of-Science por documento —
información puramente factual y de autoría propia (el resultado analítico
del pipeline), no el contenido protegido de los editores. También se
publican los metadatos abiertos de OpenAlex (CC0), que sustituyen a las
"Cited References" de WoS/Scopus para construir la red de acoplamiento
bibliográfico sin infringir licencia alguna.

Consecuencia práctica para la reproducibilidad: los pasos 1-4 (extracción,
deduplicación, cribado) y los pasos 7 y 10 (caracterización de clústeres y
cálculo de brechas, que requieren el texto de título/resumen/palabras clave
para el TF-IDF) **no pueden re-ejecutarse con los datos aquí publicados** —
requieren que el lector obtenga su propio export de Web of Science y Scopus
bajo su propia licencia institucional. Los pasos 5, 6, 8 y 9 (enriquecimiento
con OpenAlex, red de acoplamiento bibliográfico, Tree of Science y
estratificación) **sí son completamente re-ejecutables** con los datos
publicados en `data/final/`, y se verificaron de forma independiente antes
de publicar este repositorio (ver más abajo).

## Estructura

```
capitulo2-cienciometria/
├── scripts/
│   ├── 01_parse_wos.py              # requiere export propio de WoS (no incluido)
│   ├── 02_parse_scopus.py           # requiere export propio de Scopus (no incluido)
│   ├── 03_merge_dedup.py            # fusión + deduplicación por DOI
│   ├── 04_quality_screen.py         # cribado de calidad (par revisado, metadatos completos)
│   ├── 05_fetch_openalex.py         # enriquecimiento con OpenAlex (API abierta) — re-ejecutable
│   ├── 06_build_network_coupling.py # red de acoplamiento bibliográfico — re-ejecutable
│   ├── 07_characterize_clusters.py  # requiere título/resumen (no incluidos)
│   ├── 08_tree_of_science.py        # centralidades de red — re-ejecutable
│   ├── 09_tos_classify.py           # estratificación raíces/tronco/hojas — re-ejecutable
│   ├── 10_gap_analysis.py           # requiere palabras clave (no incluidas)
│   └── check_reproducibility.py     # compara una re-ejecución contra data/final/
├── data/
│   ├── raw/            (vacío — el lector coloca aquí sus propios exports WoS/Scopus)
│   ├── intermediate/   (se genera al ejecutar los pasos 1-4)
│   └── final/           datos derivados publicados (ver tabla abajo)
└── figures/             las 6 figuras del Capítulo 2 + la Figura 1.4 del Capítulo 1, con sus scripts
```

## Datos publicados en `data/final/`

| Archivo | Contenido | Origen |
|---|---|---|
| `corpus_final_metadatos.json` | 3.643 registros: índice, DOI, año, fuente, clúster, estrato ToS | Derivado propio |
| `corpus_excluidos_metadatos.json` | 66 registros excluidos en el cribado de calidad: DOI, año, fuente, motivo | Derivado propio |
| `openalex_data.json` | Metadatos OpenAlex (3.439 DOIs resueltos): referencias citadas, citas recibidas, año, título | OpenAlex (CC0) |
| `louvain_communities.json` | Asignación de clúster y modularidad de la red de acoplamiento bibliográfico | Derivado propio |
| `cluster_summaries.json` | Tamaño, año promedio, citas promedio y términos dominantes por clúster | Derivado propio |
| `tos_centralities.json` | Grado de entrada/salida, cercanía y centralidad de intermediación por nodo | Derivado propio |
| `tos_classification.json` | Estratificación raíces/tronco/hojas (Tree of Science) | Derivado propio |
| `gap_analysis_v2.json` | Puntuación de brecha estructural (Burt, 1992) para los 10 pares de clústeres | Derivado propio |

## Pipeline: de 5.188 registros brutos a 3.643 en el corpus final

1. **Extracción** — 2.529 registros únicos internos de Scopus + 2.659 de Web of Science = 5.188 identificados (Figura 2.1).
2. **Deduplicación cruzada por DOI** — 5.188 → 3.709 registros únicos.
3. **Cribado de calidad** (documento revisado por pares, metadatos completos) — 3.709 → 3.643 (66 excluidos).
4. **Enriquecimiento OpenAlex** — resolución de referencias citadas y citas recibidas para 3.439 de los 3.643 DOIs.
5. **Red de acoplamiento bibliográfico + Louvain** — cinco macro-clústeres temáticos (modularidad = 0,544).
6. **Tree of Science** — estratificación raíces/tronco/hojas sobre la red de citación (corpus + referencias externas).
7. **Análisis de brechas estructurales** (Burt, 1992) — 8 de 10 pares de clústeres con brecha significativa.

## Nota de reproducibilidad conocida

El corte tronco/hojas del Tree of Science depende de una centralidad de
intermediación (*betweenness*) **aproximada** (muestreo `k=800`, semilla
fija `42`). En verificación propia, una re-ejecución completa de los pasos
6, 8 y 9 sobre los datos aquí publicados reprodujo **exactamente** la
asignación de clústeres de Louvain, la modularidad, y los conteos agregados
y el conjunto de raíces del Tree of Science; el conjunto de nodos en el
margen del percentil de corte tronco/hojas varió en un 9% (40 de 465 nodos),
sin alterar ningún conteo agregado ni ninguna cifra reportada en el
Capítulo 2. Es una propiedad conocida de la centralidad de intermediación
aproximada sobre grafos grandes, no un defecto del pipeline, y se documenta
aquí para que quede trazable en vez de silenciada. Ejecute
`scripts/check_reproducibility.py` para repetir esta verificación.

Numeración de figuras: sigue el orden de aparición en la monografía (Figura 2.3 = estratificación Tree of Science; 2.4 = caracterización de clústeres; 2.5 = matriz de brechas; 2.6 = brecha teoría-práctica).

## Cómo verificar las cifras del capítulo sin volver a ejecutar nada

Todas las cifras, tablas y figuras del Capítulo 2 son reconstruibles
directamente a partir de los archivos en `data/final/` — no es necesario
tener acceso a Web of Science o Scopus para **verificar** lo reportado
(solo para reproducir desde cero los pasos 1, 2, 3, 7 y 10, que dependen de
contenido con licencia editorial). Para regenerar las seis figuras del
capítulo:

```bash
cd figures
python3 fig_2_1_prisma.py   # requiere solo los conteos documentados en el propio script
python3 fig_2_2_temporal.py
python3 fig_2_3_tos.py
python3 fig_2_4_clusters.py
python3 fig_2_5_gap_matrix.py
python3 fig_2_6_brecha.py
python3 fig_1_4_brecha_diseno.py
```

## Licencia

Código bajo licencia MIT (ver `LICENSE`). Dependencias en `requirements.txt` (Python ≥ 3.10). Los
datos derivados en `data/final/` se publican bajo CC BY 4.0. Los metadatos
de OpenAlex incluidos en `openalex_data.json` son CC0 (OpenAlex, 2024).

## Cita

Quintero-Avellaneda, D. F. (2026). *capitulo2-cienciometria: cartografía cienciométrica de la selección de portafolios bajo incertidumbre* [Software y datos derivados]. GitHub. https://github.com/diegofqa1001/capitulo2-cienciometria

Forma parte del ecosistema de repositorios de la tesis doctoral (Universidad Nacional de Colombia, Sede Manizales): `repo_OWA` (DOI 10.5281/zenodo.20695173), `owa-adaptive`, `motor-owa-v2`, `validacion-oe4`, `front-motor-owa`, `owa-typology` y `prisma-repo`.
