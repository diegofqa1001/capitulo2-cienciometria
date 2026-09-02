"""Figura 2.2 — Distribución temporal de la producción del corpus final."""
import sys
sys.path.insert(0, '.')
import json
from collections import Counter
from style import *
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch

with open('../data/final/corpus_final.json', encoding='utf-8') as f:
    corpus = json.load(f)

years = []
for r in corpus:
    y = r.get('Year')
    try:
        y = int(str(y).strip())
        if 1900 < y < 2027:
            years.append(y)
    except Exception:
        pass

c = Counter(years)
PRE_CUTOFF = 1995
pre_total = sum(v for y, v in c.items() if y < PRE_CUTOFF)
labels = ['≤1994'] + [str(y) for y in range(PRE_CUTOFF, 2027)]
values = [pre_total] + [c.get(y, 0) for y in range(PRE_CUTOFF, 2027)]

ACCEL_YEAR = 2016
PARTIAL_YEAR = 2026

fig, ax = plt.subplots(figsize=(11.0, 5.6), dpi=300)
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

x = range(len(labels))
colors = []
hatches = []
for lab in labels:
    if lab == '≤1994':
        colors.append(SEQ_BLUE[1])
        hatches.append(None)
    else:
        y = int(lab)
        if y == PARTIAL_YEAR:
            colors.append(CAT['C1'])
            hatches.append('////')
        elif y >= ACCEL_YEAR:
            colors.append(CAT['C1'])
            hatches.append(None)
        else:
            colors.append(SEQ_BLUE[2])
            hatches.append(None)

bars = ax.bar(x, values, color=colors, width=0.72, zorder=3, linewidth=0)
for b, h in zip(bars, hatches):
    if h:
        b.set_hatch(h)
        b.set_edgecolor('white')
        b.set_linewidth(0.6)

style_axes(ax, hide_spines=('top', 'right', 'left'), grid_axis='y')
ax.set_yticks([0, 100, 200, 300, 400])
ax.tick_params(axis='y', length=0)
ax.set_ylim(0, 410)

# Etiquetas de eje x: solo cada 5 años + el bucket inicial, para evitar saturación
tick_idx, tick_lab = [], []
for i, lab in enumerate(labels):
    if lab == '≤1994':
        tick_idx.append(i); tick_lab.append(lab)
    else:
        y = int(lab)
        if y % 5 == 0 or y == PARTIAL_YEAR:
            tick_idx.append(i); tick_lab.append(lab)
ax.set_xticks(tick_idx)
ax.set_xticklabels(tick_lab, fontsize=8.8)
ax.set_xlim(-0.7, len(labels) - 0.3)

# Línea guía en el quiebre de aceleración (2016)
accel_i = labels.index(str(ACCEL_YEAR))
ax.axvline(accel_i - 0.5, color=BASELINE, linewidth=1.0, linestyle=(0, (4, 3)), zorder=2)

# Etiquetas directas de fase (sustituyen a una leyenda tradicional)
ax.text(accel_i - 0.5 - 6.0, 385, 'antes de 2016', ha='center', fontsize=9.3,
        color=SEQ_BLUE[4], family='Poppins', fontweight='medium')
ax.plot([accel_i - 0.5 - 6.0], [368], marker='s', markersize=7, color=SEQ_BLUE[2],
        clip_on=False, zorder=5)
ax.text(accel_i - 0.5 + 7.0, 385, '2016 en adelante · aceleración', ha='center', fontsize=9.3,
        color=CAT['C1'], family='Poppins', fontweight='medium')
ax.plot([accel_i - 0.5 + 7.0 - 4.55], [368], marker='s', markersize=7, color=CAT['C1'],
        clip_on=False, zorder=5)

# Nota sobre el año parcial
partial_i = labels.index(str(PARTIAL_YEAR))
ax.annotate('2026: año en curso,\ncorte 21-ago-2026\n(dato parcial)',
            xy=(partial_i, values[partial_i]), xytext=(partial_i - 4.3, 300),
            fontsize=7.6, color=INK_SECONDARY, family='Poppins', ha='center',
            arrowprops=dict(arrowstyle='-', color=BASELINE, linewidth=1.0,
                             connectionstyle='arc3,rad=-0.15'))

title_block(fig, 'Figura 2.2 · Distribución temporal del corpus final (N = 3.643)',
            'Crecimiento sostenido con aceleración marcada a partir de 2016',
            x=0.045, y=0.965, sub_y=0.915)
source_note(fig, 'Fuente: elaboración propia a partir del corpus final Web of Science + Scopus (corte: 21 de agosto de 2026). '
                  'Los 29 años previos a 1995 (97 registros) se agregan en el bucket "≤1994" por su baja densidad individual.')

plt.tight_layout(rect=[0.01, 0.03, 0.99, 0.86])
plt.savefig('fig_2_2_temporal.png', dpi=300, bbox_inches='tight', facecolor='white')
print('OK fig_2_2_temporal.png')
