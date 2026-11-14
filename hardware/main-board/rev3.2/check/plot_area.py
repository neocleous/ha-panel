"""Plot an exported area (export_area.py) layer by layer, with the planned relief drawn on top.
    python3 plot_area.py <area.json> <out.png> [depth] [corner radius] [title]
"""
import json
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Rectangle
from matplotlib.path import Path
from matplotlib.patches import PathPatch
import numpy as np

NETCOL = {'GND': '#9e9e9e', '/Amplifier/PVDD': '#ef6c00', 'I2C_SCL': '#1565c0', 'I2C_SDA': '#00838f',
          '/Amplifier/AMP_GPIO2': '#c62828'}


def poly_patch(p, **kw):
    verts, codes = [], []
    for ring in [p['outer']] + p.get('holes', []):
        if len(ring) < 3:
            continue
        verts += ring + [ring[0]]
        codes += [Path.MOVETO] + [Path.LINETO] * (len(ring) - 1) + [Path.CLOSEPOLY]
    if not verts:
        return None
    return PathPatch(Path(np.array(verts), codes), **kw)


def relief_outline(depth, r, v1=1.5, v2=13.0):
    ue = 43.5 - depth
    lo, hi = v1 - r, v2 + r
    pts = [(43.5, lo), (ue + r, lo)]
    for a in np.linspace(-np.pi / 2, -np.pi, 24):
        pts.append((ue + r + r * np.cos(a), lo + r + r * np.sin(a)))
    for a in np.linspace(np.pi, np.pi / 2, 24):
        pts.append((ue + r + r * np.cos(a), hi - r + r * np.sin(a)))
    pts += [(43.5, hi)]
    return np.array(pts)


def main(src, out, depth=1.5, r=1.0, title=''):
    d = json.load(open(src))
    u0, u1, v0, v1 = d['area']
    layers = [('F.Cu', 'door-side face (F.Cu)'), ('In1.Cu', 'layer 2 (In1.Cu, ground)'), ('In2.Cu', 'layer 3 (In2.Cu, supply planes)'), ('B.Cu', 'back face (B.Cu)')]
    fig, axs = plt.subplots(1, 4, figsize=(24, 9.5))
    rel = relief_outline(depth, r)
    for ax, (lay, lname) in zip(axs, layers):
        ax.set_facecolor('#fbfbf6')
        for it in d['items']:
            if it['kind'] == 'pour' and it['layer'] == lay:
                c = NETCOL.get(it['net'], '#bdbdbd')
                for p in it['polys']:
                    pp = poly_patch(p, facecolor=c, alpha=0.22, edgecolor=c, lw=0.5)
                    if pp:
                        ax.add_patch(pp)
        for it in d['items']:
            if it['kind'] == 'track' and it['layer'] == lay:
                c = NETCOL.get(it['net'], '#6d4c41')
                for p in it['polys']:
                    pp = poly_patch(p, facecolor=c, alpha=0.9, edgecolor='none')
                    if pp:
                        ax.add_patch(pp)
            if it['kind'] == 'pad' and it['layer'] == lay:
                c = NETCOL.get(it['net'], '#795548')
                for p in it['polys']:
                    pp = poly_patch(p, facecolor=c, alpha=0.75, edgecolor='k', lw=0.4)
                    if pp:
                        ax.add_patch(pp)
                if lay == 'F.Cu' or it.get('tht'):
                    ax.text(it['at'][0], it['at'][1], it['ref'], fontsize=5.5, ha='center', va='center', color='k')
            if it['kind'] == 'via':
                c = NETCOL.get(it['net'], '#4e342e')
                for p in it['polys']:
                    pp = poly_patch(p, facecolor=c, alpha=0.95, edgecolor='k', lw=0.4)
                    if pp:
                        ax.add_patch(pp)
            if it['kind'] == 'courtyard' and lay == 'F.Cu':
                for p in it['polys']:
                    pp = poly_patch(p, facecolor='none', edgecolor='#7b1fa2', lw=0.6, ls='--')
                    if pp:
                        ax.add_patch(pp)
            if it['kind'] == 'silk' and ((lay == 'F.Cu' and it['layer'] == 'F.Silkscreen') or (lay == 'B.Cu' and it['layer'] == 'B.Silkscreen')):
                for p in it['polys']:
                    pp = poly_patch(p, facecolor='#212121', alpha=0.5, edgecolor='none')
                    if pp:
                        ax.add_patch(pp)
            if it['kind'] == 'drawing' and it['layer'] == 'Edge.Cuts':
                for p in it['polys']:
                    pp = poly_patch(p, facecolor='k', edgecolor='k', lw=0.8)
                    if pp:
                        ax.add_patch(pp)
        ax.add_patch(MPoly(rel, closed=True, facecolor='#ffcdd2', alpha=0.55, edgecolor='#b71c1c', lw=1.2))
        # copper keep-off line 0.3 inside the new edge
        ax.plot([43.5 - depth - 0.3] * 2, [1.5 - r - 0.3, 13.0 + r + 0.3], color='#b71c1c', lw=0.8, ls=':')
        ax.axvline(43.5, color='k', lw=1.0)
        ax.set_xlim(u0, u1)
        ax.set_ylim(v0, v1)
        ax.set_aspect('equal')
        ax.set_title(lname, fontsize=10)
        ax.grid(True, lw=0.3, alpha=0.5)
        ax.set_xlabel('u (mm)')
    axs[0].set_ylabel('v (mm)')
    fig.suptitle(title or 'Relief %.2f deep, inner corners r %.2f (red); dotted: 0.3 copper keep-off' % (depth, r), fontsize=12)
    handles = [Rectangle((0, 0), 1, 1, color=c, alpha=0.8) for c in NETCOL.values()]
    fig.legend(handles, ['ground', 'amplifier supply (PVDD)', 'I2C clock', 'I2C data', 'amplifier GPIO2'], loc='lower center', ncol=5)
    fig.tight_layout(rect=(0, 0.04, 1, 0.96))
    fig.savefig(out, dpi=150)
    print('wrote', out)


if __name__ == '__main__':
    a = sys.argv
    main(a[1], a[2], float(a[3]) if len(a) > 3 else 1.5, float(a[4]) if len(a) > 4 else 1.0, a[5] if len(a) > 5 else '')
