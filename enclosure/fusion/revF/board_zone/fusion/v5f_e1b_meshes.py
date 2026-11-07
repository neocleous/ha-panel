# rev F e1b (2026-11-07): main board outline question - read-only mesh export of the bodies around the main board from
#   "HA Panel v5 - tapered" without activating it. World mm with x_rel (as pa_world_mesh), binary STL, one file per body in
#   ~/Documents/HA_panel_renders/board_zone/mesh/. Progress and guard in board_zone/e1b_status.json (written after each body).
import adsk.core, adsk.fusion, json, math, os, struct, time, traceback
C = math.cos(math.radians(12.0)); S = math.sin(math.radians(12.0)); H = 143.3; XC = -2.55
OUT = os.path.expanduser('~/Documents/HA_panel_renders/board_zone')
GUARD = {'HOUSING_F_front': 235.9107, 'HOUSING_F_door': 47.2633, 'MAIN_BRACKET': 6.5563, 'SPKBOX_L': 25.6082,
         'SPKBOX_R': 26.3874, 'CRADLE_5807': 2.1775, 'GROMMET_usbc_F': 0.5062, 'RESP_CARRIER': 10.0716, 'BME_HOOD': 0.8029}
PRINTED = ['HOUSING_F_door', 'MAIN_BRACKET', 'SPKBOX_L', 'SPKBOX_R', 'CRADLE_5807', 'GROMMET_usbc_F', 'RESP_CARRIER',
           'BME_HOOD', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R']
COMP = ['PI5_F', 'PI5_F_cooler', 'KO_K7_fan', 'GPIO_plugA_env', 'GPIO_plugB_env', 'USBA_plug_env', 'USBA_cable_env',
        'PIPWR_a_env', 'LEAD_PI_POWER', 'PD_5807_env', 'KO_5807_pigtail', 'LEAD_PIGTAIL_20V', 'SPK_L', 'SPK_R', 'TOUCH_PCB',
        'KO_touch_back', 'RESP_pcb', 'RESP_top_env', 'RESP_mic_env', 'RESP_usbc_plug_env', 'BME680_env', 'FOAM_bme_env',
        'FOAM_bme_top_env', 'LD2410C_env_F', 'LCD_pcb_76x110', 'LCD_components_env_d8.8', 'KO_K5_LL', 'KO_K5_LR',
        'KO_K5_UL', 'KO_K5_UR', 'KO_capkey_BL', 'KO_capkey_BR', 'KO_capkey_SL', 'KO_capkey_SR', 'MAIN_pcb',
        'MAIN_front_env', 'MAIN_back_env', 'LEAD_GPIO_A', 'LEAD_GPIO_B', 'LEAD_LCD_5V', 'LEAD_SPK_L', 'LEAD_SPK_R',
        'LEAD_TOUCH', 'LEAD_RADAR', 'LEAD_USB_RESP', 'LEAD_DSI', 'LEAD_VEML', 'LEAD_BME680']
EXTRA = globals().get('E1B_EXTRA') or []          # optional extra names (set by the loader), e.g. the front


def world_mesh(body, tol_mm):
    mc = body.meshManager.createMeshCalculator()
    mc.surfaceTolerance = tol_mm / 10.0
    try:
        mc.maxNormalDeviation = math.radians(10.0)
    except Exception:
        pass
    m = mc.calculate()
    c = m.nodeCoordinatesAsDouble
    P = [(c[i] * 10 - XC, (c[i + 1] * C - c[i + 2] * S) * 10, H + (c[i + 1] * S + c[i + 2] * C) * 10) for i in range(0, len(c), 3)]
    ix = m.nodeIndices
    return P, [(ix[t], ix[t + 1], ix[t + 2]) for t in range(0, len(ix), 3)]


def write_stl(path, P, T, name):
    buf = bytearray(84 + 50 * len(T))
    hdr = ('HA panel e1b %s world mm x_rel' % name).encode()[:80]
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
    st = {'t0': time.strftime('%H:%M:%S'), 'done': [], 'missing': []}
    spath = os.path.join(OUT, 'e1b_status.json')
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
        for nm in PRINTED + COMP + list(EXTRA):
            if time.time() - t0 > 240:
                st['timebox'] = nm; break
            b = byname.get(nm)
            if b is None:
                st['missing'].append(nm); continue
            t1 = time.time()
            tol = 0.02 if nm in PRINTED or nm.startswith('HOUSING') else 0.05
            P, T = world_mesh(b, tol)
            safe = ''.join(ch if (ch.isalnum() or ch in '_.-') else '_' for ch in nm)
            n = write_stl(os.path.join(OUT, 'mesh', safe + '.stl'), P, T, safe)
            st['done'].append([nm, safe, n, round(b.volume, 4), b.isLightBulbOn, round(time.time() - t1, 1)])
            json.dump(st, open(spath, 'w'))
        st['t_s'] = round(time.time() - t0, 1)
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    json.dump(st, open(spath, 'w'))
    print(json.dumps({k: st.get(k) for k in ('t_s', 'guard_bad', 'missing', 'timebox', 'FAIL')}))


run(None)
