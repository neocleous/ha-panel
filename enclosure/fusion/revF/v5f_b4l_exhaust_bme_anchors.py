# rev F block 4l (2026-11-04): exhaust slots, BME680 spot + slots, two floor zip-tie anchors.
#   1. Exhaust (K18, rev D start 3 × 60 × 3 = 540 mm²): the door's top edge is at z 165.06, the top groove (block 5) needs
#      z ≤ 176.2 at the back, so the front shell's back wall has 9 mm above the joint: 2 slots 90 × 3 at x_rel ±45,
#      z 167.0–170.0 / 171.5–174.5, cut along world y (wall inner y −52.2…−48.1, outer −54.9…−50.8 at x 0) = 540 mm².
#      The tool stays hidden (TOOL_exhaust_slots) to re-cut after the D1 inner layer in block 5.
#   2. BME680 (K15, CJMCU-680 outline unmeasured → provisional 20 × 15 × 6 envelope, as VEML_env): back-right corner above
#      the −x box (box top z 76, lifted path 82), on the inner wall at (y −45, z 92): wall point x_rel −76.82, normal
#      (0.751, 0.643, −0.150) (B4k rays); board 1.5 off the wall; two slots 14 × 3 through the wall at ±3.0 along the wall's
#      up direction (rev D 14 × 3), behind the cloth. Retention after the caliper measurement (as the VEML6030).
#   3. Zip-tie anchors (K11 floor-edge clip bosses, 2 of 3; the third goes on the V11 cable corridor once V11 is decided):
#      bridges on the floor at (x_rel ±58.5, y −56.5): pillars 1.8 × 4 × 4.0, bar 6.6 × 4 × 1.5 (top z 8.0, under the speaker
#      boxes' lifted path z 9.0), tie opening 3.0 × 4.0.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
EXPECT = {'HOUSING_F_front': 243.65, 'HOUSING_F_door': 55.102}
P0 = (-76.82, -45.0, 92.0)
NW = (0.751, 0.643, -0.150)


def run(_context):
    X = Ctx(); out = {}
    B = adsk.fusion.BooleanTypes; tbm = X.tbm

    def vol_x(a_, b_):
        q = tbm.copy(a_); tbm.booleanOperation(q, tbm.copy(b_), B.IntersectionBooleanType); return round(q.volume * 1000, 2)

    def mv(t, dx, dy, dz):
        m = adsk.core.Matrix3D.create(); m.translation = V3(dx / 10, (dy * C + dz * S) / 10, (-dy * S + dz * C) / 10)
        tbm.transform(t, m); return t

    def wv(v):                                   # world direction → design Vector3D
        return V3(v[0], v[1] * C + v[2] * S, -v[1] * S + v[2] * C)

    def lbox(c, a1, a2, l1, l2, l3):            # box centred at world point c, axes a1, a2 (world), lengths l1, l2, l3 (a3 = a1 × a2)
        return tbm.createBox(adsk.core.OrientedBoundingBox3D.create(Dw(XC + c[0], c[1], c[2]), wv(a1), wv(a2), l1 / 10, l2 / 10, l3 / 10))
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.003:
                raise RuntimeError('guard: %s volume %s, expected %s' % (k, None if b is None else round(b.volume, 3), v))
        if X.body('TOOL_exhaust_slots') is not None:
            raise RuntimeError('TOOL_exhaust_slots exists already')
        fb = X.body('HOUSING_F_front'); f0 = fb.volume
        # 1 exhaust
        ex = X.union(X.wbox(XC - 45, XC + 45, -62, -40, 167.0, 170.0), X.wbox(XC - 45, XC + 45, -62, -40, 171.5, 174.5))
        out['exhaust_cut_mm3'] = vol_x(ex, fb)
        tool = X.add(tbm.copy(ex), 'TOOL_exhaust_slots'); tool.isLightBulbOn = False
        X.combine(fb, [X.add(ex, 'B4L_exhaust_tmp')], op=CUT)
        fb = X.body('HOUSING_F_front'); f1 = fb.volume
        # 2 BME680
        n = NW; L = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2); n = (n[0] / L, n[1] / L, n[2] / L)
        th = math.hypot(n[0], n[1]); t = (n[1] / th, -n[0] / th, 0.0)
        u = (t[1] * n[2] - t[2] * n[1], t[2] * n[0] - t[0] * n[2], t[0] * n[1] - t[1] * n[0])
        if u[2] < 0:
            u = (-u[0], -u[1], -u[2])
        add = lambda p, v, s: (p[0] + v[0] * s, p[1] + v[1] * s, p[2] + v[2] * s)
        cb = add(P0, n, 1.5 + 3.0)
        env = X.add(lbox(cb, t, u, 20.0, 15.0, 6.0), 'BME680_env'); env.isLightBulbOn = False
        sl = None
        for s in (-3.0, 3.0):
            c = add(add(P0, u, s), n, -2.25)
            bx = lbox(c, t, u, 14.0, 3.0, 7.5)
            sl = bx if sl is None else X.union(sl, bx)
        out['bme_slots_cut_mm3'] = vol_x(sl, fb)
        stool = X.add(tbm.copy(sl), 'TOOL_bme680_slots'); stool.isLightBulbOn = False
        X.combine(fb, [X.add(sl, 'B4L_bme_slots_tmp')], op=CUT)
        fb = X.body('HOUSING_F_front'); f2 = fb.volume
        out['bme_frame'] = {'n': [round(c, 3) for c in n], 't': [round(c, 3) for c in t], 'u': [round(c, 3) for c in u],
                            'env_centre': [round(c, 2) for c in cb]}
        # 3 anchors
        anc = None
        for sx in (1, -1):
            x = sx * 58.5; y = -56.5
            a = X.wbox(XC + x - 4.0, XC + x + 4.0, y - 2.5, y + 2.5, 2.0, 2.5)
            for dx in (-2.4, 2.4):
                a = X.union(a, X.wbox(XC + x + dx - 0.9, XC + x + dx + 0.9, y - 2.0, y + 2.0, 2.0, 6.5))
            a = X.union(a, X.wbox(XC + x - 3.3, XC + x + 3.3, y - 2.0, y + 2.0, 6.5, 8.0))
            anc = a if anc is None else X.union(anc, a)
        X.combine(fb, [X.add(anc, 'B4L_anchors_tmp')])
        fb = X.body('HOUSING_F_front')
        out['front_cm3'] = [round(f0, 3), round(f1, 3), round(f2, 3), round(fb.volume, 3)]; out['front_lumps'] = fb.lumps.count
        P = lambda x, y, z: X.inside(fb, XC + x, y, z)
        out['probes'] = {'exhaust_open': not P(0.0, -53.5, 168.5) and not P(0.0, -51.0, 173.0) and not P(40.0, -45.0, 173.0),
                         'exhaust_web_solid': P(0.0, -52.6, 170.75), 'wall_above_slots': P(0.0, -50.5, 175.3),
                         'wall_below_slots': P(0.0, -54.0, 166.3),
                         'bme_slots_open': all(not P(*add(add(P0, u, s), n, -1.2)) for s in (-3.0, 3.0)),
                         'bme_web_solid': P(*add(P0, n, -1.2)),
                         'anchor_bar': P(58.5, -56.5, 7.2) and P(-58.5, -56.5, 7.2), 'anchor_opening': not P(58.5, -56.5, 4.5) and not P(-58.5, -56.5, 4.5)}
        log('v5f_b4l_exhaust_bme_anchors', 'built', out)
        names = [b.name for b in X.comp.bRepBodies]
        comps = ['HOUSING_F_door', 'SPKBOX_L', 'SPKBOX_R', 'SLAB_frame', 'LD2410C_env_F', 'VEML_env', 'MIC_strip_L_env', 'MIC_strip_R_env',
                 'KO_mic_L_back', 'KO_mic_R_back', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR', 'MAIN_BRACKET', 'CRADLE_5807',
                 'RESP_CARRIER', 'RESP_top_env', 'RESP_usbc_plug_env', 'BME680_env'] + [n_ for n_ in names if n_.startswith('LCD_')]
        r = X.interference(fb, [X.body(n_) for n_ in comps])
        out['front_interference_nonzero'] = {k: v for k, v in r.items() if v > 0} or 'all 0'
        r = X.interference(env, [X.body(n_) for n_ in ('SPKBOX_R', 'KO_K5_LR', 'KO_K5_UR', 'LD2410C_env_F', 'HOUSING_F_door')])
        out['bme_env_interference_nonzero'] = {k: v for k, v in r.items() if v > 0} or 'all 0'
        bx = {}
        for s_, bn, sp in ((1, 'SPKBOX_L', 'SPK_L'), (-1, 'SPKBOX_R', 'SPK_R')):
            mod = X.union(tbm.copy(X.body(bn)), tbm.copy(X.body(sp)))
            xs = sorted((XC, XC + s_ * 115.0))
            crop = tbm.copy(fb); tbm.booleanOperation(crop, X.wbox(xs[0], xs[1], -140, 5, -5, 110), B.IntersectionBooleanType)
            if s_ < 0:
                crop = X.union(crop, tbm.copy(env))
            steps = [('lower', 0, -1.0, float(h)) for h in range(1, 7)] + [('side', -s_ * float(t_), -1.0, 6.0) for t_ in range(1, 41)] + \
                    [('in', -s_ * 40.0, -1.0 - u_, 6.0) for u_ in range(1, 77)]
            hits = []
            for (k, dx, dy, dz) in steps:
                v = vol_x(mv(tbm.copy(mod), dx, dy, dz), crop)
                if v > 0:
                    hits.append([k, dx, dy, dz, v])
            bx[bn] = hits or 'all 0 (%d steps)' % len(steps)
        out['box_paths_s40_vs_front'] = bx
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b4l_exhaust_bme_anchors', 'checks', out)
    print(json.dumps(out))
