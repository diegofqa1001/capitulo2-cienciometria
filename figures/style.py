"""Sistema visual compartido para las figuras del Capítulo 2.

Paleta y reglas tomadas de la skill dataviz (paleta validada CVD-safe,
sin "rainbow", secuencial=un solo tono, divergente=dos tonos + gris
neutro, jerarquía tipográfica clara, líneas finas, leyenda siempre
presente para >=2 series con etiquetado directo selectivo)."""
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.colors import LinearSegmentedColormap

# --- Tipografía: Poppins (geométrica, contemporánea) ---
for w in ['Regular', 'Medium', 'Bold', 'Light']:
    try:
        fm.fontManager.addfont(f'/usr/share/fonts/truetype/google-fonts/Poppins-{w}.ttf')
    except Exception:
        pass
plt.rcParams['font.family'] = 'Poppins'
plt.rcParams['font.size'] = 11

# --- Paleta categórica (orden fijo, nunca ciclado) ---
CAT = {
    'C1': '#2a78d6',  # azul
    'C2': '#eb6834',  # naranja
    'C3': '#1baf7a',  # aqua
    'C4': '#eda100',  # amarillo
    'C5': '#e87ba4',  # magenta
}
CAT_ORDER = ['C1', 'C2', 'C3', 'C4', 'C5']

# --- Tinta / cromática ---
INK_PRIMARY = '#0b0b0b'
INK_SECONDARY = '#52514e'
INK_MUTED = '#898781'
GRID = '#e1e0d9'
BASELINE = '#c3c2b7'
SURFACE = '#fcfcfb'

# --- Secuencial (un solo tono, azul, claro->oscuro) ---
SEQ_BLUE = ['#cde2fb', '#9ec5f4', '#5598e7', '#2a78d6', '#184f95', '#0d366b']
SEQ_BLUE_CMAP = LinearSegmentedColormap.from_list('seq_blue', SEQ_BLUE)

# --- Divergente (azul <-> rojo, punto medio gris neutro) ---
DIV_BLUE = '#184f95'
DIV_MID = '#f0efec'
DIV_RED = '#b32e2d'
DIV_CMAP = LinearSegmentedColormap.from_list('div_blue_red', [DIV_BLUE, '#7fa8d8', DIV_MID, '#e79a91', DIV_RED])

# --- Estado ---
STATUS_GOOD = '#0ca30c'
STATUS_CRITICAL = '#d03b3b'


def new_fig(w=7.5, h=5.0):
    fig, ax = plt.subplots(figsize=(w, h), dpi=300)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    return fig, ax


def style_axes(ax, hide_spines=('top', 'right'), grid_axis=None):
    for s in hide_spines:
        ax.spines[s].set_visible(False)
    for s in ax.spines:
        if s not in hide_spines:
            ax.spines[s].set_color(BASELINE)
            ax.spines[s].set_linewidth(0.8)
    ax.tick_params(colors=INK_SECONDARY, labelsize=9.5)
    if grid_axis:
        ax.grid(axis=grid_axis, color=GRID, linewidth=0.7, zorder=0)
        ax.set_axisbelow(True)


def title_block(ax_or_fig, title, subtitle=None, x=0.0, y=1.06, sub_y=1.015):
    kwargs = {}
    if hasattr(ax_or_fig, 'transAxes'):
        kwargs['transform'] = ax_or_fig.transAxes
    # si ax_or_fig es una Figure, NO se pasa transform: fig.text ya usa
    # transFigure (fracción de figura) por defecto; pasar transform=None
    # explícitamente rompe ese default y coloca el texto cerca del origen.
    ax_or_fig.text(x, y, title, fontsize=13, fontweight='medium', color=INK_PRIMARY,
                    ha='left', family='Poppins', **kwargs)
    if subtitle:
        ax_or_fig.text(x, sub_y, subtitle, fontsize=9.5, color=INK_MUTED, ha='left',
                        family='Poppins', **kwargs)


def source_note(fig, text, x=0.02, y=0.01):
    fig.text(x, y, text, fontsize=7.8, color=INK_MUTED, ha='left', family='Poppins')
