# Block 1: what seats the drivers today. READ-ONLY (temporary bodies and measurements between model bodies only).
# Stages:
#   bodies    the bodies of the drivers' joint: world boxes, volumes, lumps
#   spk       the model's driver (SPK_L, SPK_R) and the screw heads' envelope: level faces along y, round faces about y
#   boxfront  both boxes' fronts: faces square to y in front of y -8, round faces about y (bosses, pilots, insert holes, opening)
#   shellbay  the shell in each speaker bay: faces square to y, round faces about y, between y -2 and the chin
#   stack     needles along y at stations of one driver: every body's solid stretches
#   near      smallest distances, body to body, between the plate unit's bodies and the shell / the screen plate, with the points
#   push      the plate unit pushed forward (world +y) in steps: which bodies meet the shell or the screen plate first
# Run: runpy.run_path(D + 'd10_inspect.py')['main'](stage)  -> d10_<stage>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
L = runpy.run_path(D + 'v80_lib.py')
PLN = adsk.core.SurfaceTypes.PlaneSurfaceType; CYL = adsk.core.SurfaceTypes.CylinderSurfaceType; CON = adsk.core.SurfaceTypes.ConeSurfaceType


def ext(k, f):
    ws = [k.W(v.geometry) for v in f.vertices]
    if not ws:
        bb = f.boundingBox; ws = [k.W(bb.minPoint), k.W(bb.maxPoint)]
    return [round(fn(w[i] for w in ws), 3) for i in range(3) for fn in (min, max)]


def hits(e, box):
    return all(e[2 * i] <= box[2 * i + 1] and e[2 * i + 1] >= box[2 * i] for i in range(3))


def yfaces(k, b, box, amin=0.2):
    """Faces square to world y (planes) and round about world y (cylinders, cones) whose vertex box meets the world box."""
    P = []; R = []
    for f in b.faces:
        g = f.geometry; t = g.surfaceType
        if t not in (PLN, CYL, CON):
            continue
        if t == PLN:
            ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
            n = k.wv(nv)
            if abs(abs(n[1]) - 1) > 1e-4:
                continue
            e = ext(k, f)
            if not hits(e, box) or f.area * 100 < amin:
                continue
            P.append((round(k.W(f.pointOnFace)[1], 4), '+y' if n[1] > 0 else '-y', round(f.area * 100, 2), e[0], e[1], e[4], e[5], f.loops.count))
        else:
            a = k.unit(k.wv(g.axis))
            if abs(abs(a[1]) - 1) > 1e-3:
                continue
            e = ext(k, f)
            if not hits(e, box):
                continue
            o = k.W(g.origin)
            p = f.pointOnFace; ok, nv = f.evaluator.getNormalAtPoint(p)
            pw = k.W(p); nw = k.wv(nv)
            rad = (pw[0] - o[0], pw[2] - o[2])
            kind = 'pin ' if rad[0] * nw[0] + rad[1] * nw[2] > 0 else 'hole'
            if t == CYL:
                R.append((round(o[0], 2), round(o[2], 2), round(g.radius * 20, 3), kind, e[2], e[3], round(f.area * 100, 2), 'cyl'))
            else:
                R.append((round(o[0], 2), round(o[2], 2), round(math.hypot(rad[0], rad[1]) * 2, 3), kind, e[2], e[3], round(f.area * 100, 2), 'cone %.1f deg' % math.degrees(g.halfAngle)))
    return sorted(P), sorted(R)


def show(P, R):
    print('  level faces (square to y): y, facing, mm2, x from..to, z from..to, loops')
    for r in P:
        print('    y %9.4f %s %9.2f  x %8.3f..%8.3f  z %7.3f..%7.3f  loops %d' % r)
    print('  round faces about y: axis x, z; diameter; kind; y from..to; mm2')
    for r in R:
        print('    axis (%7.2f, %6.2f)  dia %7.3f  %s  y %8.3f..%8.3f  %8.2f  %s' % r)


def st_bodies(k, X):
    for b in k.current(X, leads=True):
        n = b.name
        if any(q in n.upper() for q in ('SPK', 'DRV', 'FOAM', 'GASKET', 'USBA', 'TOUCH_CLIP', 'RADAR', 'LD2410')):
            print('%-22s box %s  vol %10.3f  lumps %d faces %d visible %s' % (n, k.wbb(X, b), b.volume * 1000, b.lumps.count, b.faces.count, b.isLightBulbOn))


def st_spk(k, X):
    for n in ('SPK_L', 'SPK_R'):
        b = X.body(n)
        print('%s: box %s vol %.3f lumps %d faces %d' % (n, k.wbb(X, b), b.volume * 1000, b.lumps.count, b.faces.count))
        P, R = yfaces(k, b, (-200, 200, -60, 10, -5, 100), 0.05)
        show(P, R)
        other = {}
        for f in b.faces:
            t = f.geometry.surfaceType
            other[t] = other.get(t, 0) + 1
        print('  face kinds (0 plane, 1 cylinder, 2 cone, 3 sphere, 4 torus, 5 nurbs): %s' % other)
    b = X.body('DRV_screw_heads_env')
    print('DRV_screw_heads_env: vol %.3f lumps %d' % (b.volume * 1000, b.lumps.count))
    for v, bb in X.lumps(X.tbm.copy(b)):
        print('   lump %.3f box %s' % (v, bb))
    P, R = yfaces(k, b, (-200, 200, -60, 10, -5, 100), 0.05)
    show(P, R)


def st_boxfront(k, X):
    for n, sx in (('SPKBOX_L', 1), ('SPKBOX_R', -1)):
        b = X.body(n)
        x0, x1 = sorted((sx * 38.0, sx * 102.0))
        print('%s: box %s' % (n, k.wbb(X, b)))
        P, R = yfaces(k, b, (x0, x1, -8.5, 0.0, 0.0, 90.0), 0.05)
        show(P, R)
        P, R = yfaces(k, b, (x0, x1, -60.0, -8.5, 0.0, 90.0), 0.05)
        print('  deeper, round faces about y only (pilots, sleeves, the wire hole):')
        for r in R:
            print('    axis (%7.2f, %6.2f)  dia %7.3f  %s  y %8.3f..%8.3f  %8.2f  %s' % r)


def st_shellbay(k, X):
    b = X.body('HOUSING_F_front')
    for sx in (1, -1):
        x0, x1 = sorted((sx * 40.0, sx * 100.0))
        print('shell, bay at x %s..%s, y -2..7, z 0..58:' % (x0, x1))
        P, R = yfaces(k, b, (x0, x1, -2.0, 7.0, 0.0, 58.0), 0.05)
        show(P, R)


STATIONS = [('axis', 70.5, 28.0), ('top bar mid', 70.5, 49.5), ('bottom bar mid', 70.5, 6.5), ('above top bar', 70.5, 50.9), ('below top bar', 70.5, 47.5),
            ('screw inner low', 52.75, 10.25), ('screw outer low', 88.25, 10.25), ('screw inner top', 52.75, 45.75), ('screw outer top', 88.25, 45.75),
            ('side strip inner', 48.5, 28.0), ('side strip outer', 92.5, 28.0), ('corner inner low', 48.2, 5.7), ('corner outer top', 92.8, 50.3),
            ('ring edge top', 70.5, 45.5), ('ring edge side', 53.0, 28.0), ('flange mid top', 70.5, 48.6), ('between ring and edge side', 50.0, 28.0)]


def st_stack(k, X, sx=1):
    side = 'L' if sx > 0 else 'R'
    x0, x1 = sorted((sx * 40.0, sx * 100.0))
    box = (x0, x1, -14.0, 8.0, 0.0, 58.0)
    crops = {n: L['crop'](X, n, box) for n in ('HOUSING_F_front', 'SPKBOX_' + side, 'SPK_' + side, 'DRV_screw_heads_env', 'FLOOR_PLATE')}
    print('needles along y from -14 to +8 (stretches are y from..to), side %s' % side)
    for name, x, z in STATIONS:
        print(' %-26s x %+7.2f z %6.2f' % (name, sx * x, z))
        for n, c in crops.items():
            s = [(round(-14.0 + a, 3), round(-14.0 + b, 3)) for a, b in k.needle_t(X, [c], (sx * x, -14.0, z), (sx * x, 8.0, z), 0.02)]
            if s:
                print('     %-22s %s' % (n, s))


UNIT = ['SPK_L', 'SPK_R', 'DRV_screw_heads_env', 'SPKBOX_L', 'SPKBOX_R', 'FLOOR_PLATE']


def st_near(k, X):
    for fx in ('HOUSING_F_front', 'HOUSING_F_plate'):
        F = X.body(fx)
        for n in UNIT:
            r = X.mm.measureMinimumDistance(X.body(n), F)
            print('%-22s to %-16s %8.4f  at %s / %s' % (n, fx, r.value * 10, k.r2(k.W(r.positionOne), 3), k.r2(k.W(r.positionTwo), 3)))


def st_push(k, X):
    k.budget(70)
    fixed = {'HOUSING_F_front': L['crop'](X, 'HOUSING_F_front', (-110, 110, -62, 8, 0, 90)), 'HOUSING_F_plate': X.tbm.copy(X.body('HOUSING_F_plate'))}
    movers = {}
    for n in UNIT:
        m = X.tbm.copy(X.body(n))
        if n == 'FLOOR_PLATE':
            X.sec(m, X.wbox(-110, 110, -8, 9, -1, 15))
        movers[n] = m
    for d in (0.0, 0.02, 0.05, 0.1, 0.15, 0.2, 0.24, 0.26, 0.3, 0.34, 0.36, 0.4, 0.5, 0.6, 0.7, 0.8):
        row = []
        for n, m in movers.items():
            t = X.move(X.tbm.copy(m), 0.0, d, 0.0)
            for fn, f in fixed.items():
                v = X.xv(t, f)
                if abs(v) > 0.0005:
                    row.append('%s|%s %.3f' % (k.sn(n), k.sn(fn), v))
        print('forward %.2f: %s' % (d, '; '.join(row) if row else 'nothing shared'))
        if k.late():
            print('time used up'); break


def _main(stage, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'bodies': st_bodies, 'spk': st_spk, 'boxfront': st_boxfront, 'shellbay': st_shellbay, 'stack': st_stack, 'near': st_near, 'push': st_push}[stage](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(stage, tag=None, **kw):
    L['out']('d10_%s.txt' % (tag or stage), _main, stage, **kw)
# END
