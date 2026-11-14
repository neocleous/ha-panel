# recheck point 1 (block 3): the plate unit's window from the meshes, independently of the instructions.
#   For the shell lowered straight down at a forward offset s (+y), shell material that ends at height <= top of an obstacle passes
#   through the obstacle's height band. Footprints by 0.25 bands; collision if translate(shell band k, +s) meets obstacle material in
#   bands >= k. Reports, per obstacle group, the s range that is free and the band (z) that binds.
import sys, json, numpy as np, trimesh
from shapely.geometry import Polygon, MultiPolygon, box
from shapely.ops import unary_union
from shapely import affinity
E = '/mnt/user-data/uploads/print_audit_recheck/exports/'
front = trimesh.load(E + 'front.stl'); plate = trimesh.load(E + 'plate.stl')
boxL = trimesh.load(E + 'spkbox_L.stl'); boxR = trimesh.load(E + 'spkbox_R.stl'); heads = trimesh.load(E + 'comp/DRV_screw_heads_env.stl')

def secs(m, zs, win):
    out = []
    P = m.section_multiplane(plane_origin=[0, 0, 0], plane_normal=[0, 0, 1], heights=list(zs))
    W = box(*win)
    for p in P:
        if p is None:
            out.append(Polygon()); continue
        polys = [g for g in p.polygons_full]
        g = unary_union(polys).buffer(0) if polys else Polygon()
        out.append(g.intersection(W))
    return out

def free_range(shell_bands, obs_bands, svals):
    # shell band k vs obstacle union of bands >= k
    n = len(shell_bands); obs_cum = [None] * n; acc = Polygon()
    for k in range(n - 1, -1, -1):
        acc = unary_union([acc, obs_bands[k]]); obs_cum[k] = acc
    res = []
    for s in svals:
        hit = 0.0; kb = None
        for k in range(n):
            if shell_bands[k].is_empty or obs_cum[k].is_empty:
                continue
            a = affinity.translate(shell_bands[k], 0, s).intersection(obs_cum[k]).area
            if a > 1e-6 and a > hit:
                hit = a; kb = k
        res.append((s, hit, kb))
    return res

out = {}
svals = np.round(np.arange(0.0, 2.01, 0.01), 2)
# 1. front corners vs upper/lower outer driver heads (x within +-(80..96), y -6..8)
for side, xs in (('L', (80, 97)), ('R', (-97, -80))):
    win = (xs[0], -8, xs[1], 8)
    zs = np.arange(2.85, 48.6 + 0.01, 0.25)
    sb = secs(front, zs, win); hb = secs(heads, zs, win)
    r = free_range(sb, hb, svals)
    ok = [s for s, a, k in r if a <= 1e-6]
    bind = [(s, round(a, 4), round(float(zs[k]), 2) if k is not None else None) for s, a, k in r if 0 < a]
    out['corner_' + side] = {'s_free_min': min(ok) if ok else None, 'last_hits': bind[-3:]}
    print(side, 'corner: free from s =', min(ok) if ok else None, 'binding', bind[-3:])
# 2. door frame lower ends vs box backs (x +-(43..97), y -66..-40), shell rear; s positive moves shell forward
for side, m, xs in (('L', boxL, (40, 99)), ('R', boxR, (-99, -40))):
    win = (xs[0], -70, xs[1], -35)
    zs = np.arange(2.85, 84.0, 0.25)
    sb = secs(front, zs, win); bb = secs(m, zs, win)
    r = free_range(sb, bb, svals)
    ok = [s for s, a, k in r if a <= 1e-6]
    first_hit = [(s, round(a, 4), round(float(zs[k]), 2)) for s, a, k in r if a > 1e-6][:3]
    out['frame_' + side] = {'s_free_max': max(ok) if ok else None, 'first_hits': first_hit}
    print(side, 'frame: free up to s =', max(ok) if ok else None, 'first hits', first_hit)
json.dump(out, open('g/win_check.json', 'w'), indent=1)
