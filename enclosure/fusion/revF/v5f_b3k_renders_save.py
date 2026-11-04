# rev F block 3k (2026-11-04): checkpoint-3 renders + named version + f3d (MODE per run).
# Renders (1600 x 1200 + 480 x 360 check JPEGs) into ~/Documents/HA_panel_renders/:
#   HA_v5f_b3_top34.png        closed housing from the front-right, above: R3 top edge, mic and lux ports
#   HA_v5f_b3_top_under.png    the top (front shell above z 160, temporary cut body) from below: strip pockets, pins, VEML
#                              pocket; MIC_strip envelopes red, VEML_env blue
#   HA_v5f_b3_ld_cradle.png    the viewer's-right front corner (temporary cut body) from inside: LD2410C cradle, board red
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
MODE = 'renders'
OUT = os.path.expanduser('~/Documents/HA_panel_renders')
VERSION = 'rev F WIP 2026-11-04 b3: top edge R3 + top wall >= 2.5, mic strip pockets/pins/ports, VEML pocket (provisional), LD2410C cradle (Claude)'
F3D = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-wip-b3.f3d')
BASE = ['HOUSING_F_front', 'SLAB_frame', 'LCD_glass', 'FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR']
EXPECT = {'HOUSING_F_front': 242.831, 'HOUSING_F_door': 55.484, 'SPKBOX_L': 25.321, 'SPKBOX_R': 25.071}


def shoot(X, path, d, up, tgt=(XC, -35.0, 70.0), w=1600, h=1200, ortho=False):
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
    tmp = []; app0 = {}
    try:
        out['doc'] = X.doc.name
        for n, v in EXPECT.items():
            b = X.body(n)
            if b is None or abs(b.volume - v) > 0.002:
                raise RuntimeError('guard: %s volume %s, expected %s' % (n, None if b is None else round(b.volume, 3), v))
        if MODE == 'renders':
            os.makedirs(OUT, exist_ok=True)
            X.app.activeViewport.visualStyle = adsk.core.VisualStyles.ShadedWithVisibleEdgesOnlyVisualStyle
            red = ap(X, ('Paint - Enamel Glossy (Red)', 'Plastic - Glossy (Red)'))
            blue = ap(X, ('Paint - Enamel Glossy (Blue)', 'Plastic - Glossy (Blue)'))
            show = lambda keep: [setattr(b, 'isLightBulbOn', b.name in keep) for b in X.comp.bRepBodies]
            show(BASE + ['HOUSING_F_door'])
            out['top34'] = shoot(X, os.path.join(OUT, 'HA_v5f_b3_top34.png'), (-0.55, 1.0, 1.25), UP, tgt=(XC, -30.0, 172.0))
            t = X.tbm.copy(X.body('HOUSING_F_front'))
            X.tbm.booleanOperation(t, X.wbox(XC - 110, XC + 110, -60, 5, 160, 190), adsk.fusion.BooleanTypes.IntersectionBooleanType)
            cb = X.add(t, 'RENDER_tmp_top'); tmp.append(cb)
            for n, col in (('MIC_strip_L_env', red), ('MIC_strip_R_env', red), ('VEML_env', blue)):
                e = X.add(X.tbm.copy(X.body(n)), 'RENDER_tmp_' + n); tmp.append(e)
                if col is not None: e.appearance = col
            show([b.name for b in tmp])
            out['top_under'] = shoot(X, os.path.join(OUT, 'HA_v5f_b3_top_under.png'), (0.25, -0.55, -1.0), WY, tgt=(XC, -30.0, 176.0))
            for b in list(tmp):
                b.deleteMe()
            tmp.clear()
            t = X.tbm.copy(X.body('HOUSING_F_front'))
            X.tbm.booleanOperation(t, X.wbox(XC - 105, XC - 50, -50, 5, 105, 150), adsk.fusion.BooleanTypes.IntersectionBooleanType)
            cb = X.add(t, 'RENDER_tmp_corner'); tmp.append(cb)
            e = X.add(X.tbm.copy(X.body('LD2410C_env_F')), 'RENDER_tmp_ld'); tmp.append(e)
            if red is not None: e.appearance = red
            show([b.name for b in tmp])
            out['ld_cradle'] = shoot(X, os.path.join(OUT, 'HA_v5f_b3_ld_cradle.png'), (0.85, -0.75, 0.3), UP, tgt=(XC - 78.0, -18.0, 127.5))
        else:
            inv = [(b.name, round(b.volume, 3), b.isLightBulbOn) for b in X.comp.bRepBodies]
            out['n_bodies'] = len(inv); out['n_visible'] = sum(1 for i in inv if i[2])
            out['key_cm3'] = {n: v for (n, v, _) in inv if n.startswith(('HOUSING_F', 'SPKBOX', 'TOOL_cav', 'TOOL_inner_skin'))}
            out['unexpected'] = [n for (n, _, _) in inv if n.startswith('RENDER_tmp_') or n.endswith('_tmp') or ('(' in n and n.startswith(('HOUSING', 'SPKBOX')))]
            log('v5f_b3k_renders_save', 'inventory', {'bodies': inv})
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
        for n, a in app0.items():
            try: X.body(n).appearance = a
            except Exception: pass
        for b in X.comp.bRepBodies:
            if b.name in vis0: b.isLightBulbOn = vis0[b.name]
        X.app.activeViewport.visualStyle = vs0
    if MODE == 'renders':
        out['files'] = sorted(f for f in os.listdir(OUT) if f.startswith('HA_v5f_b3_'))
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('RENDER_tmp_')]
    log('v5f_b3k_renders_save', MODE, out)
    print(json.dumps(out))
