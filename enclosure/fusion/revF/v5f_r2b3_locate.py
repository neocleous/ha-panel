# rev F rework R2b-3 (2026-11-04), read-only: where the trial box shell touches the front shell (1.5 mm3 per side in R2b-2)
# and where it overlaps the speaker envelope beyond the two pegs. Bare shell (outer - inner) and the full feature list
# rebuilt as in R2b-2; world bounding boxes of every overlap lump.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
SX, SZ = 70.5, 28.0
XI, WT, YF0, YF1, YR, ZB, ZT = 46.0, 1.5, -5.7, -3.7, -52.5, 3.0, 76.0
PX = {1: (45.4, 46.9), -1: (45.3, 46.8)}


def run(_context):
    X = Ctx(); out = {}
    B = adsk.fusion.BooleanTypes; tbm = X.tbm

    def ycyl(x, z, r, y0, y1):
        return tbm.createCylinderOrCone(Dw(x, y0, z), r / 10, Dw(x, y1, z), r / 10)

    def bbw(bb):
        mn, mx = bb.minPoint, bb.maxPoint
        cs = [P3(x, y, z) for x in (mn.x, mx.x) for y in (mn.y, mx.y) for z in (mn.z, mx.z)]
        xs = [c.x * 10 - XC for c in cs]; ys = [wy(c) for c in cs]; zs = [wz(c) for c in cs]
        return [round(min(xs), 1), round(max(xs), 1), round(min(ys), 1), round(max(ys), 1), round(min(zs), 1), round(max(zs), 1)]

    def lumps_bb(t):
        if t.volume <= 0: return 0
        res = {'mm3': round(t.volume * 1000, 2), 'lumps': []}
        for i in range(t.lumps.count):
            lp = t.lumps.item(i)
            try:
                res['lumps'].append([round(lp.volume * 1000, 2)] + bbw(lp.boundingBox))
            except Exception:
                res['lumps'].append(bbw(lp.boundingBox))
        res['lumps'] = sorted(res['lumps'], key=lambda r: -r[0] if isinstance(r[0], float) else 0)[:6]
        return res
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
        for s in (1, -1):
            xr = lambda v: XC + s * v
            o = X.wbox(xr(XI), xr(130), YR, YF1, ZB, ZT); tbm.booleanOperation(o, tbm.copy(X.body('TOOL_cav_1p2_slide')), B.IntersectionBooleanType)
            t = tbm.copy(o); tbm.booleanOperation(t, tbm.copy(fcut), B.IntersectionBooleanType)
            k = '+x' if s > 0 else '-x'
            out[k + '_outer_vs_front'] = lumps_bb(t)
            i = X.wbox(xr(XI + WT), xr(130), YR + WT, YF0, ZB + WT, ZT - WT); tbm.booleanOperation(i, tbm.copy(X.body('TOOL_cav_2p7_slide')), B.IntersectionBooleanType)
            mod = tbm.copy(o); tbm.booleanOperation(mod, i, B.DifferenceBooleanType); X.union(mod, tbm.copy(X.body('SPK_L' if s > 0 else 'SPK_R')))
            for (dx, dy, dz) in ((0, -1.0, 0), (-s * 22.0, -31.0, 6.0 if s < 0 else 0.0), (-s * 22.0, -46.0, 6.0 if s < 0 else 0.0)):
                m = adsk.core.Matrix3D.create(); m.translation = V3(dx / 10, (dy * C + dz * S) / 10, (-dy * S + dz * C) / 10)
                t = tbm.copy(mod); tbm.transform(t, m); tbm.booleanOperation(t, tbm.copy(fcut), B.IntersectionBooleanType)
                out['%s_moved_%g_%g_%g' % (k, dx, dy, dz)] = lumps_bb(t)
            spk = X.body('SPK_L' if s > 0 else 'SPK_R')
            parts = {'tubes': None, 'pads_pegs': None}
            for z in (10.25, 45.75):
                tu = ycyl(xr(52.75), z, 4.0, YF0, YR)
                parts['tubes'] = tu if parts['tubes'] is None else X.union(parts['tubes'], tu)
                pp = X.union(ycyl(xr(88.25), z, 1.6, YF1, -0.2), ycyl(xr(88.25), z, 3.75, YF1 - 0.2, YF1 + 0.7))
                rp = ycyl(xr(52.75), z, 3.75, YF1 - 0.2, YF1 + 0.7); X.diff(rp, ycyl(xr(52.75), z, 1.7, YF1 - 1.0, YF1 + 1.5))
                X.union(pp, rp)
                parts['pads_pegs'] = pp if parts['pads_pegs'] is None else X.union(parts['pads_pegs'], pp)
            fw = X.wbox(xr(XI), xr(130), YF0, YF1, ZB, ZT); tbm.booleanOperation(fw, tbm.copy(o), B.IntersectionBooleanType)
            X.diff(fw, ycyl(xr(SX), SZ, 20.3, YF0 - 0.5, YF1 + 0.5)); parts['front_wall'] = fw
            for n, p in parts.items():
                t = tbm.copy(p); tbm.booleanOperation(t, tbm.copy(spk), B.IntersectionBooleanType)
                out[k + '_' + n + '_vs_spk'] = lumps_bb(t)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_r2b3_locate', 'locate', out)
    print(json.dumps(out))
