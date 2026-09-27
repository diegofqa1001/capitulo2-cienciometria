"""Figura 2.6 — Esquema de la brecha teoría-práctica: C1 aislado del resto de la red temática.

Los valores proceden de data/final/gap_analysis_v2.json (Tabla 2.3; Figura 2.5
para la matriz completa) y los p-valores de results/prueba_brechas.csv
(scripts/11_prueba_brechas_poisson.py). Convención de trazo:
- rojo punteado: índice > 1,5 y p < 0,05 (prueba de Poisson);
- rojo tenue discontinuo: índice > 1,5 con p >= 0,05;
- gris: índice próximo a 1 (sin brecha);
- azul continuo: integración por encima de lo esperado.
"""
import sys
sys.path.insert(0, '.')
import csv
import json
from style import *
from matplotlib.patches import FancyArrowPatch, Circle, FancyBboxPatch
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe

with open('../data/final/cluster_summaries.json', encoding='utf-8') as f:
    clusters = {c['cluster_rank']: c for c in json.load(f)}
with open('../data/final/gap_analysis_v2.json', encoding='utf-8') as f:
    gap = {tuple(p['par']): p for p in json.load(f)['pairs']}
pval = {}
with open('../results/prueba_brechas.csv', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        a, b = [int(x[1:]) for x in r['par'].split('-')]
        pval[(a, b)] = float(r['p_poisson'])

pos = {
    1: (1.9, 5.0),
    2: (5.9, 7.2),
    3: (6.2, 4.5),
    4: (6.8, 1.9),
    5: (9.7, 5.6),
}
labels = {
    1: 'C1\nOpciones reales',
    2: 'C2\nAmbigüedad',
    3: 'C3\nOptim. robusta',
    4: 'C4\nDecisión\ndifusa',
    5: 'C5\nConectividad',
}
GMAX = gap[(1, 4)]['gap_score']
FAINT_RED = '#e8a77a'


def radius(r):
    return 0.42 + 0.34 * (clusters[r]['n_docs'] / 1202) ** 0.5


def edge_label(i, j, frac, text, color, dx=0.0, dy=0.0):
    (x1, y1), (x2, y2) = pos[i], pos[j]
    mx, my = x1 * (1 - frac) + x2 * frac + dx, y1 * (1 - frac) + y2 * frac + dy
    ax.text(mx, my, text, ha='center', va='center', fontsize=8.3, color=color,
            family='Poppins', fontweight='bold', zorder=6, linespacing=1.25,
            path_effects=[pe.withStroke(linewidth=2.8, foreground='white')])


def gap_edge(i, j, frac, dx=0.0, dy=0.0, rad=0.06):
    key = (min(i, j), max(i, j))
    g = gap[key]['gap_score']
    sig = pval[key] < 0.05
    lw = 1.2 + 3.6 * (g / GMAX)
    if sig:
        a = FancyArrowPatch(pos[i], pos[j], arrowstyle='-', linewidth=lw, color=DIV_RED,
                             linestyle=(0, (1, 1.4)), zorder=2, alpha=0.9,
                             connectionstyle=f'arc3,rad={rad}')
        txt, col = coma(g), DIV_RED
    else:
        a = FancyArrowPatch(pos[i], pos[j], arrowstyle='-', linewidth=lw, color=FAINT_RED,
                             linestyle=(0, (4, 3)), zorder=2, alpha=0.9,
                             connectionstyle=f'arc3,rad={rad}')
        txt, col = f'{coma(g)}\n(p = {coma(pval[key], 2)})', '#b0602b'
    ax.add_patch(a)
    edge_label(i, j, frac, txt, col, dx, dy)


fig, ax = new_fig(w=10.8, h=8.8)
ax.set_xlim(0, 10.9)
ax.set_ylim(-0.4, 10.4)
ax.set_aspect('equal', adjustable='box')
ax.axis('off')

# Divisor entre práctica aplicada y el resto del campo
ax.axvline(3.9, color=GRID, linewidth=1.1, linestyle=(0, (5, 4)), zorder=1)
ax.text(1.9, 9.75, 'PRÁCTICA APLICADA\n(aislada)', ha='center', fontsize=8.8, color=DIV_RED,
        family='Poppins', fontweight='medium', linespacing=1.4)

# Núcleo teórico: C2, C3 y C4 dentro de un recuadro; C5 fuera
box = FancyBboxPatch((4.75, 0.85), 3.35, 7.2, boxstyle='round,pad=0.05,rounding_size=0.35',
                     facecolor='#f3f7fb', edgecolor=SEQ_BLUE[2], linewidth=1.0, zorder=0)
ax.add_patch(box)
ax.text(6.42, 0.35, 'NÚCLEO TEÓRICO (C2–C3 integrados)', ha='center', fontsize=8.8,
        color=SEQ_BLUE[4], family='Poppins', fontweight='medium', linespacing=1.4)
ax.text(9.7, 7.0, 'ESPECIALIDAD\nEMERGENTE', ha='center', fontsize=8.8, color=CAT['C5'],
        family='Poppins', fontweight='medium', linespacing=1.4)

# Brechas de C1 con los otros cuatro clústeres (hallazgo nuclear)
gap_edge(1, 2, 0.42)
gap_edge(1, 3, 0.42)
gap_edge(1, 4, 0.42)
gap_edge(1, 5, 0.5, dy=3.95, rad=-1.0)

# Brechas dentro del campo teórico y con C5
gap_edge(3, 4, 0.50, dx=0.45)
gap_edge(3, 5, 0.55, dy=-0.55)

# Integración C2–C3
ax.add_patch(FancyArrowPatch(pos[2], pos[3], arrowstyle='-', linewidth=5.2, color=DIV_BLUE, zorder=2))
ax.text((pos[2][0] + pos[3][0]) / 2 + 0.5, (pos[2][1] + pos[3][1]) / 2, f"{coma(gap[(2, 3)]['gap_score'])}\nintegración",
        ha='left', va='center', fontsize=8.3, color=DIV_BLUE, family='Poppins', fontweight='bold',
        linespacing=1.3, zorder=6, path_effects=[pe.withStroke(linewidth=2.8, foreground='white')])

# C2–C4: sin brecha (co-ocurrencia próxima a la esperada)
ax.add_patch(FancyArrowPatch(pos[2], pos[4], arrowstyle='-', linewidth=1.1, color=BASELINE,
                             linestyle=(0, (2, 2)), zorder=1, connectionstyle='arc3,rad=0.35'))
edge_label(2, 4, 0.7, f"{coma(gap[(2, 4)]['gap_score'])}", INK_MUTED, dx=-1.05)

# Nodos
for r, (x, y) in pos.items():
    ax.add_patch(Circle((x, y), radius(r), facecolor=CAT[f'C{r}'], edgecolor='white', linewidth=2.2, zorder=4))
    ax.text(x, y, labels[r], ha='center', va='center', fontsize=7.9, color='white',
            family='Poppins', fontweight='bold', zorder=5, linespacing=1.4)

# Pares sin co-ocurrencia (no se dibujan)
ax.text(9.7, 3.3, 'Sin co-ocurrencia\n(no se dibujan):\n'
        f'C2–C5 (p = {coma(pval[(2, 5)], 3)})\nC4–C5 (p = {coma(pval[(4, 5)], 2)})',
        ha='center', fontsize=7.4, color=INK_SECONDARY, family='Poppins', linespacing=1.35)

# Leyenda de trazos
handles = [
    Line2D([0], [0], color=DIV_RED, lw=2.4, linestyle=(0, (1, 1.2)), label='Brecha > 1,5 con p < 0,05'),
    Line2D([0], [0], color=FAINT_RED, lw=2.4, linestyle=(0, (4, 3)), label='Brecha > 1,5 con p ≥ 0,05'),
    Line2D([0], [0], color=BASELINE, lw=1.4, linestyle=(0, (2, 2)), label='Sin brecha (≈ 1)'),
    Line2D([0], [0], color=DIV_BLUE, lw=4.0, label='Integración (< 1)'),
]
leg = ax.legend(handles=handles, loc='lower center', bbox_to_anchor=(0.5, -0.02), ncol=4,
                frameon=False, fontsize=8.0, handlelength=2.6, columnspacing=1.4)
for t in leg.get_texts():
    t.set_color(INK_SECONDARY)

title_block(fig, 'Figura 2.6 · La brecha teoría-práctica', None)

plt.tight_layout(rect=[0.01, 0.02, 0.99, 0.99])
plt.savefig('fig_2_6_brecha.png', dpi=300, bbox_inches='tight', facecolor='white')
print('OK fig_2_6_brecha.png')
