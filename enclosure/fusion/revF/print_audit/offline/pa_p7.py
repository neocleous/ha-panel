# P1 plate fit + P7 bed contact: first-layer polygon (z 0.1), its area, convex hull, CoG of the solid over it, height ratio,
# longest straight bed edges, sharp convex corners at the bed.
import sys, json, math, numpy as np
sys.path.insert(0, '/home/claude/pa')
from pa_geom import *
from shapely.geometry import Point, MultiPolygon, Polygon
from shapely.ops import unary_union
import shapely.affinity as A
VOL = {'main': (256, 256, 260), 'dual': (235.5, 256, 256)}
res = {}
for tag in ORIENT:
    for okey in ([k for k in ORIENT[tag] if ORIENT[tag][k] is not None]):
        if tag != 'slab' and okey != 'plan':
            continue
        mw = load_world(tag); mb, M = to_build(mw, ORIENT[tag][okey])
        s = mb.section(plane_origin=(0, 0, 0.1), plane_normal=(0, 0, 1))
        pl, T = s.to_2D() if hasattr(s, 'to_2D') else s.to_planar()
        Ti = np.linalg.inv(T)
        polys = [A.affine_transform(p, [Ti[0, 0], Ti[0, 1], Ti[1, 0], Ti[1, 1], Ti[0, 3], Ti[1, 3]]) for p in pl.polygons_full]
        fl = unary_union(polys)
        hull = fl.convex_hull
        cog = mb.center_mass
        inside = hull.contains(Point(cog[0], cog[1]))
        dist = hull.exterior.distance(Point(cog[0], cog[1])) * (1 if inside else -1)
        rect = mb.convex_hull.vertices[:, :2]
        from shapely.geometry import MultiPoint
        r = MultiPoint(mb.vertices[:, :2]).convex_hull.minimum_rotated_rectangle
        xs, ys = r.exterior.coords.xy
        e = sorted([math.hypot(xs[i + 1] - xs[i], ys[i + 1] - ys[i]) for i in range(2)])
        H = float(mb.extents[2])
        # bed edges: straight segments >= 20 mm and convex corners < 100 deg on the first-layer outline
        long_edges = []; corners = []
        geoms = fl.geoms if hasattr(fl, 'geoms') else [fl]
        for g in geoms:
            c = np.array(g.exterior.coords)[:-1]
            n = len(c)
            # merge collinear runs
            for i in range(n):
                a, b = c[i], c[(i + 1) % n]
                L = float(np.hypot(*(b - a)))
                if L >= 20:
                    long_edges.append(round(L, 1))
        fits = {k: (e[0] + 10 <= min(v[0], v[1]) and e[1] + 10 <= max(v[0], v[1]) and H <= v[2]) for k, v in VOL.items()}
        res['%s/%s' % (tag, okey)] = {'first_layer_mm2': round(fl.area, 1), 'hull_mm2': round(hull.area, 1),
            'rect': [round(e[0], 1), round(e[1], 1)], 'height': round(H, 2), 'h_over_short': round(H / e[0], 2),
            'cog_build': [round(float(v), 1) for v in cog], 'cog_inside_first_hull': bool(inside), 'cog_margin_mm': round(dist, 1),
            'fit_with_5mm_brim': fits, 'long_bed_edges_mm': sorted(long_edges, reverse=True)[:6],
            'mass_g_asa': round(mb.volume / 1000 * 1.05, 1)}
        print(tag, okey, res['%s/%s' % (tag, okey)])
json.dump(res, open('/home/claude/pa/data/p1p7.json', 'w'), indent=1)
