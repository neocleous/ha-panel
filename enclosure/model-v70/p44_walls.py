# Block 4, its first part (architect log 2026-11-24-d, section 6, points 3 and 4): clearances and walls, measured.
# READ-ONLY for the model: temporary bodies 'TMP_*' are added for distances and deleted again. Works on p43's temporary bodies
# (k.c['b4_grommet'], ['b4_door']) or, with which='model', on the model's bodies.
#   'gap'    the grommet and the door's two seats to the base plate, body to body (bounded)
#   'walls'  rays as the FDM rule's section 3 measures walls: from points on a hole's surface, along the surface's normal into the
#            material ("true"), and the same direction laid level ("in the layer": the grommet and the door both print with world
#            z up). A ray counts when its first solid stretch starts within 0.05 of its point. Reported: the least of each, where.
#              grommet: the spot face's bore (r 2.4, square to the screw, from the countersink's top up) - "the leg beside each
#                       spot face"; the countersink (90 deg, r 1.1 at 0.93 along the axis to r 2.05 at 1.88) and the hole (r 1.1)
#              door:    the two new pilots (r 0.8, 4.6 deep from the seat at z 10.0 along the 18 deg axis)
# Run: runpy.run_path(D + 'p44_walls.py')['main']('gap')  -> p44_<stage>_<which>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
U = (0.0, math.sin(math.radians(18.0)), math.cos(math.radians(18.0)))
SCREWS = [(9.0, -79.3, 10.0), (-9.0, -79.3, 10.0)]
k_ = None


def unit(v):
    n = math.sqrt(sum(w * w for w in v)); return tuple(w / n for w in v)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


E1 = unit(cross(U, (1.0, 0.0, 0.0)))     # two directions square to the screw's axis
E2 = unit(cross(U, E1))


def pt(P, t, r, phi):
    c, s = math.cos(phi), math.sin(phi)
    e = tuple(E1[i] * c + E2[i] * s for i in range(3))
    return tuple(P[i] + U[i] * t + e[i] * r for i in range(3)), e


def ray(k, X, parts, p, n, reach=4.0):
    a = tuple(p[i] - n[i] * 0.02 for i in range(3)); b = tuple(p[i] + n[i] * reach for i in range(3))
    s = k.needle_t(X, parts, a, b, 0.02)
    if not s or s[0][0] > 0.07:
        return None
    return round(s[0][1] - 0.02, 3)


def scan(k, X, parts, P, stations, label):
    best_t, best_l = None, None
    n_ok = 0
    for (t, r, kind) in stations:
        for j in range(24):
            phi = 2 * math.pi * j / 24.0
            p, e = pt(P, t, r, phi)
            n = e if kind == 'cyl' else unit(tuple(e[i] - U[i] for i in range(3)))
            w = ray(k, X, parts, p, n)
            if w is None:
                continue
            n_ok += 1
            h = unit((n[0], n[1], 0.0)) if abs(n[2]) < 0.999 else None
            wl = ray(k, X, parts, p, h) if h else None
            if best_t is None or w < best_t[0]:
                best_t = (w, [round(v, 2) for v in p], round(t, 2), round(math.degrees(phi)))
            if wl is not None and (best_l is None or wl < best_l[0]):
                best_l = (wl, [round(v, 2) for v in p], round(t, 2), round(math.degrees(phi)))
    print('  %-40s rays that start on the face %4d; least true %s; least in the layer %s' % (label, n_ok, best_t, best_l))


def dist(X, a, b):
    r = X.mm.measureMinimumDistance(a, b)
    return round(r.value * 10.0, 3), [round(v, 2) for v in k_.W(r.positionOne)], [round(v, 2) for v in k_.W(r.positionTwo)]


def bodies(k, X, which):
    if which == 'model':
        return X.tbm.copy(X.body('GROMMET_usbc_F')), X.tbm.copy(X.body('HOUSING_F_door'))
    return X.tbm.copy(k.c['b4_grommet']), X.tbm.copy(k.c['b4_door'])


def gap(k, X, which):
    g, d = bodies(k, X, which)
    P = X.body('FLOOR_PLATE') if which == 'model' or k.c.get('b4_plate') is None else X.add(X.tbm.copy(k.c['b4_plate']), 'TMP_p', show=False)
    print('base plate measured: %s' % P.name)
    tg = X.add(g, 'TMP_g', show=False)
    print('grommet to FLOOR_PLATE %s' % (dist(X, tg, P),))
    for nm, bx in (('ear +x', (4.0, 13.0, -79.5, -75.5, 9.9, 12.5)), ('ear -x', (-13.0, -4.0, -79.5, -75.5, 9.9, 12.5))):
        t = X.wbox(*bx); X.sec(t, X.tbm.copy(g)); tb = X.add(t, 'TMP_e', show=False)
        print('  grommet %s to FLOOR_PLATE %s' % (nm, dist(X, tb, P)))
    for nm, bx in (('seat +x', (4.4, 12.4, -81.8, -76.5, 3.6, 10.01)), ('seat -x', (-12.4, -4.4, -81.8, -76.5, 3.6, 10.01))):
        t = X.wbox(*bx); X.sec(t, X.tbm.copy(d)); tb = X.add(t, 'TMP_s', show=False)
        print('door %s to FLOOR_PLATE %s; to CRADLE_5807 %s' % (nm, dist(X, tb, P), dist(X, tb, X.body('CRADLE_5807'))))
    # the door's boss tops: level faces at 10.8 and the holes' roofs
    for (bx, by) in ((-19.0, -77.0), (19.0, -74.5), (50.0, -67.0), (-50.0, -67.0)):
        t = X.wbox(bx - 7, bx + 7, by - 9, by + 9, 8.0, 12.0); X.sec(t, X.tbm.copy(d))
        zs = sorted(set(round(k.W(v.geometry)[2], 3) for v in t.vertices if k.W(v.geometry)[2] > 9.5))
        print('  door boss (%+.0f, %+.0f): vertex heights above 9.5 in its crop: %s' % (bx, by, zs))


def walls(k, X, which):
    k.budget(78)
    g, d = bodies(k, X, which)
    for P in SCREWS:
        sx = 1 if P[0] > 0 else -1
        gc = X.wbox(sx * 3.0, sx * 15.0, -83.0, -75.0, 9.9, 16.0); X.sec(gc, X.tbm.copy(g))
        st_sf = [(t, 2.4, 'cyl') for t in (1.92, 2.1, 2.4, 2.7, 3.0, 3.4, 3.8, 4.3)]
        st_cs = [(0.93 + q, 1.1 + q, 'cone') for q in (0.05, 0.25, 0.45, 0.65, 0.85, 0.93)] + [(t, 1.1, 'cyl') for t in (0.1, 0.4, 0.7)]
        print('screw at x %+.1f:' % P[0])
        scan(k, X, [gc], P, st_sf, 'grommet, spot face bore (the leg beside it)')
        scan(k, X, [gc], P, st_cs, 'grommet, countersink and hole')
        dc = X.wbox(sx * 2.0, sx * 15.0, -84.5, -75.5, 3.0, 11.0); X.sec(dc, X.tbm.copy(d))
        st_p = [(-t, 0.8, 'cyl') for t in (0.05, 0.3, 0.8, 1.4, 2.0, 2.6, 3.2, 3.8, 4.3, 4.55)]
        scan(k, X, [dc], P, st_p, 'door, pilot r 0.8 (its wall)')


def _main(stage, which):
    global k_
    k = L['load'](); X = k.K(); k_ = k
    print(L['stamp'](), 'before', X.state(), 'on', which)
    {'gap': gap, 'walls': walls}[stage](k, X, which)
    for b in [b for b in X.root.bRepBodies if b.name.startswith('TMP_')]:
        b.deleteMe()
    print(L['stamp'](), 'after', X.state())


def main(stage, which='b4'):
    L['out']('p44_%s_%s.txt' % (stage, which), _main, stage, which)
