# rev F block 4o (2026-11-04): four lead routes corrected after B4n (old bodies renamed *_b4n, hidden).
#   MIC_R: ran over the carrier boss at the ReSpeaker hole (x_rel −35.11 ± 3) → descends at x_rel −30.0, then to U4.
#   RADAR: started inside the LD2410C cradle ring → starts 3.0 behind the board's back face (normal 59°) and drops to the lane
#          crossing.
#   USB_RESP: clipped the +x box's top-rear edge (z 76) → rises to z 80 behind the box before turning forward.
#   DSI: entered MAIN_front_env's front-bottom edge (y −33.4, z 35.8) → stays at z ≤ 33 behind y −32; LCD_pcb excluded (the
#        FPC end lies on the LCD PCB at the connector).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback

ENVX = ['MAIN_front_env']
LEADS = [
    ('MIC_R', 2.0, [(-21.0, -26.5, 171.6), (-21.0, -26.5, 166.5), (-28.0, -30.0, 135.0), (-30.0, -17.19, 129.4), (-30.0, -15.21, 120.1),
                    (-32.11, -13.66, 112.8)], ['KO_mic_R_back', 'MIC_strip_R_env', 'RESP_mic_env']),
    ('RADAR', 2.5, [(-68.6, -24.3, 127.5), (-62.0, -30.0, 118.0), (-58.0, -38.0, 106.0), (-37.0, -46.0, 97.0), (-37.0, -50.0, 86.0),
                    (-37.0, -53.6, 80.0)], ['LD2410C_env_F'] + ENVX),
    ('USB_RESP', 3.5, [(52.0, -53.5, 14.2), (56.0, -55.0, 20.0), (57.0, -54.5, 80.0), (62.0, -46.0, 84.0), (77.0, -32.0, 103.0),
                       (81.0, -25.0, 116.0), (78.5, -21.5, 122.1)], ['USBA_cable_env', 'RESP_usbc_plug_env']),
    ('DSI', 3.0, [(46.8, -2.76, 114.7), (49.5, -3.10, 114.6), (49.5, -13.3, 109.8), (44.0, -26.6, 104.9), (38.0, -32.0, 86.0),
                  (36.0, -28.0, 40.0), (34.0, -32.0, 33.0), (30.0, -40.0, 30.0), (14.0, -49.5, 30.0), (11.78, -49.55, 14.0)],
     ['LCD_DSI_conn_d9.3', 'LCD_components_env_d8.8', 'LCD_pcb_76x110', 'PI5_F_cooler']),
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
        for (nm, _d, _p, _e) in LEADS:
            if X.body('LEAD_%s_b4n' % nm) is not None:
                raise RuntimeError('LEAD_%s_b4n exists already' % nm)
        for (nm, _d, _p, _e) in LEADS:
            b = X.body('LEAD_' + nm); b.name = 'LEAD_%s_b4n' % nm; b.isLightBulbOn = False
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
        out['leads'] = res
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b4o_leads_fix', 'checks', out)
    print(json.dumps(out))
