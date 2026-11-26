# Block 2: the two speaker leads' ends inside the boxes, to the driver's connector as turned (up, toward the box's roof).
#   look     READ-ONLY: each lead's lumps, round faces and where it ends inside its box
#   build    builds the new leads as temporary bodies k.c['ds_lead_L'], k.c['ds_lead_R'] (nothing put): the lead as it is (it
#            ends at the wire hole's mouth; its run inside the box was never drawn) and a new run from there through the hole to
#            the connector's top, as round bars of the lead's own radius through the waypoints WAY; prints the run's length
# Run: runpy.run_path(D + 'd26_leads.py')['main'](stage)  -> d26_<stage>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
L = runpy.run_path(D + 'v80_lib.py')
CYL = adsk.core.SurfaceTypes.CylinderSurfaceType
# waypoints of the new run for the left box (x mirrored for the right): from the lead's end at the wire hole's mouth
# (62, -54, 30: d26 look), through the hole (4.0 across, y -52.0 to -50.5), forward and up to the top face of the connector's
# envelope (z 46.25), where its axis lies one radius above the face
WAY = [(62.0, -54.0, 30.0), (62.0, -46.0, 30.0), (64.0, -36.0, 40.0), (66.5, -30.5, 47.5), (68.0, -26.0, 47.85)]


def st_look(k, X):
    for s in ('L', 'R'):
        b = X.body('LEAD_SPK_' + s)
        print('LEAD_SPK_%s: box %s, vol %.3f, lumps %d, faces %d' % (s, k.wbb(X, b), b.volume * 1000, b.lumps.count, b.faces.count))
        for f in b.faces:
            g = f.geometry
            if g.surfaceType == CYL:
                ws = [k.W(v.geometry) for v in f.vertices]
                e = [round(fn(w[i] for w in ws), 2) for i in range(3) for fn in (min, max)] if ws else None
                print('   round face r %.3f axis %s, extents %s, %.1f mm2' % (g.radius * 10, k.r2(k.unit(k.wv(g.axis)), 3), e, f.area * 100))
            elif f.area * 100 < 12:
                ws = [k.W(v.geometry) for v in f.vertices]
                e = [round(fn(w[i] for w in ws), 2) for i in range(3) for fn in (min, max)] if ws else None
                print('   small face %.2f mm2 at %s, extents %s' % (f.area * 100, k.r2(k.W(f.pointOnFace)), e))
        sx = 1 if s == 'L' else -1
        a, bb = sorted((sx * 40.0, sx * 100.0))
        t = L['crop'](X, 'LEAD_SPK_' + s, (a, bb, -53.0, -20.0, 0.0, 90.0))
        print('   inside y -53..-20: %.3f mm3, lumps %s' % (X.vol(t), X.lumps(t)))
        for y in (-52.0, -50.5, -49.5, -45.0, -40.0, -35.0, -31.0):
            c = L['crop'](X, 'LEAD_SPK_' + s, (a, bb, y - 0.05, y + 0.05, 0.0, 90.0))
            print('   slice at y %.1f: %s' % (y, X.lumps(c)))


def build(k, X, sx):
    s = 'L' if sx > 0 else 'R'
    b = X.body('LEAD_SPK_' + s)
    r = 1.6                                                  # the lead's own radius (d26 look: every round face 1.600)
    t = X.cp(b)
    pts = [(sx * p[0], p[1], p[2]) for p in WAY]
    ln = 0.0; inside = 0.0
    for p, q in zip(pts[:-1], pts[1:]):
        X.uni(t, X.cyl(p, q, r)); X.uni(t, X.sph(q, r))
        d = math.dist(p, q); ln += d
        if p[1] >= -52.0:
            inside += d
        elif q[1] > -52.0:
            inside += d * (q[1] + 52.0) / (q[1] - p[1])
    print('LEAD_SPK_%s: new run from the lead\'s end at the wire hole %s to the connector\'s top %s: %.1f along its axis, %.1f of it in front of the box\'s rear face (y -52.0)' % (
        s, pts[0], pts[-1], ln, inside))
    print('   new body %.3f mm3 in %d lumps (was %.3f)' % (X.vol(t), t.lumps.count, b.volume * 1000))
    k.c['ds_lead_' + s] = t
    for key in ('ds_box_' + s, 'ds_spk_' + s, 'ds_foam_' + s):
        if k.c.get(key) is not None:
            print('   shares with %s: %.4f' % (key, X.xv(t, k.c[key])))
    g = X.cp(b)
    for p, q in zip(pts[:-1], pts[1:]):
        X.uni(g, X.cyl(p, q, r + 0.5)); X.uni(g, X.sph(q, r + 0.5))
    for key in ('ds_box_' + s, 'ds_spk_' + s):
        if k.c.get(key) is not None:
            print('   the new run 0.5 thicker shares with %s: %.4f' % (key, X.xv(g, k.c[key])))
    return ln


def st_build(k, X):
    for sx in (1, -1):
        build(k, X, sx)


def _main(stage):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'look': st_look, 'build': st_build}[stage](k, X)
    print(L['stamp'](), 'after', X.state())


def main(stage):
    L['out']('d26_%s.txt' % stage, _main, stage)
# END
