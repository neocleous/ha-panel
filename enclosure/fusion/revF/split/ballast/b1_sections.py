"""Ballast pass, block 1: sections of every unit body below z 40, the door and the shell, at 37 heights, written with the
floor's outlines to ~/Documents/HA_panel_renders/ballast/ (read-only for the design; about 3 s).
TemporaryBRepManager.planeIntersection fails on DRV_screw_heads_env at some heights (lesson 203): those are retried at
+-0.03 / 0.07 and otherwise skipped (it lies at the front, y 0 to 1.65, away from every place studied)."""
import adsk.core, adsk.fusion, sys, time, json, os
LV = [1.0, 2.65, 3.2, 3.7, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.5, 9.0, 9.5, 10.0, 11.0, 12.0, 12.5, 13.5, 14.5, 15.0, 16.0, 17.0,
      18.0, 19.0, 20.0, 21.0, 22.0, 23.0, 24.0, 25.0, 26.0, 27.0, 28.0, 29.0, 30.0]
OUT = os.path.expanduser('~/Documents/HA_panel_renders/ballast')

def strokes(k, edges):
    polys = []
    for ed in edges:
        ev = ed.evaluator
        ok, p0, p1 = ev.getParameterExtents()
        ok, pts = ev.getStrokes(p0, p1, 0.004)
        polys.append([[round(q[0], 2), round(q[1], 2)] for q in (k.W(p) for p in pts)])
    return polys

def run(_context):
    t0 = time.time()
    k = sys.modules['cp2k']; X = k.K()
    wb = {b.name: k.wbb(X, b) for b in k.current(X, leads=True) if b.name not in k.BIG}
    for n in ('HOUSING_F_door', 'HOUSING_F_front', 'FLOOR_PLATE'):
        wb[n] = k.wbb(X, X.body(n))
    names = [n for n, e in wb.items() if e[4] < 40.0 and not n.startswith('HOUSING_F_')] + ['HOUSING_F_door', 'HOUSING_F_front']
    nrm = k.dv((0.0, 0.0, 1.0)); out = {}; fails = []
    for z in LV:
        lev = {}
        for n in names:
            e = wb[n]
            if not (e[4] < z < e[5]):
                continue
            wire = None
            for dz in (0.0, 0.03, -0.03, 0.07):
                try:
                    wire = X.tbm.planeIntersection(X.body(n), adsk.core.Plane.create(k.Wp(0.0, 0.0, z + dz), nrm)); break
                except RuntimeError:
                    pass
            if wire is None:
                fails.append(('%.2f' % z, n)); continue
            polys = strokes(k, wire.edges)
            if polys:
                lev[n] = polys
        out['%.2f' % z] = lev
    with open(os.path.join(OUT, 'sections_v65.json'), 'w') as f:
        json.dump({'model': 'HA Panel v5 - tapered v65', 'frame': 'world mm: x = viewer left, y toward screen, z up from plate underside',
                   'levels': out, 'wbb': {n: wb[n] for n in names}}, f)
    # the plate's big flat faces: underside (z 0), ledge (z 1.8, outer loop = the plate's outline), floor top (z 2.5, outer loop)
    faces = {}
    for f in X.body('FLOOR_PLATE').faces:
        if f.geometry.surfaceType != adsk.core.SurfaceTypes.PlaneSurfaceType or f.area * 100.0 < 1000:
            continue
        zs = [k.W(f.boundingBox.minPoint)[2], k.W(f.boundingBox.maxPoint)[2]]
        faces['%.2f' % (sum(zs) / 2)] = [{'outer': L.isOuter, 'edges': strokes(k, L.edges)} for L in f.loops if L.isOuter or f.loops.count <= 50]
    with open(os.path.join(OUT, 'plate_faces_v65.json'), 'w') as f:
        json.dump(faces, f)
    print('levels', len(out), 'fails', fails, 't', round(time.time() - t0, 1))
