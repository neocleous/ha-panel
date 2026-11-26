# Block 4, its first part (architect log 2026-11-24-d, section 6, point 4): the two walls, measured as the FDM rule's section 3
# measures walls, done in two ways (p44_walls.py's surface rays read the acute edges where a leaning hole meets a level face,
# 0.0 to 0.16, which are edges, not walls). READ-ONLY for the model (temporary bodies only).
#   in the layer: level rays at every print layer of the part (both print with world z up: the grommet at 10.0 + 0.20 + 0.12 k,
#     the door at 2.8 + 0.2 k), cast from the hole's axis outward in 72 directions; the first solid stretch is the wall in that
#     direction in that layer. Reported: the least, its layer and direction, where it ends.
#   true: the least distance from the hole's own faces (cylinder, and for the grommet its countersink) to every other face of
#     the part that does not touch them, each face copied on its own (bounded).
#   grommet: the spot face's bore (r 2.4, square to the screw, above the countersink's top) - "the leg beside each spot face";
#   door: the two new pilots (r 0.8, from the seat at z 10.0 down 4.6 along the 18 deg axis).
# Run: runpy.run_path(D + 'p44b_walls.py')['main']('b4')  -> p44b_<which>.txt   (which: 'b4' = p43's bodies, 'model')
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
U = (0.0, math.sin(math.radians(18.0)), math.cos(math.radians(18.0)))
SCREWS = [(9.0, -79.3, 10.0), (-9.0, -79.3, 10.0)]


def axis_at(P, z):
    t = (z - P[2]) / U[2]
    return (P[0] + U[0] * t, P[1] + U[1] * t, z), t


def level(k, X, part, P, zs, tmin, tmax, reach=6.0):
    best = None
    rows = []
    for z in zs:
        c, t = axis_at(P, z)
        if t < tmin or t > tmax:
            continue
        lay = None
        for j in range(72):
            a = 2 * math.pi * j / 72.0
            e = (math.cos(a), math.sin(a), 0.0)
            s = k.needle_t(X, [part], c, tuple(c[i] + e[i] * reach for i in range(3)), 0.02)
            if not s:
                continue
            w = s[0][1] - s[0][0]
            if s[0][0] < 0.3:          # the ray starts in material: the axis is not in the hole here
                continue
            end = tuple(round(c[i] + e[i] * s[0][1], 2) for i in range(3))
            if lay is None or w < lay[0]:
                lay = (round(w, 3), round(z, 2), j * 5, end)
        if lay:
            rows.append(lay)
            if best is None or lay[0] < best[0]:
                best = lay
    return best, rows


def faces_near(k, b, P, r, tsel):
    """the part's own faces of the hole: cylinders of radius r on the screw's axis (and cones on it), within t in tsel"""
    own = []
    for f in b.faces:
        g = f.geometry
        if g.surfaceType == 1 and abs(g.radius * 10 - r) < 0.01:
            o = k.W(g.origin); ax = k.wv(g.axis)
            if abs(abs(sum(ax[i] * U[i] for i in range(3))) - 1) < 1e-4:
                d = [o[i] - P[i] for i in range(3)]
                tt = sum(d[i] * U[i] for i in range(3))
                off = math.sqrt(max(sum(w * w for w in d) - tt * tt, 0))
                if off < 0.01:
                    own.append(f)
        if g.surfaceType == 2 and r is None:
            pass
    return own


def true_min(k, X, b, own):
    """least bounded distance from the faces in own to every other face of b that shares no edge with them"""
    tb = adsk.fusion.TemporaryBRepManager.get()
    touch = set()
    for f in own:
        for e in f.edges:
            for g in e.faces:
                touch.add(g.tempId)
    best = None
    for f in own:
        a = tb.copy(f)
        for g in b.faces:
            if g.tempId in touch:
                continue
            if not g.boundingBox.intersects(f.boundingBox):
                bb = f.boundingBox
                grow = adsk.core.BoundingBox3D.create(adsk.core.Point3D.create(bb.minPoint.x - 0.3, bb.minPoint.y - 0.3, bb.minPoint.z - 0.3),
                                                      adsk.core.Point3D.create(bb.maxPoint.x + 0.3, bb.maxPoint.y + 0.3, bb.maxPoint.z + 0.3))
                if not grow.intersects(g.boundingBox):
                    continue
            r = X.mm.measureMinimumDistance(a, tb.copy(g))
            v = r.value * 10.0
            if best is None or v < best[0]:
                best = (round(v, 3), [round(w, 2) for w in k.W(r.positionOne)], [round(w, 2) for w in k.W(r.positionTwo)])
    return best


def _main(which):
    k = L['load'](); X = k.K(); k.budget(78)
    print(L['stamp'](), 'before', X.state(), 'on', which)
    if which == 'model':
        g, d = X.tbm.copy(X.body('GROMMET_usbc_F')), X.tbm.copy(X.body('HOUSING_F_door'))
    else:
        g, d = X.tbm.copy(k.c['b4_grommet']), X.tbm.copy(k.c['b4_door'])
    gz = [round(10.0 + 0.2 + 0.12 * i, 2) for i in range(0, 32)]          # 10.2 .. 13.92
    dz = [round(2.8 + 0.2 * i, 2) for i in range(14, 37)]                # 5.6 .. 10.0
    for P in SCREWS:
        sx = 1 if P[0] > 0 else -1
        gc = X.wbox(sx * 3.0, sx * 15.0, -83.0, -75.0, 9.9, 16.0); X.sec(gc, X.tbm.copy(g))
        best, rows = level(k, X, gc, P, gz, 1.88, 6.0)
        print('screw at x %+.1f, grommet above the countersink (spot face bore), in the layer: least %s' % (P[0], best))
        print('   per layer (wall, z, direction deg from +x, end): %s' % rows)
        dc = X.wbox(sx * 2.0, sx * 15.0, -84.5, -75.5, 3.0, 11.0); X.sec(dc, X.tbm.copy(d))
        best, rows = level(k, X, dc, P, dz, -4.6, -0.05)
        print('screw at x %+.1f, door pilot, in the layer: least %s' % (P[0], best))
        print('   per layer: %s' % rows)
        # true: bounded faces
        gb = X.add(gc, 'TMP_gc', show=False)
        own = faces_near(k, gb, P, 2.4, None)
        print('   grommet: spot face bore faces found %d; true least to the faces they do not touch: %s' % (len(own), true_min(k, X, gb, own) if own else None))
        db = X.add(dc, 'TMP_dc', show=False)
        own = faces_near(k, db, P, 0.8, None)
        print('   door: pilot faces found %d; true least to the faces they do not touch: %s' % (len(own), true_min(k, X, db, own) if own else None))
        gb.deleteMe(); db.deleteMe()
    print(L['stamp'](), 'after', X.state())


def main(which='b4'):
    L['out']('p44b_%s.txt' % which, _main, which)
