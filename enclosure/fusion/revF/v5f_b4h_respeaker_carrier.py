# rev F block 4h (2026-11-04): ReSpeaker Lite on a printed carrier screwed to the LCD's four Pi standoffs.
#   Why there: the board (82.02 × 34.01, 83.60 with the jack) plus a straight USB-C plug (K14) needs ≈ 115 mm in one line.
#   Between the speaker boxes (x_rel ±46) and between the K5 lane pairs (x_rel −41.45…46.55) there are only 88–92 mm. Behind
#   the LCD, between the lower lanes (top ≤ z 87 at y −20) and the upper lanes (bottom ≥ z 139 at y −20), a plug at
#   z ≈ 122 can run outboard across the +x lane line (x_rel 46.55…53.55) with ≥ 10 mm to both lanes.
#   Carrier (design frame, parallel to the LCD back): plate x_rel −40.0…45.4, d 15.2…17.2 (front face on the standoff tips),
#   Z −56.9…2.2 (inside the boss opening x −60…53 design / Z −57.4…2.6, so the LCD + carrier + ReSpeaker go in from the
#   front as one module); Ø2.9 holes for 4 × M2.5 × 5 DIN912 into the standoffs; notch over the LCD's 2 × 2 header + pins;
#   two Ø6.0 × 5.0 bosses with Ruthex M2 × 4 holes Ø3.2 × 4.5 at the ReSpeaker holes (2.49, 31.58) / (60.20, 2.66);
#   zip-tie anchors on the mic side (K14): per vacated mic footprint two 1.2 × 3.0 slots through the plate, 1.7 either side
#   of the pad's x, Z −21…−18 (7.5 above the pad centre), so a tie holds the cable where it leaves the pad toward the
#   board's top edge; tie head on the carrier's front face (6.4 to the LCD components); ties fitted before the carrier.
#   Board: mic side toward the carrier (d 22.2), PCB d 22.2…23.71, connector side behind; board X → +x, Y → +Z,
#   X 0 at x_rel −37.6, Y 0 at Z −44.0 (USB-C face x_rel 45.28, jack end 46.0).
#   Envelopes (hidden): RESP_pcb, RESP_top_env (2.3 general + J2 6.83 + jack 5.44 + USB-C 3.40), RESP_mic_env (3.0 over
#   the board), RESP_usbc_plug_env (straight plug allowance 12.4 × 6.6 × 32 from the receptacle face, K11).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
EXPECT = {'HOUSING_F_front': (243.65, 0.003), 'HOUSING_F_door': (55.102, 0.003), 'SLAB_frame': (62.9, 0.06)}
BX0, BZ0 = -37.6, -44.0                 # board origin (x_rel, design Z)
D_MIC, D_PCB1 = 22.2, 23.71             # mic face, connector face (design depth d)


def run(_context):
    X = Ctx(); out = {}
    B = adsk.fusion.BooleanTypes; tbm = X.tbm

    def dbox(xr0, xr1, d0, d1, Z0, Z1):  # design-aligned box; x_rel, depth d (= −Y), design Z (mm)
        xr0, xr1 = sorted((xr0, xr1)); d0, d1 = sorted((d0, d1)); Z0, Z1 = sorted((Z0, Z1))
        c = P3((XC + (xr0 + xr1) / 2) / 10, -(d0 + d1) / 20, (Z0 + Z1) / 20)
        return tbm.createBox(adsk.core.OrientedBoundingBox3D.create(c, V3(1, 0, 0), V3(0, 1, 0), (xr1 - xr0) / 10, (d1 - d0) / 10, (Z1 - Z0) / 10))

    def dcyl(xr, Z, r, d0, d1):
        return tbm.createCylinderOrCone(P3((XC + xr) / 10, -d0 / 10, Z / 10), r / 10, P3((XC + xr) / 10, -d1 / 10, Z / 10), r / 10)

    def bxy(Xb, Yb):
        return BX0 + Xb, BZ0 + Yb

    def vol_x(a_, b_):
        q = tbm.copy(a_); tbm.booleanOperation(q, tbm.copy(b_), B.IntersectionBooleanType); return round(q.volume * 1000, 2)

    def dbb(b):
        bb = b.boundingBox
        return [round(bb.minPoint.x * 10 - XC, 2), round(bb.maxPoint.x * 10 - XC, 2), round(-bb.maxPoint.y * 10, 2),
                round(-bb.minPoint.y * 10, 2), round(bb.minPoint.z * 10, 2), round(bb.maxPoint.z * 10, 2)]
    try:
        for k, (v, tol) in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > tol:
                raise RuntimeError('guard: %s volume %s, expected %s' % (k, None if b is None else round(b.volume, 3), v))
        if X.body('RESP_CARRIER') is not None:
            raise RuntimeError('RESP_CARRIER exists already')
        names = [b.name for b in X.comp.bRepBodies]
        so = []
        for n in names:
            if n.startswith('LCD_Pi_standoff'):
                bb = X.body(n).boundingBox
                so.append([round((bb.minPoint.x + bb.maxPoint.x) * 5 - XC, 3), round((bb.minPoint.z + bb.maxPoint.z) * 5, 3),
                           round(-bb.minPoint.y * 10, 3), round(-bb.maxPoint.y * 10, 3), round((bb.maxPoint.x - bb.minPoint.x) * 10, 3)])
        out['standoffs_xrel_Z_dtip_dbase_dia'] = so
        out['lcd_design_boxes_xrel_d_Z'] = {n: dbb(X.body(n)) for n in ('LCD_2x2_header_d15.4', 'LCD_pins_d16.0', 'LCD_DSI_conn_d9.3',
                                                                     'LCD_pogo_header_d14.1', 'LCD_components_env_d8.8')}
        dtip = max(s[2] for s in so)
        if abs(dtip - 15.2) > 0.05:
            raise RuntimeError('standoff tip d %.3f, expected 15.2' % dtip)
        hd = X.body('LCD_2x2_header_d15.4').boundingBox; pn = X.body('LCD_pins_d16.0').boundingBox
        nx0 = min(hd.minPoint.x, pn.minPoint.x) * 10 - XC - 1.5; nx1 = max(hd.maxPoint.x, pn.maxPoint.x) * 10 - XC + 1.5
        nz0 = min(hd.minPoint.z, pn.minPoint.z) * 10 - 1.5
        out['notch_xrel_Z0'] = [round(nx0, 2), round(nx1, 2), round(nz0, 2)]
        # carrier
        cr = dbox(-40.0, 45.4, 15.2, 17.2, -56.9, 2.2)
        holes_b = [bxy(2.49, 31.58), bxy(60.20, 2.66)]
        for (xr, Z) in holes_b:
            cr = X.union(cr, dcyl(xr, Z, 3.0, 16.7, D_MIC))
        for s in so:
            X.diff(cr, dcyl(s[0], s[1], 1.45, 14.0, 18.5))
        X.diff(cr, dbox(nx0, nx1, 14.0, 18.5, nz0, 10.0))
        for (xr, Z) in holes_b:
            X.diff(cr, dcyl(xr, Z, 1.6, D_MIC - 4.5, D_MIC + 0.5))
        pads = [bxy(5.49, 17.0), bxy(76.49, 17.0)]
        for (xc, _z) in pads:
            for dx in (-1.7, 1.7):
                X.diff(cr, dbox(xc + dx - 0.6, xc + dx + 0.6, 14.0, 18.5, -21.0, -18.0))
        cb = X.add(cr, 'RESP_CARRIER')
        out['carrier_cm3'] = round(cb.volume, 3); out['carrier_lumps'] = cb.lumps.count
        # envelopes
        x1 = BX0 + 82.02; z1 = BZ0 + 34.01
        pcb = X.add(dbox(BX0, x1, D_MIC, D_PCB1, BZ0, z1), 'RESP_pcb'); pcb.isLightBulbOn = False
        top = dbox(BX0, x1, D_PCB1, D_PCB1 + 2.3, BZ0, z1)
        top = X.union(top, dbox(BX0 + 73.94, BX0 + 80.94, D_PCB1, D_PCB1 + 6.83, BZ0 + 13.04, BZ0 + 20.99))
        top = X.union(top, dbox(BX0 + 69.0, BX0 + 83.6, D_PCB1 - 0.52, D_PCB1 + 5.44, BZ0 + 2.18, BZ0 + 10.83))
        top = X.union(top, dbox(BX0 + 75.48, BX0 + 82.88, D_MIC - 0.2, D_PCB1 + 3.40, BZ0 + 23.29, BZ0 + 32.23))
        te = X.add(top, 'RESP_top_env'); te.isLightBulbOn = False
        me = X.add(dbox(BX0, x1, D_MIC - 3.0, D_MIC, BZ0, z1), 'RESP_mic_env'); me.isLightBulbOn = False
        ax_d = D_PCB1 + 1.70; ax_Z = BZ0 + (23.29 + 32.23) / 2; xf = BX0 + 82.88
        pe = X.add(dbox(xf, xf + 32.0, ax_d - 3.3, ax_d + 3.3, ax_Z - 6.2, ax_Z + 6.2), 'RESP_usbc_plug_env'); pe.isLightBulbOn = False
        out['usbc_axis_world'] = [round(xf, 2), round(-ax_d * C - ax_Z * S, 2), round(H - ax_d * S + ax_Z * C, 2)]
        for nm, (Xb, Yb) in (('U4', (5.49, 17.0)), ('U5', (76.49, 17.0))):
            xr, Z = bxy(Xb, Yb)
            out[nm + '_world'] = [round(xr, 2), round(-D_MIC * C - Z * S, 2), round(H - D_MIC * S + Z * C, 2)]
        out['env_cm3'] = {b.name: round(b.volume, 3) for b in (pcb, te, me, pe)}
        P = lambda b, xr, d, Z: b.pointContainment(P3((XC + xr) / 10, -d / 10, Z / 10)) in INS
        out['probes'] = {'plate_solid': P(cb, 0.0, 16.2, -30.0), 'standoff_hole_open': all(not P(cb, s[0], 16.2, s[1]) for s in so),
                         'boss_solid': all(P(cb, xr + 2.3, 20.0, Z) for (xr, Z) in holes_b),
                         'm2_hole_open': all(not P(cb, xr, 20.0, Z) for (xr, Z) in holes_b),
                         'notch_open': not P(cb, (nx0 + nx1) / 2, 16.2, 0.0),
                         'slots_open': all(not P(cb, xc + dx, 16.2, -19.5) for (xc, _z) in pads for dx in (-1.7, 1.7)),
                         'web_between_slots': all(P(cb, xc, 16.2, -19.5) for (xc, _z) in pads)}
        log('v5f_b4h_respeaker_carrier', 'built', out)
        # checks
        lcd = [X.body(n) for n in names if n.startswith('LCD_')]
        comps = lcd + [X.body(n) for n in ('SLAB_frame', 'HOUSING_F_front', 'HOUSING_F_door', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR',
                                            'SPKBOX_L', 'SPKBOX_R', 'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'MAIN_BRACKET',
                                            'LD2410C_env_F', 'MIC_strip_L_env', 'MIC_strip_R_env', 'KO_mic_L_back', 'KO_mic_R_back', 'VEML_env')]
        res = {}
        for b in (cb, pcb, te, me, pe):
            r = X.interference(b, comps)
            res[b.name] = {k: v for k, v in r.items() if v > 0} or 'all 0'
        out['interference_nonzero'] = res
        out['carrier_vs_RESP'] = {b.name: vol_x(cb, b) for b in (pcb, te, me)}
        mod = X.union(X.union(tbm.copy(cb), tbm.copy(pcb)), X.union(tbm.copy(te), tbm.copy(me)))
        hs = X.union(tbm.copy(X.body('HOUSING_F_front')), tbm.copy(X.body('SLAB_frame')))
        sw = []
        for u in (2, 5, 8, 11, 14, 17, 20, 25, 30):
            t = tbm.copy(mod); m = adsk.core.Matrix3D.create(); m.translation = V3(0, u / 10, 0); tbm.transform(t, m)
            sw.append([u, vol_x(t, hs)])
        out['module_front_insertion_vs_housing_slab'] = sw
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b4h_respeaker_carrier', 'checks', out)
    print(json.dumps({k: v for k, v in out.items() if k != 'lcd_design_boxes_xrel_d_Z'}))
