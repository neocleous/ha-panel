# rev F e5a2 (2026-11-09): read-only V26 on exact extents (e5a placed the parts from the loose design box, which is tilted
#   12 deg to the world: void). World extents from each body's vertices (exact for the board and keep-out boxes). Touch
#   board rev D's back parts (courtyards from hardware/touch-board/touch-board.kicad_pcb at their package maximum heights)
#   placed on TOUCH_PCB's back face: inside KO_touch_back, against every current body, and grown 1.0 against every
#   current body; LEAD_TOUCH's part inside the keep-out against J1's pads. Writes e5/e5a2_status.json.
import os, traceback
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
OUT = os.path.expanduser('~/Documents/HA_panel_renders/e5/e5a2_status.json')
GUARD = {'HOUSING_F_front': 235.9107, 'HOUSING_F_door': 47.2633, 'MAIN_BRACKET': 6.5563, 'RESP_CARRIER': 10.1214,
         'CRADLE_5807': 2.1898}
EXACT = ['TOUCH_PCB', 'KO_touch_back', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'MIC_strip_L_env', 'MIC_strip_R_env',
         'KO_mic_L_back', 'KO_mic_R_back', 'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'MAIN_C7_env', 'KO_C7_vent',
         'VEML_env', 'BME680_env', 'LD2410C_env_F']
TOUCH_PARTS = {'U1': (40.42, 49.58, 10.30, 17.70, 1.75), 'R1': (38.27, 39.73, 19.02, 21.98, 1.0),
               'R2': (41.77, 43.23, 19.02, 21.98, 1.0), 'R3': (45.27, 46.73, 19.02, 21.98, 1.0),
               'R4': (48.77, 50.23, 19.02, 21.98, 1.0), 'C1': (38.87, 40.33, 12.52, 15.48, 1.0),
               'C2': (37.07, 38.53, 12.52, 15.48, 1.0)}
J1_PADS = [(27.75, 4.2), (31.25, 4.2), (34.75, 4.2), (38.25, 4.2)]     # 2.0 (x) x 3.0 (y) SMD pads, back side
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
          'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'MAIN_C7_env', 'KO_C7_vent', 'TOUCH_PCB', 'LEAD_TOUCH']
B = adsk.fusion.BooleanTypes


def vext(body):
    q = [(v.geometry.x * 10 - XC, wy(v.geometry), wz(v.geometry)) for v in body.vertices]
    return [round(min(p[k] for p in q), 3) for k in range(3)] + [round(max(p[k] for p in q), 3) for k in range(3)]


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
        st['version'] = [X.doc.dataFile.versionNumber, X.doc.isModified]
        bad = [[k, None if X.body(k) is None else round(X.body(k).volume, 4)] for k, v in GUARD.items()
               if X.body(k) is None or abs(X.body(k).volume - v) > 0.0005]
        st['guard_bad'] = bad
        if bad:
            raise RuntimeError('GUARD %s' % bad)
        st['exact'] = {n: vext(X.body(n)) for n in EXACT if X.body(n) is not None}
        tp = st['exact']['TOUCH_PCB']
        xr0, yb, zt = tp[3], tp[1], tp[5]          # x_rel = 45 - x_kicad, back face = min y, z = 50 - y_kicad
        st['frame'] = {'x_rel_kicad0': xr0, 'back_face_y': yb, 'z_kicad0': zt}
        ko = X.body('KO_touch_back')
        parts = {}; allp = None; grown = None
        for ref, (x0, x1, y0, y1, h) in TOUCH_PARTS.items():
            s_ = X.wbox(XC + xr0 - x0, XC + xr0 - x1, yb - h, yb, zt - y0, zt - y1)
            o_ = tbm.copy(s_); tbm.booleanOperation(o_, tbm.copy(ko), B.DifferenceBooleanType)
            parts[ref] = {'x_rel': [round(xr0 - x1, 2), round(xr0 - x0, 2)], 'z': [round(zt - y1, 2), round(zt - y0, 2)],
                          'y': [round(yb - h, 2), round(yb, 2)], 'mm3': round(s_.volume * 1000, 3),
                          'outside_KO_mm3': round(o_.volume * 1000, 4)}
            allp = tbm.copy(s_) if allp is None else X.union(allp, tbm.copy(s_))
            g_ = X.wbox(XC + xr0 - x0 + 1.0, XC + xr0 - x1 - 1.0, yb - h - 1.0, yb, zt - y0 + 1.0, zt - y1 - 1.0)
            grown = g_ if grown is None else X.union(grown, g_)
        st['parts'] = parts
        og = tbm.copy(grown); tbm.booleanOperation(og, tbm.copy(ko), B.DifferenceBooleanType)
        st['grown_outside_KO_mm3'] = round(og.volume * 1000, 4)
        hits = {}
        pb = grown.boundingBox
        for n in OTHERS:
            ob = X.body(n)
            if ob is None:
                st['missing'].append(n); continue
            if gap(pb, ob.boundingBox) < 3.0:
                hits[n] = [vx(tbm, allp, ob), vx(tbm, grown, ob)]
        st['parts_x_bodies'] = hits
        # LEAD_TOUCH inside the keep-out, against J1's pads
        lk = tbm.copy(X.body('LEAD_TOUCH')); tbm.booleanOperation(lk, tbm.copy(ko), B.IntersectionBooleanType)
        if lk.volume > 0:
            bb = lk.boundingBox
            q = [(v.geometry.x * 10 - XC, wy(v.geometry), wz(v.geometry)) for v in lk.vertices]
            st['lead_touch_in_KO'] = {'mm3': round(lk.volume * 1000, 3),
                                      'vext': [round(min(p[k] for p in q), 2) for k in range(3)] + [round(max(p[k] for p in q), 2) for k in range(3)]}
        st['j1_pads_world'] = [[round(xr0 - x - 1.0, 2), round(xr0 - x + 1.0, 2), round(zt - y - 1.5, 2), round(zt - y + 1.5, 2)]
                               for (x, y) in J1_PADS]
        pads = None
        for (x, y) in J1_PADS:
            p_ = X.wbox(XC + xr0 - x - 1.0, XC + xr0 - x + 1.0, yb - 0.5, yb, zt - y - 1.5, zt - y + 1.5)
            pads = p_ if pads is None else X.union(pads, p_)
        st['j1_pads_0p5_x_lead_touch_mm3'] = vx(tbm, pads, X.body('LEAD_TOUCH'))
        st['j1_pads_0p5_mm3'] = round(pads.volume * 1000, 3)
        st['done'] = True
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    st['t_s'] = round(time.time() - t0, 1)
    json.dump(st, open(OUT, 'w'), indent=1)
    print(json.dumps({k: st.get(k) for k in ('t_s', 'done', 'guard_bad', 'missing', 'FAIL')}))


run(None)
