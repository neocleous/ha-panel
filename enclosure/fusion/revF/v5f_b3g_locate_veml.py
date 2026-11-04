# rev F block 3g (2026-11-04), read-only: locate B3f's VEML_env ∩ front (5.19 mm³) and check the top wall outside the
# designed cuts: (2.5 skin ∩ z 165…190, y −55.0…30) − front − (B3f's pocket/port tools grown 0.3) should be 0.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
YP = -26.5; ZI = 177.5; ZP = 178.3
SX0, SX1 = 7.5, 37.5
VX0, VX1, VY0, VY1 = 38.3, 53.7, -38.7, -23.3
LUX = (46.0, -31.0)


def run(_context):
    X = Ctx(); out = {}
    B = adsk.fusion.BooleanTypes; tbm = X.tbm

    def bbw(bb):
        mn, mx = bb.minPoint, bb.maxPoint
        cs = [P3(x, y, z) for x in (mn.x, mx.x) for y in (mn.y, mx.y) for z in (mn.z, mx.z)]
        return [round(min(c.x * 10 - XC for c in cs), 2), round(max(c.x * 10 - XC for c in cs), 2), round(min(wy(c) for c in cs), 2),
                round(max(wy(c) for c in cs), 2), round(min(wz(c) for c in cs), 2), round(max(wz(c) for c in cs), 2)]

    def lumps(t, n=8):
        return sorted([[round(t.lumps.item(i).volume * 1000, 3)] + bbw(t.lumps.item(i).boundingBox) for i in range(t.lumps.count)], key=lambda r: -r[0])[:n]
    try:
        fb = X.body('HOUSING_F_front')
        t = tbm.copy(X.body('VEML_env')); tbm.booleanOperation(t, tbm.copy(fb), B.IntersectionBooleanType)
        out['veml_env_x_front'] = {'mm3': round(t.volume * 1000, 3), 'lumps': lumps(t)}
        g = 0.3
        cut = None
        for s in (1, -1):
            xs = sorted((XC + s * (SX0 - 0.2 - g), XC + s * (SX1 + 0.2 + g)))
            p = X.wbox(xs[0], xs[1], YP + 3.2 + g, YP - 3.2 - g, ZI - 2.0, ZP + g)
            cut = p if cut is None else X.union(cut, p)
            cut = X.union(cut, X.wcyl_z(XC + s * 35.5, YP, 0.75 + g, ZI - 2.0, 181.0))
        cut = X.union(cut, X.wbox(XC + VX0 - g, XC + VX1 + g, VY0 - g, VY1 + g, ZI - 2.0, ZP + g))
        cut = X.union(cut, X.wcyl_z(XC + LUX[0], LUX[1], 1.0 + g, ZI - 2.0, 181.0))
        sr = tbm.copy(X.body('TOOL_outer_skin_2p5_F')); tbm.booleanOperation(sr, X.wbox(XC - 120, XC + 120, -55.0, 30, 165, 190), B.IntersectionBooleanType)
        tbm.booleanOperation(sr, tbm.copy(fb), B.DifferenceBooleanType)
        out['deficit_all_mm3'] = round(sr.volume * 1000, 2)
        tbm.booleanOperation(sr, cut, B.DifferenceBooleanType)
        out['deficit_outside_cuts'] = {'mm3': round(sr.volume * 1000, 3), 'lumps': lumps(sr)}
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b3g_locate_veml', 'locate', out)
    print(json.dumps(out))
