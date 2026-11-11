# rev F h3a (2026-11-11): step 3, block 3 - read-only: world boxes (x_rel, y, z from the vertices) of the parts the leads start and end
#   at or pass, and the end points of the present lead bodies' circular edges nearest their device ends.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_h_lib.py'), encoding='utf-8').read())
NAMES = ['GPIO_plugA_env', 'GPIO_plugB_env', 'PIPWR_a_env', 'KO_K7_fan', 'PI5_F_cooler', 'PI5_F', 'USBA_plug_env', 'USBA_cable_env', 'CRADLE_5807', 'PD_5807_env',
         'KO_5807_pigtail', 'SPKBOX_L', 'SPKBOX_R', 'TOUCH_PCB', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'KO_touch_back', 'BME680_env', 'BME_HOOD', 'LD2410C_env_F',
         'VEML_env', 'MIC_strip_L_env', 'MIC_strip_R_env', 'RESP_usbc_plug_env', 'LCD_DSI_conn_d9.3', 'LCD_2x2_header_d15.4', 'MAIN_J2_plug_env', 'FLOOR_PLATE',
         'HOUSING_F_cap', 'GROMMET_usbc_F', 'DRV_screw_heads_env', 'SPK_L', 'SPK_R']


def wbb(b):
    xs = []; ys = []; zs = []
    for v in b.vertices:
        q = W(v.geometry); xs.append(q[0]); ys.append(q[1]); zs.append(q[2])
    return [round(min(xs), 1), round(max(xs), 1), round(min(ys), 1), round(max(ys), 1), round(min(zs), 1), round(max(zs), 1)]


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        st['box'] = {n: wbb(X.body(n)) for n in NAMES if X.body(n) is not None}
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('h3a', st)


run(None)
