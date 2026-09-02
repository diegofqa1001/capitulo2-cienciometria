"""Figura 2.3 — Caracterización de los cinco macro-clústeres temáticos."""
import sys
sys.path.insert(0, '.')
import json
from style import *

with open('../data/final/cluster_summaries.json', encoding='utf-8') as f:
    clusters = json.load(f)

labels_short = {
    1: 'C1 · Opciones reales /\ninversión corporativa',
    2: 'C2 · Aversión a la\nambigüedad',
    3: 'C3 · Optimización\nrobusta',
    4: 'C4 · Decisión\nmulticriterio difusa',
    5: 'C5 · Conectividad\nde crisis',
}

fig, ax = new_fig(w=9.6, h=6.4)

xs = [c['avg_year'] for c in clusters]
ys = [c['avg_citations'] for c in clusters]
ns = [c['n_docs'] for c in clusters]
ranks = [c['cluster_rank'] for c in clusters]

# escala de tamaño de burbuja por área (no por radio) para no exagerar diferencias
max_n = max(ns)
size_scale = 5200.0
sizes = [size_scale * (n / max_n) for n in ns]

for c, x, y, s, r in zip(clusters, xs, ys, sizes, ranks):
    color = CAT[f'C{r}']
    ax.scatter([x], [y], s=[s], color=color, alpha=0.88, edgecolor='white',
               linewidth=1.6, zorder=4)

style_axes(ax, hide_spines=('top', 'right'), grid_axis='both')
ax.set_xlabel('Año de publicación promedio', fontsize=10, color=INK_SECONDARY, family='Poppins')
ax.set_ylabel('Citaciones promedio por documento', fontsize=10, color=INK_SECONDARY, family='Poppins')
ax.set_xlim(2013.5, 2025.3)
ax.set_ylim(0, 70)

# Etiquetas directas (obligatorias por la regla de relieve del sistema de diseño
# para >=3 series en un gráfico de todos-los-pares-visibles)
label_offsets = {
    1: (0, -13),
    2: (0, 13),
    3: (0, 13),
    4: (0, -14),
    5: (0, 11),
}
for c, x, y, r in zip(clusters, xs, ys, ranks):
    dx, dy = label_offsets[r]
    ax.annotate(labels_short[r], xy=(x, y), xytext=(x + dx * 0.012 + (dx and 0), y + dy),
                ha='center', va='center', fontsize=8.4, color=INK_PRIMARY, family='Poppins',
                fontweight='medium', linespacing=1.35)
    ax.annotate(f"n = {c['n_docs']}", xy=(x, y), xytext=(x + dx * 0.012, y + dy - 5.4),
                ha='center', va='center', fontsize=7.4, color=INK_MUTED, family='Poppins')

title_block(fig, 'Figura 2.3 · Caracterización de los cinco macro-clústeres temáticos',
            'Tamaño de burbuja = número de documentos · detección de comunidades de Louvain (resolución 0,5; Q = 0,544)',
            x=0.07, y=0.965, sub_y=0.925)
source_note(fig, 'Fuente: elaboración propia a partir del corpus final (N = 3.643) y del acoplamiento bibliográfico (OpenAlex, referenced_works).')

plt.tight_layout(rect=[0.02, 0.03, 0.98, 0.885])
plt.savefig('fig_2_4_clusters.png', dpi=300, bbox_inches='tight', facecolor='white')
print('OK fig_2_4_clusters.png')
