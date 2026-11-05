# rev F block 5k (2026-11-05): checkpoint-5 renders + named version + f3d (MODE per run).
# Renders (1600 × 1200 + 480 × 360 check JPEGs) into ~/Documents/HA_panel_renders/ with a temporary CLOTH body (= the 0.7
# recess volume, i.e. exactly where the cloth lies, minus the grommet sleeve opening) in dark grey:
#   HA_v5f_b5_rear34.png    closed housing from the rear-left above: door panel, joint, grommet, back seam band, top groove
#   HA_v5f_b5_front34.png   from the front-right below the slab: chin band, under-slab groove line, front corners
#   HA_v5f_b5_under.png     underside (ortho): 6 mm cloth strip, hard floor, hard rim behind the joint, feet
#   HA_v5f_b5_lap.png       door and cloth hidden, from behind: the lip (s −0.9…−2.1), root band, pads with pockets
#   HA_v5f_b5_topgroove.png close-up of the top groove + hard band at the +x rear corner
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
MODE = 'save'          # run 1 (2026-11-05): 'renders'; run 2: 'save'
OUT = os.path.expanduser('~/Documents/HA_panel_renders')
VERSION = ('rev F WIP 2026-11-05 b5: D1 inner layer + 0.7 fabric recess, lip and magnets at D1, top groove + rail, '
           'under-slab groove, USB-C grommet, feet clear of the strip (Claude)')
F3D = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-wip-b5.f3d')
ZC = 14.1


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
    X = Ctx(); out = {'mode': MODE}
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
        out['expect'] = exp
        if MODE == 'renders':
            os.makedirs(OUT, exist_ok=True)
            X.app.activeViewport.visualStyle = adsk.core.VisualStyles.ShadedWithVisibleEdgesOnlyVisualStyle
            grey = ap(X, ('Fabric (Grey)', 'Paint - Enamel Glossy (Black)', 'Plastic - Matte (Black)', 'Plastic - Glossy (Black)'))
            red = ap(X, ('Paint - Enamel Glossy (Red)', 'Plastic - Glossy (Red)'))
            cl = tb_copy(X, 'TOOL_outer_skin_0p7'); inter(X, cl, X.wbox(-250, 250, -250, 250, -5.0, TOP_Z))
            X.diff(cl, slot_out(X)); X.diff(cl, tb_copy(X, 'TOOL_floor_off12'))
            X.diff(cl, X.wbox(-250, 250, -250, YJ_F, -5.0, 2.65))
            X.diff(cl, X.wbox(XC - 12.1, XC + 12.1, -95.0, -75.0, ZC - 7.2, ZC + 7.2))
            X.diff(cl, X.wbox(-250, 250, YJ_D, YJ_F, -5.0, 260))          # the joint gap stays open
            cloth = X.add(cl, 'RENDER_tmp_CLOTH'); tmp.append(cloth)
            if grey is not None:
                cloth.appearance = grey
            out['cloth_cm3'] = round(cloth.volume, 3)
            show = lambda keep: [setattr(b, 'isLightBulbOn', b.name in keep) for b in X.comp.bRepBodies]
            base = ['HOUSING_F_front', 'HOUSING_F_door', 'GROMMET_usbc_F', 'SLAB_frame', 'LCD_glass', 'RENDER_tmp_CLOTH']
            show(base)
            out['rear34'] = shoot(X, os.path.join(OUT, 'HA_v5f_b5_rear34.png'), (0.65, -1.0, 0.55), UP, tgt=(XC, -45.0, 90.0))
            out['front34'] = shoot(X, os.path.join(OUT, 'HA_v5f_b5_front34.png'), (-0.6, 1.0, 0.15), UP, tgt=(XC, 0.0, 60.0))
            show(base + ['FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR'])
            out['under'] = shoot(X, os.path.join(OUT, 'HA_v5f_b5_under.png'), (0.0, -0.05, -1.0), WY, tgt=(XC, -38.0, 0.0), ortho=True)
            lip_view = ['HOUSING_F_front', 'SPKBOX_L', 'SPKBOX_R']
            show(lip_view)
            out['lap'] = shoot(X, os.path.join(OUT, 'HA_v5f_b5_lap.png'), (0.15, -1.0, 0.3), UP, tgt=(XC, -58.0, 80.0))
            show(base)
            out['topgroove'] = shoot(X, os.path.join(OUT, 'HA_v5f_b5_topgroove.png'), (0.8, -0.7, 0.35), UP, tgt=(XC + 72.0, -42.0, 172.0))
        else:
            inv = [(b.name, round(b.volume, 3), b.isLightBulbOn) for b in X.comp.bRepBodies]
            out['n_bodies'] = len(inv); out['n_visible'] = sum(1 for i in inv if i[2])
            out['key_cm3'] = {n: v for (n, v, _) in inv if n.startswith(('HOUSING_F', 'SPKBOX', 'CRADLE', 'RESP_CARRIER', 'MAIN_BRACKET', 'GROMMET'))}
            out['unexpected'] = [n for (n, _, _) in inv if n.startswith('RENDER_tmp_') or n.endswith('_tmp') or ('(' in n and n.startswith(('HOUSING', 'SPKBOX', 'GROMMET')))]
            log('v5f_b5k_renders_save', 'inventory', {'bodies': inv})
            em = X.des.exportManager
            out['f3d'] = em.execute(em.createFusionArchiveExportOptions(F3D))
            out['f3d_bytes'] = os.path.getsize(F3D) if os.path.exists(F3D) else None
            out['saved'] = X.doc.save(VERSION)
            out['version'] = VERSION
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    finally:
        for t in tmp:
            try: t.deleteMe()
            except Exception: pass
        for b in X.comp.bRepBodies:
            if b.name in vis0: b.isLightBulbOn = vis0[b.name]
        X.app.activeViewport.visualStyle = vs0
    if MODE == 'renders':
        out['files'] = sorted(f for f in os.listdir(OUT) if f.startswith('HA_v5f_b5_'))
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('RENDER_tmp_')]
    log('v5f_b5k_renders_save', MODE, out)
    print(json.dumps(out))
