# recheck point 1: per shell band, the offset limit it sets on its own (descending shell, box/heads/plate material above it).
#   mode 'max' (frame vs box backs: largest forward s still free) or 'min' (corners vs heads, lips vs plate: smallest s free).
import json, numpy as np, trimesh, sys
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely import affinity
E = '/mnt/user-data/uploads/print_audit_recheck/exports/'
what, side = sys.argv[1], sys.argv[2]
front = trimesh.load(E + 'front.stl')
if what == 'frame':
    obs = trimesh.load(E + ('spkbox_L.stl' if side == 'L' else 'spkbox_R.stl')); xs = (55, 99) if side == 'L' else (-99, -55)
    win = box(xs[0], -68, xs[1], -44); zs = np.arange(2.85, 84.0, 0.25); mode = 'max'
elif what == 'corner':
    obs = trimesh.load(E + 'comp/DRV_screw_heads_env.stl'); xs = (80, 97) if side == 'L' else (-97, -80)
    win = box(xs[0], -8, xs[1], 8); zs = np.arange(2.85, 48.7, 0.25); mode = 'min'
else:
    obs = trimesh.load(E + 'plate.stl'); xs = (20, 40) if side == 'L' else (-40, -20)
    win = box(xs[0], -6, xs[1], 8); zs = np.arange(2.85, 5.4, 0.05); mode = 'min'
def secs(m):
    P = m.section_multiplane(plane_origin=[0, 0, 0], plane_normal=[0, 0, 1], heights=list(zs)); out = []
    for p in P:
        out.append(Polygon() if p is None else unary_union(list(p.polygons_full)).buffer(0).intersection(win))
    return out
sb = secs(front); ob = secs(obs)
n = len(zs); cum = [None] * n; acc = Polygon()
for k in range(n - 1, -1, -1):
    acc = unary_union([acc, ob[k]]); cum[k] = acc
def free(k, s):
    return affinity.translate(sb[k], 0, s).intersection(cum[k]).area <= 1e-6
lim = []
for k in range(n):
    if sb[k].is_empty or cum[k].is_empty:
        continue
    lo, hi = 0.0, 3.0
    if mode == 'max':
        if not free(k, 0.0):
            lim.append((round(float(zs[k]), 2), -1.0)); continue
        if free(k, 3.0):
            continue
        for _ in range(14):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if free(k, mid) else (lo, mid)
        lim.append((round(float(zs[k]), 2), round(lo, 3)))
    else:
        if free(k, 0.0):
            continue
        if not free(k, 3.0):
            lim.append((round(float(zs[k]), 2), 99.0)); continue
        for _ in range(14):
            mid = (lo + hi) / 2
            lo, hi = (lo, mid) if free(k, mid) else (mid, hi)
        lim.append((round(float(zs[k]), 2), round(hi, 3)))
lim.sort(key=lambda t: t[1], reverse=(mode == 'min'))
print(what, side, mode, 'binding bands:', lim[:6])
low = [l for l in lim if l[0] <= 3.6]
print('   bands z<=3.6:', sorted(low)[:6])
json.dump({'what': what, 'side': side, 'mode': mode, 'lim': lim}, open('g/winb_%s_%s.json' % (what, side), 'w'))
