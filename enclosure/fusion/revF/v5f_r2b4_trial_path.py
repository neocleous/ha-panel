# rev F rework R2b-4 (2026-11-04), read-only: trial boxes with the R2b-3 fixes and the insertion path.
#   Fixes: rear outer face y -52.0 (was -52.5: the z-25 / z-60 magnet pads reach y -53.2, 1.0 slide-back must clear them);
#   3.5 x 3.5 step along the bottom-outboard edge (outer: z < 6.5 within 4.7 of INNER_E removed; air: z < 8.0 within 6.2)
#   so the R3.5 floor cove (and its D1 growth) stays clear.
#   Path (both boxes, the other box may already be in): lift 6 (bottom z 9.0 > Pi boss tops 8.1), in along -y at an inboard
#   offset s, sideways out to the final x at 1.0 behind, lower 6, forward 1.0 onto the gasket. Entry offsets s 28...37 tried.
#   Module = box outer envelope ∪ speaker envelope ∪ box stop pads; obstacles = front shell after the planned wall cut,
#   and the LCD + slab (fitted before the boxes).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
SX, SZ = 70.5, 28.0
XI, WT, YF0, YF1, YR, ZB, ZT = 46.0, 1.5, -5.7, -3.7, -52.0, 3.0, 76.0
ZSO, ZSI = 6.5, 8.0
BACK, LIFT = 1.0, 6.0
PX = {1: (45.4, 46.9), -1: (45.3, 46.8)}


def run(_context):
    X = Ctx(); out = {}
    B = adsk.fusion.BooleanTypes; tbm = X.tbm

    def mv(t, dx, dy, dz):
        m = adsk.core.Matrix3D.create(); m.translation = V3(dx / 10, (dy * C + dz * S) / 10, (-dy * S + dz * C) / 10)
        tbm.transform(t, m); return t

    def ycyl(x, z, r, y0, y1):
        return tbm.createCylinderOrCone(Dw(x, y0, z), r / 10, Dw(x, y1, z), r / 10)

    def isect(a, b):
        t = tbm.copy(a); tbm.booleanOperation(t, tbm.copy(b), B.IntersectionBooleanType); return t

    def vol(t): return round(t.volume * 1000, 1)

    def cav(tag): return tbm.copy(X.body('TOOL_cav_%s_slide' % tag))
    try:
        ie = X.body('INNER_E'); fb = X.body('HOUSING_F_front')
        cut = None
        for s in (1, -1):
            a, b2 = PX[s]
            xs = sorted((XC + s * a, XC + s * b2)); xo = sorted((XC + s * a, XC + s * 130))
            for p in (X.wbox(xs[0], xs[1], -53.1, 1.2, 3.7, 76.0), X.wbox(xo[0], xo[1], -53.1, -51.6, 3.7, 76.0),
                      X.wbox(xo[0], xo[1], -53.1, 1.2, 74.0, 76.0)):
                cut = p if cut is None else X.union(cut, p)
        tbm.booleanOperation(cut, tbm.copy(ie), B.IntersectionBooleanType)
        fcut = tbm.copy(fb); tbm.booleanOperation(fcut, tbm.copy(cut), B.DifferenceBooleanType)
        names = [b.name for b in X.comp.bRepBodies]
        lcd = None
        for n in [n for n in names if n.startswith('LCD_')] + ['SLAB_frame']:
            b = X.body(n)
            if b is not None:
                lcd = tbm.copy(b) if lcd is None else X.union(lcd, tbm.copy(b))
        for s in (1, -1):
            k = '+x' if s > 0 else '-x'
            xr = lambda v: XC + s * v
            o = X.wbox(xr(XI), xr(130), YR, YF1, ZB, ZT); tbm.booleanOperation(o, cav('1p2'), B.IntersectionBooleanType)
            st = X.wbox(xr(XI), xr(130), YR - 1, YF1 + 1, ZB - 1, ZSO); X.diff(st, cav('4p7')); X.diff(o, st)
            i = X.wbox(xr(XI + WT), xr(130), YR + WT, YF0, ZB + WT, ZT - WT); tbm.booleanOperation(i, cav('2p7'), B.IntersectionBooleanType)
            st = X.wbox(xr(XI), xr(130), YR - 1, YF1 + 1, ZB - 1, ZSI); X.diff(st, cav('6p2')); X.diff(i, st)
            sh = tbm.copy(o); tbm.booleanOperation(sh, tbm.copy(i), B.DifferenceBooleanType)
            r = {'shell_cm3': round(sh.volume, 3), 'shell_lumps': sh.lumps.count, 'air_inner_cm3': round(i.volume, 2)}
            spk = X.body('SPK_L' if s > 0 else 'SPK_R')
            pads = None
            for z in (10.25, 45.75):
                for xx in (52.75, 88.25):
                    p = ycyl(xr(xx), z, 3.75, YF1 - 0.2, YF1 + 0.7)
                    pads = p if pads is None else X.union(pads, p)
            mod = X.union(X.union(tbm.copy(o), tbm.copy(spk)), pads)
            r['final_vs_front'] = vol(isect(mod, fcut))
            fw = [('fwd', 0, -0.5, 0), ('fwd', 0, -BACK, 0)] + [('lower', 0, -BACK, h) for h in (2.0, 4.0, LIFT)]
            r['fwd_lower'] = [[kk, dz, vol(isect(mv(tbm.copy(mod), dx, dy, dz), fcut))] for (kk, dx, dy, dz) in fw]
            ent = {}
            best = None
            for se in (28.0, 31.0, 34.0, 37.0):
                hits = []
                for u in (10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0):
                    t = mv(tbm.copy(mod), -s * se, -BACK - u, LIFT)
                    hits.append([u, vol(isect(t, fcut)), vol(isect(t, lcd))])
                ent[str(se)] = hits
                if best is None and all(h[1] == 0 and h[2] == 0 for h in hits):
                    best = se
            r['entry'] = ent; r['best_s'] = best
            if best is not None:
                r['side'] = [[t, vol(isect(mv(tbm.copy(mod), -s * t, -BACK, LIFT), fcut)), vol(isect(mv(tbm.copy(mod), -s * t, -BACK, LIFT), lcd))]
                             for t in (2.0, 6.0, 12.0, 20.0, best)]
            out[k] = r
            log('v5f_r2b4_trial_path', k, r)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_r2b4_trial_path', 'path', out)
    print(json.dumps(out))
