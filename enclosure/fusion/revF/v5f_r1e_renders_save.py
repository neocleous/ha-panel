# rev F rework R1e (2026-11-04): checkpoint renders for the rear-door block + named version + f3d.
# Renders (1600 x 1200) into ~/Documents/HA_panel_renders/:
#   HA_v5f_r1_rear34_exploded.png  door pulled 80 mm straight back (TemporaryBRep copy), rear 3/4
#   HA_v5f_r1_rear_closed.png      closed, from behind: joint arch and USB-C slot
#   HA_v5f_r1_under.png            underside, orthographic: feet, door-screw counterbores, intake field
#   HA_v5f_r1_rear_open.png        door off, from behind: speakers, touch PCB, Pi, LCD back, LCD-screw lanes (red)
# MODE 'renders' or 'save' (one per run).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
MODE = 'renders'
OUT = os.path.expanduser('~/Documents/HA_panel_renders')
VERSION = 'rev F WIP 2026-11-04 R1: rear door split y -55, solid floor, 10 edge magnet pairs, 4 x M3 from below, USB-C bottom centre (Claude)'
F3D = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-wip-r1.f3d')
BASE = ['HOUSING_F_front', 'SLAB_frame', 'LCD_glass', 'FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR']


def wvec(dx, dy, dz):
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
    vp.saveAsImageFile(path.replace('.png', '_check.jpg'), 480, 360)
    return ok


def red_ap(X):
    try:
        for i in range(X.app.materialLibraries.count):
            lib = X.app.materialLibraries.item(i)
            if 'Appearance' not in lib.name:
                continue
            for nm in ('Paint - Enamel Glossy (Red)', 'Plastic - Glossy (Red)', 'Paint - Metal Flake (Red)'):
                ap = lib.appearances.itemByName(nm)
                if ap:
                    return X.des.appearances.itemByName(nm) or X.des.appearances.addByCopy(ap, nm)
    except Exception:
        return None


EXPECT = {'HOUSING_F_front': 265.519, 'HOUSING_F_door': 55.484}   # cm3 after R1c-2 (checked by R1d)


def run(_context):
    X = Ctx(); out = {'mode': MODE}
    vis0 = {b.name: b.isLightBulbOn for b in X.comp.bRepBodies}
    vs0 = X.app.activeViewport.visualStyle
    tmp = []
    try:
        out['doc'] = X.doc.name
        for n, v in EXPECT.items():
            b = X.body(n)
            if b is None or abs(b.volume - v) > 0.002:
                raise RuntimeError('guard: %s volume %s, expected %s' % (n, None if b is None else round(b.volume, 3), v))
        if MODE == 'renders':
            os.makedirs(OUT, exist_ok=True)
            X.app.activeViewport.visualStyle = adsk.core.VisualStyles.ShadedWithVisibleEdgesOnlyVisualStyle
            red = red_ap(X)
            t = X.tbm.copy(X.body('HOUSING_F_door'))
            m = adsk.core.Matrix3D.create(); m.translation = wvec(0, -8.0, 0)
            X.tbm.transform(t, m)
            dx = X.add(t, 'RENDER_tmp_door'); tmp.append(dx)
            if red is not None:
                dx.appearance = red
            for b in X.comp.bRepBodies:
                b.isLightBulbOn = b.name in BASE + ['PD_5807_env', 'RENDER_tmp_door']
            out['rear34_exploded'] = shoot(X, os.path.join(OUT, 'HA_v5f_r1_rear34_exploded.png'), (-0.55, -0.85, 0.35), UP)
            for b in X.comp.bRepBodies:
                b.isLightBulbOn = b.name in BASE + ['HOUSING_F_door', 'PD_5807_env']
            out['rear_closed'] = shoot(X, os.path.join(OUT, 'HA_v5f_r1_rear_closed.png'), (0.0, -1.0, 0.12), UP, ortho=True)
            out['under'] = shoot(X, os.path.join(OUT, 'HA_v5f_r1_under.png'), (0.0, 0.0, -1.0), WY, ortho=True)
            lanes = []
            for nm in ('KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR'):
                lt = X.tbm.copy(X.body(nm))
                X.tbm.booleanOperation(lt, X.wbox(-150, 150, -55.0, 150, -10, 250), adsk.fusion.BooleanTypes.IntersectionBooleanType)
                lb = X.add(lt, 'RENDER_tmp_' + nm); tmp.append(lb); lanes.append(lb.name)
                if red is not None:
                    lb.appearance = red
            inside = ['SPK_L', 'SPK_R', 'TOUCH_PCB', 'PI5_F', 'PI5_F_cooler', 'GPIO_plugA_env', 'GPIO_plugB_env', 'PD_5807_env']
            for b in X.comp.bRepBodies:
                b.isLightBulbOn = b.name in BASE + inside + lanes or (b.name.startswith('LCD_') and b.name != 'LCD_glass')
            out['rear_open'] = shoot(X, os.path.join(OUT, 'HA_v5f_r1_rear_open.png'), (-0.20, -1.0, 0.30), UP)
        else:
            inv = [(b.name, round(b.volume, 3), b.isLightBulbOn) for b in X.comp.bRepBodies]
            out['n_bodies'] = len(inv); out['n_visible'] = sum(1 for i in inv if i[2])
            out['key_cm3'] = {n: v for (n, v, _) in inv if n.startswith('HOUSING_F') or n in ('PD_5807_env', 'KO_5807_pigtail', 'HOUSING_E', 'DOOR_F_b2')
                              or n.startswith('FOOT_') or n.startswith('TOOL_inner_skin')}
            out['unexpected'] = [n for (n, _, _) in inv if n.startswith('RENDER_tmp_') or n.endswith('_tmp') or '(' in n and n.startswith('HOUSING')]
            log('v5f_r1e_renders_save', 'inventory', {'bodies': inv})
            em = X.des.exportManager
            out['f3d'] = em.execute(em.createFusionArchiveExportOptions(F3D))
            out['f3d_bytes'] = os.path.getsize(F3D) if os.path.exists(F3D) else None
            out['saved'] = X.doc.save(VERSION)
            out['version'] = VERSION
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
    if MODE == 'renders':
        out['files'] = {f: os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT) if f.startswith('HA_v5f_r1_')}
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('RENDER_tmp_')]
    log('v5f_r1e_renders_save', MODE, out)
    print(json.dumps(out))
