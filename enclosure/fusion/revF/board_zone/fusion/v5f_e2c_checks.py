# rev F e2c (2026-11-08): read-only checks of the main board rev 2 bodies (e2b) against every current body, next to the
#   same checks on the previous bodies (MAIN_*_e2): intersection volume (TemporaryBRep copies) and, where the volume is 0,
#   the minimum distance (measure manager), for every pair whose design boxes come within 1 mm. Partial results are written
#   after every pair to board_zone/e2c_checks.json (time box 270 s).
import os, traceback
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
OUT = os.path.expanduser('~/Documents/HA_panel_renders/board_zone/e2c_checks.json')
SUBJ = ['MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'MAIN_pcb_e2', 'MAIN_front_env_e2', 'MAIN_back_env_e2']
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
          'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'TOUCH_PCB', 'USBA_cable_env', 'USBA_plug_env', 'VEML_env']


def gap(a, b):
    d = [max(0.0, b.minPoint.x - a.maxPoint.x, a.minPoint.x - b.maxPoint.x),
         max(0.0, b.minPoint.y - a.maxPoint.y, a.minPoint.y - b.maxPoint.y),
         max(0.0, b.minPoint.z - a.maxPoint.z, a.minPoint.z - b.maxPoint.z)]
    return math.sqrt(sum(v * v for v in d)) * 10


def run(_context):
    st = {'t0': time.strftime('%H:%M:%S'), 'rows': [], 'missing': []}
    t0 = time.time()
    try:
        X = Ctx(); tbm = X.tbm; mm = X.app.measureManager
        subj = {k: X.body(k) for k in SUBJ}
        st['missing'] += [k for k, v in subj.items() if v is None]
        others = []
        for k in OTHERS:
            b = X.body(k)
            (others.append(b) if b is not None else st['missing'].append(k))
        for sk, sb in subj.items():
            if sb is None: continue
            for ob in others:
                if time.time() - t0 > 270:
                    st['timebox'] = [sk, ob.name]; raise StopIteration
                g = gap(sb.boundingBox, ob.boundingBox)
                if g >= 1.0: continue
                t1 = time.time()
                q = tbm.copy(sb); tbm.booleanOperation(q, tbm.copy(ob), adsk.fusion.BooleanTypes.IntersectionBooleanType)
                v = round(q.volume * 1000, 3)
                d = None; p1 = p2 = None
                if v == 0.0:
                    r = mm.measureMinimumDistance(sb, ob); d = round(r.value * 10, 3)
                    p1 = [round(r.positionOne.x * 10 - XC, 2), round(wy(r.positionOne), 2), round(wz(r.positionOne), 2)]
                st['rows'].append([sk, ob.name, v, d, p1, round(time.time() - t1, 2)])
                json.dump(st, open(OUT, 'w'))
        st['done'] = True
    except StopIteration:
        pass
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    st['t_s'] = round(time.time() - t0, 1)
    json.dump(st, open(OUT, 'w'))
    print(json.dumps({k: st.get(k) for k in ('t_s', 'done', 'missing', 'timebox', 'FAIL')}))


run(None)
