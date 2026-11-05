# rev F cap block c1g2 (2026-11-05): close-up renders (c1g's ledge_close came out empty: after the orthographic top view the
#   perspective close-up kept the old view extents). Orthographic cameras with explicit viewExtents (cm):
#   ledge_close  : +x rear corner without the cap (ledge, R0.8 edge, groove, steps, BL post), extents 4.5
#   explode_close: cap lifted 25 mm over the front shell, rear three-quarter view of the top, extents 11
#   joint_close  : assembled, +x side at the front joint (cap / front bar / slab), extents 3.5
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
OUT = os.path.expanduser('~/Documents/HA_panel_renders')
RUN = 2
EXT = ['HOUSING_F_front', 'HOUSING_F_door', 'GROMMET_usbc_F', 'SLAB_frame', 'LCD_glass']


def shoot(X, path, d, up, tgt, ext, w=1600, h=1200):
    vp = X.app.activeViewport; cam = vp.camera
    n = math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2); D = 500.0
    cam.cameraType = adsk.core.CameraTypes.OrthographicCameraType
    cam.isFitView = False
    cam.target = Dw(*tgt); cam.eye = Dw(tgt[0] + D * d[0] / n, tgt[1] + D * d[1] / n, tgt[2] + D * d[2] / n)
    cam.upVector = up; cam.isSmoothTransition = False
    cam.viewExtents = ext
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
        cu = tb_copy(X, 'HOUSING_F_cap'); mvw(X, cu, 0.0, 0.0, 25.0)
        cub = X.add(cu, 'RENDER_tmp_CAPUP'); tmp.append(cub); cub.appearance = X.body('HOUSING_F_cap').appearance
        show = lambda keep: [setattr(b, 'isLightBulbOn', b.name in keep) for b in X.comp.bRepBodies]
        f = lambda v: os.path.join(OUT, 'HA_v5f_c1_%s.png' % v)
        if RUN == 1:
            show(['HOUSING_F_front', 'HOUSING_F_door'])
            out['ledge_close'] = shoot(X, f('ledge_close'), (0.55, -0.75, 0.85), UP, (XC + 40.0, -40.0, 172.0), 4.5)
            show(EXT + ['RENDER_tmp_CAPUP'])
            out['explode_close'] = shoot(X, f('explode_close'), (0.6, -1.0, 0.8), UP, (XC, -36.0, 183.0), 11.0)
            show(EXT + ['HOUSING_F_cap'])
            out['joint_close'] = shoot(X, f('joint_close'), (1.0, -0.35, 0.45), UP, (XC + 70.0, -22.5, 176.0), 3.5)
        else:                       # run 2: ledge_close at extents 4.5 showed ≈ 10 mm only
            show(['HOUSING_F_front', 'HOUSING_F_door'])
            out['ledge_close'] = shoot(X, f('ledge_close'), (0.45, -0.8, 1.0), UP, (XC + 45.0, -40.0, 173.0), 7.0)
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
    log('v5f_c1g2_renders_close', 'renders', out)
    print(json.dumps(out))
