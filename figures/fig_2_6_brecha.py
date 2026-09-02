"""Figura 2.6 — Esquema de la brecha teoría-práctica: C1 aislado del resto de la red temática."""
import sys
sys.path.insert(0, '.')
import json
from style import *
from matplotlib.patches import FancyArrowPatch, Circle
import matplotlib.patheffects as pe

with open('../data/final/cluster_summaries.json', encoding='utf-8') as f:
    clusters = {c['cluster_rank']: c for c in json.load(f)}

pos = {
    1: (1.9, 5.0),
    2: (6.1, 7.6),
    3: (6.4, 4.4),
    4: (7.0, 1.9),
    5: (9.0, 6.3),
}
labels = {
    1: 'C1\nOpciones reales',
    2: 'C2\nAmbigüedad',
    3: 'C3\nOptim. robusta',
    4: 'C4\nFuzzy MCDM',
    5: 'C5\nConectividad',
}

fig, ax = new_fig(w=10.4, h=7.6)
ax.set_xlim(0, 10.6)
ax.set_ylim(0.5, 9.0)
ax.set_aspect('equal', adjustable='box')
ax.axis('off')

# Zona conceptual: divisor sutil entre "práctica aislada" (C1) y "núcleo teórico"
ax.axvline(3.9, color=GRID, linewidth=1.1, linestyle=(0, (5, 4)), zorder=1)
ax.text(1.9, 8.55, 'PRÁCTICA APLICADA\n(aislada)', ha='center', fontsize=8.8, color=DIV_RED,
        family='Poppins', fontweight='medium', linespacing=1.4)
ax.text(7.1, 8.55, 'NÚCLEO TEÓRICO INTERCONECTADO', ha='center', fontsize=8.8, color=SEQ_BLUE[4],
        family='Poppins', fontweight='medium')

# --- Brechas de C1 con el resto (el hallazgo nuclear) ---
c1_gaps = {2: 4.54, 3: 1.57, 4: 7.73, 5: 7.20}
gmax = max(c1_gaps.values())
for j, g in c1_gaps.items():
    lw = 1.2 + 3.6 * (g / gmax)
    a = FancyArrowPatch(pos[1], pos[j], arrowstyle='-', linewidth=lw, color=DIV_RED,
                         linestyle=(0, (1, 1.4)), zorder=2, alpha=0.85,
                         connectionstyle='arc3,rad=0.06')
    ax.add_patch(a)
    frac = {2: 0.42, 3: 0.42, 4: 0.42, 5: 0.30}[j]
    mx, my = (pos[1][0]*(1-frac) + pos[j][0]*frac), (pos[1][1]*(1-frac) + pos[j][1]*frac)
    ax.text(mx, my, f'{g:.2f}', ha='center', va='center', fontsize=8.3, color=DIV_RED,
            family='Poppins', fontweight='bold', zorder=5,
            path_effects=[pe.withStroke(linewidth=2.6, foreground='white')])

# --- Integración C2-C3 (hallazgo secundario) ---
a = FancyArrowPatch(pos[2], pos[3], arrowstyle='-', linewidth=5.2, color=DIV_BLUE, zorder=2)
ax.add_patch(a)
ax.text((pos[2][0]+pos[3][0])/2 + 0.55, (pos[2][1]+pos[3][1])/2, '0.37\nintegración',
        ha='left', va='center', fontsize=8.3, color=DIV_BLUE, family='Poppins', fontweight='bold',
        linespacing=1.3, zorder=5)

# --- Resto de pares del núcleo (de-enfatizados; ver Figura 2.4 para valores exactos) ---
secondary_pairs = [(3, 4), (3, 5), (2, 4)]
for i, j in secondary_pairs:
    a = FancyArrowPatch(pos[i], pos[j], arrowstyle='-', linewidth=1.0, color=BASELINE,
                         linestyle=(0, (2, 2)), zorder=1, alpha=0.75)
    ax.add_patch(a)

# --- Nodos ---
for r, (x, y) in pos.items():
    n = clusters[r]['n_docs']
    radius = 0.42 + 0.34 * (n / 1202) ** 0.5
    circ = Circle((x, y), radius, facecolor=CAT[f'C{r}'], edgecolor='white', linewidth=2.2, zorder=4)
    ax.add_patch(circ)
    ax.text(x, y, labels[r], ha='center', va='center', fontsize=7.9, color='white',
            family='Poppins', fontweight='bold', zorder=5, linespacing=1.4)

# Nota sobre pares sin co-ocurrencia (C2–C5, C4–C5): no se dibujan (ausencia real de vínculo)
ax.text(9.3, 3.55, 'C2–C5 y C4–C5:\nsin co-ocurrencia\n(sin vínculo)', ha='center',
        fontsize=7.2, color=INK_MUTED, family='Poppins', linespacing=1.3)

title_block(fig, 'Figura 2.6 · La brecha teoría-práctica: C1 aislado del núcleo teórico',
            'C1 (práctica aplicada) muestra brecha significativa con los cuatro clústeres restantes; '
            'C2–C3 es la única integración temática del campo',
            x=0.035, y=0.975, sub_y=0.925)
source_note(fig, 'Fuente: elaboración propia a partir de la Tabla 2.3 (puntuación de brecha estructural, Burt 1992). '
                  'Grosor de línea = magnitud de la brecha; tamaño de nodo = número de documentos del clúster.')

plt.tight_layout(rect=[0.01, 0.02, 0.99, 0.895])
plt.savefig('fig_2_6_brecha.png', dpi=300, bbox_inches='tight', facecolor='white')
print('OK fig_2_6_brecha.png')
