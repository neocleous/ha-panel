# HA panel print audit (P5 / settled items): does the slicer print a thin wall? G-code extrusion of the part (not support)
#   transformed to world (x_rel, y, z) via the build transform, then summed inside a world box per layer.
#   Usage: python3 pa_wallcheck.py <gcode tag> <tag> <okey> x0 x1 y0 y1 z0 z1
import sys, json, numpy as np
sys.path.insert(0, '/home/claude/pa')
from pa_gview import parse
from pa_geom import ORIENT, load_world, to_build, b2w
g, tag, okey = sys.argv[1:4]; x0, x1, y0, y1, z0, z1 = [float(v) for v in sys.argv[4:10]]
S = parse('/home/claude/pa/slice/gc_%s.gcode' % g)
mw = load_world(tag); mb, M = to_build(mw, ORIENT[tag][okey])
ns = S[S[:, 5] > 1]
gx = (min(ns[:, 1].min(), ns[:, 3].min()), max(ns[:, 1].max(), ns[:, 3].max()))
gy = (min(ns[:, 2].min(), ns[:, 4].min()), max(ns[:, 2].max(), ns[:, 4].max()))
b = mb.bounds
off = ((gx[0] + gx[1]) / 2 - (b[0][0] + b[1][0]) / 2, (gy[0] + gy[1]) / 2 - (b[0][1] + b[1][1]) / 2)
P = ns.copy()
mid = np.c_[(P[:, 1] + P[:, 3]) / 2 - off[0], (P[:, 2] + P[:, 4]) / 2 - off[1], P[:, 0] - 0.1]
w = b2w(M, mid)
L = np.hypot(P[:, 3] - P[:, 1], P[:, 4] - P[:, 2])
sel = (w[:, 0] >= x0) & (w[:, 0] <= x1) & (w[:, 1] >= y0) & (w[:, 1] <= y1) & (w[:, 2] >= z0) & (w[:, 2] <= z1)
zs = np.unique(P[sel, 0])
print(g, 'box', [x0, x1, y0, y1, z0, z1], 'layers with extrusion', len(zs), 'total mm', round(float(L[sel].sum()), 1))
for z in zs[:: max(1, len(zs) // 12)]:
    m = sel & (P[:, 0] == z)
    print('  build z %.2f  segs %d  mm %.1f  types %s' % (z, m.sum(), L[m].sum(), sorted(set(int(t) for t in P[m, 5]))))
