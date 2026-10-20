"""Figuras del artículo (inglés) derivado del Capítulo 2: Fig1 a Fig5.

Paleta institucional (azul marino y grises), fondo blanco, tipografía sans-serif
(Liberation Sans, métricamente equivalente a Arial), sin títulos internos, ancho
máximo de 174 mm. La información categórica se codifica también con forma de
marcador, tramado o tipo de trazo, de modo que se lee en escala de grises.

Ejecución desde la raíz del repositorio:
    python figures_article/layout_map.py          # solo si se quiere recalcular el diseño de la Fig. 1
    python figures_article/make_article_figures.py

Entradas: data/final/{cluster_summaries, gap_analysis_v2, louvain_communities,
layout_coupling_spring}.json, results/prueba_brechas.csv (paso 11),
results/robustez_particion.json (paso 12), results/consenso_estabilidad.json (paso 13).
Salidas: figures_article/Fig1..Fig5 en .png (600 ppp), .tif (600 ppp) y .eps.
"""
from pathlib import Path
import csv
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm
from matplotlib.colors import LinearSegmentedColormap, LogNorm, Normalize
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe

ROOT = Path(__file__).resolve().parent.parent
FIN = ROOT / 'data' / 'final'
RES = ROOT / 'results'
OUT = ROOT / 'figures_article'
OUT.mkdir(exist_ok=True)

for f in fm.findSystemFonts():
    if 'LiberationSans' in f:
        fm.fontManager.addfont(f)
FONT = 'Liberation Sans' if any('Liberation Sans' == x.name for x in fm.fontManager.ttflist) else 'DejaVu Sans'
plt.rcParams.update({'font.family': FONT, 'font.size': 8, 'axes.edgecolor': '#9E9E9E',
                     'axes.labelcolor': '#222222', 'xtick.color': '#444444', 'ytick.color': '#444444',
                     'savefig.facecolor': 'white', 'figure.facecolor': 'white', 'hatch.linewidth': 0.6,
                     'ps.fonttype': 42, 'pdf.fonttype': 42})
MM = 1 / 25.4
W = 174 * MM

# Paleta institucional (la misma de figures/style.py)
NAVY, NAVY2, GREY_D, GREY_M, TAUPE = '#1F3A5F', '#4F6D8F', '#3F3F3F', '#8C8C8C', '#8A7D72'
INK, INK2, GRID, LIGHT = '#111111', '#4A4A4A', '#D9D9D9', '#F0EFEC'
CAT = {1: NAVY, 2: GREY_M, 3: NAVY2, 4: GREY_D, 5: TAUPE}
MARK = {1: 'o', 2: 's', 3: '^', 4: 'D', 5: 'v'}
NAMES = {1: 'C1 Real options and corporate investment', 2: 'C2 Ambiguity and behavioural portfolio choice',
         3: 'C3 Robust portfolio optimisation', 4: 'C4 Fuzzy multi-criteria decision making',
         5: 'C5 Crisis connectedness'}
DIV = LinearSegmentedColormap.from_list('div', [NAVY, '#8FA2BA', LIGHT, '#9E9E9E', GREY_D])
SEQ = LinearSegmentedColormap.from_list('seq', ['#F4F6F9', '#C2CCD9', '#8C9DB4', '#55698A', NAVY, '#14243D'])
SEQ_G = LinearSegmentedColormap.from_list('seqg', ['#F5F5F5', '#C8C8C8', '#8C8C8C', '#5A5A5A', '#2B2B2B'])


def save(fig, name):
    for ext, kw in (('png', dict(dpi=600)), ('tif', dict(dpi=600, pil_kwargs={'compression': 'tiff_lzw'})), ('eps', {})):
        fig.savefig(OUT / f'{name}.{ext}', bbox_inches='tight', **kw)
    plt.close(fig)


labels = ['C1', 'C2', 'C3', 'C4', 'C5']
cs = {c['cluster_rank']: c for c in json.load(open(FIN / 'cluster_summaries.json', encoding='utf-8'))}
gap = {tuple(p['par']): p for p in json.load(open(FIN / 'gap_analysis_v2.json', encoding='utf-8'))['pairs']}
rob = json.load(open(RES / 'robustez_particion.json', encoding='utf-8'))
con = json.load(open(RES / 'consenso_estabilidad.json', encoding='utf-8'))
pval = {}
with open(RES / 'prueba_brechas.csv', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        a, b = [int(x[1:]) for x in r['par'].split('-')]
        pval[(a, b)] = pval[(b, a)] = float(r['p_poisson'])

# ---------------- Fig 1: science map ----------------
pos = json.load(open(FIN / 'layout_coupling_spring.json'))
pub = {int(k): v for k, v in json.load(open(FIN / 'louvain_communities.json'))['assignment'].items()}
xy = np.array([pos[k] for k in pos]); lab = np.array([pub[int(k)] + 1 for k in pos])
fig, ax = plt.subplots(figsize=(W, W * 0.86))
for c in [1, 2, 3, 4, 5]:
    m = lab == c
    ax.scatter(xy[m, 0], xy[m, 1], s=3.2, marker=MARK[c], facecolor=CAT[c], edgecolor='none', zorder=2 + c)
for c in range(1, 6):
    m = lab == c; cx, cy = np.median(xy[m, 0]), np.median(xy[m, 1])
    if c == 3: cx += 0.03; cy -= 0.09
    if c == 4: cx -= 0.06; cy += 0.05
    ax.text(cx, cy, f'C{c}', fontsize=9, fontweight='bold', color='white', ha='center', va='center', zorder=10,
            bbox=dict(boxstyle='round,pad=0.3', fc=CAT[c], ec='white', lw=1.0))
ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values(): s.set_visible(False)
handles = [Line2D([0], [0], marker=MARK[c], color='w', markerfacecolor=CAT[c], markersize=6,
                  label=f'{NAMES[c]} ({cs[c]["n_docs"]:,})') for c in range(1, 6)]
ax.legend(handles=handles, loc='upper center', frameon=False, fontsize=7.5, bbox_to_anchor=(0.5, -0.0), ncol=2,
          handletextpad=0.3, columnspacing=1.2)
save(fig, 'Fig1')

# ---------------- Fig 3: consensus co-association ----------------
M = np.array(con['seeds_baseline']['coassociation']); M2 = np.array(con['hyperparams_coassociation'])
fig, axes = plt.subplots(1, 2, figsize=(W, W * 0.47))
for ax, Mx, tag in [(axes[0], M, '(a)'), (axes[1], M2, '(b)')]:
    ax.imshow(Mx, cmap=SEQ, vmin=0, vmax=1)
    for i in range(5):
        for j in range(5):
            ax.text(j, i, f'{Mx[i, j]:.2f}', ha='center', va='center', fontsize=7.5,
                    color='white' if Mx[i, j] > 0.5 else INK)
    ax.set_xticks(range(5)); ax.set_xticklabels(labels); ax.set_yticks(range(5)); ax.set_yticklabels(labels)
    ax.text(-0.5, -0.75, tag, fontsize=9, fontweight='bold', color=INK, ha='left', va='bottom')
    ax.tick_params(length=0)
    for s in ax.spines.values(): s.set_visible(False)
sm = plt.cm.ScalarMappable(cmap=SEQ, norm=Normalize(0, 1)); sm.set_array([])
cb = fig.colorbar(sm, ax=axes, fraction=0.025, pad=0.02); cb.set_label('Probability of co-membership', fontsize=7.5)
cb.outline.set_visible(False); cb.ax.tick_params(labelsize=7)
save(fig, 'Fig3')

# ---------------- Fig 2: gap matrices ----------------
lex = np.full((5, 5), np.nan); inf = np.zeros((5, 5), bool)
for (i, j), p in gap.items():
    if p['gap_score_inf']:
        inf[i - 1, j - 1] = inf[j - 1, i - 1] = True
    else:
        lex[i - 1, j - 1] = lex[j - 1, i - 1] = p['gap_score']
cit = np.full((5, 5), np.nan)
for r in rob['network_gap']:
    i, j = r['pair'][0] - 1, r['pair'][1] - 1
    cit[i, j] = cit[j, i] = r['perm_ratio']
vmax_l, vmin_l = np.nanmax(lex), np.nanmin(lex)


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


fig, axes = plt.subplots(1, 2, figsize=(W, W * 0.5))
for ax, kind, tag in [(axes[0], 'lex', '(a)'), (axes[1], 'cit', '(b)')]:
    for i in range(5):
        for j in range(5):
            x, y = j, 4 - i
            if i == j:
                ax.add_patch(mpatches.Rectangle((x, y), 1, 1, fc='#E6E6E6', ec='white', lw=1.5)); continue
            if kind == 'lex' and inf[i, j]:
                ax.add_patch(mpatches.Rectangle((x, y), 1, 1, fc=GREY_D, ec='white', lw=1.5, hatch='////'))
                mk = '*' + ('†' if pval[(i + 1, j + 1)] < 0.05 else '')
                ax.text(x + .5, y + .5, f'none\n{mk}', ha='center', va='center', fontsize=7.2, color='white',
                        fontweight='bold', linespacing=1.0, bbox=dict(boxstyle='round,pad=0.12', fc=GREY_D, ec='none'))
                continue
            if kind == 'lex':
                v = lex[i, j]; lv = np.log(v)
                t = 0.5 + 0.5 * min(lv / np.log(vmax_l), 1) if lv >= 0 else 0.5 - 0.5 * min(lv / np.log(vmin_l), 1)
                col = DIV(t)
                mk = ('*' if v > 1.5 else '') + ('†' if pval[(i + 1, j + 1)] < 0.05 else '')
                txt = f'{v:.2f}' + (f'\n{mk}' if mk else '')
            else:
                v = cit[i, j]; t = min(np.log(v) / np.log(70), 1); col = SEQ_G(t); txt = f'{v:.1f}'
            ax.add_patch(mpatches.Rectangle((x, y), 1, 1, fc=col, ec='white', lw=1.5))
            ax.text(x + .5, y + .5, txt, ha='center', va='center', fontsize=7.5, fontweight='bold',
                    color='white' if lum(col) < 0.55 else INK, linespacing=1.0)
    ax.set_xlim(0, 5); ax.set_ylim(0, 5); ax.set_aspect('equal')
    ax.set_xticks(np.arange(5) + .5); ax.set_xticklabels(labels)
    ax.set_yticks(np.arange(5) + .5); ax.set_yticklabels(labels[::-1])
    ax.tick_params(length=0)
    for s in ax.spines.values(): s.set_visible(False)
    ax.text(0, 5.12, tag, fontsize=9, fontweight='bold', color=INK, ha='left', va='bottom')
sm = plt.cm.ScalarMappable(cmap=DIV, norm=Normalize(0, 1)); sm.set_array([])
cb = fig.colorbar(sm, ax=axes[0], fraction=0.046, pad=0.04, ticks=[0, 0.5, 1])
cb.ax.set_yticklabels([f'{vmin_l:.2f} integrated', '1 independence', f'{vmax_l:.2f} gap'], fontsize=6.8); cb.outline.set_visible(False)
sm2 = plt.cm.ScalarMappable(cmap=SEQ_G, norm=LogNorm(1, 70)); sm2.set_array([])
cb2 = fig.colorbar(sm2, ax=axes[1], fraction=0.046, pad=0.04, ticks=[1, 1.5, 5, 20, 60])
cb2.ax.set_yticklabels(['1', '1.5', '5', '20', '60'], fontsize=6.8); cb2.outline.set_visible(False)
fig.subplots_adjust(wspace=0.55)
save(fig, 'Fig2')

# ---------------- Fig 4: lexical versus citation gap ----------------
fig, ax = plt.subplots(figsize=(W * 0.82, W * 0.62))
offsets = {(1, 2): (6, 4), (1, 3): (6, -10), (1, 4): (6, 4), (1, 5): (6, -10), (2, 3): (6, 4), (2, 4): (-8, 7),
           (3, 4): (6, 4), (3, 5): (6, 4), (2, 5): (-6, 8), (4, 5): (-6, 8)}
for r in rob['network_gap']:
    pr = tuple(r['pair']); p = gap[pr]
    x = np.inf if p['gap_score_inf'] else p['gap_score']; y = r['perm_ratio']
    censored = np.isinf(x); xp = 40 if censored else x
    if censored:
        mk, col = '>', GREY_D
    elif x > 1.5 and y > 1.5:
        mk, col = 'o', NAVY
    elif x <= 1.5 and y <= 1.5:
        mk, col = 's', GREY_M
    else:
        mk, col = 'D', NAVY2
    ax.scatter(xp, y, s=34, marker=mk, color=col, edgecolor='white', linewidth=0.6, zorder=3)
    dx, dy = offsets[pr]
    ax.annotate(f'C{pr[0]}–C{pr[1]}', (xp, y), xytext=(dx, dy), textcoords='offset points', fontsize=7,
                color=INK, ha='left' if dx > 0 else 'right')
ax.set_xscale('log'); ax.set_yscale('log')
ax.axvline(1.5, color='#A6A6A6', lw=0.8, ls='--'); ax.axhline(1.5, color='#A6A6A6', lw=0.8, ls='--')
ax.set_xlabel('Lexical gap score (expected / observed keyword co-occurrence)')
ax.set_ylabel('Citation gap, permutation null\n(expected / observed coupling weight)')
for s in ('top', 'right'): ax.spines[s].set_visible(False)
ax.grid(color='#EEEEEE', lw=0.5, zorder=0); ax.set_axisbelow(True)
ax.set_xlim(0.25, 80); ax.set_ylim(0.8, 120)
from matplotlib.ticker import FixedLocator, FixedFormatter, NullFormatter
ax.xaxis.set_major_locator(FixedLocator([0.3, 1, 1.5, 3, 10, 30])); ax.xaxis.set_major_formatter(FixedFormatter(['0.3', '1', '1.5', '3', '10', '30'])); ax.xaxis.set_minor_formatter(NullFormatter())
ax.yaxis.set_major_locator(FixedLocator([1, 1.5, 3, 10, 30, 100])); ax.yaxis.set_major_formatter(FixedFormatter(['1', '1.5', '3', '10', '30', '100'])); ax.yaxis.set_minor_formatter(NullFormatter())
ax.legend(handles=[Line2D([0], [0], marker='o', color='w', markerfacecolor=NAVY, markersize=6, label='hole on both measures'),
                   Line2D([0], [0], marker='D', color='w', markerfacecolor=NAVY2, markersize=5.5, label='parallel vocabularies'),
                   Line2D([0], [0], marker='s', color='w', markerfacecolor=GREY_M, markersize=6, label='integrated (lexical)'),
                   Line2D([0], [0], marker='>', color='w', markerfacecolor=GREY_D, markersize=6, label='no lexical co-occurrence')],
          loc='upper left', frameon=False, fontsize=6.8)
save(fig, 'Fig4')

# ---------------- Fig 5: theory–practice gap schematic ----------------
fig, ax = plt.subplots(figsize=(W, W * 0.66)); ax.axis('off'); ax.set_xlim(0, 10.6); ax.set_ylim(-0.6, 10.2)
P = {1: (1.6, 4.6), 2: (5.9, 6.9), 3: (6.2, 3.9), 4: (6.8, 1.2), 5: (9.6, 4.9)}
GMAX = gap[(1, 4)]['gap_score']


def rad(c):
    return 0.38 + 0.32 * (cs[c]['n_docs'] / 1202) ** 0.5


def label(i, j, frac, text, color, dx=0, dy=0):
    (x1, y1), (x2, y2) = P[i], P[j]
    ax.text(x1 * (1 - frac) + x2 * frac + dx, y1 * (1 - frac) + y2 * frac + dy, text, ha='center', va='center',
            fontsize=7.2, color=color, fontweight='bold', zorder=6,
            path_effects=[pe.withStroke(linewidth=2.5, foreground='white')])


def edge(i, j, frac, dx=0, dy=0, r=0.06):
    key = (min(i, j), max(i, j)); p = gap[key]
    g = p['gap_score']; sig = pval[key] < 0.05
    if p['gap_score_inf']:
        lw, txt = 1.4, f'none (p = {pval[key]:.3f})'
    else:
        lw, txt = 1.0 + 3.2 * (g / GMAX), f'{g:.2f}' + ('' if sig else f' (p = {pval[key]:.2f})')
    style = (0, (1, 1.3)) if sig else (0, (4, 3))
    col = GREY_D if sig else '#A6A6A6'
    ax.add_patch(mpatches.FancyArrowPatch(P[i], P[j], arrowstyle='-', linewidth=lw, color=col, linestyle=style,
                                          zorder=2, connectionstyle=f'arc3,rad={r}'))
    label(i, j, frac, txt, col if sig else INK2, dx, dy)


ax.plot([3.6, 3.6], [-0.3, 9.0], color=GRID, lw=0.9, ls=(0, (5, 4)))
ax.text(1.6, 8.6, 'APPLIED BLOCK', ha='center', fontsize=8, color=INK, fontweight='bold')
ax.add_patch(mpatches.FancyBboxPatch((4.75, 0.35), 2.95, 7.25, boxstyle='round,pad=0.05,rounding_size=0.3',
                                     fc='#F4F6F9', ec='#8C9DB4', lw=0.8, zorder=0))
ax.text(6.22, -0.25, 'THEORETICAL CORE', ha='center', fontsize=8, color=NAVY, fontweight='bold')
ax.text(9.6, 6.2, 'EMERGING\nSPECIALTY', ha='center', fontsize=7.5, color=INK2, fontweight='bold')
edge(1, 2, 0.42); edge(1, 3, 0.42); edge(1, 4, 0.42)
edge(1, 5, 0.5, dy=3.55, r=-0.68)
edge(3, 4, 0.5, dx=0.42)
edge(3, 5, 0.62, dy=-0.38)
edge(2, 5, 0.55, dx=0.25, dy=-0.42, r=-0.12)
edge(4, 5, 0.5, dx=0.75, dy=-0.1, r=0.12)
ax.add_patch(mpatches.FancyArrowPatch(P[2], P[3], arrowstyle='-', linewidth=4.5, color=NAVY, zorder=2))
ax.text((P[2][0] + P[3][0]) / 2 + 0.25, (P[2][1] + P[3][1]) / 2, f"{gap[(2, 3)]['gap_score']:.2f}\nintegration",
        ha='left', va='center', fontsize=7.2, color=NAVY, fontweight='bold', zorder=6,
        path_effects=[pe.withStroke(linewidth=2.5, foreground='white')])
ax.add_patch(mpatches.FancyArrowPatch(P[2], P[4], arrowstyle='-', linewidth=1.0, color='#BFBFBF',
                                      linestyle='-', zorder=1, connectionstyle='arc3,rad=0.35'))
label(2, 4, 0.7, f"{gap[(2, 4)]['gap_score']:.2f}", INK2, dx=-0.95)
for c, (x, y) in P.items():
    ax.add_patch(mpatches.Circle((x, y), rad(c), fc=CAT[c], ec='white', lw=1.8, zorder=4))
    ax.text(x, y, f'C{c}', ha='center', va='center', fontsize=8.5, color='white', fontweight='bold', zorder=5)
ax.legend(handles=[Line2D([0], [0], color=GREY_D, lw=2.2, ls=(0, (1, 1.1)), label='gap > 1.5, p < 0.05'),
                   Line2D([0], [0], color='#A6A6A6', lw=2.2, ls=(0, (4, 3)), label='gap > 1.5, p ≥ 0.05'),
                   Line2D([0], [0], color='#BFBFBF', lw=1.2, label='independence (≈ 1)'),
                   Line2D([0], [0], color=NAVY, lw=4, label='integration (< 1)')],
          loc='upper center', bbox_to_anchor=(0.5, -0.02), ncol=4, frameon=False, fontsize=7, handlelength=2.6)
save(fig, 'Fig5')
print('Fig1-Fig5 escritas en', OUT)
