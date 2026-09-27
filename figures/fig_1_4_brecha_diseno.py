"""Figura 1.4 — De la brecha teoría-práctica al posicionamiento arquitectónico de la tesis.
Panel izquierdo: hallazgo empírico (cartografía cienciométrica, Capítulo 2) — la práctica
aplicada (C1) está estructuralmente desconectada del núcleo teórico interconectado.
Panel derecho: decisión de diseño (no deducida del corpus) — el motor OWA-difuso prioriza
sensibilidad conductual e interpretabilidad auditable, renunciando a la capacidad predictiva
no lineal, como estrategia explícita para tender un puente hacia el núcleo teórico."""
import sys
sys.path.insert(0, '.')
from style import *
from matplotlib.patches import FancyArrowPatch, Circle, Polygon
import matplotlib.patheffects as pe
import numpy as np

fig, (axL, axR) = plt.subplots(1, 2, figsize=(12.6, 6.6), dpi=300)
fig.patch.set_facecolor('white')

# ============================= PANEL IZQUIERDO =============================
axL.set_facecolor('white')
axL.set_xlim(0, 10)
axL.set_ylim(0, 10)
axL.set_aspect('equal', adjustable='box')
axL.axis('off')

pos = {
    'C1': (2.0, 5.0),
    'C2': (6.2, 7.4),
    'C3': (6.5, 4.4),
    'C4': (7.2, 1.9),
    'C5': (9.25, 6.2),
}
labels = {
    'C1': 'C1\nPráctica aplicada\n(opciones reales)',
    'C2': 'C2\nAmbigüedad',
    'C3': 'C3\nOptim. robusta',
    'C4': 'C4\nDecisión difusa',
    'C5': 'C5\nConectividad',
}
sizes = {'C1': 1202, 'C2': 989, 'C3': 381, 'C4': 279, 'C5': 161}

axL.axvline(4.05, color=GRID, linewidth=1.1, linestyle=(0, (5, 4)), zorder=1)
axL.text(2.0, 9.35, 'PRÁCTICA APLICADA\n(aislada)', ha='center', fontsize=8.6, color=DIV_RED,
          family='Poppins', fontweight='medium', linespacing=1.35)
from matplotlib.patches import FancyBboxPatch
axL.add_patch(FancyBboxPatch((5.0, 0.95), 3.2, 7.75, boxstyle='round,pad=0.05,rounding_size=0.35',
                             facecolor='#f3f7fb', edgecolor=SEQ_BLUE[2], linewidth=1.0, zorder=0))
axL.text(6.6, 9.35, 'NÚCLEO TEÓRICO\n(C2–C3 integrados)', ha='center', fontsize=8.6, color=SEQ_BLUE[4],
          family='Poppins', fontweight='medium', linespacing=1.35)
axL.text(9.25, 7.35, 'EMERGENTE', ha='center', fontsize=7.8, color=CAT['C5'],
          family='Poppins', fontweight='medium')

# C1 frente a los otros cuatro clústeres (índice > 1,5 y p < 0,05 en los cuatro pares)
for j in ['C2', 'C3', 'C4', 'C5']:
    a = FancyArrowPatch(pos['C1'], pos[j], arrowstyle='-', linewidth=1.8, color=DIV_RED,
                         linestyle=(0, (1, 1.6)), zorder=2, alpha=0.85,
                         connectionstyle='arc3,rad=%s' % (-0.75 if j == 'C5' else 0.06))
    axL.add_patch(a)

# Integración C2-C3 (co-ocurrencia por encima de la esperada)
a = FancyArrowPatch(pos['C2'], pos['C3'], arrowstyle='-', linewidth=4.6, color=DIV_BLUE, zorder=2)
axL.add_patch(a)

# C3-C4 (1,70; p < 0,05) y C3-C5 (1,68; p = 0,20): brechas por encima del umbral;
# C2-C4 (1,03): sin brecha (valores en la Tabla 2.3 y results/prueba_brechas.csv)
axL.add_patch(FancyArrowPatch(pos['C3'], pos['C4'], arrowstyle='-', linewidth=1.5, color=DIV_RED,
                              linestyle=(0, (1, 1.6)), zorder=2, alpha=0.85))
axL.add_patch(FancyArrowPatch(pos['C3'], pos['C5'], arrowstyle='-', linewidth=1.5, color='#e8a77a',
                              linestyle=(0, (4, 3)), zorder=2))
axL.add_patch(FancyArrowPatch(pos['C2'], pos['C4'], arrowstyle='-', linewidth=1.0, color=BASELINE,
                              linestyle=(0, (2, 2)), zorder=1, connectionstyle='arc3,rad=0.35'))
for (i, j), txt, col, dx, dy in [(('C3', 'C4'), '1,70', DIV_RED, 0.42, 0.0),
                                 (('C3', 'C5'), '1,68', '#b0602b', 0.0, -0.40)]:
    mx, my = (pos[i][0] + pos[j][0]) / 2 + dx, (pos[i][1] + pos[j][1]) / 2 + dy
    axL.text(mx, my, txt, ha='center', va='center', fontsize=7.4, color=col, family='Poppins',
             fontweight='bold', zorder=6, path_effects=[pe.withStroke(linewidth=2.4, foreground='white')])

def node_label(ax, cx, cy, lines, fontsize=7.3, line_gap=0.30):
    """Coloca cada línea de la etiqueta por separado (evita el bug de centrado
    automático multilínea de matplotlib, que puede empujar la primera línea
    fuera del nodo y volverla invisible en blanco-sobre-blanco)."""
    n = len(lines)
    top_y = cy + (n - 1) * line_gap / 2
    for i, line in enumerate(lines):
        ax.text(cx, top_y - i * line_gap, line, ha='center', va='center', fontsize=fontsize,
                color='white', family='Poppins', fontweight='bold', zorder=5)

label_lines = {
    'C1': ['C1', 'Práctica', 'aplicada'],
    'C2': ['C2', 'Ambigüe-', 'dad'],
    'C3': ['C3', 'Optim.', 'robusta'],
    'C4': ['C4', 'Decisión', 'difusa'],
    'C5': ['C5', 'Conecti-', 'vidad'],
}
for k, (x, y) in pos.items():
    r = 0.50 + 0.26 * (sizes[k] / 1202) ** 0.5
    axL.add_patch(Circle((x, y), r, facecolor=CAT[k], edgecolor='white', linewidth=2.0, zorder=4))
    node_label(axL, x, y, label_lines[k], fontsize=6.9, line_gap=0.28)

axL.text(5.0, 0.2, 'Hallazgo empírico (Cap. 2): C1 presenta brecha (> 1,5; p < 0,05)\n'
                     'con los otros cuatro clústeres; C2–C3 es la única integración',
          ha='center', fontsize=8.0, color=INK_SECONDARY, family='Poppins', linespacing=1.4)

axL.text(0.0, 10.55, 'A. La brecha teoría–práctica', ha='left', fontsize=12.5,
          fontweight='medium', color=INK_PRIMARY, family='Poppins', transform=axL.transData)

# ============================= PANEL DERECHO =============================
axR.set_facecolor('white')
axR.set_xlim(0, 10)
axR.set_ylim(0, 10)
axR.set_aspect('equal', adjustable='box')
axR.axis('off')

# Triángulo de propiedades deseables
V = {
    'pred': np.array([5.0, 8.8]),
    'cond': np.array([1.4, 2.2]),
    'interp': np.array([8.6, 2.2]),
}
tri = Polygon([V['pred'], V['cond'], V['interp']], closed=True, facecolor='#f4f3ef',
              edgecolor=BASELINE, linewidth=1.2, zorder=1)
axR.add_patch(tri)

vlabels = {
    'pred': 'Capacidad predictiva\nno lineal',
    'cond': 'Sensibilidad\nconductual',
    'interp': 'Interpretabilidad\nauditable',
}
voffsets = {'pred': (0, 0.55), 'cond': (-0.9, -0.35), 'interp': (0.9, -0.35)}
for k, v in V.items():
    axR.add_patch(Circle(v, 0.16, facecolor=INK_PRIMARY, edgecolor='none', zorder=4))
    dx, dy = voffsets[k]
    ha = 'center' if dx == 0 else ('right' if dx < 0 else 'left')
    axR.text(v[0] + dx, v[1] + dy, vlabels[k], ha=ha, va='center', fontsize=8.7,
              color=INK_PRIMARY, family='Poppins', fontweight='medium', linespacing=1.3, zorder=5)

# Punto de diseño de la tesis: sobre la arista sensibilidad-interpretabilidad,
# desplazado lejos del vértice predictivo (elección de diseño)
t = 0.5
p_tesis = V['cond'] * (1 - t) + V['interp'] * t
p_tesis[1] += 0.55  # ligera elevación por el componente adaptativo IOWA
axR.add_patch(Circle(p_tesis, 0.22, facecolor=CAT['C1'], edgecolor='white', linewidth=2.2, zorder=6))
axR.annotate('Arquitectura OWA-difusa\n(esta tesis)', xy=p_tesis, xytext=(p_tesis[0], p_tesis[1] + 1.35),
             ha='center', fontsize=9.0, color=CAT['C1'], family='Poppins', fontweight='bold',
             linespacing=1.35, zorder=6,
             arrowprops=dict(arrowstyle='-', color=CAT['C1'], linewidth=1.3),
             path_effects=[pe.withStroke(linewidth=3, foreground='white')])

axR.text(5.0, 0.35, 'Decisión de diseño: se prioriza sensibilidad\n'
                     'conductual e interpretabilidad auditable (Rudin, 2019), como puente\n'
                     'hacia el núcleo teórico bajo trazabilidad regulatoria (MiFID II; Reglamento de IA de la UE)',
          ha='center', fontsize=8.0, color=INK_SECONDARY, family='Poppins', linespacing=1.4)

axR.text(0.0, 10.55, 'B. El posicionamiento arquitectónico de la tesis', ha='left', fontsize=12.5,
          fontweight='medium', color=INK_PRIMARY, family='Poppins', transform=axR.transData)

plt.tight_layout(rect=[0.01, 0.01, 0.99, 0.97])
plt.savefig('fig_1_4_brecha_diseno.png', dpi=300, bbox_inches='tight', facecolor='white')
print('OK fig_1_4_brecha_diseno.png')
