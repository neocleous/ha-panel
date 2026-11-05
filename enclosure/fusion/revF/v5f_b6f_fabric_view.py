# rev F block 6f (2026-11-05): the fabric on the model (Daniel 12:51 "I want to see the model with the fabric on").
#   The cloth of B6r (0.7 recess, B5k definition with the inlet at z 20.6, seam (b) wrap: front cloth in front of A + 0.9 u
#   plus the 0.7 layer on F, door cloth behind A + 1.2 u plus the layer on D → 0.3 cloth-to-cloth gap) as two visible,
#   non-printed bodies: RENDER_FABRIC_front (front belt) and RENDER_FABRIC_door (door panel), appearance 'Fabric (Grey)'
#   (decision 3 a, dark grey). The RENDER_ prefix keeps them out of the interference filters and the printed-part list.
#   Not saved as a version: they stay in the open document until Daniel saves or discards.
#   Pictures of the r2 state with the fabric → ~/Documents/HA_panel_renders/HA_v5f_r2_fabric_{front34,side,rear34,under,
#   seam}.png (1600 × 1200) + _check.jpg; viewport left on the front-3/4 view, other bodies' visibility as before.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
OUT = os.path.expanduser('~/Documents/HA_panel_renders')
SEAM = os.path.expanduser('~/Documents/v5f_seam_I.json')
EXPECT = {'HOUSING_F_front': 240.8876, 'HOUSING_F_door': 51.101}
ZC = 20.6
NAMES = ('RENDER_FABRIC_front', 'RENDER_FABRIC_door')
EXT = ['HOUSING_F_front', 'HOUSING_F_door', 'GROMMET_usbc_F', 'SLAB_frame', 'LCD_glass'] + list(NAMES)
FEET = ['FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR']


def vsub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def vadd(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def vmul(a, k): return (a[0] * k, a[1] * k, a[2] * k)
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def unit(a):
    l = math.sqrt(dot(a, a)); return (a[0] / l, a[1] / l, a[2] / l)
def dist(a, b): return math.sqrt(dot(vsub(a, b), vsub(a, b)))


def load_stations(min_gap=2.0):                 # as B6s-3b / B6r
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


def set_cam(X, d, up, tgt, ortho=False, fit=True, dist_mm=600.0):
    vp = X.app.activeViewport
    cam = vp.camera
    n = math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2)
    cam.cameraType = adsk.core.CameraTypes.OrthographicCameraType if ortho else adsk.core.CameraTypes.PerspectiveCameraType
    cam.target = Dw(*tgt)
    cam.eye = Dw(tgt[0] + dist_mm * d[0] / n, tgt[1] + dist_mm * d[1] / n, tgt[2] + dist_mm * d[2] / n)
    cam.upVector = up; cam.isSmoothTransition = False
    cam.isFitView = fit
    vp.camera = cam
    vp.refresh()
    return vp


def shoot(X, path, d, up, tgt, ortho=False, fit=True, dist_mm=600.0):
    vp = set_cam(X, d, up, tgt, ortho, fit, dist_mm)
    ok = vp.saveAsImageFile(path, 1600, 1200)
    vp.saveAsImageFile(path.replace('.png', '_check.jpg'), 480, 360)
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
    t0 = time.time()
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.002:
                raise RuntimeError('guard: %s volume %s, expected %s' % (k, None if b is None else round(b.volume, 4), v))
        if any(X.body(n) is not None for n in NAMES):
            raise RuntimeError('fabric bodies exist already')
        if not os.path.isdir(OUT):
            os.makedirs(OUT)
        grey = ap(X, ('Fabric (Grey)', 'Plastic - Matte (Black)'))
        out['appearance'] = grey.name if grey else None
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
        bf = X.add(cf, NAMES[0]); bd = X.add(cd, NAMES[1])
        for b in (bf, bd):
            if grey is not None:
                b.appearance = grey
        bf = X.body(NAMES[0]); bd = X.body(NAMES[1])
        out['fabric_cm3_lumps'] = {'front': [round(bf.volume, 3), bf.lumps.count], 'door': [round(bd.volume, 3), bd.lumps.count]}
        out['fabric_x_parts_mm3'] = {'front_x_front': vol_x(X, bf, X.body('HOUSING_F_front')), 'door_x_door': vol_x(X, bd, X.body('HOUSING_F_door')),
                                     'front_x_door': vol_x(X, bf, X.body('HOUSING_F_door')), 'door_x_front': vol_x(X, bd, X.body('HOUSING_F_front')),
                                     'front_x_doorcloth': vol_x(X, bf, bd), 'door_x_grommet': vol_x(X, bd, X.body('GROMMET_usbc_F'))}
        X.app.activeViewport.visualStyle = adsk.core.VisualStyles.ShadedWithVisibleEdgesOnlyVisualStyle
        show = lambda keep: [setattr(b, 'isLightBulbOn', b.name in keep) for b in X.comp.bRepBodies]
        f = lambda v: os.path.join(OUT, 'HA_v5f_r2_fabric_%s.png' % v)
        show(EXT)
        out['front34'] = shoot(X, f('front34'), (0.6, 1.0, 0.35), UP, tgt=(XC, -20.0, 90.0))
        out['side'] = shoot(X, f('side'), (1.0, 0.0, 0.0), UP, tgt=(XC, -35.0, 90.0), ortho=True)
        out['rear34'] = shoot(X, f('rear34'), (0.65, -1.0, 0.55), UP, tgt=(XC, -45.0, 90.0))
        hs = ray_hits(X, (XC, -58.0, 95.0), (1, 0, 0), NAMES)
        tg = (XC + hs[-1][2], hs[-1][3], hs[-1][4]) if hs else (XC + 80.0, -58.0, 95.0)
        out['seam_target'] = [round(tg[0] - XC, 1), round(tg[1], 1), round(tg[2], 1)]
        out['seam'] = shoot(X, f('seam'), (1.0, -0.45, 0.3), UP, tgt=tg, fit=False, dist_mm=150.0)
        show(EXT + FEET)
        out['under'] = shoot(X, f('under'), (0.0, -0.05, -1.0), WY, tgt=(XC, -38.0, 0.0), ortho=True)
        out['files'] = sorted(f_ for f_ in os.listdir(OUT) if f_.startswith('HA_v5f_r2_fabric_'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    finally:
        for b in X.comp.bRepBodies:
            if b.name in vis0:
                b.isLightBulbOn = vis0[b.name]
        for n in NAMES:
            b = X.body(n)
            if b is not None:
                b.isLightBulbOn = True
        X.app.activeViewport.visualStyle = vs0
        try:
            set_cam(X, (0.6, 1.0, 0.35), UP, (XC, -20.0, 90.0))
        except Exception:
            pass
    out['visible'] = sorted(b.name for b in X.comp.bRepBodies if b.isLightBulbOn)
    out['t_s'] = round(time.time() - t0, 1)
    log('v5f_b6f_fabric_view', 'fabric', out)
    print(json.dumps(out, separators=(',', ':')))
