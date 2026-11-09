# rev F e6c (2026-11-09): read-only checks on the e6b door (V24: door N52 D8 x 2, lip N52 D8 x 1). Per pocket, along
#   lines parallel to its axis (containment on local crops, 0.1 steps bisected to 0.002, x passed as design x): the skin
#   from the new floor to the door's inner face (axis, r 2.0 x 4, r 3.5 / 4.0 x 8), the pocket depth from the floor to the
#   outer surface at r 4.45 x 8 (a 2.0 magnet's protrusion), the lap gap and the pad skin on the axis, the lip pocket's
#   depth at r 3.5 x 4. Magnets as solids (door D8 x 2 on the new floor, lip D8 x 1 on the lip pocket floor) against every
#   current body, again grown 0.5. KO_K5_* / KO_capkey_* and every current body against the new door and the old one
#   (HOUSING_F_door_e6). Writes e6/e6c_checks.json.
import os, traceback
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py'), encoding='utf-8').read())
OUT = os.path.expanduser('~/Documents/HA_panel_renders/e6/e6c_checks.json')
GUARD = {'HOUSING_F_front': 235.9107, 'HOUSING_F_door_e6': 47.2633, 'HOUSING_F_cap': 9.9441, 'GROMMET_usbc_F': 0.5062}
NEW_DOOR = 47.0198            # 47.2633 - 10 x pi x 4.15^2 x 0.45 / 1000
R_POCKET = 4.15
T_DOOR, T_LIP, R_MAG = 2.0, 1.0, 4.0
OTHERS = ['BME680_env', 'BME_HOOD', 'CRADLE_5807', 'FOAM_bme_env', 'FOAM_bme_top_env', 'FOOT_FL', 'FOOT_FR', 'FOOT_RL',
          'FOOT_RR', 'GPIO_plugA_env', 'GPIO_plugB_env', 'GROMMET_usbc_F', 'HOUSING_F_cap', 'HOUSING_F_front',
          'KO_5807_pigtail', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR', 'KO_K7_fan', 'KO_capkey_BL', 'KO_capkey_BR',
          'KO_capkey_SL', 'KO_capkey_SR', 'KO_mic_L_back', 'KO_mic_R_back', 'KO_touch_back', 'KO_C7_vent', 'LCD_glass',
          'LCD_panel_body', 'LCD_pcb_76x110', 'LCD_components_env_d8.8', 'LD2410C_env_F', 'LEAD_BME680', 'LEAD_DSI',
          'LEAD_GPIO_A', 'LEAD_GPIO_B', 'LEAD_LCD_5V', 'LEAD_MIC_L', 'LEAD_MIC_R', 'LEAD_PIGTAIL_20V', 'LEAD_PI_POWER',
          'LEAD_RADAR', 'LEAD_SPK_L', 'LEAD_SPK_R', 'LEAD_TOUCH', 'LEAD_USB_RESP', 'LEAD_VEML', 'MAIN_BRACKET',
          'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'MAIN_C7_env', 'MIC_strip_L_env', 'MIC_strip_R_env', 'PD_5807_env',
          'PI5_F', 'PI5_F_cooler', 'PIPWR_a_env', 'RESP_CARRIER', 'RESP_mic_env', 'RESP_pcb', 'RESP_top_env',
          'RESP_usbc_plug_env', 'SLAB_frame', 'SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R',
          'TOUCH_PCB', 'USBA_cable_env', 'USBA_plug_env', 'VEML_env']
B = adsk.fusion.BooleanTypes


def wpt(p):
    return (p.x * 10 - XC, wy(p), wz(p))


def gap(a, b):
    d = [max(0.0, b.minPoint.x - a.maxPoint.x, a.minPoint.x - b.maxPoint.x),
         max(0.0, b.minPoint.y - a.maxPoint.y, a.minPoint.y - b.maxPoint.y),
         max(0.0, b.minPoint.z - a.maxPoint.z, a.minPoint.z - b.maxPoint.z)]
    return math.sqrt(sum(v * v for v in d)) * 10


def vx(a, b):
    tbm = adsk.fusion.TemporaryBRepManager.get()
    q = tbm.copy(a); tbm.booleanOperation(q, tbm.copy(b), B.IntersectionBooleanType); return round(q.volume * 1000, 4)


def first_change(body, c, a, k0, dk, kmax, want):
    """walk c + k a from k0 in steps dk until containment == want; bisect; return k (mm) or None"""
    ins = lambda k: body.pointContainment(P3(c.x + a.x * k / 10, c.y + a.y * k / 10, c.z + a.z * k / 10)) in INS
    k = k0
    while abs(k - k0) <= kmax:
        k1 = k + dk
        if ins(k1) == want:
            lo, hi = k, k1
            while abs(hi - lo) > 0.002:
                m = (lo + hi) / 2
                if ins(m) == want:
                    hi = m
                else:
                    lo = m
            return round((lo + hi) / 2, 3)
        k = k1
    return None


def run(_context):
    st = {'t0': time.strftime('%H:%M:%S')}
    t0 = time.time()
    try:
        X = Ctx(); tbm = X.tbm
        st['version'] = [X.doc.dataFile.versionNumber, X.doc.isModified]
        bad = [[k, None if X.body(k) is None else round(X.body(k).volume, 4)] for k, v in GUARD.items()
               if X.body(k) is None or abs(X.body(k).volume - v) > 0.0005]
        nd = X.body('HOUSING_F_door')
        if nd is None or abs(nd.volume - NEW_DOOR) > 0.0005:
            bad.append(['HOUSING_F_door', None if nd is None else round(nd.volume, 4)])
        st['guard_bad'] = bad
        if bad:
            raise RuntimeError('GUARD %s' % bad)
        od = X.body('HOUSING_F_door_e6'); front = X.body('HOUSING_F_front')
        floors = []
        for f in nd.faces:
            if f.geometry.objectType != adsk.core.Cylinder.classType():
                continue
            g = adsk.core.Cylinder.cast(f.geometry)
            if abs(g.radius * 10 - R_POCKET) > 0.005:
                continue
            a = g.axis.copy(); a.normalize()
            if nw_of(a)[1] > 0:
                a.scaleBy(-1.0)
            o = g.origin; cands = []
            for e in f.edges:
                for af in e.faces:
                    if af != f and af.geometry.objectType == adsk.core.Plane.classType():
                        pl = adsk.core.Plane.cast(af.geometry); nn = pl.normal.copy(); nn.normalize()
                        if abs(abs(nn.dotProduct(a)) - 1.0) < 1e-6:
                            cands.append((pl.origin.x - o.x) * a.x + (pl.origin.y - o.y) * a.y + (pl.origin.z - o.z) * a.z)
            t = min(cands)
            floors.append((P3(o.x + a.x * t, o.y + a.y * t, o.z + a.z * t), a))
        st['n_pockets'] = len(floors)
        rows = []; mags_d = []; mags_l = []
        for (c, a) in sorted(floors, key=lambda r: (wpt(r[0])[0] > 0, wpt(r[0])[2])):
            cw = wpt(c)
            crop = X.wbox(XC + cw[0] - 12, XC + cw[0] + 12, cw[1] - 12, cw[1] + 12, cw[2] - 12, cw[2] + 12)
            dq = tbm.copy(nd); inter(X, dq, tbm.copy(crop))
            fq = tbm.copy(front); inter(X, fq, tbm.copy(crop))
            r_ = adsk.core.Vector3D.create(1, 0, 0) if abs(a.x) < 0.9 else adsk.core.Vector3D.create(0, 1, 0)
            u = a.crossProduct(r_); u.normalize(); v = a.crossProduct(u); v.normalize()
            off = lambda rr, th: P3(c.x + (u.x * math.cos(th) + v.x * math.sin(th)) * rr / 10,
                                    c.y + (u.y * math.cos(th) + v.y * math.sin(th)) * rr / 10,
                                    c.z + (u.z * math.cos(th) + v.z * math.sin(th)) * rr / 10)
            skins = []
            for rr, na in ((0.0, 1), (2.0, 4), (3.5, 8), (4.0, 8)):
                for k in range(na):
                    q = off(rr, 2 * math.pi * k / na)
                    s_in = first_change(dq, q, a, -0.05, -0.1, 3.0, False)    # leaving the door going inward
                    skins.append(None if s_in is None else round(-s_in, 3))
            rims = []
            for k in range(8):
                q = off(4.45, 2 * math.pi * k / 8)
                s_out = first_change(dq, q, a, 0.0, 0.1, 6.0, False)          # leaving the door going outward
                rims.append(s_out)
            k_in = first_change(dq, c, a, -0.05, -0.1, 3.0, False)           # door inner face on the axis
            k_pad = first_change(fq, c, a, k_in, -0.05, 2.0, True)           # pad face
            k_lip = first_change(fq, c, a, k_pad - 0.05, -0.05, 2.0, False)   # lip pocket floor
            lipd = []
            for k in range(4):
                q = off(3.5, 2 * math.pi * k / 4)
                kf = first_change(fq, q, a, k_pad - 0.05, -0.05, 2.0, False)
                kb = first_change(fq, q, a, kf - 0.05, -0.05, 6.0, True) if kf is not None else None
                pend = first_change(fq, off(4.45, 2 * math.pi * k / 4), a, k_pad - 0.05, -0.1, 6.0, False)
                lipd.append([kf, kb, pend])
            row = {'floor_w': [round(x, 3) for x in cw], 'n_w': [round(x, 4) for x in nw_of(a)],
                   'skin_min_max': [min(s for s in skins if s is not None), max(s for s in skins if s is not None)],
                   'skins': skins, 'rim_depth_min_max': [min(x for x in rims if x is not None), max(x for x in rims if x is not None)],
                   'rims': rims, 'axis_inner': k_in, 'axis_pad': k_pad, 'axis_lip_floor': k_lip,
                   'lap_gap': None if None in (k_in, k_pad) else round(k_in - k_pad, 3),
                   'pad_skin': None if None in (k_pad, k_lip) else round(k_pad - k_lip, 3),
                   'magnet_gap_axis': None if k_lip is None else round(-k_lip, 3),
                   'lip_r3.5_[floor, pad_back_or_None, pad_end_r4.45]': lipd}
            row['door_magnet_protrusion_max'] = round(T_DOOR - row['rim_depth_min_max'][0], 3)
            rows.append(row)
            mags_d.append(tbm.createCylinderOrCone(c, R_MAG / 10, P3(c.x + a.x * T_DOOR / 10, c.y + a.y * T_DOOR / 10,
                                                                      c.z + a.z * T_DOOR / 10), R_MAG / 10))
            lf = P3(c.x + a.x * k_lip / 10, c.y + a.y * k_lip / 10, c.z + a.z * k_lip / 10)
            mags_l.append(tbm.createCylinderOrCone(lf, R_MAG / 10, P3(lf.x - a.x * T_LIP / 10, lf.y - a.y * T_LIP / 10,
                                                                       lf.z - a.z * T_LIP / 10), R_MAG / 10))
            st['pockets'] = rows
            json.dump(st, open(OUT, 'w'), indent=1)
        md = mags_d[0]
        for m in mags_d[1:]:
            X.union(md, m)
        ml = mags_l[0]
        for m in mags_l[1:]:
            X.union(ml, m)
        st['magnet_cm3'] = [round(md.volume, 5), round(ml.volume, 5)]
        res = {}
        for nm, mg in (('door_magnets', md), ('lip_magnets', ml)):
            hits = {}
            for on in OTHERS + ['HOUSING_F_door']:
                ob = X.body(on)
                if ob is None or gap(mg.boundingBox, ob.boundingBox) > 2.0:
                    continue
                v_ = vx(mg, ob)
                if v_ > 0:
                    hits[on] = v_
            res[nm] = hits
        st['magnets_x_bodies_mm3'] = res
        # grown 0.5 (radius 4.5, 0.5 longer each way) against the same bodies: who is within 0.5
        near = {}
        for nm, mags, tt, sgn in (('door_magnets', floors, T_DOOR, 1), ('lip_magnets', floors, T_LIP, -1)):
            g_ = None
            for i, (c, a) in enumerate(sorted(floors, key=lambda r: (wpt(r[0])[0] > 0, wpt(r[0])[2]))):
                base = 0.0 if sgn > 0 else rows[i]['axis_lip_floor']
                p0 = P3(c.x + a.x * (base - 0.5 * sgn) / 10, c.y + a.y * (base - 0.5 * sgn) / 10, c.z + a.z * (base - 0.5 * sgn) / 10)
                p1 = P3(c.x + a.x * (base + (tt + 0.5) * sgn) / 10, c.y + a.y * (base + (tt + 0.5) * sgn) / 10,
                        c.z + a.z * (base + (tt + 0.5) * sgn) / 10)
                cy = tbm.createCylinderOrCone(p0, (R_MAG + 0.5) / 10, p1, (R_MAG + 0.5) / 10)
                g_ = cy if g_ is None else X.union(g_, cy)
            within = []
            for on in OTHERS + ['HOUSING_F_door']:
                ob = X.body(on)
                if ob is None or gap(g_.boundingBox, ob.boundingBox) > 2.0:
                    continue
                if vx(g_, ob) > 0:
                    within.append(on)
            near[nm] = within
        st['within_0.5'] = near
        KO = ('KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR', 'KO_capkey_BL', 'KO_capkey_BR', 'KO_capkey_SL', 'KO_capkey_SR')
        st['ko_x_door_new_old'] = {k: [vx(X.body(k), nd), vx(X.body(k), od)] for k in KO}
        diff = {}
        for on in OTHERS:
            ob = X.body(on)
            if ob is None or gap(od.boundingBox, ob.boundingBox) > 0.5:
                continue
            a_, b_ = vx(nd, ob), vx(od, ob)
            if a_ > 0 or b_ > 0:
                diff[on] = [a_, b_]
        st['door_x_bodies_new_old'] = diff
        st['done'] = True
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    st['t_s'] = round(time.time() - t0, 1)
    json.dump(st, open(OUT, 'w'), indent=1)
    print(json.dumps({k: st.get(k) for k in ('t_s', 'done', 'guard_bad', 'n_pockets', 'magnets_x_bodies_mm3', 'within_0.5', 'FAIL')}))


run(None)
