"""Figura 2.1 — Flujo PRISMA de conformación del corpus."""
import sys
sys.path.insert(0, '.')
from style import *
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(10.2, 6.6), dpi=300)
fig.patch.set_facecolor('white')
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

BOX_W, BOX_H = 3.0, 1.05


def box(cx, cy, title, value, sub, color, w=BOX_W, h=BOX_H, text_color='white',
        title_size=9.3, title_y=None, value_y=None, sub_y=None, line_gap=0.22):
    """Cada línea del título se dibuja por separado (sin bloque multilinea
    autocentrado de matplotlib), de modo que la posición vertical de cada
    línea es explícita y nunca se sale del rectángulo de la caja."""
    b = FancyBboxPatch((cx - w/2, cy - h/2), w, h,
                        boxstyle="round,pad=0.02,rounding_size=0.12",
                        linewidth=0, facecolor=color, zorder=3)
    ax.add_patch(b)
    if title_y is None:
        title_y = cy + 0.24
    if value_y is None:
        value_y = cy - 0.14
    if sub_y is None:
        sub_y = cy - 0.42
    lines = title.split('\n')
    for i, line in enumerate(lines):
        ly = title_y - i * line_gap
        ax.text(cx, ly, line, ha='center', va='center', fontsize=title_size,
                color=text_color, family='Poppins', fontweight='medium', zorder=4)
    ax.text(cx, value_y, value, ha='center', va='center', fontsize=15,
            color=text_color, family='Poppins', fontweight='bold', zorder=4)
    if sub:
        ax.text(cx, sub_y, sub, ha='center', va='center', fontsize=7.6,
                color=text_color, family='Poppins', zorder=4, alpha=0.92)


def arrow(x1, y1, x2, y2, color=BASELINE):
    a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=13,
                         linewidth=1.4, color=color, zorder=2, shrinkA=2, shrinkB=2)
    ax.add_patch(a)


def side_note(cx, cy, text, color=DIV_RED):
    b = FancyBboxPatch((cx - 1.55, cy - 0.34), 3.1, 0.68,
                        boxstyle="round,pad=0.02,rounding_size=0.10",
                        linewidth=1.1, edgecolor=color, facecolor='#fdf3f2', zorder=3)
    ax.add_patch(b)
    ax.text(cx, cy, text, ha='center', va='center', fontsize=7.6,
            color=INK_PRIMARY, family='Poppins', zorder=4)


# Fila 1: identificación por fuente
box(2.7, 9.0, 'IDENTIFICACIÓN · SCOPUS', '2.532', '2.529 únicos internos (−3 DOI dup.)', CAT['C2'])
box(7.3, 9.0, 'IDENTIFICACIÓN · WEB OF SCIENCE', '2.659', '2.659 únicos internos (0 DOI dup.)', CAT['C1'])

arrow(2.7, 9.0 - BOX_H/2, 5.0, 7.42)
arrow(7.3, 9.0 - BOX_H/2, 5.0, 7.42)

# Fila 2: total identificación (caja más alta para dos líneas de título sin colisión)
ROW2_CY, ROW2_H = 6.85, 1.4
box(5.0, ROW2_CY, 'TOTAL IDENTIFICACIÓN\n(unicidad por fuente)', '5.188', 'Scopus 2.529 + WoS 2.659',
    INK_SECONDARY, w=4.6, h=ROW2_H, title_size=9.6,
    title_y=ROW2_CY + 0.48, value_y=ROW2_CY - 0.05, sub_y=ROW2_CY - 0.38)

arrow(5.0, ROW2_CY - ROW2_H/2, 5.0, 5.32)
side_note(8.35, (ROW2_CY - ROW2_H/2 + 5.4) / 2, '−1.479 duplicados\ncruzados por DOI\n(Scopus y WoS)')

# Fila 3: tras deduplicación cruzada
ROW3_CY, ROW3_H = 4.7, 1.4
box(5.0, ROW3_CY, 'CRIBADO · DEDUPLICACIÓN\nCRUZADA POR DOI', '3.709', 'registros únicos',
    CAT['C3'], w=4.6, h=ROW3_H, title_size=9.6,
    title_y=ROW3_CY + 0.48, value_y=ROW3_CY - 0.05, sub_y=ROW3_CY - 0.38)

arrow(5.0, ROW3_CY - ROW3_H/2, 5.0, 3.22)
side_note(8.35, (ROW3_CY - ROW3_H/2 + 3.175) / 2, '−66 excluidos:\n60 idioma · 4 sin resumen\n2 retractados')

# Fila 4: corpus final
box(5.0, 2.55, 'INCLUSIÓN · CORPUS FINAL', '3.643', 'registros únicos analizados', CAT['C4'],
    h=1.25, text_color=INK_PRIMARY)

fig.text(0.5, 0.965, 'Figura 2.1', ha='center', fontsize=10.5, color=INK_MUTED, family='Poppins')
fig.text(0.5, 0.935, 'Flujo PRISMA de conformación del corpus cienciométrico',
         ha='center', fontsize=13.5, color=INK_PRIMARY, family='Poppins', fontweight='medium')
source_note(fig, 'Fuente: elaboración propia a partir de las extracciones de Web of Science y Scopus (21 de agosto de 2026).')

plt.tight_layout(rect=[0, 0.02, 1, 0.90])
plt.savefig('fig_2_1_prisma.png', dpi=300, bbox_inches='tight', facecolor='white')
print('OK fig_2_1_prisma.png')
