# Block 3, checks on the model after p36 (READ-ONLY for the model; temporary bodies 'TMP_*' are added for measuring and deleted).
#   stage 'fits'   smallest distances, body to body, round the grommet; local ones through hidden temporary crops
#   stage 'way'    the grommet's way in on the door (lifted 2.3, pushed in, set down) against the door and the cradle
#   stage 'slide'  the door's grommet corner (door crop, grommet, its two screws) moved straight back out, 0 to 60, against
#                  every current body the swept box meets
#   stage 'drv'    the driver's line at the grommet's two screws (MICRO: shaft 3 x 60, handle 13 x 97; MICROG grip 40),
#                  on the bench (door and grommet only) and on the unit (every current body)
#   stage 'grid'   level faces of the three changed bodies in the changed places against their layer grids, and the
#                  faces that face down there (overhangs)
# Run: runpy.run_path(D + 'p37_checks.py')['main']('fits')  -> p37_<stage>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
U = (0.0, math.sin(math.radians(18.0)), math.cos(math.radians(18.0)))
SCREWS = [(9.0, -79.3, 10.0), (-9.0, -79.3, 10.0)]
T_TOP = 2.03
LIFT = 2.3


def at(P, t):
    return (P[0] + U[0] * t, P[1] + U[1] * t, P[2] + U[2] * t)


def tmp(X, tb, name):
    return X.add(tb, 'TMP_' + name, show=False)


def crop(X, name, box):
    t = X.wbox(*box); X.sec(t, X.tbm.copy(X.body(name))); return t


def dist(X, a, b):
    r = X.mm.measureMinimumDistance(a, b)
    return round(r.value * 10.0, 3), [round(v, 2) for v in k_.W(r.positionOne)], [round(v, 2) for v in k_.W(r.positionTwo)]


k_ = None


def fits(k, X):
    G, Dr, P, C = X.body('GROMMET_usbc_F'), X.body('HOUSING_F_door'), X.body('FLOOR_PLATE'), X.body('CRADLE_5807')
    for a, b in ((G, Dr), (G, C), (G, P), (G, X.body('SCREWS_M2x6_env')), (Dr, C), (X.body('PD_5807_env'), G)):
        if a is None or b is None:
            continue
        print('%-16s to %-16s %s' % (a.name, b.name, dist(X, a, b)))
    # local: the grommet's parts
    parts = {'flange (y < -83.6)': (-16, 16, -87, -83.6, 9, 35), 'sleeve': (-13, 13, -83.6, -81.0, 12.3, 29),
             'leg and tab (y > -81.65)': (-13, 13, -81.65, -76, 9.9, 14)}
    for nm, box in parts.items():
        t = tmp(X, crop(X, 'GROMMET_usbc_F', box), 'g')
        for b in (Dr, C, P):
            print('  grommet %-24s to %-16s %s' % (nm, b.name, dist(X, t, b)))
        t.deleteMe()
    # local: the door's seats and baffle
    for nm, box in (('seat +x', (4.4, 12.4, -81.8, -76.8, 3.6, 10.01)), ('seat -x', (-12.4, -4.4, -81.8, -76.8, 3.6, 10.01)),
                    ('baffle', (-13.7, 13.7, -81.06, -79.8, 28.1, 31.5)), ('cut-out sill', (-12.8, 12.8, -84.5, -81.0, 11.0, 12.01))):
        t = tmp(X, crop(X, 'HOUSING_F_door', box), 'd')
        out = []
        for b in k.current(X, leads=True):
            if b.name in ('HOUSING_F_door', 'RENDER_FABRIC_door') or b.name.startswith('TMP_'):
                continue
            q = t.boundingBox
            bx = adsk.core.BoundingBox3D.create(k.P3(q.minPoint.x - 0.8, q.minPoint.y - 0.8, q.minPoint.z - 0.8),
                                                k.P3(q.maxPoint.x + 0.8, q.maxPoint.y + 0.8, q.maxPoint.z + 0.8))
            if not bx.intersects(b.boundingBox):
                continue
            d = dist(X, t, b)
            if d[0] < 6.0:
                out.append((d[0], b.name, d[1], d[2]))
        out.sort()
        print('  door %-12s nearest: %s' % (nm, out[:5]))
        t.deleteMe()


def way(k, X):
    g = X.tbm.copy(X.body('GROMMET_usbc_F'))
    door = crop(X, 'HOUSING_F_door', (-20, 20, -90, -70, 2.0, 40))
    cr = X.tbm.copy(X.body('CRADLE_5807'))
    path = [(0, -dy, LIFT) for dy in (12, 8, 6, 4, 3, 2, 1, 0.5)] + [(0, 0, h) for h in (2.3, 2.0, 1.5, 1.0, 0.5, 0.2, 0.0)]
    worst = None
    for d in path:
        t = X.tbm.copy(g); X.move(t, *d)
        vd = X.xv(t, door); vc = X.xv(t, cr)
        print('  grommet moved %-18s: in the door %.4f, in the cradle %.4f' % (d, vd, vc))
    # clearances, lifted and pushed home, and at the start of the drop
    for d in ((0, 0, LIFT), (0, -3.0, LIFT)):
        t = X.tbm.copy(g); X.move(t, *d)
        a = tmp(X, t, 'gw')
        print('  at %s: to the door %s, to the cradle %s' % (d, dist(X, a, X.body('HOUSING_F_door')), dist(X, a, X.body('CRADLE_5807'))))
        a.deleteMe()


def slide(k, X):
    box = (-16.0, 16.0, -86.5, -75.5, 2.8, 34.0)
    mov = [crop(X, 'HOUSING_F_door', box), X.tbm.copy(X.body('GROMMET_usbc_F'))]
    s = X.tbm.copy(X.body('SCREWS_M2x6_env')); X.sec(s, X.wbox(-12, 12, -84, -76, 5, 13)); mov.append(s)
    sweep = (-17.0, 17.0, -150.0, -74.5, 2.0, 35.0)
    sw = X.wbox(*sweep)
    fixed = []
    for b in k.current(X, leads=True):
        if b.name in ('HOUSING_F_door', 'GROMMET_usbc_F', 'SCREWS_M2x6_env', 'RENDER_FABRIC_door') or b.name.startswith('TMP_'):
            continue
        if b.boundingBox.intersects(sw.boundingBox):
            c = X.tbm.copy(b); X.sec(c, X.tbm.copy(sw))
            if c.faces.count:
                fixed.append((b.name, c))
    print('fixed bodies in the sweep: %s' % [n for n, c in fixed])
    for d in (60, 40, 30, 20, 15, 10, 8, 6, 5, 4, 3, 2, 1.5, 1.0, 0.5, 0.2, 0.0):
        hit = {}
        for i, m in enumerate(mov):
            t = X.tbm.copy(m); X.move(t, 0, -d, 0)
            for n, c in fixed:
                v = X.xv(t, c)
                if abs(v) > 0.0005:
                    hit['%s~%s' % (('door', 'grommet', 'screws')[i], n)] = round(v, 4)
        print('  back %5.1f: %s' % (d, hit if hit else 'clear'))


def drv(k, X, which='bench', idx=(0, 1)):
    k.budget(75)
    if which == 'bench':
        hard = [X.body('HOUSING_F_door'), X.body('GROMMET_usbc_F')]
    else:
        hard = [b for b in k.current(X, leads=False) if b.name not in ('SCREWS_M2x6_env', 'RENDER_FABRIC_door')]
    for i in idx:
        P = SCREWS[i]
        o = at(P, T_TOP)
        if which != 'bench':      # only bodies whose box comes within 30 of the line's first 160
            e = at(P, T_TOP + 160.0)
            lo = [min(o[j], e[j]) - 30.0 for j in range(3)]; hi = [max(o[j], e[j]) + 30.0 for j in range(3)]
            sw = X.wbox(lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])
            hard = [b for b in hard if b.boundingBox.intersects(sw.boundingBox)]
        print('screw at x %+.1f, head top %s, %s (%d bodies)' % (P[0], [round(v, 2) for v in o], which, len(hard)))
        print('   ' + k.probe(X, o, U, k.MICRO, k.MICROG, hard, st0=0.5, step=2.0 if which == 'bench' else 3.0))


def grid(k, X):
    spec = {'GROMMET_usbc_F': (10.0, 0.20, 0.12, (-16, 16, -87, -76, 9.9, 34.1)),
            'HOUSING_F_door': (2.8, 0.20, 0.20, (-15, 15, -85, -76, 2.7, 32)),
            'FLOOR_PLATE': (0.0, 0.20, 0.20, [(x - 4.5, x + 4.5, y - 4.5, y + 4.5, -0.1, 3.0) for (x, y) in
                                              ((-19, -77), (19, -74.5), (50, -67), (-50, -67), (64, -45), (-72, -38), (51, -14), (-51, -14))]
                            + [(x - 8, x + 8, y - 8, y + 8, -0.1, 3.0) for (x, y) in ((80, -5.5), (-80, -5.5), (30, -70.6), (-30, -70.6))]
                            + [(52, 78, -90, -64, -0.1, 3.0), (-78, -52, -90, -64, -0.1, 3.0)])}
    for name, (bed, first, lh, box) in spec.items():
        b = X.body(name)
        lv, dn = [], []
        for f in b.faces:
            ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
            n = k.wv(nv); p = k.W(f.pointOnFace)
            bl = box if isinstance(box, list) else [box]
            if not any(q[0] <= p[0] <= q[1] and q[2] <= p[1] <= q[3] and q[4] <= p[2] <= q[5] for q in bl):
                continue
            a = f.area * 100.0
            if f.geometry.surfaceType == 0 and abs(n[2]) > 0.999:
                h = p[2] - bed
                kk = (h - first) / lh if h > first + 1e-6 else (0 if abs(h) < 1e-6 else (h / first))
                off = 0.0 if abs(h) < 1e-6 or abs(h - first) < 1e-4 else (h - first) - round((h - first) / lh) * lh
                lv.append((round(p[2], 3), 'up' if n[2] > 0 else 'down', round(a, 2), round(off, 4), [round(v, 1) for v in p]))
            elif n[2] < -0.5 and a > 0.05:
                dn.append((round(math.degrees(math.acos(-n[2])), 1), round(a, 2), [round(v, 2) for v in p]))
        lv.sort()
        print('%s: level faces in the changed places (bed %.1f, first %.2f, then %.2f)' % (name, bed, first, lh))
        for r in lv:
            print('   z %8.3f %-4s area %8.2f  off grid %+.4f  at %s' % r)
        if name != 'FLOOR_PLATE':
            print('  faces facing down, not level (angle from straight down, area, point):')
            for r in sorted(dn):
                print('   ', r)


def _main(stage):
    global k_
    k = L['load'](); X = k.K(); k_ = k
    print(L['stamp'](), 'before', X.state())
    if stage.startswith('drv'):
        drv(k, X, 'bench' if stage == 'drv' else 'unit', (0, 1) if stage == 'drv' else (int(stage[-1]),))
    else:
        {'fits': fits, 'way': way, 'slide': slide, 'grid': grid}[stage](k, X)
    for b in [b for b in X.root.bRepBodies if b.name.startswith('TMP_')]:
        b.deleteMe()
    print(L['stamp'](), 'after', X.state())


def main(stage):
    L['out']('p37_%s.txt' % stage, _main, stage)
