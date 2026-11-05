# rev F cap block c2f2 (2026-11-05): re-shoot c2f's orthographic views. In c2f the first orthographic shot after a
#   perspective one came out at the wrong scale (top, cap_underside: a few mm of the lux port filled the frame) – the extents
#   were set before the camera type change had been applied (this also explains c1g2's first ledge_close; lesson 54 amended).
#   Now the camera is applied twice: type / eye / target / up first, then viewExtents on the re-read camera.
#   Shots: top (assembled), cap_underside, pads_top (front shell, no cap, nearly plan view of the back), inside_back /
#   inside_lanes (cut at y −27, from inside / below), all orthographic.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
OUT = os.path.expanduser('~/Documents/HA_panel_renders')
EXT = ['HOUSING_F_front', 'HOUSING_F_door', 'GROMMET_usbc_F', 'SLAB_frame', 'LCD_glass']
LANES = ['KO_capkey_BL', 'KO_capkey_BR', 'KO_capkey_SL', 'KO_capkey_SR']


def shoot(X, path, d, up, tgt, ext, w=1600, h=1200):
    vp = X.app.activeViewport
    n = math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2); D = 500.0
    cam = vp.camera
    cam.cameraType = adsk.core.CameraTypes.OrthographicCameraType
    cam.isFitView = False; cam.isSmoothTransition = False
    cam.target = Dw(*tgt); cam.eye = Dw(tgt[0] + D * d[0] / n, tgt[1] + D * d[1] / n, tgt[2] + D * d[2] / n)
    cam.upVector = up
    vp.camera = cam
    cam = vp.camera
    cam.isSmoothTransition = False; cam.viewExtents = ext
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
        X.app.activeViewport.visualStyle = adsk.core.VisualStyles.ShadedWithVisibleEdgesOnlyVisualStyle
        app_f, app_c = X.body('HOUSING_F_front').appearance, X.body('HOUSING_F_cap').appearance

        def add(tb, name, app):
            b = X.add(tb, name); tmp.append(b)
            if app is not None:
                b.appearance = app
            return b
        box = lambda: X.wbox(XC - 90.0, XC + 90.0, -75.0, -27.0, 150.0, 182.0)
        fc = tb_copy(X, 'HOUSING_F_front'); inter(X, fc, box()); add(fc, 'RENDER_tmp_FRONTCUT', app_f)
        cc = tb_copy(X, 'HOUSING_F_cap'); inter(X, cc, box()); add(cc, 'RENDER_tmp_CAPCUT', app_c)
        for k in LANES:
            lc = tb_copy(X, k); inter(X, lc, box()); add(lc, 'RENDER_tmp_' + k, None)
        show = lambda keep: [setattr(b, 'isLightBulbOn', b.name in keep) for b in X.comp.bRepBodies]
        f = lambda v: os.path.join(OUT, 'HA_v5f_c2_%s.png' % v)
        show(EXT + ['HOUSING_F_cap'])
        out['top'] = shoot(X, f('top'), (0.0, -0.001, 1.0), WY, (XC, -32.0, 180.0), 17.0)
        show(['HOUSING_F_cap'])
        out['cap_underside'] = shoot(X, f('cap_underside'), (0.35, -0.45, -1.0), WY, (XC, -34.0, 177.0), 17.0)
        show(['HOUSING_F_front', 'HOUSING_F_door'])
        out['pads_top'] = shoot(X, f('pads_top'), (0.15, -0.35, 1.0), WY, (XC, -38.0, 172.0), 15.0)
        show(['RENDER_tmp_FRONTCUT', 'RENDER_tmp_CAPCUT'])
        out['inside_back'] = shoot(X, f('inside_back'), (0.45, 1.0, -0.45), UP, (XC, -40.0, 169.0), 12.0)
        show(['RENDER_tmp_FRONTCUT', 'RENDER_tmp_CAPCUT'] + ['RENDER_tmp_' + k for k in LANES])
        out['inside_lanes'] = shoot(X, f('inside_lanes'), (0.45, 1.0, -0.45), UP, (XC, -40.0, 169.0), 12.0)
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
    out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('RENDER_tmp_')]
    log('v5f_c2f2_renders_ortho', 'renders', out)
    print(json.dumps(out))
