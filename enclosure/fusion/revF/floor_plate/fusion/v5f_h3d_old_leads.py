# rev F h3d (2026-11-11): step 3, block 3 - read-only: the same pairs on the leads of version 49 (the _v49 backups), to tell what the
#   new routes changed from what was there before: distance, and the overlap where the distance is 0.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_h_lib.py'), encoding='utf-8').read())
PAIRS = [('LEAD_LCD_5V_v49', 'KO_K5_LR'), ('LEAD_LCD_5V_v49', 'KO_K5_UR'), ('LEAD_DSI_v49', 'KO_K5_LL'), ('LEAD_DSI_v49', 'PI5_F_cooler'), ('LEAD_DSI_v49', 'SPKBOX_L'),
         ('LEAD_DSI_v49', 'PI5_components_env'), ('LEAD_PIGTAIL_20V_v49', 'PI5_components_env'), ('LEAD_BME680_v49', 'HOUSING_F_front'),
         ('LEAD_BME680_v49', 'SPKBOX_R'), ('LEAD_BME680_v49', 'KO_K5_LR'), ('LEAD_GPIO_B_v49', 'KO_K7_fan'), ('LEAD_TOUCH_v49', 'HOUSING_F_front'),
         ('LEAD_RADAR_v49', 'KO_K5_LR'), ('LEAD_SPK_L_v49', 'SPKBOX_L'), ('LEAD_USB_RESP', 'KO_K5_LL'), ('LEAD_MIC_L', 'RESP_CARRIER')]


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        rows = {}
        for a, b in PAIRS:
            A = X.body(a); B_ = X.body(b)
            if A is None or B_ is None:
                rows[a + '~' + b] = 'missing'; continue
            d = X.app.measureManager.measureMinimumDistance(A, B_).value * 10.0
            e = [round(d, 2)]
            if d < 0.005:
                e.append(round(xvol(X, X.cp(A), tcopy(X, b)), 2))
            rows[a[5:] + '~' + b] = e
        st['rows'] = rows
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('h3d', st)


run(None)
