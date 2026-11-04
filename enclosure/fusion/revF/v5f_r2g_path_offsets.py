# rev F rework R2g (2026-11-04), read-only: the box insertion path at entry offset s 40 (was 37), 1 mm steps.
#   R2f: at s 37 / lift 6 the box's top-outboard front corner (x_rel ±54.9…56.5, z 77.7…82.2) touches the rear end of the
#   front shell's lip (y −61.5…−64.4) when the box front is ≈ 56 behind its final pose (0.54 mm³). A larger s moves that
#   corner inboard, where the opening is higher.
#   Only the part that differs from R2f is swept: sideways t 38...40 (lower and t 1...37 are the same path, R2f) and back out
#   along -y at s 40 (u 1...76). Module = box ∪ speaker envelope; obstacles = front shell (cropped to the module's half)
#   ∪ LCD + slab.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
CASES = [(40.0, 6.0)]


def run(_context):
    X = Ctx(); out = {}
    B = adsk.fusion.BooleanTypes; tbm = X.tbm

    def mv(t, dx, dy, dz):
        m = adsk.core.Matrix3D.create(); m.translation = V3(dx / 10, (dy * C + dz * S) / 10, (-dy * S + dz * C) / 10)
        tbm.transform(t, m); return t
    try:
        fb = X.body('HOUSING_F_front')
        names = [b.name for b in X.comp.bRepBodies]
        lcd = None
        for n in [n for n in names if n.startswith('LCD_')] + ['SLAB_frame']:
            lcd = tbm.copy(X.body(n)) if lcd is None else X.union(lcd, tbm.copy(X.body(n)))
        for s, bx, sp in ((1, 'SPKBOX_L', 'SPK_L'), (-1, 'SPKBOX_R', 'SPK_R')):
            mod = X.union(tbm.copy(X.body(bx)), tbm.copy(X.body(sp)))
            xs = sorted((XC, XC + s * 115.0))
            crop = tbm.copy(fb); tbm.booleanOperation(crop, X.wbox(xs[0], xs[1], -140, 5, -5, 95), B.IntersectionBooleanType)
            obst = X.union(crop, tbm.copy(lcd))
            for (se, lift) in CASES:
                steps = [('side', -s * float(t), -1.0, lift) for t in range(38, int(se) + 1)] + \
                        [('in', -s * se, -1.0 - u, lift) for u in range(1, 77)]
                hits = []
                for (k, dx, dy, dz) in steps:
                    t = mv(tbm.copy(mod), dx, dy, dz); tbm.booleanOperation(t, tbm.copy(obst), B.IntersectionBooleanType)
                    v = round(t.volume * 1000, 2)
                    if v > 0:
                        hits.append([k, dx, dy, dz, v])
                key = '%s s%g lift%g' % (bx, se, lift)
                out[key] = hits or 'all 0 (%d steps)' % len(steps)
                log('v5f_r2g_path_offsets', key, out[key])
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_r2g_path_offsets', 'paths', out)
    print(json.dumps(out))
