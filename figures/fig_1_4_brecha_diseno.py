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
    'C2': (6.3, 7.6),
    'C3': (6.6, 4.3),
    'C4': (7.4, 1.8),
    'C5': (9.1, 6.1),
}
labels = {
    'C1': 'C1\nPráctica aplicada\n(opciones reales)',
    'C2': 'C2\nAmbigüedad',
    'C3': 'C3\nOptim. robusta',
    'C4': 'C4\nFuzzy MCDM',
    'C5': 'C5\nConectividad',
}
sizes = {'C1': 1202, 'C2': 989, 'C3': 381, 'C4': 279, 'C5': 161}

axL.axvline(4.05, color=GRID, linewidth=1.1, linestyle=(0, (5, 4)), zorder=1)
axL.text(2.0, 9.35, 'PRÁCTICA APLICADA\n(aislada)', ha='center', fontsize=8.6, color=DIV_RED,
          family='Poppins', fontweight='medium', linespacing=1.35)
axL.text(7.35, 9.35, 'NÚCLEO TEÓRICO\nINTERCONECTADO', ha='center', fontsize=8.6, color=SEQ_BLUE[4],
          family='Poppins', fontweight='medium', linespacing=1.35)

# C1 desconectado de los otros cuatro (brechas significativas, Burt 1992)
for j in ['C2', 'C3', 'C4', 'C5']:
    a = FancyArrowPatch(pos['C1'], pos[j], arrowstyle='-', linewidth=1.8, color=DIV_RED,
                         linestyle=(0, (1, 1.6)), zorder=2, alpha=0.85,
                         connectionstyle='arc3,rad=0.06')
    axL.add_patch(a)

# Integración C2-C3 (único par sin brecha significativa)
a = FancyArrowPatch(pos['C2'], pos['C3'], arrowstyle='-', linewidth=4.6, color=DIV_BLUE, zorder=2)
axL.add_patch(a)

# resto de pares del núcleo, de-enfatizados
for i, j in [('C3', 'C4'), ('C3', 'C5'), ('C2', 'C4')]:
    a = FancyArrowPatch(pos[i], pos[j], arrowstyle='-', linewidth=1.0, color=BASELINE,
                         linestyle=(0, (2, 2)), zorder=1, alpha=0.75)
    axL.add_patch(a)

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
    'C4': ['C4', 'Fuzzy', 'MCDM'],
    'C5': ['C5', 'Conecti-', 'vidad'],
}
for k, (x, y) in pos.items():
    r = 0.50 + 0.26 * (sizes[k] / 1202) ** 0.5
    axL.add_patch(Circle((x, y), r, facecolor=CAT[k], edgecolor='white', linewidth=2.0, zorder=4))
    node_label(axL, x, y, label_lines[k], fontsize=6.9, line_gap=0.28)

axL.text(5.0, 0.35, 'Hallazgo empírico (Cap. 2): 8 de 10 pares de clústeres muestran\n'
                     'brecha estructural significativa (Burt, 1992); C2–C3 es la única integración',
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
# desplazado lejos del vértice predictivo (renuncia deliberada a ese vértice)
t = 0.5
p_tesis = V['cond'] * (1 - t) + V['interp'] * t
p_tesis[1] += 0.55  # ligera elevación por el componente adaptativo IOWA
axR.add_patch(Circle(p_tesis, 0.22, facecolor=CAT['C1'], edgecolor='white', linewidth=2.2, zorder=6))
axR.annotate('Arquitectura OWA-difusa\n(esta tesis)', xy=p_tesis, xytext=(p_tesis[0], p_tesis[1] + 1.35),
             ha='center', fontsize=9.0, color=CAT['C1'], family='Poppins', fontweight='bold',
             linespacing=1.35, zorder=6,
             arrowprops=dict(arrowstyle='-', color=CAT['C1'], linewidth=1.3),
             path_effects=[pe.withStroke(linewidth=3, foreground='white')])

axR.text(5.0, 0.35, 'Decisión de diseño —no deducida del corpus—: se prioriza sensibilidad\n'
                     'conductual e interpretabilidad auditable (Rudin, 2019), como puente\n'
                     'hacia el núcleo teórico bajo trazabilidad regulatoria (MiFID II; EU AI Act)',
          ha='center', fontsize=8.0, color=INK_SECONDARY, family='Poppins', linespacing=1.4)

axR.text(0.0, 10.55, 'B. El posicionamiento arquitectónico de la tesis', ha='left', fontsize=12.5,
          fontweight='medium', color=INK_PRIMARY, family='Poppins', transform=axR.transData)

fig.text(0.02, 0.985, 'Figura 1.4 · De la brecha teoría-práctica al posicionamiento arquitectónico de la tesis',
          fontsize=13.5, fontweight='medium', color=INK_PRIMARY, family='Poppins', ha='left')
fig.text(0.02, 0.945, 'El hallazgo empírico del Capítulo 2 (panel A) motiva —sin determinarla lógicamente— '
                       'la decisión de diseño del motor OWA-difuso (panel B)',
          fontsize=9.5, color=INK_MUTED, family='Poppins', ha='left')
fig.text(0.02, 0.012, 'Fuente: elaboración propia. Panel A: cartografía cienciométrica del Capítulo 2 '
                       '(N = 3.643 registros; puntuación de brecha de Burt, 1992; ver Figura 2.6). '
                       'Panel B: síntesis conceptual del criterio de diseño desarrollado en el Capítulo 4 '
                       'y discutido en la Sección 9.3.', fontsize=7.6, color=INK_MUTED, family='Poppins')

plt.tight_layout(rect=[0.01, 0.03, 0.99, 0.90])
plt.savefig('fig_1_4_brecha_diseno.png', dpi=300, bbox_inches='tight', facecolor='white')
print('OK fig_1_4_brecha_diseno.png')
