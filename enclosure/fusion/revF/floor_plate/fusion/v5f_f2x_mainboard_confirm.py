# rev F f2x (2026-11-10): floor plate pass, block 2 - read-only confirmation of the main board behind the display
#   (Daniel 14:22: 2 a). Pose: centre x_rel 2.55, Zd -28.5, back face 23.7 behind the LCD PCB (0.5 over the ReSpeaker's
#   6.83 J2); ReSpeaker 4 mm lower, modelled by its real zones (E0 envelopes) instead of the uniform envelope; posts d7;
#   clearances graded with grown copies. Derived from f1d. Part boxes from hardware/main-board (rev 2.1 KiCad positions,
#   MAIN_env heights), TemporaryBRep boxes in the design frame against every current body.
#   Writes ~/Documents/HA_panel_renders/fp/f2x_fit.json. Loader per README lesson 86; readOnly.
import adsk.core, adsk.fusion, json, math, os, time, traceback
C = math.cos(math.radians(12.0)); S = math.sin(math.radians(12.0)); H = 143.3; XC = -2.55
OUT = os.path.expanduser('~/Documents/HA_panel_renders/fp')
YPCB = -7.4                      # LCD PCB back face (design Y, mm)
XCB = 2.55                       # board centre, x_rel
DB = 23.7                        # board back face behind the LCD PCB back face
YB = YPCB - DB                   # board back face (toward the LCD)
YF = YB - 1.6                    # board component face (toward the door)
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
    'back_NID_2p9': (9.75, 61.05, 0.75, 13.25, -4.5, -1.6),
    'back_C5_2p9': (22.8, 32.8, 27.5, 37.5, -4.5, -1.6),
    'back_C6_2p9': (10.5, 20.5, 14.0, 24.0, -4.5, -1.6),
    'back_C7_2p9': (47.9, 53.5, -4.84, 0.74, -4.5, -1.6),
    'back_J1_2p9': (40.8, 49.2, 41.9, 48.7, -4.5, -1.6),
    'back_J5_2p9': (69.0, 82.4, 0.6, 7.4, -4.5, -1.6),
    'back_J6_2p9': (34.3, 47.7, 20.6, 27.4, -4.5, -1.6),
    'back_J8_2p9': (8.1, 14.9, 39.8, 48.2, -4.5, -1.6),
    'back_J9_2p9': (73.8, 82.2, 40.6, 47.4, -4.5, -1.6),
    'back_J10_2p9': (61.65, 67.74, 0.92, 12.08, -4.5, -1.6),
    'back_J3_2p9': (53.4, 65.6, 34.0, 38.5, -4.5, -1.6),
    'back_J4_2p9': (44.0, 48.6, 34.0, 38.5, -4.5, -1.6),
    'back_J7_2p9': (53.1, 72.9, 41.0, 43.0, -4.5, -1.6),
    'back_LK1_2p9': (26.2, 35.8, 45.3, 47.3, -4.5, -1.6),
    'back_J2_body_3p46': (13.8, 26.2, 39.0, 50.0, -5.06, -1.6),
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
POSES = {'zc-28.5': (-28.5, RESP + ('RESP_CARRIER',))}
GROW = (0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0)
M = -4.0                         # ReSpeaker moved along the slab (design Z)
# ReSpeaker zones (x_rel0, x_rel1, depth0, depth1, Zd0, Zd1) from the board frame: x_rel = -37.6 + X, Zd = -44 + Y
RZ = {'RESP_pcb': (-37.6, 44.42, 22.2, 23.71, -44.0, -9.99), 'RESP_mic_side_3p0': (-37.6, 44.42, 19.2, 22.2, -44.0, -9.99),
      'RESP_low_2p3': (-37.6, 44.42, 23.71, 26.01, -44.0, -9.99), 'RESP_J2_6p83': (36.34, 43.34, 23.71, 30.54, -30.96, -23.01),
      'RESP_jack_5p44': (31.4, 46.0, 23.71, 29.15, -41.82, -33.17), 'RESP_usbc_3p4': (37.88, 45.28, 23.71, 27.11, -20.71, -11.77),
      'RESP_usbc_plug': (45.28, 77.28, 22.11, 28.71, -22.44, -10.04)}


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

        extra = []
        for n, (x0, x1, d0, d1, z0, z1) in RZ.items():
            tb = box(tbm, x0, x1, -d1, -d0, z0 + M, z1 + M)
            bb = tb.boundingBox
            extra.append(('moved:' + n, tb, (bb.minPoint.x, bb.maxPoint.x, bb.minPoint.y, bb.maxPoint.y, bb.minPoint.z, bb.maxPoint.z)))
        bodies = bodies + extra
        for pn, (zc, leave) in POSES.items():
            rows = []

            def mk(k, g):
                if k.startswith('post'):
                    kx, ky = HOLES[int(k[4])]
                    xr = XCB - 45.0 + kx; zd = zc + 22.5 - ky
                    return tbm.createCylinderOrCone(P(xr, YPCB - 9.8, zd), (3.5 + g) / 10.0, P(xr, YB, zd), (3.5 + g) / 10.0)
                if k.startswith('thru'):                       # the post's footprint through the wall: must pass the LCD opening
                    kx, ky = HOLES[int(k[4])]
                    xr = XCB - 45.0 + kx; zd = zc + 22.5 - ky
                    return tbm.createCylinderOrCone(P(xr, YPCB - 0.5, zd), (3.5 + g) / 10.0, P(xr, YPCB - 9.8, zd), (3.5 + g) / 10.0)
                return part_box(tbm, zc, PARTS[k], g)
            keys = list(PARTS) + ['post%d' % i for i in range(4)] + ['thru%d' % i for i in range(4)]
            for k in keys:
                tg = mk(k, GROW[-1]); gb = tg.boundingBox
                g6 = (gb.minPoint.x, gb.maxPoint.x, gb.minPoint.y, gb.maxPoint.y, gb.minPoint.z, gb.maxPoint.z)
                for n, b, bb in bodies:
                    if n in leave:
                        continue
                    if bb[1] < g6[0] or bb[0] > g6[1] or bb[3] < g6[2] or bb[2] > g6[3] or bb[5] < g6[4] or bb[4] > g6[5]:
                        continue
                    if clash(tg, b) <= 0.0005:
                        continue
                    vn = clash(mk(k, 0.0), b)
                    first = None
                    if vn <= 0.0005:
                        for g in GROW:
                            if clash(mk(k, g), b) > 0.0005:
                                first = g; break
                    rows.append([k, n, round(vn, 2), first])
            res['poses'][pn] = {'zc': zc, 'rows': rows}
            st[pn] = round(time.time() - t0, 1)
            json.dump(st, open(os.path.join(OUT, 'f2x_status.json'), 'w'))
        json.dump(res, open(os.path.join(OUT, 'f2x_fit.json'), 'w'), separators=(',', ':'))
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-4:]
    st['t_end'] = round(time.time() - t0, 1)
    json.dump(st, open(os.path.join(OUT, 'f2x_status.json'), 'w'))
    print(json.dumps(st))


run(None)
