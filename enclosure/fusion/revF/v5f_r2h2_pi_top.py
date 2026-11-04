# rev F rework R2h-2 (2026-11-04), read-only: the rest of the Pi at the R2h lift (2.0): PI5_F + cooler + GPIO plugs cropped
# to z ≥ 11, moved back u 0...70 (1 mm) at lift 2.0, ∩ (front shell cropped to x_rel ±60, y -140...8, z 9...60 ∪ SPKBOX_L ∪ SPKBOX_R).
# R2h covered z < 12 against the Pi bosses and the floor.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
LIFT = 2.0


def run(_context):
    X = Ctx(); out = {}
    B = adsk.fusion.BooleanTypes; tbm = X.tbm

    def mv(t, dx, dy, dz):
        m = adsk.core.Matrix3D.create(); m.translation = V3(dx / 10, (dy * C + dz * S) / 10, (-dy * S + dz * C) / 10)
        tbm.transform(t, m); return t
    try:
        t0 = time.time()
        pi = None
        for n in ('PI5_F', 'PI5_F_cooler', 'GPIO_plugA_env', 'GPIO_plugB_env'):
            pi = tbm.copy(X.body(n)) if pi is None else X.union(pi, tbm.copy(X.body(n)))
        tbm.booleanOperation(pi, X.wbox(XC - 60, XC + 60, -70, 10, 11.0, 60), B.IntersectionBooleanType)
        ob = tbm.copy(X.body('HOUSING_F_front')); tbm.booleanOperation(ob, X.wbox(XC - 60, XC + 60, -140, 8, 9, 60), B.IntersectionBooleanType)
        ob = X.union(X.union(ob, tbm.copy(X.body('SPKBOX_L'))), tbm.copy(X.body('SPKBOX_R')))
        hits = []
        for u in range(0, 71):
            t = mv(tbm.copy(pi), 0, -float(u), LIFT); tbm.booleanOperation(t, tbm.copy(ob), B.IntersectionBooleanType)
            v = round(t.volume * 1000, 2)
            if v > 0:
                hits.append([u, v])
        out['pi_top_cm3'] = round(pi.volume, 3)
        out['path_lift2'] = hits or 'all 0 (u 0...70, 1 mm)'
        out['s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_r2h2_pi_top', 'check', out)
    print(json.dumps(out))
