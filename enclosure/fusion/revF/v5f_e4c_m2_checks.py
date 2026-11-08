# rev F e4c (2026-11-08): read-only checks of the four M2 pilots built by e4b, on the built solids.
#   Per pilot, from its faces: depth, blind or through, the coaxial boss. Wall = the largest w for which a ring around the
#   bore (r 0.85 ... 0.8 + w, from 0.35 below the face to 0.05 short of the end) lies wholly in the part; chamfer wall the
#   same ring at r 1.15 ... 1.1 + w over the chamfer; skin = the longest disc (r 0.75) under a blind bottom that lies wholly
#   in the part. Control: the same measure on the old D3.2 holes (<name>_e4) must give the audit's 1.4. Then the M2 x 6
#   tip margin and engagement (board on the boss face: ReSpeaker 1.51 K14, 5807 1.6 estimate), the screw (D2.0 shank to the
#   tip, head allowance D4.2 x 1.8) against every current body, the bodies near the exit of a through hole, the 5807
#   driver line straight up (D1.5 / 3.0 / 4.0; bodies present at assembly step 11, KO_ and LEAD_ left out), and the
#   interference of the new and the old part with every current body near them. Writes m2_e4/e4c_checks.json as it goes.
import os, traceback
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
OUT = os.path.expanduser('~/Documents/HA_panel_renders/m2_e4/e4c_checks.json')
SUBJ = {'RESP_CARRIER': {'board': 1.51, 'boards': ['RESP_pcb', 'RESP_top_env', 'RESP_mic_env'], 'driver': False},
        'CRADLE_5807': {'board': 1.6, 'boards': ['PD_5807_env'], 'driver': True}}
OTHERS = ['BME680_env', 'BME_HOOD', 'CRADLE_5807', 'FOAM_bme_env', 'FOAM_bme_top_env', 'FOOT_FL', 'FOOT_FR', 'FOOT_RL',
          'FOOT_RR', 'GPIO_plugA_env', 'GPIO_plugB_env', 'GROMMET_usbc_F', 'HOUSING_F_cap', 'HOUSING_F_door', 'HOUSING_F_front',
          'KO_5807_pigtail', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR', 'KO_K7_fan', 'KO_capkey_BL', 'KO_capkey_BR',
          'KO_capkey_SL', 'KO_capkey_SR', 'KO_mic_L_back', 'KO_mic_R_back', 'KO_touch_back', 'LCD_2x2_header_d15.4',
          'LCD_DSI_conn_d9.3', 'LCD_M2.5_standoff_d9.0', 'LCD_M2.5_standoff_d9.0 (1)', 'LCD_M2.5_standoff_d9.0 (2)',
          'LCD_M2.5_standoff_d9.0 (3)', 'LCD_Pi_standoff_d15.2', 'LCD_Pi_standoff_d15.2 (1)', 'LCD_Pi_standoff_d15.2 (2)',
          'LCD_Pi_standoff_d15.2 (3)', 'LCD_glass', 'LCD_panelFPC_conn_d9.5', 'LCD_panel_body', 'LCD_pcb_76x110',
          'LCD_pins_d16.0', 'LCD_pogo_header_d14.1', 'LCD_touchFPC_conn_d9.3', 'LCD_components_env_d8.8', 'LD2410C_env_F',
          'LEAD_BME680', 'LEAD_DSI', 'LEAD_GPIO_A', 'LEAD_GPIO_B', 'LEAD_LCD_5V', 'LEAD_MIC_L', 'LEAD_MIC_R',
          'LEAD_PIGTAIL_20V', 'LEAD_PI_POWER', 'LEAD_RADAR', 'LEAD_SPK_L', 'LEAD_SPK_R', 'LEAD_TOUCH', 'LEAD_USB_RESP',
          'LEAD_VEML', 'MAIN_BRACKET', 'MIC_strip_L_env', 'MIC_strip_R_env', 'PD_5807_env', 'PI5_F', 'PI5_F_cooler',
          'PIPWR_a_env', 'RESP_CARRIER', 'RESP_mic_env', 'RESP_pcb', 'RESP_top_env', 'RESP_usbc_plug_env', 'SENSOR_strip_L',
          'SENSOR_strip_R', 'SLAB_frame', 'SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'SPK_driver_D40', 'SPK_driver_D40 (1)',
          'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'TOUCH_PCB', 'USBA_cable_env', 'USBA_plug_env', 'VEML_env',
          'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'MAIN_C7_env', 'KO_C7_vent']
NOT_AT_STEP11 = ('HOUSING_F_door', 'GROMMET_usbc_F', 'HOUSING_F_cap', 'BME680_env', 'BME_HOOD', 'FOAM_bme_env',
                 'FOAM_bme_top_env', 'LD2410C_env_F')
SCREW_L, R_MAJ, HEAD_R, HEAD_K = 6.0, 1.0, 2.1, 1.8
R_DRV = (0.75, 1.5, 2.0)                    # driver tool radii: D1.5 (hex key), D3.0 and D4.0 (screwdriver shanks)
B = adsk.fusion.BooleanTypes


def w(p):
    return [round(p.x * 10 - XC, 3), round(wy(p), 3), round(wz(p), 3)]


def wv(v):
    return [round(v.x, 5), round(v.y * C - v.z * S, 5), round(v.y * S + v.z * C, 5)]


def at(o, a, t):
    return P3(o.x + a.x * t / 10, o.y + a.y * t / 10, o.z + a.z * t / 10)


def gap(a, b):
    d = [max(0.0, b.minPoint.x - a.maxPoint.x, a.minPoint.x - b.maxPoint.x),
         max(0.0, b.minPoint.y - a.maxPoint.y, a.minPoint.y - b.maxPoint.y),
         max(0.0, b.minPoint.z - a.maxPoint.z, a.minPoint.z - b.maxPoint.z)]
    return math.sqrt(sum(v * v for v in d)) * 10


def concave(f, o, a):
    p = f.pointOnFace
    ok, n = f.evaluator.getNormalAtPoint(p)
    d = V3(p.x - o.x, p.y - o.y, p.z - o.z); t = d.dotProduct(a)
    return n.dotProduct(V3(d.x - a.x * t, d.y - a.y * t, d.z - a.z * t)) < 0


def tproj(o, a, q):
    return ((q.x - o.x) * a.x + (q.y - o.y) * a.y + (q.z - o.z) * a.z) * 10


def adjacent(f):                            # faces sharing an edge with f (compared by tempId)
    res, ids = [], {f.tempId}
    for e in f.edges:
        for ff in e.faces:
            if ff.tempId not in ids:
                ids.add(ff.tempId); res.append(ff)
    return res


def run(_context):
    st = {'t0': time.strftime('%H:%M:%S')}
    t00 = time.time()
    try:
        X = Ctx(); tbm = X.tbm; mm = X.app.measureManager
        st['version'] = [X.doc.dataFile.versionNumber, X.doc.dataFile.latestVersionNumber, X.doc.isModified]

        def cyl(o, a, r, t0, t1):
            return tbm.createCylinderOrCone(at(o, a, t0), r / 10, at(o, a, t1), r / 10)

        def ring(o, a, r_in, r_out, t0, t1):
            q = cyl(o, a, r_out, t0, t1); tbm.booleanOperation(q, cyl(o, a, r_in, t0 - 0.01, t1 + 0.01), B.DifferenceBooleanType)
            return q

        def outside(tool, part):            # tool volume (mm3) not inside the part
            q = tbm.copy(tool); tbm.booleanOperation(q, tbm.copy(part), B.DifferenceBooleanType)
            return q.volume * 1000

        def largest(make, part, lo, hi):    # largest w in [lo, hi] for which make(w) lies in the part (to 0.001)
            if outside(make(lo), part) > 1e-4:
                return None
            if outside(make(hi), part) <= 1e-4:
                return '>= %.1f' % hi
            for _ in range(13):
                mid = (lo + hi) / 2
                if outside(make(mid), part) <= 1e-4:
                    lo = mid
                else:
                    hi = mid
            return round(lo, 3)

        for name, cfg in SUBJ.items():
            body = X.body(name); old = X.body(name + '_e4')
            res = {'vol': round(body.volume, 4), 'vol_old': round(old.volume, 4), 'lumps': body.lumps.count, 'pilots': [],
                   'control_old_holes': []}
            # control: the same wall measure on the old D3.2 x 4.5 holes (audit: 1.4)
            for f in old.faces:
                if f.geometry.objectType != adsk.core.Cylinder.classType():
                    continue
                cy = adsk.core.Cylinder.cast(f.geometry); a = cy.axis.copy(); a.normalize(); o = cy.origin
                if abs(cy.radius * 10 - 1.6) > 0.005 or not concave(f, o, a):
                    continue
                ts = [tproj(o, a, v.geometry) for e in f.edges for v in (e.startVertex, e.endVertex)]
                t0, t1 = min(ts), max(ts)
                if old.pointContainment(at(o, a, t1 + 0.05)) in INS:
                    a = V3(-a.x, -a.y, -a.z); t0, t1 = -t1, -t0
                res['control_old_holes'].append({'top_w': w(at(o, a, t1)), 'depth': round(t1 - t0, 3),
                                                 'wall': largest(lambda x: ring(o, a, 1.65, 1.6 + x, t0 + 0.05, t1 - 0.05),
                                                                 old, 0.06, 4.0)})
            cyls = [f for f in body.faces if f.geometry.objectType == adsk.core.Cylinder.classType()]
            for f in cyls:
                cy = adsk.core.Cylinder.cast(f.geometry)
                a = cy.axis.copy(); a.normalize(); o = cy.origin
                if abs(cy.radius * 10 - 0.8) > 0.005 or not concave(f, o, a):
                    continue
                adj = adjacent(f)
                cone = [g for g in adj if g.geometry.objectType == adsk.core.Cone.classType()]
                if len(cone) != 1:                        # concave r 0.8 without a chamfer cone: a root fillet
                    continue
                cone = cone[0]
                cone_t = [tproj(o, a, v.geometry) for e in cone.edges for v in (e.startVertex, e.endVertex)]
                cyl_t = [tproj(o, a, v.geometry) for e in f.edges for v in (e.startVertex, e.endVertex)]
                if max(cone_t) > max(cyl_t) + 0.01:       # cone at the + end: + points out of the hole
                    t_face, t_cb, t_end = max(cone_t), min(cone_t), min(cyl_t)
                else:
                    a = V3(-a.x, -a.y, -a.z); t_face, t_cb, t_end = -min(cone_t), -max(cone_t), -max(cyl_t)
                ends = [g for g in adj if g.tempId != cone.tempId]
                if len(ends) != 1:
                    raise RuntimeError('%s: pilot end faces %d' % (name, len(ends)))
                end = ends[0]
                blind = end.area * 100 < 2.2              # D1.6 disc = 2.01 mm2; a through hole ends on a big face
                depth = t_face - t_end
                boss = None
                for g in cyls:
                    cy2 = adsk.core.Cylinder.cast(g.geometry)
                    a2 = cy2.axis.copy(); a2.normalize()
                    d = V3(cy2.origin.x - o.x, cy2.origin.y - o.y, cy2.origin.z - o.z)
                    if abs(abs(a2.dotProduct(a)) - 1) < 1e-6 and d.crossProduct(a).length * 10 < 0.01 \
                            and not concave(g, cy2.origin, a2) and cy2.radius * 10 > 1.0:
                        boss = round(cy2.radius * 20, 3)
                p = {'top_w': w(at(o, a, t_face)), 'axis_out_w': wv(a), 'blind': blind, 'depth': round(depth, 3),
                     'chamfer_depth': round(t_face - t_cb, 3), 'end_face_mm2': round(end.area * 100, 3), 'boss_od': boss}
                p['wall_bore'] = largest(lambda x: ring(o, a, 0.85, 0.8 + x, t_face - depth + 0.05, t_face - 0.35),
                                         body, 0.06, 4.0)
                p['wall_chamfer'] = largest(lambda x: ring(o, a, 1.15, 1.1 + x, t_face - 0.28, t_face - 0.02), body,
                                            0.06, 4.0)
                p['pilot_open'] = round(tbm.copy(cyl(o, a, 0.75, t_face - depth + 0.05, t_face - 0.35)).volume * 1000 -
                                        outside(cyl(o, a, 0.75, t_face - depth + 0.05, t_face - 0.35), body), 6)
                if blind:
                    p['skin'] = largest(lambda x: cyl(o, a, 0.75, t_end - x, t_end - 0.05), body, 0.1, 6.0)
                else:
                    p['exit_open_below'] = outside(cyl(o, a, 0.75, t_end - 1.0, t_end - 0.05), body) > 0.99 * (
                        math.pi * 0.75 ** 2 * 0.95)
                board = cfg['board']; tip = SCREW_L - board
                p['screw'] = {'board': board, 'in_plastic': round(tip, 3), 'below_chamfer': round(tip - (t_face - t_cb), 3),
                              'tip_margin': round(depth - tip, 3), 'margin_to': 'bottom' if blind else 'exit'}
                shank = cyl(o, a, R_MAJ, t_face + board, t_face - tip)
                head = cyl(o, a, HEAD_R, t_face + board, t_face + board + HEAD_K)
                sx, hx = {}, {}
                for on in OTHERS:
                    ob = X.body(on)
                    if ob is None:
                        continue
                    for tool, store, skip in ((shank, sx, [name] + cfg['boards']), (head, hx, cfg['boards'])):
                        if on in skip or gap(tool.boundingBox, ob.boundingBox) > 0:
                            continue
                        q = tbm.copy(tool); tbm.booleanOperation(q, tbm.copy(ob), B.IntersectionBooleanType)
                        if q.volume > 1e-9:
                            store[on] = round(q.volume * 1000, 4)
                p['shank_x'] = sx or 'all 0'
                p['head_x'] = hx or 'all 0'
                if not blind:
                    beyond = {}
                    for on in OTHERS:
                        ob = X.body(on)
                        if ob is None or on == name:
                            continue
                        r = mm.measureMinimumDistance(at(o, a, t_end), ob)
                        if r.value * 10 < 25.0:
                            beyond[on] = round(r.value * 10, 2)
                    p['bodies_within_25_of_exit_centre'] = beyond
                for rd in (R_DRV if cfg['driver'] else ()):
                    def blocked(L):
                        t = cyl(o, a, rd, t_face + board + HEAD_K, t_face + board + HEAD_K + L)
                        hit = []
                        for on in OTHERS:
                            if on in NOT_AT_STEP11 or on.startswith(('KO_', 'LEAD_')):
                                continue
                            ob = X.body(on)
                            if ob is None or gap(t.boundingBox, ob.boundingBox) > 0:
                                continue
                            q = tbm.copy(t); tbm.booleanOperation(q, tbm.copy(ob), B.IntersectionBooleanType)
                            if q.volume > 1e-9:
                                hit.append(on)
                        return hit
                    key = 'driver_free_d%.1f' % (2 * rd)
                    if not blocked(150.0):
                        p[key] = '>= 150'
                    else:
                        lo, hi = 0.0, 150.0
                        for _ in range(11):
                            mid = (lo + hi) / 2
                            if blocked(mid):
                                hi = mid
                            else:
                                lo = mid
                        p[key] = [round(lo, 2), blocked(hi)]
                res['pilots'].append(p)
                st[name] = res
                json.dump(st, open(OUT, 'w'), indent=1)
            if len(res['pilots']) != 2:
                raise RuntimeError('%s: %d pilots found' % (name, len(res['pilots'])))
            ix = {}
            for on in OTHERS:
                ob = X.body(on)
                if ob is None or on == name or gap(body.boundingBox, ob.boundingBox) > 1.0:
                    continue
                row = []
                for sb in (body, old):
                    q = tbm.copy(sb); tbm.booleanOperation(q, tbm.copy(ob), B.IntersectionBooleanType)
                    row.append(round(q.volume * 1000, 3))
                if row[0] > 0 or row[1] > 0:
                    ix[on] = row
            res['interference_new_old'] = ix
            st[name] = res
            json.dump(st, open(OUT, 'w'), indent=1)
        st['done'] = True
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    st['t_s'] = round(time.time() - t00, 1)
    json.dump(st, open(OUT, 'w'), indent=1)
    print(json.dumps({k: st.get(k) for k in ('t_s', 'done', 'FAIL')}))


run(None)
