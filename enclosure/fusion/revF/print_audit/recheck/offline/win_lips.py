# recheck point 1: the chin's lips over the plate's tongues: free s (shell offset forward) and the vertical gap at home.
import json, numpy as np, trimesh
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely import affinity
E = '/mnt/user-data/uploads/print_audit_recheck/exports/'
front = trimesh.load(E + 'front.stl'); plate = trimesh.load(E + 'plate.stl')
def secs(m, zs, win):
    P = m.section_multiplane(plane_origin=[0, 0, 0], plane_normal=[0, 0, 1], heights=list(zs)); W = box(*win); out = []
    for p in P:
        if p is None:
            out.append(Polygon()); continue
        g = unary_union(list(p.polygons_full)).buffer(0); out.append(g.intersection(W))
    return out
zs = np.arange(2.85, 13.0, 0.1)
res = {}
for side, xs in (('L', (30, 99)), ('R', (-99, -30))):
    win = (xs[0], -20, xs[1], 10)
    sb = secs(front, zs, win); pb = secs(plate, zs, win)
    n = len(zs); cum = [None] * n; acc = Polygon()
    for k in range(n - 1, -1, -1):
        acc = unary_union([acc, pb[k]]); cum[k] = acc
    free = []
    for s in np.round(np.arange(0.0, 2.01, 0.01), 2):
        hit = 0; kb = None
        for k in range(n):
            if sb[k].is_empty or cum[k].is_empty:
                continue
            a = affinity.translate(sb[k], 0, s).intersection(cum[k]).area
            if a > 1e-6 and a > hit:
                hit = a; kb = k
        free.append((float(s), hit, None if kb is None else round(float(zs[kb]), 2)))
    ok = [s for s, a, z in free if a <= 1e-6]
    # tongue tops: plate material above z 2.85 in this window
    tz = [round(float(z), 2) for z, g in zip(zs, pb) if not g.is_empty]
    res[side] = {'s_free_min': min(ok) if ok else None, 'hits_near': [f for f in free if f[1] > 0][-3:],
                 'plate_above_2.85_z': [tz[0], tz[-1]] if tz else None}
    print(side, res[side])
    # vertical gap at home: for the tongue's xy footprint (plate material z in [2.85, 6]), the lowest shell material above it
    tf = unary_union([g for z, g in zip(zs, pb) if z <= 6.0 and not g.is_empty])
    ztop = max([z for z, g in zip(zs, pb) if not g.is_empty and z <= 6.0] or [None])
    lows = [(round(float(z), 2), round(g.intersection(tf).area, 3)) for z, g in zip(zs, sb) if not g.is_empty and g.intersection(tf).area > 1e-4]
    print(side, 'tongue footprint area', round(tf.area, 2), 'tongue top band z', ztop, 'shell over tongue first z', lows[:3])
    res[side]['tongue_area'] = round(tf.area, 2); res[side]['tongue_top_band'] = ztop; res[side]['shell_over_tongue'] = lows[:5]
    print(side, 'tongue bounds', [round(v, 2) for v in tf.bounds])
json.dump(res, open('g/win_lips.json', 'w'), indent=1)
