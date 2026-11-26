# Block 4: the slab (SLAB_frame) and the screen plate (HOUSING_F_plate) as they stand at version 71. READ-ONLY.
# Everything in the slab frame (x, d, Zd): x = world x, d = depth behind the glass's front, Zd = height along the screen.
#   stage 'slab'   the slab's planar faces: those square to d (level in its print, glass side down) and those square to Zd
#                  (the rims' faces), with their extents; the faces at the two x ends near d 0 (AA-C7)
#   stage 'plate'  the screen plate's faces square to Zd near its top and bottom edges; its round holes (r 1.5 to 2.5) with axis
#                  and ends; the planar faces round each screw hole on both sides
#   stage 'pair'   bounded distances: the slab's rims to the plate's edges, the slab's rebate to the glass (LCD_* bodies)
# Run: runpy.run_path(D + 'p42_slab_inspect.py')['main']('slab')  -> p42_<stage>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
k_ = None


def sface(k, f):
    g = f.geometry
    ws = [k.Sf(v.geometry) for v in f.vertices]
    ext = [round(fn(w[i] for w in ws), 3) for i in range(3) for fn in (min, max)] if ws else None
    p = k.Sf(f.pointOnFace)
    ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
    n = (nv.x, -nv.y, nv.z)     # slab frame: x, d (= -design y), Zd (= design z)
    return g.surfaceType, [round(w, 3) for w in p], [round(w, 3) for w in n], round(f.area * 100.0, 2), ext


def slab(k, X):
    b = X.body('SLAB_frame')
    bb = b.boundingBox
    a = k.Sf(bb.minPoint); e = k.Sf(bb.maxPoint)
    print('SLAB_frame volume %.3f faces %d; slab-frame box x %.3f..%.3f d %.3f..%.3f Zd %.3f..%.3f' % (
        b.volume * 1000, b.faces.count, min(a[0], e[0]), max(a[0], e[0]), min(a[1], e[1]), max(a[1], e[1]), min(a[2], e[2]), max(a[2], e[2])))
    lv, zf, other = [], [], []
    for f in b.faces:
        t, p, n, ar, ext = sface(k, f)
        if t == 0 and abs(abs(n[1]) - 1) < 1e-4:
            lv.append((p[1], 'toward d+' if n[1] > 0 else 'toward d-', ar, ext))
        elif t == 0 and abs(abs(n[2]) - 1) < 1e-4:
            zf.append((p[2], 'up' if n[2] > 0 else 'down', ar, ext))
        else:
            other.append((t, p, n, ar, ext))
    print('planar faces square to d (level in a glass-down print): d, which way the material is NOT, area, ext [x0,x1,d0,d1,z0,z1]')
    for r in sorted(lv):
        print('   d %8.3f %-10s %9.2f %s' % r)
    print('planar faces square to Zd:')
    for r in sorted(zf):
        print('   Zd %8.3f %-5s %9.2f %s' % r)
    print('other faces with d < 1.5 (the front roll and anything at the two x ends):')
    for r in sorted(other, key=lambda q: q[1][0]):
        if r[4] and r[4][2] < 1.5:
            print('   type %d at %s n %s area %.2f ext %s' % r)
    print('faces of any kind touching x beyond |x| > 99 and d < 1.0:')
    for f in b.faces:
        t, p, n, ar, ext = sface(k, f)
        if ext and (ext[1] > 99.0 or ext[0] < -99.0) and ext[2] < 1.0:
            print('   type %d at %s n %s area %.2f ext %s' % (t, p, n, ar, ext))


def plate(k, X):
    b = X.body('HOUSING_F_plate')
    bb = b.boundingBox
    a = k.Sf(bb.minPoint); e = k.Sf(bb.maxPoint)
    print('HOUSING_F_plate volume %.3f faces %d; slab-frame box x %.3f..%.3f d %.3f..%.3f Zd %.3f..%.3f' % (
        b.volume * 1000, b.faces.count, min(a[0], e[0]), max(a[0], e[0]), min(a[1], e[1]), max(a[1], e[1]), min(a[2], e[2]), max(a[2], e[2])))
    zf, lv = [], []
    for f in b.faces:
        t, p, n, ar, ext = sface(k, f)
        if t == 0 and abs(abs(n[2]) - 1) < 1e-4:
            zf.append((p[2], 'up' if n[2] > 0 else 'down', ar, ext))
        if t == 0 and abs(abs(n[1]) - 1) < 1e-4:
            lv.append((p[1], 'toward d+' if n[1] > 0 else 'toward d-', ar, ext))
    print('planar faces square to Zd:')
    for r in sorted(zf):
        print('   Zd %8.3f %-5s %9.2f %s' % r)
    print('planar faces square to d:')
    for r in sorted(lv):
        print('   d %8.3f %-10s %9.2f %s' % r)
    print('round holes r 1.5..3.0 (world):')
    for h in k.holes_of(b, 1.5, 3.0):
        A = k.Sf(k.Wp(*h['A'])); B = k.Sf(k.Wp(*h['B']))
        print('   %s r %.3f  A %s B %s  (slab frame A %s B %s) L %.2f cov %.2f axis %s' % (h['k'], h['r'], h['A'], h['B'], k.r2(A, 3), k.r2(B, 3), h['L'], h['cov'], h['a']))


def dist(X, a, b):
    r = X.mm.measureMinimumDistance(a, b)
    return round(r.value * 10.0, 4), [round(v, 3) for v in k_.Sf(r.positionOne)], [round(v, 3) for v in k_.Sf(r.positionTwo)]


def pair(k, X):
    S, P = X.body('SLAB_frame'), X.body('HOUSING_F_plate')
    print('slab to plate %s' % (dist(X, S, P),))
    for nm, box in (('upper rim', (-110, 110, -5, 30, 172.0, 185.0)), ('lower rim', (-110, 110, -5, 30, 40.0, 54.0))):
        t = X.dbox(*box); X.sec(t, X.tbm.copy(S)); tb = X.add(t, 'TMP_r', show=False)
        print('slab %s (Zd %.0f..%.0f) to plate %s' % (nm, box[4], box[5], dist(X, tb, P)))
        tb.deleteMe()
    lcd = [b for b in k.current(X) if b.name.startswith('LCD_')]
    print('LCD bodies: %s' % [b.name for b in lcd])
    for b in lcd:
        d = dist(X, S, b)
        if d[0] < 3.0:
            print('   slab to %-28s %s' % (b.name, d))


def _main(stage):
    global k_
    k = L['load'](); X = k.K(); k_ = k
    k.budget(70)
    print(L['stamp'](), 'before', X.state())
    {'slab': slab, 'plate': plate, 'pair': pair}[stage](k, X)
    for b in [b for b in X.root.bRepBodies if b.name.startswith('TMP_')]:
        b.deleteMe()
    print(L['stamp'](), 'after', X.state())


def main(stage):
    L['out']('p42_%s.txt' % stage, _main, stage)
