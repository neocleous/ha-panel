# rev F e5c (2026-11-09): read-only - V23b, the BME680 and VEML6030 leads re-routed to main-board J10, as temporary D3
#   tubes (polylines from the offline router: voxel distance field of the e5b meshes, 0.5 mm, with main board rev 2.1's
#   front parts as courtyard x height boxes; >= 2 mm clearance asked except at the ends). Sensor ends unchanged (d12a,
#   c2c/d8b points). Each lead ends at its J10 column (x_rel -18.42 BME680, -20.97 VEML6030; rows z 73.69-81.31, centre
#   77.5) on the board's front face y -63.4, after a 13.4 straight stub. Checks against every current body and the board's
#   front parts near J10 (boxes, KiCad courtyards x heights as MAIN_env rev 2.1): intersection, and the same tube grown
#   by 1.0 and 2.0 (clearance class); the old leads (control) against the bodies they were allowed to touch.
#   Writes e5/e5c_checks.json as it goes.
import os, traceback
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
OUT = os.path.expanduser('~/Documents/HA_panel_renders/e5/e5c_checks.json')
GUARD = {'HOUSING_F_front': 235.9107, 'HOUSING_F_door': 47.2633, 'MAIN_BRACKET': 6.5563, 'RESP_CARRIER': 10.1214,
         'CRADLE_5807': 2.1898, 'LEAD_BME680': 0.7753, 'LEAD_VEML': 1.1381}
ROUTES = {
    'LEAD_BME680': [(-71.841, -40.737, 93.534), (-72.752, -41.517, 85.625), (-66.557, -36.212, 84.387),
                    (-43.25, -35.75, 96.75), (-18.42, -50.0, 77.5), (-18.42, -63.4, 77.5)],
    'LEAD_VEML': [(0.0, -39.7, 175.75), (0.0, -39.7, 165.0), (-20.97, -50.0, 77.5), (-20.97, -63.4, 77.5)]}
DESIGNED = {'LEAD_BME680': ['HOUSING_F_front', 'BME680_env', 'BME_HOOD', 'FOAM_bme_env', 'FOAM_bme_top_env',
                            'MAIN_front_env', 'MAIN_pcb'],
            'LEAD_VEML': ['VEML_env', 'HOUSING_F_cap', 'MAIN_front_env', 'MAIN_pcb']}
# main board rev 2.1 front parts near J10: x_rel, y (front face -63.4 + height), z  (KiCad courtyards, MAIN_env heights)
PARTS = {'PS1': (-16.05, 35.25, -63.4, -35.9, 70.75, 83.25), 'J5_plug': (-37.4, -24.0, -63.4, -53.6, 76.62, 83.38),
         'F3': (-29.33, -21.95, -63.4, -60.46, 83.78, 87.44), 'R105': (-22.83, -19.87, -63.4, -61.6, 69.84, 71.3),
         'R100': (-19.42, -16.46, -63.4, -61.6, 69.65, 71.11), 'C10': (-30.01, -26.61, -63.4, -61.6, 74.22, 76.18),
         'C102': (-22.57, -19.17, -63.4, -61.6, 67.18, 69.14), 'C101': (-18.7, -15.3, -63.4, -61.6, 66.93, 68.89),
         'C110': (-30.01, -26.61, -63.4, -61.6, 70.9, 72.86), 'R19': (-33.18, -30.22, -63.4, -61.6, 83.79, 85.25),
         'L101': (-33.75, -24.25, -63.4, -58.0, 60.35, 70.45), 'C7': (-8.46, -2.88, -63.4, -50.9, 83.26, 88.84)}
OTHERS = ['BME680_env', 'BME_HOOD', 'CRADLE_5807', 'FOAM_bme_env', 'FOAM_bme_top_env', 'FOOT_FL', 'FOOT_FR', 'FOOT_RL',
          'FOOT_RR', 'GPIO_plugA_env', 'GPIO_plugB_env', 'GROMMET_usbc_F', 'HOUSING_F_cap', 'HOUSING_F_door', 'HOUSING_F_front',
          'KO_5807_pigtail', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR', 'KO_K7_fan', 'KO_capkey_BL', 'KO_capkey_BR',
          'KO_capkey_SL', 'KO_capkey_SR', 'KO_mic_L_back', 'KO_mic_R_back', 'KO_touch_back', 'LCD_2x2_header_d15.4',
          'LCD_DSI_conn_d9.3', 'LCD_M2.5_standoff_d9.0', 'LCD_M2.5_standoff_d9.0 (1)', 'LCD_M2.5_standoff_d9.0 (2)',
          'LCD_M2.5_standoff_d9.0 (3)', 'LCD_Pi_standoff_d15.2', 'LCD_Pi_standoff_d15.2 (1)', 'LCD_Pi_standoff_d15.2 (2)',
          'LCD_Pi_standoff_d15.2 (3)', 'LCD_glass', 'LCD_panelFPC_conn_d9.5', 'LCD_panel_body', 'LCD_pcb_76x110',
          'LCD_pins_d16.0', 'LCD_pogo_header_d14.1', 'LCD_touchFPC_conn_d9.3', 'LCD_components_env_d8.8', 'LD2410C_env_F',
          'LEAD_DSI', 'LEAD_GPIO_A', 'LEAD_GPIO_B', 'LEAD_LCD_5V', 'LEAD_MIC_L', 'LEAD_MIC_R',
          'LEAD_PIGTAIL_20V', 'LEAD_PI_POWER', 'LEAD_RADAR', 'LEAD_SPK_L', 'LEAD_SPK_R', 'LEAD_TOUCH', 'LEAD_USB_RESP',
          'MAIN_BRACKET', 'MIC_strip_L_env', 'MIC_strip_R_env', 'PD_5807_env', 'PI5_F', 'PI5_F_cooler',
          'PIPWR_a_env', 'RESP_CARRIER', 'RESP_mic_env', 'RESP_pcb', 'RESP_top_env', 'RESP_usbc_plug_env', 'SENSOR_strip_L',
          'SENSOR_strip_R', 'SLAB_frame', 'SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'SPK_driver_D40', 'SPK_driver_D40 (1)',
          'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'TOUCH_PCB', 'USBA_cable_env', 'USBA_plug_env', 'VEML_env',
          'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'MAIN_C7_env', 'KO_C7_vent']
B = adsk.fusion.BooleanTypes


def tube(X, pts, dia):
    r = dia / 2.0; tb = None; L = 0.0
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        L += math.sqrt(sum((b[j] - a[j]) ** 2 for j in range(3)))
        c = X.tbm.createCylinderOrCone(Dw(XC + a[0], a[1], a[2]), r / 10, Dw(XC + b[0], b[1], b[2]), r / 10)
        tb = c if tb is None else X.union(tb, c)
        if i > 0:
            X.union(tb, X.tbm.createSphere(Dw(XC + a[0], a[1], a[2]), r / 10))
    return tb, round(L, 1)


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
        new = {}; grown = {}
        for nm, pts in ROUTES.items():
            new[nm], L = tube(X, pts, 3.0)
            grown[nm] = {g: tube(X, pts, 3.0 + 2 * g)[0] for g in (1.0, 2.0)}
            st.setdefault('len_mm', {})[nm] = L
            st.setdefault('cm3', {})[nm] = round(new[nm].volume, 4)
        st['mutual_mm3'] = vx(tbm, new['LEAD_BME680'], new['LEAD_VEML'])
        json.dump(st, open(OUT, 'w'), indent=1)
        for nm in ROUTES:
            rows = {}; g1 = []; g2 = []
            nb = new[nm].boundingBox
            for on in OTHERS:
                ob = X.body(on)
                if ob is None:
                    st['missing'].append(on); continue
                if gap(nb, ob.boundingBox) > 6.0:
                    continue
                v = vx(tbm, new[nm], ob)
                if on in DESIGNED[nm]:
                    rows[on] = [v, vx(tbm, X.body(nm), ob)]          # new, old (control)
                    continue
                if v > 0:
                    rows[on] = v
                if vx(tbm, grown[nm][2.0], ob) > 0:
                    g2.append(on)
                    if vx(tbm, grown[nm][1.0], ob) > 0:
                        g1.append(on)
            pr = {}
            for pn, (x0, x1, y0, y1, z0, z1) in PARTS.items():
                pb = X.wbox(XC + x0, XC + x1, y0, y1, z0, z1)
                pr[pn] = [vx(tbm, new[nm], pb), vx(tbm, grown[nm][1.0], pb) > 0, vx(tbm, grown[nm][2.0], pb) > 0]
            st.setdefault('leads', {})[nm] = {'hits_and_designed': rows, 'within_1': g1, 'within_2': g2, 'parts': pr}
            json.dump(st, open(OUT, 'w'), indent=1)
        # the old leads: what they touched (control for the inherited sensor-end contacts)
        for nm in ROUTES:
            ob_old = X.body(nm); rows = {}
            for on in OTHERS:
                o2 = X.body(on)
                if o2 is None or gap(ob_old.boundingBox, o2.boundingBox) > 0.5:
                    continue
                v = vx(tbm, ob_old, o2)
                if v > 0:
                    rows[on] = v
            st.setdefault('old_hits', {})[nm] = rows
        st['done'] = True
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    st['t_s'] = round(time.time() - t0, 1)
    json.dump(st, open(OUT, 'w'), indent=1)
    print(json.dumps({k: st.get(k) for k in ('t_s', 'done', 'guard_bad', 'missing', 'FAIL')}))


run(None)
