"""Section pictures in world coordinates. usage: sec.py out.png axis value a0 a1 b0 b1 PART[:colour] ...
axis x -> picture axes (y, z); axis y -> (x, z); axis z -> (x, y)."""
import sys, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from fdm_lib import *

_cache = {}
def world_mesh(name):
    if name not in _cache:
        m = load_model_mesh(name)
        _cache[name] = trimesh.Trimesh(vertices=to_world(m.vertices), faces=m.faces, process=False)
    return _cache[name]

def section_polys(name, axis, value):
    m = world_mesh(name)
    ax = 'xyz'.index(axis)
    n = np.zeros(3); n[ax] = 1.0
    o = np.zeros(3); o[ax] = value
    lines = trimesh.intersections.mesh_plane(m, n, o)
    if len(lines) == 0:
        return []
    keep = [i for i in range(3) if i != ax]
    seg = np.round(lines[:, :, keep], 5)
    seg = seg[np.linalg.norm(seg[:, 0] - seg[:, 1], axis=1) > 1e-6]
    from shapely.ops import polygonize
    from shapely.geometry import LineString, MultiLineString
    ml = unary_union(MultiLineString([LineString(s) for s in seg]))
    faces = list(polygonize(ml))
    a = seg[:, 0]; b = seg[:, 1]
    out = []
    for f in faces:
        q = f.representative_point(); x0, y0 = q.x, q.y
        cond = (a[:, 1] > y0) != (b[:, 1] > y0)
        xs = a[cond, 0] + (y0 - a[cond, 1]) * (b[cond, 0] - a[cond, 0]) / (b[cond, 1] - a[cond, 1])
        if np.count_nonzero(xs > x0) % 2 == 1:
            out.append(f)
    return polys_of(unary_union(out)) if out else []

def patch(poly, **kw):
    verts = []; codes = []
    for ring in [poly.exterior] + list(poly.interiors):
        c = np.asarray(ring.coords)
        verts += list(c); codes += [Path.MOVETO] + [Path.LINETO] * (len(c) - 2) + [Path.CLOSEPOLY]
    return PathPatch(Path(verts, codes), **kw)

def draw(out, axis, value, win, parts, title='', notes=(), size=7.0, grid=None):
    a0, a1, b0, b1 = win
    fig, ax = plt.subplots(figsize=(size, size * (b1 - b0) / (a1 - a0) + 0.5), dpi=110)
    cols = ['#9aa7b4', '#e9b44c', '#7fb685', '#c97b84', '#8e7dbe', '#5fa8d3']
    for i, spec in enumerate(parts):
        nm, _, col = spec.partition(':')
        for p in section_polys(nm, axis, value):
            ax.add_patch(patch(p, facecolor=col or cols[i % len(cols)], edgecolor='k', linewidth=0.5, alpha=0.95))
    ax.set_xlim(a0, a1); ax.set_ylim(b0, b1); ax.set_aspect('equal')
    lab = {'x': ('world y', 'world z'), 'y': ('world x', 'world z'), 'z': ('world x', 'world y')}[axis]
    ax.set_xlabel(lab[0] + ' (mm)'); ax.set_ylabel(lab[1] + ' (mm)')
    if grid:
        ax.set_xticks(np.arange(np.floor(a0 / grid) * grid, a1 + 1e-9, grid)); ax.set_yticks(np.arange(np.floor(b0 / grid) * grid, b1 + 1e-9, grid))
    ax.grid(True, linewidth=0.3, alpha=0.6)
    for (x, y, s) in notes:
        ax.annotate(s, (x, y), fontsize=8, color='#b00020')
    ax.set_title(title or 'section %s = %.2f' % (axis, value), fontsize=9)
    fig.tight_layout(); fig.savefig(out); plt.close(fig)

if __name__ == '__main__':
    out, axis, value = sys.argv[1], sys.argv[2], float(sys.argv[3])
    win = [float(v) for v in sys.argv[4:8]]
    draw(out, axis, value, win, sys.argv[8:], grid=float(os.environ.get('GRID', '0')) or None)
