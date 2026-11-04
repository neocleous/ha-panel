# rev F block 4i (2026-11-04): +x speaker box – the sealed USB-A pocket becomes a slot to the box's rear face.
#   Daniel 2026-11-04 21:58: side-exit right-angle USB-A plug on the ReSpeaker cable, plugged into the Pi's rear-stack lower
#   port before the Pi goes in. The plug rides in with the Pi (in from behind at lift 2.0, then lowered 2.0), so the box
#   needs a slot along the plug's whole travel, open toward the Pi (x_rel 44) and through the rear face (y −52):
#   V1 (plug) x_rel 44.0…55.65, y −36.95…−20.95; V2 (cable run) x_rel 44.0…57.15, y −53.0…−36.0; both z 9.7…20.7
#   (plug allowance z 10.2…18.2 + 2.0 lift + 0.5). Walls 1.5 to the chamber: W1 x 46.0…57.15, y −37.0…−19.45; W2 x 46.0…58.65,
#   y −52.0…−35.5; z 8.2…22.2. SPKBOX_L before the change kept hidden as SPKBOX_L_r2.
#   Envelopes (hidden): USBA_plug_env = overmould allowance x 45.15…55.15, y −35.0…−22.9, z 10.2…18.2 + strain relief Ø6
#   y −35…−45 at (x 50.0, z 14.2); USBA_cable_env Ø4 y −45…−53 then the exit.
#   Checks: chamber air lost; Pi path (lift 2.0, u 0…70, 1 mm) with the plug vs the new box; final pose plug/cable vs box.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
EXPECT = {'SPKBOX_L': 25.321, 'HOUSING_F_front': 243.65}
Z0, Z1 = 9.7, 20.7


def run(_context):
    X = Ctx(); out = {}
    B = adsk.fusion.BooleanTypes; tbm = X.tbm

    def vol_x(a_, b_):
        q = tbm.copy(a_); tbm.booleanOperation(q, tbm.copy(b_), B.IntersectionBooleanType); return round(q.volume * 1000, 2)

    def mv(t, dx, dy, dz):
        m = adsk.core.Matrix3D.create(); m.translation = V3(dx / 10, (dy * C + dz * S) / 10, (-dy * S + dz * C) / 10)
        tbm.transform(t, m); return t

    def ycyl(x, z, r, y0, y1):
        return tbm.createCylinderOrCone(Dw(x, y0, z), r / 10, Dw(x, y1, z), r / 10)
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.003:
                raise RuntimeError('guard: %s volume %s, expected %s' % (k, None if b is None else round(b.volume, 3), v))
        if X.body('SPKBOX_L_r2') is not None:
            raise RuntimeError('SPKBOX_L_r2 exists already')
        bx = X.body('SPKBOX_L'); v0 = bx.volume
        keep = X.add(tbm.copy(bx), 'SPKBOX_L_r2'); keep.isLightBulbOn = False
        W = X.union(X.wbox(XC + 46.0, XC + 57.15, -37.0, -19.45, Z0 - 1.5, Z1 + 1.5), X.wbox(XC + 46.0, XC + 58.65, -52.0, -35.5, Z0 - 1.5, Z1 + 1.5))
        V = X.union(X.wbox(XC + 44.0, XC + 55.65, -36.95, -20.95, Z0, Z1), X.wbox(XC + 44.0, XC + 57.15, -53.0, -36.0, Z0, Z1))
        Vold = X.wbox(XC + 46.0, XC + 55.15, -36.95, -20.95, 9.95, 17.95)
        out['air_lost_mm3'] = round(tbm.copy(W).volume * 1000 - vol_x(W, bx) - vol_x(W, Vold), 1)
        Wj = tbm.copy(W)
        tbm.booleanOperation(Wj, X.wbox(XC + 46.0, XC + 120, -52.0, 5, 0, 80), B.IntersectionBooleanType)
        X.combine(bx, [X.add(Wj, 'B4I_walls_tmp')])
        bx = X.body('SPKBOX_L'); v1 = bx.volume
        X.combine(bx, [X.add(V, 'B4I_slot_tmp')], op=CUT)
        bx = X.body('SPKBOX_L')
        out['box_cm3'] = [round(v0, 3), round(v1, 3), round(bx.volume, 3)]; out['box_lumps'] = bx.lumps.count
        plug = X.wbox(XC + 45.15, XC + 55.15, -35.0, -22.9, 10.2, 18.2)
        plug = X.union(plug, ycyl(XC + 50.0, 14.2, 3.0, -35.0, -45.0))
        pe = X.add(plug, 'USBA_plug_env'); pe.isLightBulbOn = False
        ce = X.add(ycyl(XC + 52.0, 14.2, 2.0, -45.0, -53.5), 'USBA_cable_env'); ce.isLightBulbOn = False
        P = lambda x, y, z: X.inside(bx, XC + x, y, z)
        out['probes'] = {'slot_open_front': not P(50.0, -28.0, 15.0), 'slot_open_rear_face': not P(52.0, -51.5, 15.0),
                         'slot_open_lifted': not P(54.0, -40.0, 20.2), 'outboard_wall': P(57.9, -45.0, 15.0) and P(56.4, -28.0, 15.0),
                         'ceiling_wall': P(52.0, -45.0, 21.5), 'floor_wall': P(52.0, -45.0, 8.9), 'front_end_wall': P(50.0, -20.2, 15.0),
                         'chamber_air_outboard': not P(62.0, -45.0, 15.0), 'chamber_air_below': not P(52.0, -45.0, 6.0)}
        log('v5f_b4i_spkbox_usb_slot', 'built', out)
        pi = tbm.copy(X.body('PI5_F')); tbm.booleanOperation(pi, X.wbox(XC + 30, XC + 60, -70, 5, 5, 30), B.IntersectionBooleanType)
        mod = X.union(X.union(pi, tbm.copy(pe)), tbm.copy(ce))
        crop = tbm.copy(bx); tbm.booleanOperation(crop, X.wbox(XC + 40, XC + 70, -60, 5, 0, 40), B.IntersectionBooleanType)
        pp = []
        for u in [0] + list(range(1, 71)):
            v = vol_x(mv(tbm.copy(mod), 0, -float(u), 2.0), crop)
            if v > 0:
                pp.append([u, v])
        out['pi_plug_path_lift2_vs_box'] = pp or 'all 0 (71 steps)'
        out['lower_2_vs_box'] = [[h, vol_x(mv(tbm.copy(mod), 0, 0, h), crop)] for h in (2.0, 1.0, 0.0)]
        r = X.interference(pe, [bx, X.body('SPK_L'), X.body('HOUSING_F_front'), X.body('PI5_F_cooler')])
        out['plug_env_interference'] = r
        r = X.interference(ce, [bx, X.body('HOUSING_F_front'), X.body('MAIN_BRACKET'), X.body('HOUSING_F_door')])
        out['cable_env_interference'] = r
        out['box_vs_spk_L_mm3'] = vol_x(bx, X.body('SPK_L'))
        out['box_vs_front_mm3'] = vol_x(bx, X.body('HOUSING_F_front'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b4i_spkbox_usb_slot', 'checks', out)
    print(json.dumps(out))
