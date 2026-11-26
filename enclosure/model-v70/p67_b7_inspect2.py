# Block 7, more of the parts as they stand at version 75. READ-ONLY (temporary bodies only).
#   'hood'   BME_HOOD's frame (the top plate's outer face: normal n and a point), every planar face parallel to it with its bed
#            height in the hood's print (top plate's outer face down: bed = (p_top - p).n), every non-planar face; the shell's two
#            pins through the hood (cylinders near the hood's holes); the distance from the hood's top plate's curved edge to the shell
#   'boxL'   SPKBOX_L faces round the plug pocket's step (x 53..61, y -40..-31, z 8..20); the USB-A plug's box
#   'boxR'   SPKBOX_R to the shell: the nearest points, and faces round them
# Run: runpy.run_path(D + 'p67_b7_inspect2.py')['main'](stage)  -> p67_<stage>.txt
import runpy, math

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def hood(k, X):
    b = X.body('BME_HOOD'); top = None
    for f in b.faces:
        if f.geometry.surfaceType == k.PLN and abs(f.area * 100 - 242.4) < 1.0:
            ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); top = (k.W(f.pointOnFace), k.unit(k.wv(nv)))
    p0, n = top
    print('top plate outer face: point %s normal %s' % (k.r2(p0, 4), k.r2(n, 5)))
    for f in b.faces:
        g = f.geometry; p = k.W(f.pointOnFace); a = f.area * 100
        if g.surfaceType == k.PLN:
            ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); m = k.unit(k.wv(nv))
            c = sum(m[i] * n[i] for i in range(3))
            if abs(abs(c) - 1) < 1e-3:
                bed = sum((p0[i] - p[i]) * n[i] for i in range(3))
                print('   level in print: bed %.4f  normal %s (%s in print)  %7.2f mm2  at %s' % (bed, '+n' if c > 0 else '-n', 'faces the bed' if c > 0 else 'faces up', a, k.r2(p)))
        else:
            ws = [k.W(v.geometry) for v in f.vertices]
            print('   non-planar type %d  %7.2f mm2 at %s, box %s' % (g.surfaceType, a, k.r2(p), [round(fn(w[i] for w in ws), 2) for i in range(3) for fn in (min, max)] if ws else None))
    S = X.body('HOUSING_F_front')
    for r in k.holes_of(b, rmin=1.0, rmax=1.3):
        ax = r['a']; A = r['A']
        c = X.cyl(tuple(A[i] - 6 * ax[i] for i in range(3)), tuple(A[i] + 8 * ax[i] for i in range(3)), 1.15)
        X.sec(c, X.tbm.copy(S))
        if c.faces.count:
            st = k.needle_t(X, [c], tuple(A[i] - 6 * ax[i] for i in range(3)), tuple(A[i] + 8 * ax[i] for i in range(3)), 0.02)
            print('hood hole %s axis %s: shell along the axis from A-6: %s' % (A, ax, st))
        for f in S.faces:
            g = f.geometry
            if g.surfaceType == k.CYL and abs(g.radius * 10 - 0.9) < 0.05:
                o = k.W(g.origin)
                dd = math.sqrt(max(0.0, sum((o[i] - A[i]) ** 2 for i in range(3)) - (sum((o[i] - A[i]) * ax[i] for i in range(3))) ** 2))
                if dd < 0.5:
                    ws = [k.W(v.geometry) for v in f.vertices]
                    ts = [sum((w[i] - A[i]) * ax[i] for i in range(3)) for w in ws]
                    print('   shell pin r 0.9, %.2f mm2, along the axis from A: %.3f .. %.3f' % (f.area * 100, min(ts), max(ts)))
    t = X.add(X.tbm.copy(S), 'TMP_s', show=False)
    for f in b.faces:
        if f.geometry.surfaceType not in (k.PLN, k.CYL) and f.area * 100 > 5:
            r = X.mm.measureMinimumDistance(f, t)
            print('   non-planar face %.2f mm2 to the shell: %.3f at %s / %s' % (f.area * 100, r.value * 10, k.r2(k.W(r.positionOne)), k.r2(k.W(r.positionTwo))))
    t.deleteMe()


def boxL(k, X):
    b = X.body('SPKBOX_L')
    for r in sorted(k.faces(X, b, (52, 62, -41, -30, 6, 22), amin=0.05), key=lambda r: (r[0], str(r[1]))):
        print('   ', r)
    print('USBA_plug_env', k.wbb(X, X.body('USBA_plug_env')))
    c = X.wbox(50, 62, -40, -31, 6, 22); X.sec(c, X.tbm.copy(b))
    for z in (12.0, 15.2, 17.0):
        for y in (-37.0, -36.0, -35.7, -35.0, -34.0):
            print('   z %.1f y %.1f along x: %s' % (z, y, [(round(50 + a, 2), round(50 + q, 2)) for a, q in k.needle_t(X, [c], (50.0, y, z), (62.0, y, z), 0.02)]))


def boxR(k, X):
    b = X.body('SPKBOX_R'); S = X.body('HOUSING_F_front')
    r = X.mm.measureMinimumDistance(b, S)
    p1 = k.W(r.positionOne); p2 = k.W(r.positionTwo)
    print('SPKBOX_R to the shell: %.3f at %s / %s' % (r.value * 10, k.r2(p1), k.r2(p2)))
    for f in b.faces:
        ws = [k.W(v.geometry) for v in f.vertices]
        if ws and min(abs(w[0] - p1[0]) + abs(w[1] - p1[1]) + abs(w[2] - p1[2]) for w in ws) < 1.0:
            g = f.geometry
            if g.surfaceType == k.PLN:
                ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
                print('   face plane n %s %.2f mm2 box %s' % (k.r2(k.wv(nv), 3), f.area * 100, [round(fn(w[i] for w in ws), 2) for i in range(3) for fn in (min, max)]))
            else:
                print('   face type %d %.2f mm2 box %s' % (g.surfaceType, f.area * 100, [round(fn(w[i] for w in ws), 2) for i in range(3) for fn in (min, max)]))
    bL = X.body('SPKBOX_L'); r = X.mm.measureMinimumDistance(bL, S)
    print('SPKBOX_L to the shell: %.3f at %s / %s' % (r.value * 10, k.r2(k.W(r.positionOne)), k.r2(k.W(r.positionTwo))))


def _main(stage):
    k = L['load'](); X = k.K(); k.budget(75)
    print(L['stamp'](), 'before', X.state())
    {'hood': hood, 'boxL': boxL, 'boxR': boxR}[stage](k, X)
    for t in [t for t in X.root.bRepBodies if t.name.startswith('TMP_')]:
        t.deleteMe()
    print(L['stamp'](), 'after', X.state())


def main(stage):
    L['out']('p67_%s.txt' % stage, _main, stage)
