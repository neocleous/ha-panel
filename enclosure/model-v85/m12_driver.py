# Block 1b and the close: each driver's room in its box and in the shell, read on the model as it stands. READ-ONLY.
# The driver as the model draws it (D481, ../model-v80/d20_build.py): axis x +-70.5, z 28.0; flange y -3.8 to 0.0; basket 40 across at the
# flange to 37.5 at y -15.8 (13 before the rear end), 37.5 to y -18.8; magnet 32 across (the data sheet's) from y -18.8 to the rear
# end at y -28.8 (25.0 behind the flange's back: Daniel's "25mm approx"); the connector's envelope up, 32 wide, to 18.25 from the
# axis (34.25 - 16: Daniel's "about 34.25" over the connector), over the last 10; the ring 36 across, 2.0 proud of the flange's front.
#   room   each zone of the driver as a temporary body, to the box and to the shell: the least distance and the two points;
#          the same zones grown by g all round: what they share with the box (so where the room ends); the rear end on the axis:
#          the stretch of air behind it in the box; the driver set deeper by 0.9 (a depth of 25.9) and 2.0: what it shares
#   faces  the box's faces within 3.0 of the driver's magnet and rear end: kind, normal, point, area
# Run: L.checked('m12_driver.py', sha)['main'](stage, tag)  -> m12_<stage>_<tag>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/box_margins_v85/'
L = runpy.run_path(D + 'm00_lib.py')
AX = 70.5; AZ = 28.0
Y_BACK = -3.8; Y_REAR = -28.8


def zones(k, X, sx, rear=Y_REAR, mr=16.0):
    cx = sx * AX
    z = {}
    z['basket'] = X.cyl((cx, Y_BACK, AZ), (cx, rear + 13.0, AZ), 20.0, 18.75)
    z['band 37.5'] = X.cyl((cx, rear + 13.0, AZ), (cx, rear + 10.0, AZ), 18.75)
    z['magnet'] = X.cyl((cx, rear + 10.0, AZ), (cx, rear, AZ), mr)
    z['rear face'] = X.cyl((cx, rear + 0.01, AZ), (cx, rear, AZ), mr)
    z['connector'] = X.wbox(cx - 16.0, cx + 16.0, rear + 10.0, rear, AZ, AZ + 18.25)
    z['ring'] = X.cyl((cx, 0.0, AZ), (cx, 2.0, AZ), 18.0)
    return z


def dist(k, X, a, b):
    r = X.mm.measureMinimumDistance(a, b)
    return r.value * 10.0, k.r2(k.W(r.positionOne), 2), k.r2(k.W(r.positionTwo), 2)


def st_room(k, X, sides=('L', 'R'), grow=(0.3, 0.5, 0.7, 1.0, 1.5, 2.0)):
    k.budget(72)
    for s in sides:
        sx = 1 if s == 'L' else -1; cx = sx * AX
        B = X.body('SPKBOX_' + s); S = X.body('HOUSING_F_front'); Bc = X.tbm.copy(B)
        d, p, q = dist(k, X, X.body('SPK_' + s), B)
        print('%s: the model\'s driver SPK_%s to SPKBOX_%s %.4f at %s / %s' % (s, s, s, d, p, q))
        z = zones(k, X, sx)
        for nm, t in z.items():
            tgt = S if nm == 'ring' else B
            d, p, q = dist(k, X, t, tgt)
            print('   %-10s to %-15s %.4f  driver %s / %s' % (nm, tgt.name, d, p, q))
        for nm in ('basket', 'band 37.5', 'magnet', 'connector'):
            row = []
            for g in grow:
                if nm == 'connector':
                    t = X.wbox(cx - 16.0 - g, cx + 16.0 + g, Y_REAR + 10.0 + g, Y_REAR - g, AZ - g, AZ + 18.25 + g)
                elif nm == 'magnet':
                    t = X.cyl((cx, Y_REAR + 10.0, AZ), (cx, Y_REAR - g, AZ), 16.0 + g)
                elif nm == 'basket':
                    t = X.cyl((cx, Y_BACK - 0.05, AZ), (cx, Y_REAR + 13.0, AZ), 20.0 + g, 18.75 + g)
                else:
                    t = X.cyl((cx, Y_REAR + 13.0, AZ), (cx, Y_REAR + 10.0, AZ), 18.75 + g)
                row.append('%.1f: %.3f' % (g, X.xv(t, Bc)))
            print('   %-10s grown all round, shares with the box: %s' % (nm, '; '.join(row)))
        st = k.needle_t(X, [Bc], (cx, Y_REAR, AZ), (cx, Y_REAR - 8.0, AZ), 0.02)
        print('   behind the rear end on the axis, the box solid at %s (mm behind the rear end)' % st)
        for dy in (0.9, 2.0):
            t = X.cyl((cx, Y_REAR + 10.0, AZ), (cx, Y_REAR - dy, AZ), 16.0)
            X.uni(t, X.wbox(cx - 16.0, cx + 16.0, Y_REAR + 10.0 - dy, Y_REAR - dy, AZ, AZ + 18.25))
            print('   magnet and connector %.1f deeper (depth %.1f): share %.3f with the box' % (dy, 25.0 + dy, X.xv(t, Bc)))
        if k.late():
            print('time'); return


def facelist(k, X, B, m, within):
    rows = []
    for f in B.faces:
        dd = X.mm.measureMinimumDistance(m, f).value * 10.0
        if dd > within:
            continue
        g = f.geometry; t = g.surfaceType
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
        ws = [k.W(v.geometry) for v in f.vertices]
        ext = [round(fn(w[i] for w in ws), 2) for i in range(3) for fn in (min, max)] if ws else None
        r = X.mm.measureMinimumDistance(m, f)
        rows.append((round(dd, 3), {0: 'plane', 1: 'cyl', 2: 'cone'}.get(t, str(t)), k.r2(k.wv(nv), 3), k.r2(k.W(r.positionTwo), 2), round(f.area * 100, 1), ext,
                     round(g.radius * 10, 3) if t == 1 else None))
    return sorted(rows)


def st_faces(k, X, sides=('L', 'R'), side_within=1.05, rear_within=2.05):
    """The box's faces nearer than aim 2 allows: within side_within of the driver behind y -4.0 (basket, band, magnet, connector),
    and within rear_within of its rear end (the rear face of magnet and connector, 0.01 thick)."""
    k.budget(72)
    for s in sides:
        sx = 1 if s == 'L' else -1; cx = sx * AX
        B = X.body('SPKBOX_' + s)
        m = X.cyl((cx, -4.0, AZ), (cx, Y_REAR + 13.0, AZ), 19.98, 18.75)
        X.uni(m, X.cyl((cx, Y_REAR + 13.0, AZ), (cx, Y_REAR + 10.0, AZ), 18.75))
        X.uni(m, X.cyl((cx, Y_REAR + 10.0, AZ), (cx, Y_REAR, AZ), 16.0))
        X.uni(m, X.wbox(cx - 16.0, cx + 16.0, Y_REAR + 10.0, Y_REAR, AZ, AZ + 18.25))
        print('SPKBOX_%s: faces within %.2f of the driver behind y -4.0 (distance, kind, normal, nearest point on the face, mm2, box, radius):' % (s, side_within))
        for r in facelist(k, X, B, m, side_within):
            print('   %s' % (r,))
        rr = X.cyl((cx, Y_REAR + 0.01, AZ), (cx, Y_REAR, AZ), 16.0)
        X.uni(rr, X.wbox(cx - 16.0, cx + 16.0, Y_REAR + 0.01, Y_REAR, AZ, AZ + 18.25))
        print('SPKBOX_%s: faces within %.2f of the rear end (magnet and connector):' % (s, rear_within))
        for r in facelist(k, X, B, rr, rear_within):
            print('   %s' % (r,))
        if k.late():
            print('time'); return


def _main(stage, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'room': st_room, 'faces': st_faces}[stage](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(stage, tag='', **kw):
    L['out']('m12_%s%s.txt' % (stage, ('_' + tag) if tag else ''), _main, stage, **kw)
# END
