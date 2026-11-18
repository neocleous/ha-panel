"""recheck3: section panels of version 67 (filled) with version 66's outline (red) where its mesh is at hand.
spec: list of dicts {axis, value, win:[a0,a1,b0,b1], parts:[names], title, grid}. usage: r3_sec.py out.png spec.json [ncol]"""
import sys, json, os, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import fdm_lib
from fdm_lib import *
import sec
from sec import patch
M66 = '/home/claude/r3/scan66/mesh'
_c66 = {}
def world66(name):
    if name not in _c66:
        fv = os.path.join(M66, name + '.v.f32')
        if not os.path.exists(fv):
            _c66[name] = None
        else:
            v = np.fromfile(fv, dtype=np.float32).reshape(-1, 3).astype(float); t = np.fromfile(os.path.join(M66, name + '.t.i32'), dtype=np.int32).reshape(-1, 3)
            _c66[name] = trimesh.Trimesh(vertices=to_world(v), faces=t, process=True)
    return _c66[name]
def lines66(name, axis, value):
    m = world66(name)
    if m is None: return []
    ax = 'xyz'.index(axis); n = np.zeros(3); n[ax] = 1.0; o = np.zeros(3); o[ax] = value
    L = trimesh.intersections.mesh_plane(m, n, o)
    keep = [i for i in range(3) if i != ax]
    return L[:, :, keep] if len(L) else []
COLS = {'HOUSING_F_front': '#9aa7b4', 'HOUSING_F_plate': '#e9b44c', 'SLAB_frame': '#7fb685', 'FLOOR_PLATE': '#c9a27b', 'HOUSING_F_door': '#8e7dbe', 'HOUSING_F_cap': '#5fa8d3',
        'SPKBOX_L': '#d98880', 'SPKBOX_R': '#d98880', 'RESP_CARRIER': '#76b7b2', 'CRADLE_5807': '#b07aa1', 'TOUCH_CLIP_L': '#edc948', 'TOUCH_CLIP_R': '#edc948', 'GROMMET_usbc_F': '#59a14f', 'BME_HOOD': '#f28e2b'}
def panels(out, specs, ncol=3, size=4.6):
    n = len(specs); nrow = (n + ncol - 1) // ncol
    fig, axs = plt.subplots(nrow, ncol, figsize=(size * ncol, size * nrow), dpi=110, squeeze=False)
    for ax in axs.ravel()[n:]: ax.axis('off')
    for ax, sp in zip(axs.ravel(), specs):
        axis, value, (a0, a1, b0, b1), parts = sp['axis'], sp['value'], sp['win'], sp['parts']
        for nm in parts:
            for p in sec.section_polys(nm, axis, value):
                ax.add_patch(patch(p, facecolor=COLS.get(nm, '#bbbbbb'), edgecolor='k', linewidth=0.5))
            if sp.get('old', True):
                for s in lines66(nm, axis, value):
                    ax.plot(s[:, 0], s[:, 1], color='#d00000', linewidth=0.6, alpha=0.8)
        ax.set_xlim(a0, a1); ax.set_ylim(b0, b1); ax.set_aspect('equal')
        lab = {'x': ('y', 'z'), 'y': ('x', 'z'), 'z': ('x', 'y')}[axis]
        ax.set_xlabel('world ' + lab[0], fontsize=7); ax.set_ylabel('world ' + lab[1], fontsize=7)
        g = sp.get('grid', 1.0)
        ax.set_xticks(np.arange(np.ceil(a0 / g) * g, a1 + 1e-9, g)); ax.set_yticks(np.arange(np.ceil(b0 / g) * g, b1 + 1e-9, g))
        ax.tick_params(labelsize=6); ax.grid(True, linewidth=0.3, alpha=0.6)
        ax.set_title('%s  [%s = %.2f]' % (sp.get('title', ''), axis, value), fontsize=8)
    fig.tight_layout(); fig.savefig(out); plt.close(fig)
if __name__ == '__main__':
    specs = json.load(open(sys.argv[2])); panels(sys.argv[1], specs, ncol=int(sys.argv[3]) if len(sys.argv) > 3 else 3)
