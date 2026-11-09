# rev F e5b (2026-11-09): read-only mesh export of the current bodies for routing the J10 sensor leads (V23b), from
#   "HA Panel v5 - tapered" version 40 without activating it. World mm with x_rel (as e1b), binary STL, surface tolerance
#   0.1, one file per body in ~/Documents/HA_panel_renders/e5/mesh/; files already there are skipped, so a timed-out run
#   is resumed by running it again. Progress and guard in e5/e5b_status.json (written after each body).
import adsk.core, adsk.fusion, json, math, os, struct, time, traceback
C = math.cos(math.radians(12.0)); S = math.sin(math.radians(12.0)); H = 143.3; XC = -2.55
OUT = os.path.expanduser('~/Documents/HA_panel_renders/e5')
GUARD = {'HOUSING_F_front': 235.9107, 'HOUSING_F_door': 47.2633, 'MAIN_BRACKET': 6.5563, 'RESP_CARRIER': 10.1214,
         'CRADLE_5807': 2.1898}
NAMES = ['HOUSING_F_front', 'HOUSING_F_cap', 'HOUSING_F_door', 'SLAB_frame', 'MAIN_BRACKET', 'SPKBOX_L', 'SPKBOX_R',
         'SPK_L', 'SPK_R', 'SPK_driver_D40', 'SPK_driver_D40 (1)', 'BME680_env', 'BME_HOOD', 'FOAM_bme_env',
         'FOAM_bme_top_env', 'VEML_env', 'LD2410C_env_F', 'MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'MAIN_C7_env',
         'KO_C7_vent', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR', 'KO_K7_fan', 'KO_capkey_BL', 'KO_capkey_BR',
         'KO_capkey_SL', 'KO_capkey_SR', 'KO_mic_L_back', 'KO_mic_R_back', 'MIC_strip_L_env', 'MIC_strip_R_env',
         'SENSOR_strip_L', 'SENSOR_strip_R', 'RESP_CARRIER', 'RESP_pcb', 'RESP_top_env', 'RESP_mic_env',
         'RESP_usbc_plug_env', 'CRADLE_5807', 'PD_5807_env', 'KO_5807_pigtail', 'PI5_F', 'PI5_F_cooler', 'PIPWR_a_env',
         'GPIO_plugA_env', 'GPIO_plugB_env', 'USBA_plug_env', 'USBA_cable_env', 'GROMMET_usbc_F', 'LCD_glass',
         'LCD_panel_body', 'LCD_pcb_76x110', 'LCD_components_env_d8.8', 'LCD_2x2_header_d15.4', 'LCD_DSI_conn_d9.3',
         'LCD_M2.5_standoff_d9.0', 'LCD_M2.5_standoff_d9.0 (1)', 'LCD_M2.5_standoff_d9.0 (2)', 'LCD_M2.5_standoff_d9.0 (3)',
         'LCD_Pi_standoff_d15.2', 'LCD_Pi_standoff_d15.2 (1)', 'LCD_Pi_standoff_d15.2 (2)', 'LCD_Pi_standoff_d15.2 (3)',
         'LCD_panelFPC_conn_d9.5', 'LCD_pins_d16.0', 'LCD_pogo_header_d14.1', 'LCD_touchFPC_conn_d9.3', 'TOUCH_PCB',
         'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'KO_touch_back', 'LEAD_BME680', 'LEAD_VEML', 'LEAD_DSI', 'LEAD_GPIO_A',
         'LEAD_GPIO_B', 'LEAD_LCD_5V', 'LEAD_MIC_L', 'LEAD_MIC_R', 'LEAD_PIGTAIL_20V', 'LEAD_PI_POWER', 'LEAD_RADAR',
         'LEAD_SPK_L', 'LEAD_SPK_R', 'LEAD_TOUCH', 'LEAD_USB_RESP', 'FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR']


def world_mesh(body, tol_mm):
    mc = body.meshManager.createMeshCalculator()
    mc.surfaceTolerance = tol_mm / 10.0
    try:
        mc.maxNormalDeviation = math.radians(15.0)
    except Exception:
        pass
    m = mc.calculate()
    c = m.nodeCoordinatesAsDouble
    P = [(c[i] * 10 - XC, (c[i + 1] * C - c[i + 2] * S) * 10, H + (c[i + 1] * S + c[i + 2] * C) * 10) for i in range(0, len(c), 3)]
    ix = m.nodeIndices
    return P, [(ix[t], ix[t + 1], ix[t + 2]) for t in range(0, len(ix), 3)]


def write_stl(path, P, T, name):
    buf = bytearray(84 + 50 * len(T))
    hdr = ('HA panel e5b %s world mm x_rel' % name).encode()[:80]
    buf[0:len(hdr)] = hdr
    struct.pack_into('<I', buf, 80, len(T))
    off = 84
    for (a, b_, c_) in T:
        pa, pb, pc = P[a], P[b_], P[c_]
        u = (pb[0] - pa[0], pb[1] - pa[1], pb[2] - pa[2]); v = (pc[0] - pa[0], pc[1] - pa[1], pc[2] - pa[2])
        n = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
        L = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2) or 1.0
        struct.pack_into('<12fH', buf, off, n[0] / L, n[1] / L, n[2] / L, pa[0], pa[1], pa[2], pb[0], pb[1], pb[2],
                         pc[0], pc[1], pc[2], 0)
        off += 50
    with open(path, 'wb') as f:
        f.write(buf)
    return len(T)


def run(_context):
    spath = os.path.join(OUT, 'e5b_status.json')
    st = json.load(open(spath)) if os.path.exists(spath) else {'done': [], 'missing': []}
    st['t0'] = time.strftime('%H:%M:%S'); st.pop('timebox', None); st.pop('FAIL', None)
    t0 = time.time()
    try:
        os.makedirs(os.path.join(OUT, 'mesh'), exist_ok=True)
        app = adsk.core.Application.get()
        doc = [d for d in app.documents if d.name == 'HA Panel v5 - tapered'][0]
        des = adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
        root = des.rootComponent
        byname = {}
        for i in range(root.bRepBodies.count):
            b = root.bRepBodies.item(i)
            byname.setdefault(b.name, b)
        bad = [k for k, v in GUARD.items() if k not in byname or abs(byname[k].volume - v) > 0.0005]
        if doc.isModified:
            bad.append('document modified')
        st['guard_bad'] = bad
        if bad:
            raise RuntimeError('GUARD %s' % bad)
        for nm in NAMES:
            safe = ''.join(ch if (ch.isalnum() or ch in '_.-') else '_' for ch in nm)
            path = os.path.join(OUT, 'mesh', safe + '.stl')
            if os.path.exists(path):
                continue
            if time.time() - t0 > 200:
                st['timebox'] = nm; break
            b = byname.get(nm)
            if b is None:
                if nm not in st['missing']:
                    st['missing'].append(nm)
                continue
            t1 = time.time()
            P, T = world_mesh(b, 0.1)
            n = write_stl(path, P, T, safe)
            st['done'].append([nm, safe, n, round(b.volume, 4), b.isLightBulbOn, round(time.time() - t1, 1)])
            json.dump(st, open(spath, 'w'))
        st['t_s'] = round(time.time() - t0, 1)
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    json.dump(st, open(spath, 'w'))
    print(json.dumps({k: st.get(k) for k in ('t_s', 'guard_bad', 'missing', 'timebox', 'FAIL')}))


run(None)
