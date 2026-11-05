# rev F cap block c1g (2026-11-05): step-1 checkpoint renders → ~/Documents/HA_panel_renders/HA_v5f_c1_*.png (1600 × 1200).
#   explode_rear34 / explode_side: cap lifted 35 mm (temporary copy, deleted after); assembled_rear34: joint line + heads;
#   top: orthographic top view; ledge_close: +x rear corner without the cap, 150 mm away (ledge, R0.8 edge, groove, lip zone,
#   BL post); post_close: BL post from inside (front shell cut at x_rel 10 by a temporary copy, deleted after).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
OUT = os.path.expanduser('~/Documents/HA_panel_renders')
EXT = ['HOUSING_F_front', 'HOUSING_F_door', 'GROMMET_usbc_F', 'SLAB_frame', 'LCD_glass']


def shoot(X, path, d, up, tgt, dist=None, ortho=False, w=1600, h=1200):
    vp = X.app.activeViewport; cam = vp.camera
    n = math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2); D = dist or 600.0
    cam.cameraType = adsk.core.CameraTypes.OrthographicCameraType if ortho else adsk.core.CameraTypes.PerspectiveCameraType
    cam.isFitView = dist is None
    cam.target = Dw(*tgt); cam.eye = Dw(tgt[0] + D * d[0] / n, tgt[1] + D * d[1] / n, tgt[2] + D * d[2] / n)
    cam.upVector = up; cam.isSmoothTransition = False
    if dist is None:
        cam.isFitView = True
    vp.camera = cam; vp.refresh()
    ok = vp.saveAsImageFile(path, w, h)
    vp.saveAsImageFile(path.replace('.png', '_tiny.jpg'), 240, 180)
    return ok


def run(_context):
    X = Ctx(); out = {}
    vis0 = {b.name: b.isLightBulbOn for b in X.comp.bRepBodies}
    vs0 = X.app.activeViewport.visualStyle
    tmp = []
    try:
        os.makedirs(OUT, exist_ok=True)
        X.app.activeViewport.visualStyle = adsk.core.VisualStyles.ShadedWithVisibleEdgesOnlyVisualStyle
        cu = tb_copy(X, 'HOUSING_F_cap'); mvw(X, cu, 0.0, 0.0, 35.0)
        cub = X.add(cu, 'RENDER_tmp_CAPUP'); tmp.append(cub); cub.appearance = X.body('HOUSING_F_cap').appearance
        fc = tb_copy(X, 'HOUSING_F_front'); X.diff(fc, X.wbox(XC - 250, XC + 10.0, -250, 250, -10, 260))
        fcb = X.add(fc, 'RENDER_tmp_FRONTCUT'); tmp.append(fcb); fcb.appearance = X.body('HOUSING_F_front').appearance
        show = lambda keep: [setattr(b, 'isLightBulbOn', b.name in keep) for b in X.comp.bRepBodies]
        f = lambda v: os.path.join(OUT, 'HA_v5f_c1_%s.png' % v)
        show(EXT + ['RENDER_tmp_CAPUP'])
        out['explode_rear34'] = shoot(X, f('explode_rear34'), (0.65, -1.0, 0.75), UP, (XC, -35.0, 150.0))
        out['explode_side'] = shoot(X, f('explode_side'), (1.0, -0.15, 0.25), UP, (XC, -35.0, 150.0))
        show(EXT + ['HOUSING_F_cap'])
        out['assembled_rear34'] = shoot(X, f('assembled_rear34'), (0.65, -1.0, 0.75), UP, (XC, -35.0, 150.0))
        out['top'] = shoot(X, f('top'), (0.0, -0.001, 1.0), WY, (XC, -30.0, 180.0), ortho=True)
        show(['HOUSING_F_front', 'HOUSING_F_door'])
        out['ledge_close'] = shoot(X, f('ledge_close'), (0.55, -0.75, 0.85), UP, (XC + 40.0, -40.0, 172.0), dist=150.0)
        show(['RENDER_tmp_FRONTCUT'])
        out['post_close'] = shoot(X, f('post_close'), (-0.9, 0.35, 0.45), UP, (XC + 28.0, -40.0, 168.0), dist=130.0)
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
    out['files'] = sorted(f_ for f_ in os.listdir(OUT) if f_.startswith('HA_v5f_c1_'))
    out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('RENDER_tmp_')]
    log('v5f_c1g_renders', 'renders', out)
    print(json.dumps(out))
