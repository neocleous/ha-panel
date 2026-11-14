# recheck point 1: door frame's lower ends vs the boxes' backs: largest forward offset s that is free (shell lowered straight).
import json, numpy as np, trimesh, sys
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely import affinity
E = '/mnt/user-data/uploads/print_audit_recheck/exports/'
front = trimesh.load(E + 'front.stl')
side = sys.argv[1]
bx = trimesh.load(E + ('spkbox_L.stl' if side == 'L' else 'spkbox_R.stl'))
xs = (55, 99) if side == 'L' else (-99, -55)
win = box(xs[0], -68, xs[1], -44)
zs = np.arange(2.85, 45.0, 0.25)
def secs(m):
    P = m.section_multiplane(plane_origin=[0, 0, 0], plane_normal=[0, 0, 1], heights=list(zs)); out = []
    for p in P:
        if p is None:
            out.append(Polygon()); continue
        out.append(unary_union(list(p.polygons_full)).buffer(0).intersection(win))
    return out
sb = secs(front); bb = secs(bx)
# box material in bands >= k (descending shell meets box material that sits at or above where the shell point ends)
n = len(zs); cum = [None] * n; acc = Polygon()
for k in range(n - 1, -1, -1):
    acc = unary_union([acc, bb[k]]); cum[k] = acc
res = []
for s in np.round(np.arange(1.30, 1.81, 0.01), 2):
    hit = 0.0; kb = None
    for k in range(n):
        if sb[k].is_empty or cum[k].is_empty:
            continue
        a = affinity.translate(sb[k], 0, s).intersection(cum[k]).area
        if a > hit:
            hit = a; kb = k
    res.append((float(s), round(hit, 5), None if kb is None else round(float(zs[kb]), 2)))
ok = [s for s, a, z in res if a <= 1e-6]
print(side, 'free up to s =', max(ok) if ok else None, ' first hits:', [r for r in res if r[1] > 1e-6][:4])
# the gap in place (s = 0): min y-distance between shell and box material in the window, per band
gaps = []
for k in range(n):
    if sb[k].is_empty or bb[k].is_empty:
        continue
    gaps.append((round(float(zs[k]), 2), round(sb[k].distance(bb[k]), 3)))
gm = min(gaps, key=lambda g: g[1]) if gaps else None
print(side, 'in place, nearest shell-box gap in this window', gm, 'shell lowest z here', min([z for z, g in zip(zs, sb) if not g.is_empty]))
json.dump({'side': side, 'free_max': max(ok) if ok else None, 'res': res, 'gap_in_place': gm}, open('g/win_frame_%s.json' % side, 'w'))
