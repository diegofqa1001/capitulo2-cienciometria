"""Figura 2.4 — Matriz divergente de brechas estructurales entre clústeres (Burt, 1992)."""
import sys
sys.path.insert(0, '.')
import json
import numpy as np
from style import *
import matplotlib.patches as mpatches

with open('../data/final/gap_analysis_v2.json', encoding='utf-8') as f:
    data = json.load(f)

labels = {1: 'C1', 2: 'C2', 3: 'C3', 4: 'C4', 5: 'C5'}
n = 5
mat = np.full((n, n), np.nan)
inf_mask = np.zeros((n, n), dtype=bool)
for p in data['pairs']:
    i, j = p['par']
    v = p['gap_score']
    if p['gap_score_inf']:
        inf_mask[i-1, j-1] = True
        inf_mask[j-1, i-1] = True
        mat[i-1, j-1] = np.nan
        mat[j-1, i-1] = np.nan
    else:
        mat[i-1, j-1] = v
        mat[j-1, i-1] = v

finite_vals = [p['gap_score'] for p in data['pairs'] if not p['gap_score_inf']]
vmax = max(finite_vals)   # ~7.73
vmin = min(finite_vals)   # ~0.37

def color_for(v):
    """Normaliza en escala log centrada en 1 (sin brecha) y mapea a DIV_CMAP."""
    if v is None or np.isnan(v):
        return '#ffffff'
    lv = np.log(v)
    if lv >= 0:
        t = 0.5 + 0.5 * min(lv / np.log(vmax), 1.0)
    else:
        t = 0.5 - 0.5 * min(-lv / -np.log(vmin), 1.0)
    return DIV_CMAP(t)

fig, ax = new_fig(w=8.6, h=8.2)
ax.set_position([0.17, 0.255, 0.66, 0.60])

cell = 1.0
for i in range(n):
    for j in range(n):
        x, y = j, n - 1 - i
        if i == j:
            ax.add_patch(mpatches.Rectangle((x, y), cell, cell, facecolor=GRID, edgecolor='white', linewidth=2, zorder=2))
            continue
        v = mat[i, j]
        if inf_mask[i, j]:
            ax.add_patch(mpatches.Rectangle((x, y), cell, cell, facecolor=DIV_RED, edgecolor='white',
                                             linewidth=2, zorder=2, hatch='xxxx', alpha=0.92))
            ax.text(x + 0.5, y + 0.5, 'S/C', ha='center', va='center', fontsize=10.5,
                    color='white', family='Poppins', fontweight='bold', zorder=3)
        elif not np.isnan(v):
            col = color_for(v)
            ax.add_patch(mpatches.Rectangle((x, y), cell, cell, facecolor=col, edgecolor='white', linewidth=2, zorder=2))
            # luminancia aproximada para decidir color de texto
            rgb = col[:3] if isinstance(col, tuple) else col
            lum = 0.299*rgb[0] + 0.587*rgb[1] + 0.114*rgb[2]
            txt_color = 'white' if lum < 0.62 else INK_PRIMARY
            flag = ' *' if v > 1.5 else ''
            ax.text(x + 0.5, y + 0.5, f'{v:.2f}{flag}', ha='center', va='center', fontsize=11.5,
                    color=txt_color, family='Poppins', fontweight='bold', zorder=3)

ax.set_xlim(0, n)
ax.set_ylim(0, n)
ax.set_aspect('equal')
ax.set_xticks([i + 0.5 for i in range(n)])
ax.set_yticks([i + 0.5 for i in range(n)])
ax.set_xticklabels([labels[i+1] for i in range(n)], fontsize=11.5, family='Poppins', fontweight='medium')
ax.set_yticklabels([labels[n-i] for i in range(n)], fontsize=11.5, family='Poppins', fontweight='medium')
ax.tick_params(length=0)
for s in ax.spines.values():
    s.set_visible(False)

# Barra de gradiente diverging como referencia de lectura (no una leyenda categórica)
grad_ax = fig.add_axes([0.20, 0.135, 0.62, 0.026])
grad = np.linspace(-1, 1, 256).reshape(1, -1)
grad_ax.imshow(grad, aspect='auto', cmap=DIV_CMAP, extent=[vmin, vmax, 0, 1])
grad_ax.set_yticks([])
grad_ax.set_xscale('log')
grad_ax.set_xticks([vmin, 1, vmax])
grad_ax.set_xticklabels([f'{vmin:.2f}\nintegración', '1,0\nsin brecha', f'{vmax:.2f}\nbrecha significativa'],
                         fontsize=7.6, family='Poppins', color=INK_SECONDARY)
grad_ax.tick_params(length=0)
for s in grad_ax.spines.values():
    s.set_visible(False)

fig.text(0.5, 0.085, 'gap$_{ij}$ = (f$_i$ · f$_j$ / N) / cooc$_{ij}$     ·     * brecha significativa (> 1,5)     ·     S/C = sin co-ocurrencia observada',
         ha='center', fontsize=8.0, color=INK_MUTED, family='Poppins')

title_block(fig, 'Figura 2.4 · Brechas estructurales entre clústeres temáticos',
            '8 de 10 pares de clústeres muestran una brecha significativa (Burt, 1992); C2–C3 es la única integración',
            x=0.10, y=0.975, sub_y=0.935)
source_note(fig, 'Fuente: elaboración propia. Puntuación de brecha calculada sobre palabra clave dominante y exclusiva por clúster (N = 3.643).', y=0.025)

plt.savefig('fig_2_5_gap_matrix.png', dpi=300, bbox_inches='tight', facecolor='white')
print('OK fig_2_5_gap_matrix.png')
