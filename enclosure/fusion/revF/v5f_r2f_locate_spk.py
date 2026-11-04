# rev F rework R2f (2026-11-04), read-only: locate what R2d left open.
#   A. SPKBOX_L/R ∩ SPK_L/R lumps with world bounding boxes (expected: the two pegs, 2 x 22.5 mm3, and the +x plug pocket).
#   B. The R2d box-path contact at u 55 (0.5 mm3 vs the front shell, both boxes): lumps with world bounding boxes.
#   C. The insertion path at 1 mm steps vs the front shell (lower h 1...6, side t 1...37 at 1.0 back, in u 1...76 at s 37):
#      the R2d 5 mm steps can step over a thin feature. Front shell cropped to the module's half (x_rel 0...±115) for speed.
#   D. The R2d Pi-path contact (3.7 / 3.0 mm3 vs the front shell at 20 / 30 back, 1.0 above the seat): PI5_F + cooler + GPIO
#      plugs moved 25 back, 1.0 up, ∩ the front shell cropped to x_rel ±52, y -95...5, z 0...40: lumps (one slow boolean).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback


def run(_context):
    X = Ctx(); out = {}
    B = adsk.fusion.BooleanTypes; tbm = X.tbm

    def bbw(bb):
        mn, mx = bb.minPoint, bb.maxPoint
        cs = [P3(x, y, z) for x in (mn.x, mx.x) for y in (mn.y, mx.y) for z in (mn.z, mx.z)]
        xs = [c.x * 10 - XC for c in cs]; ys = [wy(c) for c in cs]; zs = [wz(c) for c in cs]
        return [round(min(xs), 1), round(max(xs), 1), round(min(ys), 1), round(max(ys), 1), round(min(zs), 1), round(max(zs), 1)]

    def lumps(t):
        ls = [t.lumps.item(i) for i in range(t.lumps.count)]
        return sorted([[round(lp.volume * 1000, 2)] + bbw(lp.boundingBox) for lp in ls], key=lambda r: -r[0])

    def mv(t, dx, dy, dz):
        m = adsk.core.Matrix3D.create(); m.translation = V3(dx / 10, (dy * C + dz * S) / 10, (-dy * S + dz * C) / 10)
        tbm.transform(t, m); return t
    try:
        fb = X.body('HOUSING_F_front')
        for bx, sp in (('SPKBOX_L', 'SPK_L'), ('SPKBOX_R', 'SPK_R')):
            t = tbm.copy(X.body(bx)); tbm.booleanOperation(t, tbm.copy(X.body(sp)), B.IntersectionBooleanType)
            out[bx] = {'box_spk_mm3': round(t.volume * 1000, 2), 'box_spk_lumps': lumps(t)}
        log('v5f_r2f_locate_spk', 'box vs spk', dict(out))
        mods = {}
        for s, bx, sp in ((1, 'SPKBOX_L', 'SPK_L'), (-1, 'SPKBOX_R', 'SPK_R')):
            mod = X.union(tbm.copy(X.body(bx)), tbm.copy(X.body(sp)))
            xs = sorted((XC, XC + s * 115.0))
            crop = tbm.copy(fb); tbm.booleanOperation(crop, X.wbox(xs[0], xs[1], -140, 5, -5, 95), B.IntersectionBooleanType)
            mods[s] = (bx, mod, crop)
            t = mv(tbm.copy(mod), -s * 37.0, -56.0, 6.0); tbm.booleanOperation(t, tbm.copy(crop), B.IntersectionBooleanType)
            out[bx]['u55_mm3'] = round(t.volume * 1000, 2); out[bx]['u55_lumps'] = lumps(t)
        log('v5f_r2f_locate_spk', 'u55', {k: {kk: vv for kk, vv in v.items() if kk.startswith('u55')} for k, v in out.items()})
        sw = {}
        for s in (1, -1):
            bx, mod, crop = mods[s]
            steps = [('lower', 0, -1.0, float(h)) for h in range(1, 7)] + [('side', -s * float(t), -1.0, 6.0) for t in range(1, 38)] + \
                    [('in', -s * 37.0, -1.0 - u, 6.0) for u in range(1, 77)]
            hits = []
            for (k, dx, dy, dz) in steps:
                t = mv(tbm.copy(mod), dx, dy, dz); tbm.booleanOperation(t, tbm.copy(crop), B.IntersectionBooleanType)
                v = round(t.volume * 1000, 2)
                if v > 0:
                    hits.append([k, dx, dy, dz, v])
            sw[bx] = hits or 'all 0 (%d steps)' % len(steps)
            log('v5f_r2f_locate_spk', 'sweep ' + bx, sw[bx])
        out['sweep'] = sw
        pi = None
        for n in ('PI5_F', 'PI5_F_cooler', 'GPIO_plugA_env', 'GPIO_plugB_env'):
            pi = tbm.copy(X.body(n)) if pi is None else X.union(pi, tbm.copy(X.body(n)))
        cp = tbm.copy(fb); tbm.booleanOperation(cp, X.wbox(XC - 52, XC + 52, -95, 5, 0, 40), B.IntersectionBooleanType)
        t = mv(pi, 0, -25.0, 1.0); tbm.booleanOperation(t, cp, B.IntersectionBooleanType)
        out['pi_u25_lift1'] = {'mm3': round(t.volume * 1000, 2), 'lumps': lumps(t)}
        log('v5f_r2f_locate_spk', 'pi u25', out['pi_u25_lift1'])
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_r2f_locate_spk', 'locate', out)
    print(json.dumps(out))
