# rev F e5a (2026-11-09): read-only inputs for V23b / V26 / V27 from "HA Panel v5 - tapered" (version 40).
#   World boxes of the touch, strip, sensor, lead and main-board bodies; the cap's D1.5 ports and D1.8 pins (axis point
#   at the face's ends, direction); V26: touch board rev D's back parts (courtyards from hardware/touch-board, at their
#   package maximum heights) as temporary solids, placed on TOUCH_PCB's back face, against KO_touch_back (must lie inside)
#   and every current body (must be 0); KO_touch_back itself against every current body. Writes e5/e5a_status.json.
import os, traceback
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
OUT = os.path.expanduser('~/Documents/HA_panel_renders/e5/e5a_status.json')
GUARD = {'HOUSING_F_front': 235.9107, 'HOUSING_F_door': 47.2633, 'MAIN_BRACKET': 6.5563, 'RESP_CARRIER': 10.1214,
         'CRADLE_5807': 2.1898}
BOXES = ['TOUCH_PCB', 'KO_touch_back', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'LEAD_TOUCH', 'MIC_strip_L_env', 'MIC_strip_R_env',
         'KO_mic_L_back', 'KO_mic_R_back', 'SENSOR_strip_L', 'SENSOR_strip_R', 'LEAD_MIC_L', 'LEAD_MIC_R', 'HOUSING_F_cap',
         'VEML_env', 'LEAD_VEML', 'BME680_env', 'BME_HOOD', 'FOAM_bme_env', 'FOAM_bme_top_env', 'LEAD_BME680', 'MAIN_pcb',
         'MAIN_front_env', 'MAIN_back_env', 'MAIN_C7_env', 'KO_C7_vent', 'LEAD_RADAR', 'LD2410C_env_F', 'SPKBOX_R',
         'SPKBOX_L', 'MAIN_BRACKET', 'RESP_pcb', 'RESP_CARRIER', 'LCD_pcb_76x110', 'LCD_components_env_d8.8', 'SLAB_frame']
# touch board rev D back parts: courtyard in KiCad (x0, x1, y0, y1) and the height above the back face (package maximum)
TOUCH_PARTS = {'U1': (40.42, 49.58, 10.30, 17.70, 1.75), 'R1': (38.27, 39.73, 19.02, 21.98, 1.0),
               'R2': (41.77, 43.23, 19.02, 21.98, 1.0), 'R3': (45.27, 46.73, 19.02, 21.98, 1.0),
               'R4': (48.77, 50.23, 19.02, 21.98, 1.0), 'C1': (38.87, 40.33, 12.52, 15.48, 1.0),
               'C2': (37.07, 38.53, 12.52, 15.48, 1.0)}
OTHERS = ['BME680_env', 'BME_HOOD', 'CRADLE_5807', 'FOAM_bme_env', 'FOAM_bme_top_env', 'FOOT_FL', 'FOOT_FR', 'FOOT_RL',
          'FOOT_RR', 'GPIO_plugA_env', 'GPIO_plugB_env', 'GROMMET_usbc_F', 'HOUSING_F_cap', 'HOUSING_F_door', 'HOUSING_F_front',
          'KO_5807_pigtail', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR', 'KO_K7_fan', 'KO_capkey_BL', 'KO_capkey_BR',
          'KO_capkey_SL', 'KO_capkey_SR', 'KO_mic_L_back', 'KO_mic_R_back', 'LCD_2x2_header_d15.4',
          'LCD_DSI_conn_d9.3', 'LCD_M2.5_standoff_d9.0', 'LCD_M2.5_standoff_d9.0 (1)', 'LCD_M2.5_standoff_d9.0 (2)',
          'LCD_M2.5_standoff_d9.0 (3)', 'LCD_Pi_standoff_d15.2', 'LCD_Pi_standoff_d15.2 (1)', 'LCD_Pi_standoff_d15.2 (2)',
          'LCD_Pi_standoff_d15.2 (3)', 'LCD_glass', 'LCD_panelFPC_conn_d9.5', 'LCD_panel_body', 'LCD_pcb_76x110',
          'LCD_pins_d16.0', 'LCD_pogo_header_d14.1', 'LCD_touchFPC_conn_d9.3', 'LCD_components_env_d8.8', 'LD2410C_env_F',
          'LEAD_BME680', 'LEAD_DSI', 'LEAD_GPIO_A', 'LEAD_GPIO_B', 'LEAD_LCD_5V', 'LEAD_MIC_L', 'LEAD_MIC_R',
          'LEAD_PIGTAIL_20V', 'LEAD_PI_POWER', 'LEAD_RADAR', 'LEAD_SPK_L', 'LEAD_SPK_R', 'LEAD_USB_RESP',
          'LEAD_VEML', 'MAIN_BRACKET', 'MIC_strip_L_env', 'MIC_strip_R_env', 'PD_5807_env', 'PI5_F', 'PI5_F_cooler',
          'PIPWR_a_env', 'RESP_CARRIER', 'RESP_mic_env', 'RESP_pcb', 'RESP_top_env', 'RESP_usbc_plug_env', 'SENSOR_strip_L',
          'SENSOR_strip_R', 'SLAB_frame', 'SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'SPK_driver_D40', 'SPK_driver_D40 (1)',
          'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'USBA_cable_env', 'USBA_plug_env', 'VEML_env',
          'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'MAIN_C7_env', 'KO_C7_vent']
B = adsk.fusion.BooleanTypes


def wpt(p):
    return [round(p.x * 10 - XC, 3), round(wy(p), 3), round(wz(p), 3)]


def wbb(bb):
    pts = [(x, y, z) for x in (bb.minPoint.x, bb.maxPoint.x) for y in (bb.minPoint.y, bb.maxPoint.y)
           for z in (bb.minPoint.z, bb.maxPoint.z)]
    w = [(p[0] * 10 - XC, (p[1] * C - p[2] * S) * 10, H + (p[1] * S + p[2] * C) * 10) for p in pts]
    return [round(min(q[k] for q in w), 3) for k in range(3)] + [round(max(q[k] for q in w), 3) for k in range(3)]


def gap(a, b):
    d = [max(0.0, b.minPoint.x - a.maxPoint.x, a.minPoint.x - b.maxPoint.x),
         max(0.0, b.minPoint.y - a.maxPoint.y, a.minPoint.y - b.maxPoint.y),
         max(0.0, b.minPoint.z - a.maxPoint.z, a.minPoint.z - b.maxPoint.z)]
    return math.sqrt(sum(v * v for v in d)) * 10


def vx(tbm, a, b):
    q = tbm.copy(a); tbm.booleanOperation(q, tbm.copy(b), B.IntersectionBooleanType); return round(q.volume * 1000, 4)


def run(_context):
    st = {'t0': time.strftime('%H:%M:%S'), 'missing': []}
    t0 = time.time()
    try:
        X = Ctx(); tbm = X.tbm
        st['version'] = [X.doc.dataFile.versionNumber, X.doc.dataFile.latestVersionNumber, X.doc.isModified]
        bad = [[k, None if X.body(k) is None else round(X.body(k).volume, 4)] for k, v in GUARD.items()
               if X.body(k) is None or abs(X.body(k).volume - v) > 0.0005]
        st['guard_bad'] = bad
        if bad:
            raise RuntimeError('GUARD %s' % bad)
        st['boxes'] = {}
        for n in BOXES:
            b = X.body(n)
            if b is None:
                st['missing'].append(n); continue
            st['boxes'][n] = {'bb': wbb(b.boundingBox), 'cm3': round(b.volume, 4), 'vis': b.isLightBulbOn,
                              'lumps': b.lumps.count}
        # cap ports and pins
        cyl = []
        for f in X.body('HOUSING_F_cap').faces:
            if f.geometry.objectType != adsk.core.Cylinder.classType():
                continue
            g = adsk.core.Cylinder.cast(f.geometry); r = round(g.radius * 10, 3)
            if r not in (0.75, 0.9):
                continue
            a = g.axis; a.normalize(); o = g.origin
            # face extent along the axis from its vertices' projections
            ts = [((v.geometry.x - o.x) * a.x + (v.geometry.y - o.y) * a.y + (v.geometry.z - o.z) * a.z) * 10 for v in f.vertices]
            bbw = wbb(f.boundingBox)
            if not ts:
                ts = [0.0]
            p0 = P3(o.x + a.x * min(ts) / 10, o.y + a.y * min(ts) / 10, o.z + a.z * min(ts) / 10)
            p1 = P3(o.x + a.x * max(ts) / 10, o.y + a.y * max(ts) / 10, o.z + a.z * max(ts) / 10)
            cyl.append({'r': r, 'p0': wpt(p0), 'p1': wpt(p1), 'dir': [round(a.x, 4), round(a.y * C - a.z * S, 4),
                                                                      round(a.y * S + a.z * C, 4)], 'bb': bbw,
                        'nv': f.vertices.count, 'area_mm2': round(f.area * 100, 3)})
        st['cap_cyl'] = cyl
        json.dump(st, open(OUT, 'w'), indent=1)
        # V26
        tp = X.body('TOUCH_PCB'); bbt = wbb(tp.boundingBox)
        xr0, yb, zt = bbt[3], bbt[1], bbt[5]                  # x_rel = max - x_kicad; back face = min y; z = top - y_kicad
        st['touch_frame'] = {'x_rel_of_kicad0': xr0, 'back_face_y': yb, 'z_of_kicad0': zt, 'pcb_bb': bbt}
        ko = X.body('KO_touch_back')
        parts = {}; allp = None
        for ref, (x0, x1, y0, y1, h) in TOUCH_PARTS.items():
            s_ = X.wbox(XC + xr0 - x0, XC + xr0 - x1, yb - h, yb, zt - y0, zt - y1)
            out_ko = tbm.copy(s_); tbm.booleanOperation(out_ko, tbm.copy(ko), B.DifferenceBooleanType)
            parts[ref] = {'x_rel': [round(xr0 - x1, 2), round(xr0 - x0, 2)], 'z': [round(zt - y1, 2), round(zt - y0, 2)],
                          'y': [round(yb - h, 2), round(yb, 2)], 'mm3': round(s_.volume * 1000, 3),
                          'outside_KO_mm3': round(out_ko.volume * 1000, 4)}
            allp = tbm.copy(s_) if allp is None else X.union(allp, tbm.copy(s_))
        st['v26_parts'] = parts
        # the same parts grown 1.0 sideways (x, z) and 1.0 further back (-y): a 0 here means >= 1.0 clearance
        grown = None
        for ref, (x0, x1, y0, y1, h) in TOUCH_PARTS.items():
            g_ = X.wbox(XC + xr0 - x0 + 1.0, XC + xr0 - x1 - 1.0, yb - h - 1.0, yb, zt - y0 + 1.0, zt - y1 - 1.0)
            grown = g_ if grown is None else X.union(grown, g_)
        hits = {}; kohits = {}
        pb = allp.boundingBox
        for n in OTHERS + ['TOUCH_PCB', 'LEAD_TOUCH']:
            ob = X.body(n)
            if ob is None:
                st['missing'].append(n); continue
            if gap(pb, ob.boundingBox) < 3.0:
                hits[n] = [vx(tbm, allp, tbm.copy(ob)), vx(tbm, grown, tbm.copy(ob))]
            if gap(ko.boundingBox, ob.boundingBox) < 3.0:
                kohits[n] = [vx(tbm, tbm.copy(ko), tbm.copy(ob)), round(X.app.measureManager.measureMinimumDistance(ko, ob).value * 10, 3)]
            json.dump(st, open(OUT, 'w'), indent=1)
        st['v26_parts_x_bodies'] = hits
        st['v26_KO_x_bodies'] = kohits
        st['done'] = True
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    st['t_s'] = round(time.time() - t0, 1)
    json.dump(st, open(OUT, 'w'), indent=1)
    print(json.dumps({k: st.get(k) for k in ('t_s', 'done', 'guard_bad', 'missing', 'FAIL')}))


run(None)
