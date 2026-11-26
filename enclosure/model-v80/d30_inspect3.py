# Block 3 (the faces on the grid, D458, D471): what is there before anything moves. READ-ONLY (temporary bodies only).
#   plate    FLOOR_PLATE: its level faces by height (z, looking up or down, area, count, off the 0.2 grid); each face at the
#            heights D458 names (0.5, 2.5, 3.7, 4.35, 7.5, 12.5) with its box; its round faces with an upright axis (holes,
#            counterbores, posts): radius, centre, from z to z
#   boxes    SPKBOX_L / _R: the level faces that look down or up along z below z 8 (feet, floors) with their boxes; round faces
#            with an upright axis below z 12 (the floor inserts' holes); the faces at y -0.78 (tab tops) with their boxes
#   shell    HOUSING_F_front: its level faces (square to y) at y -23.3 and y -63.5 with box, area and which way each looks
#   front    for each face D458 names: the bodies of the unit that stand in front of it within 1.0, with the true distance
#            (a slab 0.05 thick laid on the face, cropped to the face's box, measured to each body near it)
#   feet     the foot bodies and whatever else touches the recess floors
#   top      every body whose lowest point lies near the base plate's top, with its distance to the plate
#   nb       the neighbours of the faces that will move (kind, slope), to see where a root is tapered or an edge chamfered
# Run: runpy.run_path(D + 'd30_inspect3.py')['main'](stage)  -> d30_<stage>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
L = runpy.run_path(D + 'v80_lib.py')
PLN = adsk.core.SurfaceTypes.PlaneSurfaceType
CYL = adsk.core.SurfaceTypes.CylinderSurfaceType
NAMED_Z = (0.5, 2.5, 3.7, 4.35, 7.5, 12.5)


def fbox(k, f):
    pts = [k.W(v.geometry) for v in f.vertices]
    for e in f.edges:
        ev = e.evaluator; ok, t0, t1 = ev.getParameterExtents(); ok, sp = ev.getStrokes(t0, t1, 0.02)
        pts += [k.W(q) for q in sp]
    if not pts:
        return None
    return [round(fn(q[i] for q in pts), 3) for i in range(3) for fn in (min, max)]


def level(k, b, ax):
    out = []
    for f in b.faces:
        if f.geometry.surfaceType != PLN:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); n = k.wv(nv)
        if abs(abs(n[ax]) - 1) > 1e-4:
            continue
        out.append((f, k.W(f.pointOnFace), 1 if n[ax] > 0 else -1))
    return out


def off(h, lh=0.2):
    q = h / lh
    return (q - round(q)) * lh


def st_plate(k, X):
    b = X.body('FLOOR_PLATE')
    print('FLOOR_PLATE: box %s, volume %.3f' % (k.r2(k.wbb(X, b), 3), b.volume * 1000))
    g = {}
    fs = level(k, b, 2)
    for f, p, s in fs:
        a = g.setdefault((round(p[2], 4), s), [0.0, 0]); a[0] += f.area * 100; a[1] += 1
    print('level faces by height: z, looks, mm2, faces, off the 0.2 grid')
    for (z, s), (ar, n) in sorted(g.items()):
        o = off(z)
        print('   z %8.4f %-4s %10.2f  %3d  %s' % (z, 'up' if s > 0 else 'down', ar, n, '' if abs(o) < 0.002 else 'OFF %+.3f' % o))
    for zz in NAMED_Z:
        print('faces at z %.2f:' % zz)
        for f, p, s in fs:
            if abs(p[2] - zz) < 0.003:
                print('   %-4s %9.2f mm2  box %s' % ('up' if s > 0 else 'down', f.area * 100, fbox(k, f)))
    rows = []
    for f in b.faces:
        gm = f.geometry
        if gm.surfaceType != CYL:
            continue
        a = k.unit(k.wv(gm.axis))
        if abs(abs(a[2]) - 1) > 1e-3:
            continue
        o = k.W(gm.origin); bx = fbox(k, f)
        if bx is None:
            continue
        rows.append((round(o[0], 2), round(o[1], 2), round(gm.radius * 10, 3), bx[4], bx[5], round(f.area * 100, 1)))
    grp = {}
    for r in set(rows):
        grp.setdefault((r[2], r[3], r[4]), []).append((r[0], r[1]))
    print('round faces with an upright axis, grouped: radius, from z to z: count, centres (the first eight)')
    for key, cs in sorted(grp.items()):
        print('   r %6.3f  z %6.3f .. %6.3f : %3d  %s' % (key + (len(cs), sorted(cs)[:8])))


def st_boxes(k, X):
    for nm in ('SPKBOX_L', 'SPKBOX_R'):
        b = X.body(nm)
        print('%s: box %s' % (nm, k.r2(k.wbb(X, b), 3)))
        for f, p, s in sorted(level(k, b, 2), key=lambda r: (r[1][2], r[2])):
            if p[2] < 8.0:
                print('   level z %7.4f %-4s %9.2f mm2 box %s' % (p[2], 'up' if s > 0 else 'down', f.area * 100, fbox(k, f)))
        rows = []
        for f in b.faces:
            gm = f.geometry
            if gm.surfaceType != CYL:
                continue
            a = k.unit(k.wv(gm.axis))
            if abs(abs(a[2]) - 1) > 1e-3:
                continue
            o = k.W(gm.origin); bx = fbox(k, f)
            if bx is None or bx[4] > 12.0:
                continue
            rows.append((round(o[0], 2), round(o[1], 2), round(gm.radius * 10, 3), bx[4], bx[5]))
        for r in sorted(set(rows)):
            print('   round, upright axis: (%7.2f, %7.2f) r %6.3f  z %6.3f .. %6.3f' % r)
        for f, p, s in level(k, b, 1):
            if abs(p[1] + 0.78) < 0.003 or abs(p[1] + 0.8) < 0.003:
                print('   level y %7.4f %-12s %9.2f mm2 box %s' % (p[1], 'looks +y' if s > 0 else 'looks -y', f.area * 100, fbox(k, f)))


def st_shell(k, X):
    b = X.body('HOUSING_F_front')
    for f, p, s in level(k, b, 1):
        if abs(p[1] + 23.3) < 0.01 or abs(p[1] + 63.5) < 0.01 or abs(p[1] + 63.494) < 0.01:
            print('HOUSING_F_front level y %8.4f %-9s height %8.4f  %8.2f mm2  box %s' % (p[1], 'looks +y' if s > 0 else 'looks -y', 6.7992 - p[1], f.area * 100, fbox(k, f)))


def near_face(k, X, body, f, p, s, ax, reach=1.0, skip=()):
    """Bodies of the unit in front of face f (looking along axis ax in direction s) within 'reach': true distances from a thin
    slab laid on the face (0.05 thick, inside the body) cropped to the face's box."""
    bx = fbox(k, f)
    lo = list(bx)
    if s > 0:
        lo[2 * ax] = p[ax] - 0.05; lo[2 * ax + 1] = p[ax]
    else:
        lo[2 * ax] = p[ax]; lo[2 * ax + 1] = p[ax] + 0.05
    piece = X.wbox(*lo); X.sec(piece, X.tbm.copy(body))
    if not piece.faces.count:
        return []
    zone = list(bx); zone[2 * ax] = min(bx[2 * ax], p[ax]) - (0.0 if s > 0 else reach); zone[2 * ax + 1] = max(bx[2 * ax + 1], p[ax]) + (reach if s > 0 else 0.0)
    for i in (0, 1, 2):
        if i != ax:
            zone[2 * i] -= 0.3; zone[2 * i + 1] += 0.3
    zb = X.wbox(*zone)
    out = []
    for ob in k.current(X, leads=True):
        if ob.name == body.name or ob.name in skip:
            continue
        if not ob.boundingBox.intersects(zb.boundingBox):
            continue
        c = X.tbm.copy(ob); X.sec(c, X.tbm.copy(zb))
        if not c.faces.count:
            continue
        r = X.mm.measureMinimumDistance(piece, c)
        out.append((round(r.value * 10, 3), ob.name))
    return sorted(out)


def st_front(k, X, which=('plate', 'shell', 'boxes')):
    k.budget(70)
    if 'plate' in which:
        b = X.body('FLOOR_PLATE')
        for f, p, s in sorted(level(k, b, 2), key=lambda r: r[1][2]):
            if not any(abs(p[2] - zz) < 0.003 for zz in NAMED_Z) or f.area * 100 < 1.0:
                continue
            if abs(p[2] - 2.5) < 0.003:
                continue                                           # the top is read by st_top
            print('FLOOR_PLATE z %.2f %-4s %8.2f mm2 at (%.1f, %.1f): %s' % (p[2], 'up' if s > 0 else 'down', f.area * 100, p[0], p[1], near_face(k, X, b, f, p, s, 2)))
            if k.late():
                print('time'); return
    if 'shell' in which:
        b = X.body('HOUSING_F_front')
        for f, p, s in level(k, b, 1):
            if abs(p[1] + 23.3) < 0.01 or abs(p[1] + 63.5) < 0.01 or abs(p[1] + 63.494) < 0.01:
                print('HOUSING_F_front y %.4f %s %8.2f mm2: %s' % (p[1], 'looks +y' if s > 0 else 'looks -y', f.area * 100, near_face(k, X, b, f, p, s, 1)))
    if 'boxes' in which:
        for nm in ('SPKBOX_L', 'SPKBOX_R'):
            b = X.body(nm)
            for f, p, s in level(k, b, 1):
                if abs(p[1] + 0.78) < 0.003:
                    print('%s y %.4f %s %8.2f mm2: %s' % (nm, p[1], 'looks +y' if s > 0 else 'looks -y', f.area * 100, near_face(k, X, b, f, p, s, 1)))
            for f, p, s in level(k, b, 2):
                if p[2] < 4.0 and s < 0 and f.area * 100 > 5.0:
                    print('%s z %.4f down %8.2f mm2 at (%.1f, %.1f): %s' % (nm, p[2], f.area * 100, p[0], p[1], near_face(k, X, b, f, p, s, 2)))


def st_top(k, X, top=2.5):
    """What stands on or just above the base plate's top face: every body of the unit whose lowest point lies within 1.0 above it,
    with its true distance to the plate."""
    k.budget(70)
    P = X.body('FLOOR_PLATE')
    rows = []
    for ob in k.current(X, leads=True):
        if ob.name == 'FLOOR_PLATE':
            continue
        w = k.wbb(X, ob)
        if w[4] > top + 1.0 or w[5] < top - 0.5:
            continue
        r = X.mm.measureMinimumDistance(ob, P)
        rows.append((round(w[4], 3), round(r.value * 10, 3), ob.name, k.r2(k.W(r.positionTwo), 2)))
        if k.late():
            print('time'); break
    print('bodies whose lowest point lies between z %.1f and %.1f: lowest z, distance to the base plate, name, the plate\'s nearest point' % (top - 0.5, top + 1.0))
    for r in sorted(rows):
        print('   %7.3f  %7.3f  %-22s %s' % r)


def st_feet(k, X):
    P = X.body('FLOOR_PLATE')
    for ob in k.current(X, leads=True):
        w = k.wbb(X, ob)
        if ob.name != 'FLOOR_PLATE' and w[4] < 1.0:
            r = X.mm.measureMinimumDistance(ob, P)
            print('%-22s box %s  volume %.3f  to the plate %.3f at %s; visible %s' % (ob.name, k.r2(w, 3), ob.volume * 1000, r.value * 10, k.r2(k.W(r.positionTwo), 2), ob.isLightBulbOn))


def nb(k, f):
    """The faces that share an edge with f: kind, a few figures, box; grouped."""
    T = adsk.core.SurfaceTypes
    names = {T.PlaneSurfaceType: 'plane', T.CylinderSurfaceType: 'cylinder', T.ConeSurfaceType: 'cone', T.TorusSurfaceType: 'torus', T.SphereSurfaceType: 'sphere'}
    seen = {}; out = {}
    for e in f.edges:
        for g in e.faces:
            if g.tempId == f.tempId or g.tempId in seen:
                continue
            seen[g.tempId] = 1
            gm = g.geometry; kind = names.get(gm.surfaceType, 'other %s' % gm.surfaceType)
            if kind == 'plane':
                ok, nv = g.evaluator.getNormalAtPoint(g.pointOnFace); n = k.r2(k.wv(nv), 3)
                key = ('plane', tuple(n))
            elif kind == 'cylinder':
                a = k.r2(k.unit(k.wv(gm.axis)), 2); key = ('cylinder', round(gm.radius * 10, 3), tuple(abs(q) for q in a))
            elif kind == 'cone':
                a = k.r2(k.unit(k.wv(gm.axis)), 2); key = ('cone', round(math.degrees(gm.halfAngle), 1), round(gm.radius * 10, 3), tuple(abs(q) for q in a))
            elif kind == 'torus':
                key = ('torus', round(gm.majorRadius * 10, 3), round(gm.minorRadius * 10, 3))
            else:
                key = (kind,)
            a = out.setdefault(key, [0, None]); a[0] += 1
            if a[1] is None:
                a[1] = fbox(k, g)
    return out


def st_nb(k, X):
    P = X.body('FLOOR_PLATE')
    for f, p, s in level(k, P, 2):
        if (abs(p[2] - 2.5) < 0.003 and s > 0 and f.area * 100 > 1000) or (abs(p[2]) < 0.003 and f.area * 100 > 1000):
            print('FLOOR_PLATE face z %.2f (%.2f mm2), its neighbours: kind, figures: count, the first one\'s box' % (p[2], f.area * 100))
            for key, (n, bx) in sorted(nb(k, f).items(), key=lambda r: str(r[0])):
                print('   %-60s %4d  %s' % (key, n, bx))
    for zz in (1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.6, 2.7, 5.55, 6.5, 9.4, 8.0, 2.8, 1.0):
        rows = [(round(f.area * 100, 2), 'up' if s > 0 else 'down', fbox(k, f)) for f, p, s in level(k, P, 2) if abs(p[2] - zz) < 0.003]
        print('FLOOR_PLATE faces at z %.2f: %d; %s' % (zz, len(rows), sorted(rows, key=lambda r: -r[0])[:4]))
    for nm in ('SPKBOX_L', 'SPKBOX_R'):
        b = X.body(nm)
        for f, p, s in level(k, b, 2):
            if abs(p[2] - 3.7) < 0.003 and s < 0:
                print('%s bottom face z 3.7 (%.2f mm2), neighbours:' % (nm, f.area * 100))
                for key, (n, bx) in sorted(nb(k, f).items(), key=lambda r: str(r[0])):
                    print('   %-60s %4d  %s' % (key, n, bx))
        for f, p, s in level(k, b, 1):
            if abs(p[1] + 0.78) < 0.003:
                print('%s tab top y %.4f (%.2f mm2), neighbours:' % (nm, p[1], f.area * 100))
                for key, (n, bx) in sorted(nb(k, f).items(), key=lambda r: str(r[0])):
                    print('   %-60s %4d  %s' % (key, n, bx))
    S = X.body('HOUSING_F_front')
    for f, p, s in level(k, S, 1):
        if abs(p[1] + 23.3) < 0.01 or abs(p[1] + 63.5) < 0.01:
            print('HOUSING_F_front face y %.4f (%.2f mm2) box %s, neighbours:' % (p[1], f.area * 100, fbox(k, f)))
            for key, (n, bx) in sorted(nb(k, f).items(), key=lambda r: str(r[0])):
                print('   %-60s %4d  %s' % (key, n, bx))


def _main(stage, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'plate': st_plate, 'boxes': st_boxes, 'shell': st_shell, 'front': st_front, 'top': st_top, 'feet': st_feet, 'nb': st_nb}[stage](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(stage, tag='', **kw):
    L['out']('d30_%s%s.txt' % (stage, ('_' + tag) if tag else ''), _main, stage, **kw)
# END
