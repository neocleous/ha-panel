# rev F rework R2h (2026-11-04), read-only: Pi insertion lift.
#   R2d/R2f: at 1.0 above its seat the Pi's underside (microSD socket at the -x end) hits the rear -x Pi boss
#   (x_rel -42.7…-36.7, y -57.6…-51.4) when the Pi is 20–30 behind its seat (5.6 mm³ at 25).
#   1. Lowest PI5_F vertex (world z) inside each Pi boss's x band (boss centre ± 3.0), and the boss tops (highest front-shell
#      vertex in a Ø6 box around each boss centre, z 2...12) -> lift needed = max(top - zmin) + 0.5, rounded up to 0.5.
#   2. Check: PI5_F + cooler + GPIO plugs cropped to z < 12 (one slow boolean), moved back u 1...70 at that lift, ∩ the front
#      shell cropped to x_rel -48...26, y -62...0, z 0...12 (1 mm steps).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
BOSSES = [(-39.65, -54.5), (-39.65, -5.5), (18.35, -54.5), (18.35, -5.5)]   # x_rel, y (Pi holes after the b2c shift)


def run(_context):
    X = Ctx(); out = {}
    B = adsk.fusion.BooleanTypes; tbm = X.tbm

    def mv(t, dx, dy, dz):
        m = adsk.core.Matrix3D.create(); m.translation = V3(dx / 10, (dy * C + dz * S) / 10, (-dy * S + dz * C) / 10)
        tbm.transform(t, m); return t
    try:
        t0 = time.time()
        pv = []
        for v in X.body('PI5_F').vertices:
            p = v.geometry; pv.append((p.x * 10 - XC, wy(p), wz(p)))
        fb = X.body('HOUSING_F_front')
        fv = []
        for v in fb.vertices:
            p = v.geometry; xr = p.x * 10 - XC
            if -46 < xr < 25:
                fv.append((xr, wy(p), wz(p)))
        res = {}
        for (bx, by) in BOSSES:
            zp = [z for (x, y, z) in pv if abs(x - bx) <= 3.0]
            zt = [z for (x, y, z) in fv if abs(x - bx) <= 3.0 and abs(y - by) <= 3.0 and 2.0 < z < 12.0]
            res['%g,%g' % (bx, by)] = {'pi_zmin_band': round(min(zp), 2) if zp else None, 'boss_top': round(max(zt), 2) if zt else None}
        out['bands'] = res
        need = max(r['boss_top'] - r['pi_zmin_band'] for r in res.values() if r['boss_top'] is not None and r['pi_zmin_band'] is not None)
        lift = math.ceil((need + 0.5) * 2) / 2.0
        out['need'] = round(need, 2); out['lift'] = lift; out['n_vertices'] = [len(pv), len(fv)]; out['s_vertices'] = round(time.time() - t0, 1)
        log('v5f_r2h_pi_lift', 'bands', out)
        pi = None
        for n in ('PI5_F', 'PI5_F_cooler', 'GPIO_plugA_env', 'GPIO_plugB_env'):
            pi = tbm.copy(X.body(n)) if pi is None else X.union(pi, tbm.copy(X.body(n)))
        tbm.booleanOperation(pi, X.wbox(XC - 60, XC + 60, -70, 10, -5, 12.0), B.IntersectionBooleanType)
        cp = tbm.copy(fb); tbm.booleanOperation(cp, X.wbox(XC - 48, XC + 26, -62, 0, 0, 12), B.IntersectionBooleanType)
        hits = []
        for u in [0] + list(range(1, 71)):
            t = mv(tbm.copy(pi), 0, -float(u), lift); tbm.booleanOperation(t, tbm.copy(cp), B.IntersectionBooleanType)
            v = round(t.volume * 1000, 2)
            if v > 0:
                hits.append([u, v])
        out['path_lift'] = hits or 'all 0 (u 0...70, 1 mm)'
        out['s_total'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_r2h_pi_lift', 'check', out)
    print(json.dumps(out))
