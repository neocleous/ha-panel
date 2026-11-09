# rev F e5d (2026-11-09): V23b commit - the BME680 and VEML6030 leads to main-board J10 as checked by e5c. Old leads
#   renamed LEAD_BME680_e5 / LEAD_VEML_e5 (hidden); the new D3 tubes added as LEAD_BME680 / LEAD_VEML (hidden, like the
#   old), appearance copied. Then the exact minimum distance (measure manager) from each new lead to every current body
#   whose box comes within 10 mm. Not saved here (e5e saves). Writes e5/e5d_status.json.
import os, traceback
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
OUT = os.path.expanduser('~/Documents/HA_panel_renders/e5/e5d_status.json')
GUARD = {'HOUSING_F_front': 235.9107, 'HOUSING_F_door': 47.2633, 'MAIN_BRACKET': 6.5563, 'RESP_CARRIER': 10.1214,
         'CRADLE_5807': 2.1898, 'LEAD_BME680': 0.7753, 'LEAD_VEML': 1.1381}
NEW_CM3 = {'LEAD_BME680': 0.6381, 'LEAD_VEML': 0.8101}          # e5c
ROUTES = {
    'LEAD_BME680': [(-71.841, -40.737, 93.534), (-72.752, -41.517, 85.625), (-66.557, -36.212, 84.387),
                    (-43.25, -35.75, 96.75), (-18.42, -50.0, 77.5), (-18.42, -63.4, 77.5)],
    'LEAD_VEML': [(0.0, -39.7, 175.75), (0.0, -39.7, 165.0), (-20.97, -50.0, 77.5), (-20.97, -63.4, 77.5)]}
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


def run(_context):
    st = {'t0': time.strftime('%H:%M:%S')}
    t0 = time.time()
    try:
        X = Ctx()
        st['version'] = [X.doc.dataFile.versionNumber, X.doc.isModified]
        bad = [[k, None if X.body(k) is None else round(X.body(k).volume, 4)] for k, v in GUARD.items()
               if X.body(k) is None or abs(X.body(k).volume - v) > 0.0005]
        for n in ('LEAD_BME680_e5', 'LEAD_VEML_e5'):
            if X.body(n) is not None:
                bad.append(n + ' exists')
        st['guard_bad'] = bad
        if bad:
            raise RuntimeError('GUARD %s' % bad)
        built = {}
        for nm, pts in ROUTES.items():
            tb, L = tube(X, pts, 3.0)
            if abs(tb.volume - NEW_CM3[nm]) > 0.0005:
                raise RuntimeError('%s rebuilt %.4f != e5c %.4f' % (nm, tb.volume, NEW_CM3[nm]))
            built[nm] = (tb, L)
        for nm, (tb, L) in built.items():
            old = X.body(nm); app = old.appearance; mat = old.material
            old.name = nm + '_e5'; old.isLightBulbOn = False
            nb = X.add(tb, nm); nb.isLightBulbOn = False
            try:
                nb.material = mat
            except Exception:
                pass
            try:
                nb.appearance = app
            except Exception:
                pass
            st.setdefault('added', {})[nm] = {'cm3': round(nb.volume, 4), 'lumps': nb.lumps.count, 'len_mm': L,
                                              'old_cm3': round(X.body(nm + '_e5').volume, 4)}
        json.dump(st, open(OUT, 'w'), indent=1)
        mm = X.app.measureManager
        for nm in ROUTES:
            nb = X.body(nm); rows = []
            for on in OTHERS + [n for n in ROUTES if n != nm]:
                ob = X.body(on)
                if ob is None or gap(nb.boundingBox, ob.boundingBox) > 10.0:
                    continue
                r = mm.measureMinimumDistance(nb, ob)
                p = r.positionOne
                rows.append([round(r.value * 10, 3), on, [round(p.x * 10 - XC, 2), round(wy(p), 2), round(wz(p), 2)]])
            st.setdefault('min_dist', {})[nm] = sorted(rows)
            json.dump(st, open(OUT, 'w'), indent=1)
        st['modified'] = X.doc.isModified
        st['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
        st['done'] = True
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    st['t_s'] = round(time.time() - t0, 1)
    json.dump(st, open(OUT, 'w'), indent=1)
    log('v5f_e5d_leads', 'run', {k: st.get(k) for k in ('added', 'guard_bad', 'FAIL', 't_s')})
    print(json.dumps({k: st.get(k) for k in ('t_s', 'done', 'guard_bad', 'added', 'FAIL')}))


run(None)
