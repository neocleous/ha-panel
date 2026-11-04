# rev F block 4n (2026-11-04): every lead routed as a tube along a polyline (hidden bodies LEAD_*), lengths and clearances.
#   World x_rel, y, z (mm). Tube Ø = bundle allowance. Ends sit on/in the connector envelopes they plug into (excluded per
#   lead). Leads ending at the main board stop at a nominal landing inside MAIN_front_env (B1 places the connectors).
#   Not modelled here: the Pi USB-C power cable (V11, Daniel's decision pending), the speaker leads inside the boxes (≈ 25),
#   D4a (Option B only).
#   DSI: 15-pin end assumed to enter the LCD connector from +x (STEP slot open on both long sides – check on the board);
#   the FPC (16 wide) runs edge-on through the 10-mm gap between the carrier (x_rel 45.4) and the boss opening (55.55).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback

ENVX = ['MAIN_front_env']
LEADS = [
    # name, Ø, points, excluded bodies
    ('GPIO_A', 5.0, [(-25.9, -5.0, 32.5), (-25.9, -5.5, 40.0), (-24.0, -30.0, 44.0), (-20.0, -45.0, 50.0)], ['GPIO_plugA_env'] + ENVX),
    ('GPIO_B', 3.5, [(10.95, -5.0, 32.5), (10.95, -5.5, 40.0), (6.0, -30.0, 44.0), (0.0, -45.0, 50.0)], ['GPIO_plugB_env'] + ENVX),
    ('LCD_5V', 3.0, [(32.85, -28.3, 135.2), (30.0, -34.0, 125.0), (28.0, -32.0, 90.0), (-20.0, -26.0, 60.0), (-30.0, -10.0, 42.0),
                     (-31.9, -5.0, 33.0)], ['GPIO_plugA_env', 'LCD_2x2_header_d15.4']),
    ('MIC_L', 2.0, [(21.0, -26.5, 171.6), (21.0, -26.5, 166.5), (36.0, -30.0, 135.0), (38.89, -17.19, 129.4), (38.89, -15.21, 120.1),
                    (38.89, -13.66, 112.8)], ['KO_mic_L_back', 'MIC_strip_L_env', 'RESP_mic_env']),
    ('MIC_R', 2.0, [(-21.0, -26.5, 171.6), (-21.0, -26.5, 166.5), (-30.0, -30.0, 135.0), (-32.11, -17.19, 129.4), (-32.11, -15.21, 120.1),
                    (-32.11, -13.66, 112.8)], ['KO_mic_R_back', 'MIC_strip_R_env', 'RESP_mic_env']),
    ('SPK_L', 3.2, [(62.0, -51.0, 30.0), (62.0, -53.5, 30.0), (55.0, -56.0, 33.0), (47.0, -56.5, 37.0), (40.0, -53.6, 40.0)], ['SPKBOX_L'] + ENVX),
    ('SPK_R', 3.2, [(-62.0, -51.0, 30.0), (-62.0, -53.5, 30.0), (-55.0, -56.0, 33.0), (-47.0, -56.5, 37.0), (-40.0, -53.6, 40.0)], ['SPKBOX_R'] + ENVX),
    ('RADAR', 2.5, [(-71.2, -22.8, 116.5), (-71.0, -24.0, 113.0), (-58.0, -38.0, 106.0), (-37.0, -46.0, 97.0), (-37.0, -50.0, 86.0),
                    (-37.0, -53.6, 80.0)], ['LD2410C_env_F'] + ENVX),
    ('TOUCH', 2.5, [(12.0, 2.0, 46.0), (12.0, 1.0, 52.0), (8.0, -20.0, 56.0), (4.0, -45.0, 60.0)], ['KO_touch_back', 'TOUCH_PCB'] + ENVX),
    ('VEML', 3.0, [(46.0, -36.0, 171.0), (44.0, -34.0, 150.0), (40.0, -35.0, 130.0), (40.0, -34.0, 95.0), (36.0, -15.0, 70.0),
                   (36.0, 0.5, 52.0), (36.0, 2.0, 46.0)], ['VEML_env', 'KO_touch_back', 'TOUCH_PCB']),
    ('BME680', 3.0, [(-72.05, -40.92, 83.45), (-60.0, -32.0, 94.0), (-50.0, -26.0, 96.0), (-38.0, -22.0, 92.0), (-38.0, -8.0, 60.0),
                     (-36.0, 0.5, 52.0), (-36.0, 2.0, 46.0)], ['BME680_env', 'KO_touch_back', 'TOUCH_PCB']),
    ('PIGTAIL_20V', 3.2, [(0.0, -64.77, 16.0), (0.0, -62.0, 22.0), (0.0, -58.5, 32.0), (0.0, -55.0, 37.5), (0.0, -53.6, 37.5)],
     ['PD_5807_env'] + ENVX),
    ('USB_RESP', 3.5, [(52.0, -53.5, 14.2), (56.0, -55.0, 20.0), (57.0, -54.5, 74.0), (62.0, -46.0, 82.0), (77.0, -32.0, 103.0),
                       (81.0, -25.0, 116.0), (78.5, -21.5, 122.1)], ['USBA_cable_env', 'RESP_usbc_plug_env']),
    ('DSI', 3.0, [(46.8, -2.76, 114.7), (49.5, -3.10, 114.6), (49.5, -13.3, 109.8), (44.0, -26.6, 104.9), (38.0, -32.0, 86.0),
                  (36.0, -28.0, 40.0), (30.0, -40.0, 30.0), (14.0, -49.5, 30.0), (11.78, -49.55, 14.0)], ['LCD_DSI_conn_d9.3', 'LCD_components_env_d8.8', 'PI5_F_cooler']),
]
OBST = ['HOUSING_F_front', 'HOUSING_F_door', 'SLAB_frame', 'SPKBOX_L', 'SPKBOX_R', 'PI5_F', 'PI5_F_cooler', 'KO_K7_fan', 'KO_K5_LL', 'KO_K5_LR',
        'KO_K5_UL', 'KO_K5_UR', 'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'MAIN_BRACKET', 'CRADLE_5807', 'PD_5807_env', 'RESP_CARRIER',
        'RESP_pcb', 'RESP_top_env', 'RESP_mic_env', 'RESP_usbc_plug_env', 'LD2410C_env_F', 'MIC_strip_L_env', 'MIC_strip_R_env',
        'KO_mic_L_back', 'KO_mic_R_back', 'VEML_env', 'BME680_env', 'TOUCH_PCB', 'KO_touch_back', 'GPIO_plugA_env', 'GPIO_plugB_env',
        'USBA_plug_env', 'USBA_cable_env']


def run(_context):
    X = Ctx(); out = {}
    B = adsk.fusion.BooleanTypes; tbm = X.tbm
    try:
        if X.body('LEAD_GPIO_A') is not None:
            raise RuntimeError('LEAD_* exist already')
        names = [b.name for b in X.comp.bRepBodies]
        obst = OBST + [n for n in names if n.startswith('LCD_')]
        ob = {n: X.body(n) for n in obst if X.body(n) is not None}
        res = {}
        for (nm, dia, pts, excl) in LEADS:
            r = dia / 2.0
            tb = None
            L = 0.0
            for i in range(len(pts) - 1):
                a, b = pts[i], pts[i + 1]
                L += math.sqrt(sum((b[k] - a[k]) ** 2 for k in range(3)))
                c = tbm.createCylinderOrCone(Dw(XC + a[0], a[1], a[2]), r / 10, Dw(XC + b[0], b[1], b[2]), r / 10)
                tb = c if tb is None else X.union(tb, c)
                if i > 0:
                    tb = X.union(tb, tbm.createSphere(Dw(XC + a[0], a[1], a[2]), r / 10))
            body = X.add(tb, 'LEAD_' + nm); body.isLightBulbOn = False
            lb = body.boundingBox
            hits = {}
            for on, o in ob.items():
                if on in excl:
                    continue
                obb = o.boundingBox
                if obb.maxPoint.x < lb.minPoint.x or obb.minPoint.x > lb.maxPoint.x or obb.maxPoint.y < lb.minPoint.y or \
                        obb.minPoint.y > lb.maxPoint.y or obb.maxPoint.z < lb.minPoint.z or obb.minPoint.z > lb.maxPoint.z:
                    continue
                q = tbm.copy(o)
                if on == 'PI5_F':
                    tbm.booleanOperation(q, tbm.createBox(adsk.core.OrientedBoundingBox3D.create(
                        P3((lb.minPoint.x + lb.maxPoint.x) / 2, (lb.minPoint.y + lb.maxPoint.y) / 2, (lb.minPoint.z + lb.maxPoint.z) / 2),
                        V3(1, 0, 0), V3(0, 1, 0), lb.maxPoint.x - lb.minPoint.x + 1, lb.maxPoint.y - lb.minPoint.y + 1,
                        lb.maxPoint.z - lb.minPoint.z + 1)), B.IntersectionBooleanType)
                tbm.booleanOperation(q, tbm.copy(tb), B.IntersectionBooleanType)
                v = round(q.volume * 1000, 2)
                if v > 0:
                    hits[on] = v
            res[nm] = {'L_mm': round(L, 1), 'dia': dia, 'hits_mm3': hits or 'all 0'}
            log('v5f_b4n_leads', 'lead', {nm: res[nm]})
        out['leads'] = res
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b4n_leads', 'checks', out)
    print(json.dumps(out))
