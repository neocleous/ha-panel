# rev F block 4j (2026-11-04): V11 – Pi USB-C power plug options modelled at the Pi's rear edge (hidden envelopes).
#   Pi USB-C (PI5_F, b2q): x_rel −36.3…−27.6 (centre −31.95), z 9.4–12.6 (centre 11.0), face y −59.3; the inner back wall is
#   20.0–21.6 behind it. No overmould dimensions exist (architect log 11-03 K11): allowances below, design pass 2 measures.
#   c  straight 0.2 m: rigid overmould 12.4 × 6.6 × 20 + strain relief Ø6 × 15 (K11 allowance 30–40 incl. relief).
#   a  CableCreation 90° adapter (male → female) + the straight 0.2 m: adapter body 12.5 × 7.5 × 12 behind the face; the
#      straight plug (12.4 × 6.6 × 20 rigid + Ø6 × 12 relief) out of the female port: a_up (port on top, y −67.3),
#      a_px / a_mx (port on the +x / −x side, y −65.3; both plug orientations: wide axis along y or along z).
#   b  5 A elbow cable ≥ 0.5 m: elbow body 12.5 × 7.5 × 14 behind the face, cable Ø5: b_up (exit on top at y −70.8, 30 up),
#      b_px / b_mx (exit on the side at y −66.3, 20 out).
#   Checks per option against the door, the front shell, the main board and its envelopes, the bracket, the 5807 cradle and
#   envelope, the Pi (rear 15 mm), and the K5 lanes.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
XU, ZU, YF = -31.95, 11.0, -59.3


def run(_context):
    X = Ctx(); out = {}
    B = adsk.fusion.BooleanTypes; tbm = X.tbm

    def ycyl(x, z, r, y0, y1):
        return tbm.createCylinderOrCone(Dw(XC + x, y0, z), r / 10, Dw(XC + x, y1, z), r / 10)

    def xcyl(y, z, r, x0, x1):
        return tbm.createCylinderOrCone(Dw(XC + x0, y, z), r / 10, Dw(XC + x1, y, z), r / 10)

    def box(x0, x1, y0, y1, z0, z1):
        return X.wbox(XC + x0, XC + x1, y0, y1, z0, z1)

    def vol_x(a_, b_):
        q = tbm.copy(a_); tbm.booleanOperation(q, tbm.copy(b_), B.IntersectionBooleanType); return round(q.volume * 1000, 2)
    try:
        if X.body('V11c_straight') is not None:
            raise RuntimeError('V11 envelopes exist already')
        ad = lambda depth: box(XU - 6.25, XU + 6.25, YF - depth, YF, ZU - 3.75, ZU + 3.75)
        opts = {}
        opts['V11c_straight'] = X.union(box(XU - 6.2, XU + 6.2, YF - 20.0, YF, ZU - 3.3, ZU + 3.3), ycyl(XU, ZU, 3.0, YF - 20.0, YF - 35.0))
        t = X.union(ad(12.0), box(XU - 6.2, XU + 6.2, -70.6, -64.0, ZU + 3.75, ZU + 23.75))
        opts['V11a_up'] = X.union(t, tbm.createCylinderOrCone(Dw(XC + XU, -67.3, ZU + 23.75), 0.3, Dw(XC + XU, -67.3, ZU + 35.75), 0.3))
        for s, nm in ((1, 'V11a_px'), (-1, 'V11a_mx')):
            x0 = XU + s * 6.25; x1 = x0 + s * 20.0
            t = X.union(ad(12.0), box(x0, x1, -71.5, -59.1, ZU - 3.3, ZU + 3.3))
            t = X.union(t, box(x0, x1, -68.6, -62.0, ZU - 6.2, ZU + 6.2))
            opts[nm] = X.union(t, xcyl(-65.3, ZU, 3.0, x1, x1 + s * 12.0))
        opts['V11b_up'] = X.union(ad(14.0), tbm.createCylinderOrCone(Dw(XC + XU, -70.8, ZU + 3.75), 0.25, Dw(XC + XU, -70.8, ZU + 33.75), 0.25))
        for s, nm in ((1, 'V11b_px'), (-1, 'V11b_mx')):
            x0 = XU + s * 6.25
            opts[nm] = X.union(ad(14.0), xcyl(-66.3, ZU, 2.5, x0, x0 + s * 20.0))
        bodies = {}
        for nm, t in opts.items():
            b = X.add(t, nm); b.isLightBulbOn = False; bodies[nm] = b
        pi = tbm.copy(X.body('PI5_F')); tbm.booleanOperation(pi, box(-60, 60, -75, -45, 0, 40), B.IntersectionBooleanType)
        obst = {n: X.body(n) for n in ('HOUSING_F_door', 'HOUSING_F_front', 'MAIN_pcb', 'MAIN_back_env', 'MAIN_front_env', 'MAIN_BRACKET',
                                        'CRADLE_5807', 'PD_5807_env', 'KO_K5_LL', 'KO_K5_LR')}
        res = {}
        for nm, b in bodies.items():
            r = {k: vol_x(b, o) for k, o in obst.items()}
            r['PI5_F_rear'] = vol_x(b, pi)
            res[nm] = {k: v for k, v in r.items() if v > 0} or 'all 0'
        out['option_hits_mm3'] = res
        # free length straight behind the receptacle (ray along −y from the face centre)
        hp = adsk.core.ObjectCollection.create()
        fs = X.comp.findBRepUsingRay(Dw(XC + XU, YF - 0.5, ZU), V3(0, -C, S), adsk.fusion.BRepEntityTypes.BRepFaceEntityType, -1.0, False, hp)
        hits = []
        for i in range(fs.count):
            n = fs.item(i).body.name
            if n.startswith(('HOUSING_F', 'CRADLE', 'MAIN_', 'PD_')):
                p = hp.item(i); hits.append([n, round(abs(wy(p) - YF), 2)])
        out['ray_back_from_face'] = sorted(hits, key=lambda h: h[1])[:4]
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b4j_v11_options', 'checks', out)
    print(json.dumps(out))
