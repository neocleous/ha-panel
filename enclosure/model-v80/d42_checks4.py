# Block 4 (D467, PR48): the carrier's pilots and the ReSpeaker's two screws, read on the model as it stands. READ-ONLY.
# Slab frame: x, d = depth behind the glass's front, zd. The carrier prints plate down, bed at d 15.2, height d - 15.2.
#   fits   for each of the two pilots: its floor (bounded face) to the plate's bed face and to the screw's tip face; the pilot's
#          round face and its chamfer to the boss's round face; the board's bearing on the boss top; the screw's lump (volume,
#          from d to d); what the lump shares with every body of the unit; the bodies within 2.0 of it that it does not share
#          with; and the driver's way: a bar along the axis behind the head, 150 long, of radius 2.1 (a head of 4.2), 3 and 4 -
#          the bodies it shares with at each radius
#   tips   the figures computed for a board of 1.51 and of 1.6 by both readings of the head (d41_build4.tips)
# Run: runpy.run_path(D + 'd42_checks4.py')['main'](stage)  -> d42_<stage>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
L = runpy.run_path(D + 'v80_lib.py')
PLN = adsk.core.SurfaceTypes.PlaneSurfaceType
CYL = adsk.core.SurfaceTypes.CylinderSurfaceType
CON = adsk.core.SurfaceTypes.ConeSurfaceType
BED = 15.2


def fd(k, f):
    return k.Sf(f.pointOnFace)[1]


def level(k, f):
    if f.geometry.surfaceType != PLN:
        return False
    ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
    return abs(abs(nv.y) - 1) < 1e-4


def mind(X, a, b):
    return X.app.measureManager.measureMinimumDistance(a, b).value * 10.0


def onaxis(k, f, x, zd, tol=0.02):
    g = f.geometry
    o = k.Sf(g.origin)
    return abs(o[0] - x) < tol and abs(o[2] - zd) < tol


def st_fits(k, X, which=None, bars=True):
    car = X.body('RESP_CARRIER'); scr = X.body('SCREWS_M2x6_env')
    cur = k.current(X, leads=True)
    bedf = [f for f in car.faces if level(k, f) and abs(fd(k, f) - BED) < 1e-3]
    print('RESP_CARRIER %.3f mm3, lumps %d; SCREWS_M2x6_env %.3f mm3, lumps %d; bed faces %d (%.2f mm2)' % (
        car.volume * 1000, car.lumps.count, scr.volume * 1000, scr.lumps.count, len(bedf), sum(f.area for f in bedf) * 100))
    axes = sorted({(round(k.Sf(f.geometry.origin)[0], 2), round(k.Sf(f.geometry.origin)[2], 2)) for f in car.faces
                   if f.geometry.surfaceType == CYL and abs(f.geometry.radius * 10 - 0.8) < 0.01})
    for i, (x, zd) in enumerate(axes):
        if which is not None and i != which:
            continue
        print('pilot %d at slab x %.2f, zd %.2f' % (i, x, zd))
        pil = [f for f in car.faces if f.geometry.surfaceType == CYL and abs(f.geometry.radius * 10 - 0.8) < 0.01 and onaxis(k, f, x, zd)]
        boss = [f for f in car.faces if f.geometry.surfaceType == CYL and abs(f.geometry.radius * 10 - 3.0) < 0.01 and onaxis(k, f, x, zd)]
        cham = [f for f in car.faces if f.geometry.surfaceType == CON and onaxis(k, f, x, zd) and abs(fd(k, f) - 22.05) < 0.3]
        root = [f for f in car.faces if f.geometry.surfaceType == CON and onaxis(k, f, x, zd) and fd(k, f) < 19.0]
        flo = [f for f in car.faces if level(k, f) and abs(fd(k, f) - 16.6) < 0.3 and math.hypot(k.Sf(f.pointOnFace)[0] - x, k.Sf(f.pointOnFace)[2] - zd) < 0.85]
        top = [f for f in car.faces if level(k, f) and abs(fd(k, f) - 22.2) < 1e-3 and math.hypot(k.Sf(f.pointOnFace)[0] - x, k.Sf(f.pointOnFace)[2] - zd) < 3.1]
        print('   faces found: pilot %d, boss %d, chamfer %d, root cone %d, floor %d, boss top %d' % (len(pil), len(boss), len(cham), len(root), len(flo), len(top)))
        f0 = flo[0]
        print('   floor at d %.4f (bed %.4f), %.3f mm2; to the bed face %.4f (the plate under the floor)' % (fd(k, f0), fd(k, f0) - BED, f0.area * 100, min(mind(X, f0, b) for b in bedf)))
        print('   pilot\'s round face to the boss\'s round face %.4f; chamfer to the boss\'s round face %.4f; pilot to the root cone %.4f' % (
            min(mind(X, a, b) for a in pil for b in boss), min(mind(X, a, b) for a in cham for b in boss), min(mind(X, a, b) for a in pil for b in root)))
        print('   boss top (the board bears on it): %.3f mm2 at d %.4f; chamfer %.3f mm2' % (sum(f.area for f in top) * 100, fd(k, top[0]), sum(f.area for f in cham) * 100))
        # the screw's lump on this axis
        lump = None
        for lp in scr.lumps:
            t = X.tbm.copy(lp)
            cy = [f for f in t.faces if f.geometry.surfaceType == CYL and abs(f.geometry.radius * 10 - 1.0) < 0.01]
            if cy and onaxis(k, cy[0], x, zd, 0.05):
                lump = lp
        if lump is None:
            print('   NO SCREW on this axis'); continue
        ds = sorted(fd(k, f) for f in lump.faces if level(k, f))
        tipf = [f for f in lump.faces if level(k, f) and abs(fd(k, f) - ds[0]) < 1e-3]
        t = X.tbm.copy(lump)
        print('   screw: %.3f mm3; tip at d %.4f (bed %.4f), head top at d %.4f; tip face to the floor face %.4f; in the boss %.4f, below the chamfer %.4f' % (
            X.vol(t), ds[0], ds[0] - BED, ds[-1], mind(X, tipf[0], f0), 22.2 - ds[0], 21.9 - ds[0]))
        sh = []; nr = []
        bb = lump.boundingBox
        for ob in cur:
            if ob.name == 'SCREWS_M2x6_env':
                continue
            ob_bb = ob.boundingBox
            if (ob_bb.minPoint.x - 0.3 > bb.maxPoint.x or ob_bb.maxPoint.x + 0.3 < bb.minPoint.x or ob_bb.minPoint.y - 0.3 > bb.maxPoint.y or
                    ob_bb.maxPoint.y + 0.3 < bb.minPoint.y or ob_bb.minPoint.z - 0.3 > bb.maxPoint.z or ob_bb.maxPoint.z + 0.3 < bb.minPoint.z):
                continue
            v = X.xv(X.tbm.copy(lump), X.tbm.copy(ob))
            if v and v > 1e-6:
                sh.append('%s %.4f' % (ob.name, v))
            else:
                dd = mind(X, X.tbm.copy(lump), ob)
                if dd < 2.0:
                    nr.append('%s %.3f' % (ob.name, dd))
        print('   shares with: %s' % (', '.join(sh) or 'nothing'))
        print('   within 2.0 without sharing: %s' % (', '.join(nr) or 'nothing'))
        if not bars:
            continue
        big = X.tbm.createCylinderOrCone(k.Dp(x, ds[-1] + 0.05, zd), 0.4, k.Dp(x, ds[-1] + 150.0, zd), 0.4)
        cps = [(ob.name, X.tbm.copy(ob)) for ob in cur if ob.name != 'SCREWS_M2x6_env' and ob.boundingBox.intersects(big.boundingBox)]
        print('   bodies whose boxes the driver\'s way crosses: %d' % len(cps))
        for r in (2.1, 3.0, 4.0):
            hit = []
            for nm, cb in cps:
                c = X.tbm.createCylinderOrCone(k.Dp(x, ds[-1] + 0.05, zd), r / 10.0, k.Dp(x, ds[-1] + 150.0, zd), r / 10.0)
                X.sec(c, cb)
                if c.faces.count and X.vol(c) > 1e-4:
                    dsb = [k.Sf(vx.geometry)[1] for vx in c.vertices]
                    hit.append(('%s %.2f (d %.1f..%.1f)' % (nm, X.vol(c), min(dsb), max(dsb))) if dsb else '%s %.2f' % (nm, X.vol(c)))
            print('   driver\'s way, a bar %.1f across behind the head, 150 long: %s' % (2 * r, ', '.join(hit) or 'free'))


def st_tips(k, X):
    for r in runpy.run_path(D + 'd41_build4.py')['tips']():
        print(r)


def _main(stage, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'fits': st_fits, 'tips': st_tips}[stage](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(stage, tag='', **kw):
    L['out']('d42_%s%s.txt' % (stage, ('_' + tag) if tag else ''), _main, stage, **kw)
# END
