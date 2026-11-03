# rev F block 1g (2026-11-03): checkpoint-1 renders ~/Documents/HA_v5f_b1_{front34,rear34,under,under_open}.png.
# under_open: TemporaryBRep copies of the door assembly (DOOR_F, PI5_F, cooler, GPIO plug envelopes, feet) dropped 70 mm
# (the >= 50 mm cable slack of K11) are added as RENDER_tmp_* bodies, the originals hidden, and everything restored after.
# Run with MODE = 'outside' (front34, rear34, under) or MODE = 'open' (under_open).
# --- paste v5f_common.py above this line ---
MODE = 'outside'
SHOW = ['HOUSING_E', 'SLAB_frame', 'LCD_glass', 'DOOR_F', 'FOOT_FL', 'FOOT_FR', 'FOOT_ML', 'FOOT_MR', 'FOOT_RL', 'FOOT_RR']
DOOR_ASM = ['DOOR_F', 'PI5_F', 'PI5_F_cooler', 'GPIO_plugA_env', 'GPIO_plugB_env', 'FOOT_FL', 'FOOT_FR', 'FOOT_ML', 'FOOT_MR', 'FOOT_RL', 'FOOT_RR']


def wvec(dx, dy, dz):                     # world direction -> design vector
    return V3(dx, dy * C + dz * S, -dy * S + dz * C)


def shoot(X, path, d, up, w=1600, h=1200, ortho=False):
    vp = X.app.activeViewport
    cam = vp.camera
    tgt = Dw(XC, -35.0, 70.0)
    n = math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2)
    eye = Dw(XC + 600 * d[0] / n, -35.0 + 600 * d[1] / n, 70.0 + 600 * d[2] / n)
    cam.cameraType = adsk.core.CameraTypes.OrthographicCameraType if ortho else adsk.core.CameraTypes.PerspectiveCameraType
    cam.target = tgt; cam.eye = eye; cam.upVector = up; cam.isSmoothTransition = False
    cam.isFitView = True
    vp.camera = cam
    vp.refresh()
    ok = vp.saveAsImageFile(path, w, h)
    small = path.replace('.png', '_check.jpg')     # small JPEG for the remote check (keeps transfer small)
    vp.saveAsImageFile(small, 320, 240)
    return ok


def run(_context):
    X = Ctx()
    docs = os.path.expanduser('~/Documents')
    vis0 = {b.name: b.isLightBulbOn for b in X.comp.bRepBodies}
    out = {}
    try:
        X.app.activeViewport.visualStyle = adsk.core.VisualStyles.ShadedWithVisibleEdgesOnlyVisualStyle
        if MODE == 'outside':
            for b in X.comp.bRepBodies:
                b.isLightBulbOn = b.name in SHOW
            out['front34'] = shoot(X, os.path.join(docs, 'HA_v5f_b1_front34.png'), (0.55, 0.85, 0.35), UP)
            out['rear34'] = shoot(X, os.path.join(docs, 'HA_v5f_b1_rear34.png'), (-0.55, -0.85, 0.35), UP)
            out['under'] = shoot(X, os.path.join(docs, 'HA_v5f_b1_under.png'), (0.0, 0.0, -1.0), WY, ortho=True)
        else:
            tmp = []
            mv = adsk.core.Matrix3D.create(); mv.translation = wvec(0, 0, -7.0)    # -70 mm world z (cm)
            for nm in DOOR_ASM:
                b = X.body(nm)
                tb = X.tbm.copy(b); X.tbm.transform(tb, mv)
                tmp.append(X.add(tb, 'RENDER_tmp_' + nm))
            for b in X.comp.bRepBodies:
                b.isLightBulbOn = (b.name in ('HOUSING_E', 'SLAB_frame', 'LCD_glass')) or b.name.startswith('RENDER_tmp_')
            out['under_open'] = shoot(X, os.path.join(docs, 'HA_v5f_b1_under_open.png'), (0.75, 0.55, -0.45), UP)
            for t in tmp:
                t.deleteMe()
    finally:
        for b in X.comp.bRepBodies:
            if b.name in vis0:
                b.isLightBulbOn = vis0[b.name]
    out['files'] = {f: os.path.getsize(os.path.join(docs, f)) for f in os.listdir(docs) if f.startswith('HA_v5f_b1_') and '_check' not in f}
    log('v5f_b1g_renders', MODE, out)
    print(json.dumps(out))
