"""Figura 2.5 — Estratificación Tree of Science (Robledo, Osorio y López, 2014)."""
import sys
sys.path.insert(0, '.')
import json
from style import *
import numpy as np

with open('../data/final/tos_classification.json', encoding='utf-8') as f:
    tos = json.load(f)

n_roots, n_trunk, n_leaves = tos['n_roots'], tos['n_trunk'], tos['n_leaves']
total = tos['total_network']

tiers = [
    ('Hojas', n_leaves, SEQ_BLUE[1], 'literatura periférica y de aplicación reciente'),
    ('Tronco', n_trunk, SEQ_BLUE[3], 'obras estructurantes de conexión temática'),
    ('Raíces', n_roots, SEQ_BLUE[5], 'obras seminales y fundacionales del campo'),
]

fig, ax = new_fig(w=9.6, h=5.6)
ax.set_position([0.30, 0.20, 0.62, 0.58])

y_pos = [2, 1, 0]
xmax = total * 1.02
for (name, val, color, desc), y in zip(tiers, y_pos):
    ax.barh(y, val, color=color, height=0.62, zorder=3)
    pct = 100 * val / total
    ax.text(val + xmax * 0.015, y, f'{val:,}'.replace(',', '.') + f'  ·  {pct:.2f} %',
            va='center', ha='left', fontsize=11, color=INK_PRIMARY, family='Poppins', fontweight='bold')
    ax.text(-xmax * 0.02, y + 0.30, name, va='center', ha='right', fontsize=12.5,
            color=INK_PRIMARY, family='Poppins', fontweight='medium')
    ax.text(-xmax * 0.02, y - 0.28, desc, va='center', ha='right', fontsize=8.0,
            color=INK_MUTED, family='Poppins')

ax.set_xlim(0, xmax)
ax.set_ylim(-0.6, 2.6)
ax.set_yticks([])
style_axes(ax, hide_spines=('top', 'right', 'left'), grid_axis='x')
ax.set_xlabel('Número de nodos en la red de citación (N = %s totales, corpus + externos)' % f'{total:,}'.replace(',', '.'),
              fontsize=9, color=INK_SECONDARY, family='Poppins')
ax.tick_params(axis='x', labelsize=9)

title_block(fig, 'Figura 2.5 · Estratificación Tree of Science de la red de citación',
            'Distribución fuertemente sesgada: solo 1,71 % de los nodos son obras raíz',
            x=0.045, y=0.965, sub_y=0.90)
source_note(fig, 'Fuente: elaboración propia. Clasificación por root_score (grado de salida y cercanía normalizados, '
                  'convención saliente) y percentiles sobre la red completa de citación (corpus final + referencias externas).')

plt.savefig('fig_2_3_tos.png', dpi=300, bbox_inches='tight', facecolor='white')
print('OK fig_2_3_tos.png')
