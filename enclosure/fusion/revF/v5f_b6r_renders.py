# rev F block 6r (2026-11-05): final renders (brief 6.4) → ~/Documents/HA_v5f_final_{front34,side,rear34,under,under_open,
#   interior}.png (1600 × 1200) + _check.jpg (480 × 360) + _tiny.jpg (240 × 180).
#   Temporary bodies (deleted at the end): RENDER_tmp_CLOTH = the 0.7 recess (B5k definition, inlet at z 20.6) with the
#   seam (b) wrap: front cloth in front of A + 0.9 u plus the 0.7 layer on F (A + 0.2 u … 0.9 u, s −0.7…2.5), door cloth
#   behind A + 1.2 u plus the layer on D (A + 1.2 u … 1.9 u) → 0.3 cloth-to-cloth gap; RENDER_tmp_DOOR (door + grommet +
#   door cloth pulled back 70 mm) for under_open.
#   front34 / rear34 / under / side: closed unit (side orthographic from +x = viewer's left); under_open: door off (pulled
#   back 70 mm, its normal removal direction), from behind below; interior: door and cloth hidden, from behind above.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
OUT = os.path.expanduser('~/Documents')
SEAM = os.path.expanduser('~/Documents/v5f_seam_I.json')
EXPECT = {'HOUSING_F_front': 239.797, 'HOUSING_F_door': 50.601}
ZC = 20.6
EXT = ['HOUSING_F_front', 'HOUSING_F_door', 'GROMMET_usbc_F', 'SLAB_frame', 'LCD_glass', 'RENDER_tmp_CLOTH']
FEET = ['FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR']
INT = ['SLAB_frame', 'LCD_glass', 'LCD_panel_body', 'LCD_pcb_76x110', 'PI5_F', 'PI5_F_cooler', 'SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R',
       'TOUCH_PCB', 'MAIN_BRACKET', 'MAIN_pcb', 'RESP_CARRIER', 'RESP_pcb', 'CRADLE_5807', 'PD_5807_env', 'LD2410C_env_F', 'BME680_env',
       'VEML_env', 'MIC_strip_L_env', 'MIC_strip_R_env', 'GPIO_plugA_env', 'GPIO_plugB_env', 'LEAD_GPIO_A', 'LEAD_GPIO_B', 'LEAD_LCD_5V',
       'LEAD_MIC_L', 'LEAD_MIC_R', 'LEAD_SPK_L', 'LEAD_SPK_R', 'LEAD_TOUCH', 'LEAD_VEML', 'LEAD_BME680', 'LEAD_RADAR', 'LEAD_USB_RESP',
       'LEAD_DSI', 'LEAD_PIGTAIL_20V', 'LEAD_PI_POWER']


def vsub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def vadd(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def vmul(a, k): return (a[0] * k, a[1] * k, a[2] * k)
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def unit(a):
    l = math.sqrt(dot(a, a)); return (a[0] / l, a[1] / l, a[2] / l)
def dist(a, b): return math.sqrt(dot(vsub(a, b), vsub(a, b)))


def load_stations(min_gap=2.0):                 # as B6s-3b
    raw = json.load(open(SEAM))['raw']
    for s in raw:
        for k in ('P', 'n', 'A'):
            s[k] = tuple(s[k])
    st = [raw[0]]
    for s in raw[1:-1]:
        if dist(s['P'], st[-1]['P']) >= min_gap:
            st.append(s)
    if dist(raw[-1]['P'], st[-1]['P']) < 1.0:
        st.pop()
    st.append(raw[-1])
    for k, s in enumerate(st):
        a = st[max(k - 1, 0)]['P']; b = st[min(k + 1, len(st) - 1)]['P']
        t = unit(vsub(b, a)); n = s['n']
        u = unit(cross(t, n))
        if u[1] > 0:
            u = vmul(u, -1.0)
        tp = unit(cross(n, u))
        if dot(tp, t) < 0:
            tp = vmul(tp, -1.0)
        s['u'] = u; s['t'] = tp
        s['a'] = 8.0 if k == 0 else dist(s['P'], st[k - 1]['P']) / 2 + 0.4
        s['b'] = 8.0 if k == len(st) - 1 else dist(s['P'], st[k + 1]['P']) / 2 + 0.4
        s['odd'] = k % 2
    return st


def half_box(X, O, s):
    u, t, n = s['u'], s['t'], s['n']
    L, s0, s1 = (21.0, -3.9, 5.4) if s['odd'] else (20.0, -3.5, 5.0)
    c = vadd(vadd(vadd(O, vmul(u, -L / 2)), vmul(t, (s['b'] - s['a']) / 2)), vmul(n, (s0 + s1) / 2))
    return X.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(Dw(XC + c[0], c[1], c[2]), wv(u), wv(t),
                                                                  L / 10, (s['a'] + s['b']) / 10, (s1 - s0) / 10))


def union_all(X, bs):
    while len(bs) > 1:
        nb = []
        for i in range(0, len(bs) - 1, 2):
            X.tbm.booleanOperation(bs[i], bs[i + 1], B.UnionBooleanType); nb.append(bs[i])
        if len(bs) % 2:
            nb.append(bs[-1])
        bs = nb
    return bs[0]


def shoot(X, path, d, up, tgt, w=1600, h=1200, ortho=False):
    vp = X.app.activeViewport
    cam = vp.camera
    n = math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2)
    cam.cameraType = adsk.core.CameraTypes.OrthographicCameraType if ortho else adsk.core.CameraTypes.PerspectiveCameraType
    cam.target = Dw(*tgt); cam.eye = Dw(tgt[0] + 600 * d[0] / n, tgt[1] + 600 * d[1] / n, tgt[2] + 600 * d[2] / n)
    cam.upVector = up; cam.isSmoothTransition = False
    cam.isFitView = True
    vp.camera = cam
    vp.refresh()
    ok = vp.saveAsImageFile(path, w, h)
    vp.saveAsImageFile(path.replace('.png', '_check.jpg'), 480, 360)
    vp.saveAsImageFile(path.replace('.png', '_tiny.jpg'), 240, 180)
    return ok


def ap(X, names):
    try:
        for i in range(X.app.materialLibraries.count):
            lib = X.app.materialLibraries.item(i)
            if 'Appearance' not in lib.name:
                continue
            for nm in names:
                a = lib.appearances.itemByName(nm)
                if a:
                    return X.des.appearances.itemByName(nm) or X.des.appearances.addByCopy(a, nm)
    except Exception:
        return None


def run(_context):
    X = Ctx(); out = {}
    vis0 = {b.name: b.isLightBulbOn for b in X.comp.bRepBodies}
    vs0 = X.app.activeViewport.visualStyle
    tmp = []
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.002:
                raise RuntimeError('guard: %s volume %s, expected %s' % (k, None if b is None else round(b.volume, 3), v))
        X.app.activeViewport.visualStyle = adsk.core.VisualStyles.ShadedWithVisibleEdgesOnlyVisualStyle
        grey = ap(X, ('Fabric (Grey)', 'Paint - Enamel Glossy (Black)', 'Plastic - Matte (Black)', 'Plastic - Glossy (Black)'))
        st = load_stations()
        R09 = union_all(X, [half_box(X, vadd(s['A'], vmul(s['u'], 0.9)), s) for s in st])
        R12 = union_all(X, [half_box(X, vadd(s['A'], vmul(s['u'], 1.2)), s) for s in st])
        RF = tb_copy(X, 'TOOL_seam_RF'); RD = tb_copy(X, 'TOOL_seam_RD')
        cl = tb_copy(X, 'TOOL_outer_skin_0p7'); inter(X, cl, X.wbox(-250, 250, -250, 250, -5.0, TOP_Z))
        X.diff(cl, slot_out(X)); X.diff(cl, tb_copy(X, 'TOOL_floor_off12'))
        X.diff(cl, X.wbox(-250, 250, -250, YJ_F, -5.0, 2.65))
        X.diff(cl, X.wbox(XC - 12.1, XC + 12.1, -95.0, -75.0, ZC - 7.2, ZC + 7.2))
        LJ = X.wbox(-250, 250, -66.0, -48.0, 2.5, 260)
        wx = tb_copy(X, 'REF_F_outer'); inter(X, wx, X.tbm.copy(LJ))
        ie = inter(X, tb_copy(X, 'INNER_E'), X.wbox(-250, 250, -68.0, -46.0, 0, 260))
        X.diff(ie, inter(X, tb_copy(X, 'TOOL_inner_skin_0p7'), X.wbox(-250, 250, -68.0, -46.0, 0, 260)))
        X.diff(wx, ie)                                                    # wall + cloth layer, s −0.7…2.5, near the joint
        fs09 = X.wbox(-250, 250, -52.0, 250, -20, 260); X.union(fs09, X.tbm.copy(R09))
        fs12 = X.wbox(-250, 250, -52.0, 250, -20, 260); X.union(fs12, X.tbm.copy(R12))
        cf = X.tbm.copy(cl); inter(X, cf, fs09)
        wf = X.tbm.copy(wx); inter(X, wf, X.tbm.copy(R09)); X.diff(wf, X.tbm.copy(RF)); X.union(cf, wf)
        cd = X.tbm.copy(cl); X.diff(cd, fs12)
        wd = X.tbm.copy(wx); inter(X, wd, X.tbm.copy(RD)); X.diff(wd, X.tbm.copy(R12)); X.union(cd, wd)
        cdq = X.tbm.copy(cd)
        X.union(cf, cd)
        cloth = X.add(cf, 'RENDER_tmp_CLOTH'); tmp.append(cloth)
        if grey is not None:
            cloth.appearance = grey
        out['cloth_cm3'] = round(cloth.volume, 3)
        dm = tb_copy(X, 'HOUSING_F_door'); X.union(dm, tb_copy(X, 'GROMMET_usbc_F')); mvw(X, dm, 0.0, -70.0, 0.0)
        mvw(X, cdq, 0.0, -70.0, 0.0)
        dmb = X.add(dm, 'RENDER_tmp_DOOR'); tmp.append(dmb)
        dcb = X.add(cdq, 'RENDER_tmp_DOORCLOTH'); tmp.append(dcb)
        try:
            dmb.appearance = X.body('HOUSING_F_door').appearance
        except Exception:
            pass
        if grey is not None:
            dcb.appearance = grey
        show = lambda keep: [setattr(b, 'isLightBulbOn', b.name in keep) for b in X.comp.bRepBodies]
        f = lambda v: os.path.join(OUT, 'HA_v5f_final_%s.png' % v)
        show(EXT)
        out['front34'] = shoot(X, f('front34'), (0.6, 1.0, 0.35), UP, tgt=(XC, -20.0, 90.0))
        out['side'] = shoot(X, f('side'), (1.0, 0.0, 0.0), UP, tgt=(XC, -35.0, 90.0), ortho=True)
        out['rear34'] = shoot(X, f('rear34'), (0.65, -1.0, 0.55), UP, tgt=(XC, -45.0, 90.0))
        show(EXT + FEET)
        out['under'] = shoot(X, f('under'), (0.0, -0.05, -1.0), WY, tgt=(XC, -38.0, 0.0), ortho=True)
        # cloth on the front part only for the open views
        front_cloth = X.tbm.copy(cl); inter(X, front_cloth, X.tbm.copy(fs09)); X.union(front_cloth, X.tbm.copy(wf))
        fcb = X.add(front_cloth, 'RENDER_tmp_FRONTCLOTH'); tmp.append(fcb)
        if grey is not None:
            fcb.appearance = grey
        show(['HOUSING_F_front', 'RENDER_tmp_FRONTCLOTH', 'RENDER_tmp_DOOR', 'RENDER_tmp_DOORCLOTH'] + INT + FEET)
        out['under_open'] = shoot(X, f('under_open'), (0.6, -1.0, -0.35), UP, tgt=(XC, -75.0, 45.0))
        show(['HOUSING_F_front'] + INT)
        out['interior'] = shoot(X, f('interior'), (0.35, -1.0, 0.9), UP, tgt=(XC, -40.0, 70.0))
        out['missing'] = [n for n in INT + EXT + FEET if X.body(n) is None]
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    finally:
        for t in tmp:
            try:
                t.deleteMe()
            except Exception:
                pass
        for b in X.comp.bRepBodies:
            if b.name in vis0:
                b.isLightBulbOn = vis0[b.name]
        X.app.activeViewport.visualStyle = vs0
    out['files'] = sorted(f_ for f_ in os.listdir(OUT) if f_.startswith('HA_v5f_final_'))
    out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('RENDER_tmp_')]
    log('v5f_b6r_renders', 'renders', out)
    print(json.dumps(out))
