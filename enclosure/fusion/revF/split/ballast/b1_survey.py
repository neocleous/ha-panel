"""Ballast pass, block 1: the base plate's own features and the unit's low bodies (read-only).
Prints: (1) the plate's horizontal faces by height (floor top z 2.5, ledge z 1.8, pads, posts, counterbores, recesses);
(2) the inner loops of the floor's top face grouped by size (the intake field: 475 holes Ø2.0 on a 3.0 grid);
(3) every unit body below z 40 with its world box; (4) the Ø8.3 magnet pockets in the door and the shell.
World frame mm: x = viewer's left, y toward the screen, z up from the plate's underside."""
import adsk.core, adsk.fusion, sys, time, math

def run(_context):
    t0 = time.time()
    k = sys.modules['cp2k']; X = k.K()
    PL = adsk.core.SurfaceTypes.PlaneSurfaceType; CYL = adsk.core.SurfaceTypes.CylinderSurfaceType
    o = k.W(adsk.core.Point3D.create(0, 0, 0))
    def wn(v):
        p = k.W(adsk.core.Point3D.create(v.x, v.y, v.z)); d = [p[i] - o[i] for i in range(3)]; L = math.sqrt(sum(q * q for q in d)); return [q / L for q in d]
    def wbb(bb):
        ps = [k.W(adsk.core.Point3D.create(x, y, z)) for x in (bb.minPoint.x, bb.maxPoint.x) for y in (bb.minPoint.y, bb.maxPoint.y) for z in (bb.minPoint.z, bb.maxPoint.z)]
        return [round(min(p[i] for p in ps), 2) if j == 0 else round(max(p[i] for p in ps), 2) for i in range(3) for j in (0, 1)]
    b = X.body('FLOOR_PLATE'); top = None
    print('--- (1) plate faces square to z, area 5 to 5000 mm2 one by one')
    for f in b.faces:
        if f.geometry.surfaceType != PL:
            continue
        n = wn(f.geometry.normal)
        if abs(n[2]) < 0.99:
            continue
        e = wbb(f.boundingBox); z = round((e[4] + e[5]) / 2.0, 2); a = f.area * 100.0
        up = (n[2] > 0) != f.isParamReversed
        if f.loops.count > 400 and abs(z - 2.5) < 0.05:
            top = f
        if 5 <= a <= 5000:
            print('z %5.2f %-4s area %6.1f  centre x %7.2f y %7.2f  size %5.2f x %5.2f' % (z, 'up' if up else 'down', a, (e[0] + e[1]) / 2, (e[2] + e[3]) / 2, e[1] - e[0], e[3] - e[2]))
        elif a > 5000:
            print('z %5.2f %-4s area %8.1f  big face, loops %d, bounds %s' % (z, 'up' if up else 'down', a, f.loops.count, e[:4]))
    print('--- (2) floor-top loops grouped')
    groups = {}
    for L in top.loops:
        if L.isOuter:
            continue
        e = wbb(L.boundingBox)
        groups.setdefault((round(e[1] - e[0], 1), round(e[3] - e[2], 1), L.edges.count), []).append(e)
    for key in sorted(groups, key=lambda q: -len(groups[q])):
        es = groups[key]
        print('w %.1f h %.1f edges %d: n %d, centres %s' % (key[0], key[1], key[2], len(es),
              [(round((e[0] + e[1]) / 2, 2), round((e[2] + e[3]) / 2, 2)) for e in es][:12]))
    print('--- (3) unit bodies below z 40')
    rows = sorted(((bb.name, k.wbb(X, bb)) for bb in k.current(X, leads=True)), key=lambda r: r[1][4])
    for n, e in rows:
        if e[4] < 40.0:
            print('%-26s x %7.1f..%7.1f  y %7.1f..%7.1f  z %6.1f..%6.1f' % (n, e[0], e[1], e[2], e[3], e[4], e[5]))
    print('--- (4) magnet pockets r 4.15')
    for n in ('HOUSING_F_door', 'HOUSING_F_front'):
        seen = []
        for f in X.body(n).faces:
            g = f.geometry
            if g.surfaceType != CYL or abs(g.radius * 10.0 - 4.15) > 0.02:
                continue
            q = k.W(f.centroid); key = tuple(round(v, 0) for v in q)
            if key not in seen:
                seen.append(key); print(n, 'centroid (%.1f, %.1f, %.1f)' % tuple(q))
    print('t', round(time.time() - t0, 1))
