# rev F f1d (2026-11-10): floor plate pass, block 1 (concept, second round) - read-only first fit check for Daniel's
#   question 3: the main board behind the display on a carrier with four posts (the LCD's Pi standoffs carry the
#   ReSpeaker carrier). Board parallel to the LCD PCB, parts toward the door, same way up, centred between the LCD-screw
#   lanes (x_rel 2.55). Part boxes from hardware/main-board (rev 2.1: KiCad positions, MAIN_env heights), built as
#   TemporaryBRep boxes in the design frame and intersected with every current body (nominal and grown 1.5 mm).
#   Poses: A z_c -24.5 (posts just clear of the ReSpeaker as it sits), B z_c -28.5 (ReSpeaker 4 mm lower: its bodies are
#   left out of pose B). Writes ~/Documents/HA_panel_renders/fp/f1d_fit.json. Loader per README lesson 86; readOnly.
import adsk.core, adsk.fusion, json, math, os, time, traceback
C = math.cos(math.radians(12.0)); S = math.sin(math.radians(12.0)); H = 143.3; XC = -2.55
OUT = os.path.expanduser('~/Documents/HA_panel_renders/fp')
YPCB = -7.4                      # LCD PCB back face (design Y, mm)
XCB = 2.55                       # board centre, x_rel
DB = 24.6                        # board back face behind the LCD PCB back face
YB = YPCB - DB                   # board back face (toward the LCD)
YF = YB - 1.6                    # board component face (toward the door)
SKIP = ('MAIN_pcb', 'MAIN_front_env', 'MAIN_back_env', 'MAIN_C7_env', 'KO_C7_vent', 'MAIN_BRACKET', 'LEAD_GPIO_A',
        'LEAD_GPIO_B', 'LEAD_LCD_5V', 'LEAD_SPK_L', 'LEAD_SPK_R', 'LEAD_RADAR', 'LEAD_TOUCH', 'LEAD_VEML', 'LEAD_BME680',
        'LEAD_PIGTAIL_20V', 'LEAD_PI_POWER', 'KO_5807_pigtail')
CUR = ['HOUSING_F_front', 'HOUSING_F_door', 'HOUSING_F_cap', 'SLAB_frame', 'RESP_CARRIER', 'RESP_pcb', 'RESP_top_env',
       'RESP_mic_env', 'RESP_usbc_plug_env', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR', 'KO_capkey_BL', 'KO_capkey_BR',
       'KO_capkey_SL', 'KO_capkey_SR', 'MIC_strip_L_env', 'MIC_strip_R_env', 'KO_mic_L_back', 'KO_mic_R_back', 'VEML_env',
       'LD2410C_env_F', 'BME_HOOD', 'BME680_env', 'FOAM_bme_env', 'FOAM_bme_top_env', 'SPKBOX_L', 'SPKBOX_R', 'PI5_F',
       'PI5_F_cooler', 'KO_K7_fan', 'TOUCH_PCB', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'CRADLE_5807', 'PD_5807_env',
       'GPIO_plugA_env', 'GPIO_plugB_env', 'LEAD_MIC_L', 'LEAD_MIC_R', 'LEAD_USB_RESP', 'LEAD_DSI', 'USBA_plug_env',
       'USBA_cable_env', 'PIPWR_a_env']
RESP = ('RESP_pcb', 'RESP_top_env', 'RESP_mic_env', 'RESP_usbc_plug_env', 'LEAD_USB_RESP', 'LEAD_MIC_L', 'LEAD_MIC_R')
# part: (kx0, kx1, ky0, ky1, d0, d1) - KiCad board coordinates, depth from the component face toward the door (+) or
# from the back face toward the LCD (negative values = behind the component face: -1.6 = back face)
PARTS = {
    'pcb': (0.0, 90.0, -5.0, 50.0, -1.6, 0.0),
    'back_joints_2p9': (2.0, 88.0, -3.0, 48.0, -4.5, -1.6),
    'front_low_6p5': (0.0, 88.0, -5.0, 50.0, 0.0, 6.5),
    'NID100_27p5': (9.75, 61.05, 0.75, 13.25, 0.0, 27.5),
    'C5_16': (22.8, 32.8, 27.5, 37.5, 0.0, 16.0),
    'C6_16': (10.5, 20.5, 14.0, 24.0, 0.0, 16.0),
    'C7_vent_15p5': (47.9, 53.5, -4.84, 0.74, 0.0, 15.5),
    'J1_plug_lead_19p8': (40.8, 49.2, 41.9, 48.7, 0.0, 19.8),
    'J5_plug_lead_19p8': (69.0, 82.4, 0.6, 7.4, 0.0, 19.8),
    'J6_plug_lead_19p8': (34.3, 47.7, 20.6, 27.4, 0.0, 19.8),
    'J8_plug_lead_19p8': (8.1, 14.9, 39.8, 48.2, 0.0, 19.8),
    'J9_plug_lead_19p8': (73.8, 82.2, 40.6, 47.4, 0.0, 19.8),
    'J10_header_16p5': (61.65, 67.74, 0.92, 12.08, 0.0, 16.5),
    'J2_usbc_plug': (13.8, 26.2, 50.0, 70.0, -6.73, -0.23),
}
HOLES = [(3.5, 3.5), (86.5, 3.5), (3.5, 46.5), (86.5, 46.5)]
POSES = {'A_zc-24.5': (-24.5, ()), 'B_zc-28.5_resp_lower': (-28.5, RESP)}


def P(xr, y, z):
    return adsk.core.Point3D.create((xr + XC) / 10.0, y / 10.0, z / 10.0)


def box(tbm, x0, x1, y0, y1, z0, z1):
    obb = adsk.core.OrientedBoundingBox3D.create(P((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2),
                                                 adsk.core.Vector3D.create(1, 0, 0), adsk.core.Vector3D.create(0, 1, 0),
                                                 (x1 - x0) / 10.0, (y1 - y0) / 10.0, (z1 - z0) / 10.0)
    return tbm.createBox(obb)


def part_box(tbm, zc, spec, g=0.0):
    kx0, kx1, ky0, ky1, d0, d1 = spec
    return box(tbm, XCB - 45.0 + kx0 - g, XCB - 45.0 + kx1 + g, YF - d1 - g, YF - d0 + g, zc + 22.5 - ky1 - g, zc + 22.5 - ky0 + g)


def run(_context):
    st = {'t0': time.strftime('%Y-%m-%d %H:%M:%S'), 'missing': []}
    t0 = time.time()
    res = {'YB': YB, 'YF': YF, 'poses': {}}
    try:
        app = adsk.core.Application.get()
        doc = [d for d in app.documents if d.name == 'HA Panel v5 - tapered'][0]
        des = adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
        root = des.rootComponent
        tbm = adsk.fusion.TemporaryBRepManager.get()
        byname = {}
        for b in root.bRepBodies:
            byname.setdefault(b.name, b)
        bodies = []
        for n in CUR + sorted(k for k in byname if k.startswith('LCD_')):
            b = byname.get(n)
            if b is None:
                st['missing'].append(n); continue
            bb = b.boundingBox
            bodies.append((n, b, (bb.minPoint.x, bb.maxPoint.x, bb.minPoint.y, bb.maxPoint.y, bb.minPoint.z, bb.maxPoint.z)))

        def clash(tool, body):
            t = tbm.copy(body)
            try:
                tbm.booleanOperation(t, tool, adsk.fusion.BooleanTypes.IntersectionBooleanType)
            except Exception:
                return 0.0
            try:
                return t.volume * 1000.0
            except Exception:
                return 0.0

        for pn, (zc, leave) in POSES.items():
            rows = []
            tools = {}
            for k, spec in PARTS.items():
                tools[k] = (part_box(tbm, zc, spec), part_box(tbm, zc, spec, 1.5))
            for i, (kx, ky) in enumerate(HOLES):
                xr = XCB - 45.0 + kx; zd = zc + 22.5 - ky
                for g, slot in ((0.0, 0), (1.5, 1)):
                    cyl = tbm.createCylinderOrCone(P(xr, YPCB - 9.8, zd), (3.5 + g) / 10.0, P(xr, YB, zd), (3.5 + g) / 10.0)
                    tools.setdefault('post%d_d7' % i, [None, None])[slot] = cyl
            for k, (tn, tg) in tools.items():
                gb = tg.boundingBox
                g6 = (gb.minPoint.x, gb.maxPoint.x, gb.minPoint.y, gb.maxPoint.y, gb.minPoint.z, gb.maxPoint.z)
                for n, b, bb in bodies:
                    if n in leave:
                        continue
                    if bb[1] < g6[0] or bb[0] > g6[1] or bb[3] < g6[2] or bb[2] > g6[3] or bb[5] < g6[4] or bb[4] > g6[5]:
                        continue
                    vg = clash(tg, b)
                    if vg <= 0.0005:
                        continue
                    vn = clash(tn, b)
                    rows.append([k, n, round(vn, 2), round(vg, 2)])
            res['poses'][pn] = {'zc': zc, 'rows': rows}
            st[pn] = round(time.time() - t0, 1)
            json.dump(st, open(os.path.join(OUT, 'f1d_status.json'), 'w'))
        json.dump(res, open(os.path.join(OUT, 'f1d_fit.json'), 'w'), separators=(',', ':'))
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-4:]
    st['t_end'] = round(time.time() - t0, 1)
    json.dump(st, open(os.path.join(OUT, 'f1d_status.json'), 'w'))
    print(json.dumps(st))


run(None)
