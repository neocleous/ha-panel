# rev F rework R2e (2026-11-04): checkpoint renders for the speaker-box block + named version + f3d (MODE per run).
# Renders (1600 x 1200 + 480 x 360 check JPEGs) into ~/Documents/HA_panel_renders/:
#   HA_v5f_r2_rear_open.png   door off, rear 3/4: boxes (blue) with speakers, touch PCB, LCD back
#   HA_v5f_r2_box_path.png    -x box in place, +x box + speaker (red copy) at its entry pose: lifted 6, 40 inboard, 40 back
#   HA_v5f_r2_box_front.png   +x box + speaker alone, front 3/4: stop pads, pegs, basket hole, plug pocket
#   HA_v5f_r2_box_rear.png    +x box alone, rear 3/4: clamp tubes, wire hole, cove step
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
MODE = 'renders'
OUT = os.path.expanduser('~/Documents/HA_panel_renders')
VERSION = 'rev F WIP 2026-11-04 R2: separate speaker boxes SPKBOX_L/R (clamp tubes, stop pads, plug pocket), chamber walls removed (Claude)'
F3D = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-wip-r2.f3d')
BASE = ['HOUSING_F_front', 'SLAB_frame', 'LCD_glass', 'FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR']
EXPECT = {'HOUSING_F_front': 238.880, 'HOUSING_F_door': 55.484, 'SPKBOX_L': 25.321, 'SPKBOX_R': 25.071}


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
            for n in ('SPKBOX_L', 'SPKBOX_R'):
                b = X.body(n); app0[n] = b.appearance
                if blue is not None: b.appearance = blue
            lcds = [b.name for b in X.comp.bRepBodies if b.name.startswith('LCD_') and b.name != 'LCD_glass']
            show = lambda keep: [setattr(b, 'isLightBulbOn', b.name in keep) for b in X.comp.bRepBodies]
            show(BASE + ['SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'TOUCH_PCB'] + lcds)
            out['rear_open'] = shoot(X, os.path.join(OUT, 'HA_v5f_r2_rear_open.png'), (-0.35, -1.0, 0.45), UP)
            mod = X.union(X.tbm.copy(X.body('SPKBOX_L')), X.tbm.copy(X.body('SPK_L')))
            m = adsk.core.Matrix3D.create(); dx, dy, dz = -40.0, -41.0, 6.0
            m.translation = V3(dx / 10, (dy * C + dz * S) / 10, (-dy * S + dz * C) / 10); X.tbm.transform(mod, m)
            pb = X.add(mod, 'RENDER_tmp_boxL_entry'); tmp.append(pb)
            if red is not None: pb.appearance = red
            show(BASE + ['SPKBOX_R', 'SPK_R', pb.name])
            out['box_path'] = shoot(X, os.path.join(OUT, 'HA_v5f_r2_box_path.png'), (-0.25, -1.0, 0.55), UP)
            show(['SPKBOX_L', 'SPK_L'])
            out['box_front'] = shoot(X, os.path.join(OUT, 'HA_v5f_r2_box_front.png'), (-0.9, 1.0, 0.4), UP, tgt=(XC + 70.0, -25.0, 40.0))
            show(['SPKBOX_L'])
            out['box_rear'] = shoot(X, os.path.join(OUT, 'HA_v5f_r2_box_rear.png'), (-0.8, -1.0, 0.35), UP, tgt=(XC + 70.0, -25.0, 40.0))
        else:
            inv = [(b.name, round(b.volume, 3), b.isLightBulbOn) for b in X.comp.bRepBodies]
            out['n_bodies'] = len(inv); out['n_visible'] = sum(1 for i in inv if i[2])
            out['key_cm3'] = {n: v for (n, v, _) in inv if n.startswith(('HOUSING_F', 'SPKBOX', 'TOOL_cav', 'TOOL_inner_skin'))}
            out['unexpected'] = [n for (n, _, _) in inv if n.startswith('RENDER_tmp_') or n.endswith('_tmp') or ('(' in n and n.startswith(('HOUSING', 'SPKBOX')))]
            log('v5f_r2e_renders_save', 'inventory', {'bodies': inv})
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
        out['files'] = sorted(f for f in os.listdir(OUT) if f.startswith('HA_v5f_r2_'))
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('RENDER_tmp_')]
    log('v5f_r2e_renders_save', MODE, out)
    print(json.dumps(out))
