# rev F block 5k-2 (2026-11-05): two close-up renders for checkpoint 5 (B5k's "topgroove" shot fitted the whole housing because
# the camera had isFitView = True). Same temporary CLOTH body as B5k (recess volume minus sleeve opening, joint gap open),
# camera at a fixed distance (isFitView = False):
#   HA_v5f_b5_topgroove.png  (replaces B5k's) top groove + rail line + 3.2 hard band at the +x rear corner, 150 mm away
#   HA_v5f_b5_grommet.png    USB-C grommet flange on the door's cloth face, bottom of the back, 140 mm away
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
OUT = os.path.expanduser('~/Documents/HA_panel_renders')
ZC = 14.1


def shoot_at(X, path, d, up, tgt, dist, w=1600, h=1200):
    vp = X.app.activeViewport
    cam = vp.camera
    n = math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2)
    cam.cameraType = adsk.core.CameraTypes.PerspectiveCameraType
    cam.isFitView = False
    cam.target = Dw(*tgt); cam.eye = Dw(tgt[0] + dist * d[0] / n, tgt[1] + dist * d[1] / n, tgt[2] + dist * d[2] / n)
    cam.upVector = up; cam.isSmoothTransition = False
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
        lg = json.load(open(LOG))
        last = lambda s: [e for e in lg if e['script'] == s][-1]['data']
        exp = {'HOUSING_F_front': last('v5f_b5h_grooves')['cm3'][2], 'HOUSING_F_door': last('v5f_b5g_recess_feet')['door_cm3'][1],
               'GROMMET_usbc_F': last('v5f_b5i2_grommet_open')['cm3'][1]}
        for n, v in exp.items():
            b = X.body(n)
            if b is None or abs(b.volume - v) > 0.002:
                raise RuntimeError('guard: %s volume %s, expected %s' % (n, None if b is None else round(b.volume, 3), v))
        X.app.activeViewport.visualStyle = adsk.core.VisualStyles.ShadedWithVisibleEdgesOnlyVisualStyle
        grey = ap(X, ('Fabric (Grey)', 'Paint - Enamel Glossy (Black)', 'Plastic - Matte (Black)', 'Plastic - Glossy (Black)'))
        cl = tb_copy(X, 'TOOL_outer_skin_0p7'); inter(X, cl, X.wbox(-250, 250, -250, 250, -5.0, TOP_Z))
        X.diff(cl, slot_out(X)); X.diff(cl, tb_copy(X, 'TOOL_floor_off12'))
        X.diff(cl, X.wbox(-250, 250, -250, YJ_F, -5.0, 2.65))
        X.diff(cl, X.wbox(XC - 12.1, XC + 12.1, -95.0, -75.0, ZC - 7.2, ZC + 7.2))
        X.diff(cl, X.wbox(-250, 250, YJ_D, YJ_F, -5.0, 260))
        cloth = X.add(cl, 'RENDER_tmp_CLOTH'); tmp.append(cloth)
        if grey is not None:
            cloth.appearance = grey
        base = ['HOUSING_F_front', 'HOUSING_F_door', 'GROMMET_usbc_F', 'SLAB_frame', 'LCD_glass', 'RENDER_tmp_CLOTH']
        for b in X.comp.bRepBodies:
            b.isLightBulbOn = b.name in base
        out['topgroove'] = shoot_at(X, os.path.join(OUT, 'HA_v5f_b5_topgroove.png'), (0.8, -0.7, 0.35), UP, (XC + 72.0, -42.0, 172.0), 150.0)
        out['grommet'] = shoot_at(X, os.path.join(OUT, 'HA_v5f_b5_grommet.png'), (0.35, -1.0, 0.3), UP, (XC, -84.0, 14.0), 140.0)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    finally:
        for t in tmp:
            try: t.deleteMe()
            except Exception: pass
        for b in X.comp.bRepBodies:
            if b.name in vis0: b.isLightBulbOn = vis0[b.name]
        X.app.activeViewport.visualStyle = vs0
    out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('RENDER_tmp_')]
    log('v5f_b5k2_closeups', 'renders', out)
    print(json.dumps(out))
