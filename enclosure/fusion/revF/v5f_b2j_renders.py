# rev F block 2j (2026-11-03): checkpoint-2 renders ~/Documents/HA_v5f_b2_{front34,cut,under_open,k5_section}.png
# (1600 x 1200 + 320 x 240 _check.jpg), one MODE per run:
#   'outside'  front34 of the closed panel (lattices on the chin).
#   'cut'      HOUSING_E copy cut at world z 55 (chamber ceilings and everything above removed), seen from behind and
#              above: speakers, partitions, baffles, touch PCB, Pi on the door.
#   'open'     door assembly (DOOR_F, Pi, cooler, GPIO plug envelopes, feet) copied and dropped 70 mm, from below-front.
#   'k5'       side section at world x 47.5 (the +x screw axes, x_rel 50.05): copies of the housing, slab, glass, door,
#              +x speaker and the KO_K5_LL / KO_K5_UL lanes cut to x <= 47.5, orthographic from +x; lanes red if the
#              appearance library is reachable.
# All copies are RENDER_tmp_* TemporaryBRep bodies, deleted after the shot; visibility restored.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
MODE = 'outside'
SHOW = ['HOUSING_E', 'SLAB_frame', 'LCD_glass', 'DOOR_F', 'FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR']
DOOR_ASM = ['DOOR_F', 'PI5_F', 'PI5_F_cooler', 'GPIO_plugA_env', 'GPIO_plugB_env', 'FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR']
INSIDE = ['SPK_L', 'SPK_R', 'TOUCH_PCB']


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
    vp.saveAsImageFile(path.replace('.png', '_check.jpg'), 320, 240)
    return ok


def red(X):
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


def run(_context):
    X = Ctx()
    docs = os.path.expanduser('~/Documents')
    vis0 = {b.name: b.isLightBulbOn for b in X.comp.bRepBodies}
    out = {'mode': MODE}
    tmp = []
    try:
        X.app.activeViewport.visualStyle = adsk.core.VisualStyles.ShadedWithVisibleEdgesOnlyVisualStyle
        B = adsk.fusion.BooleanTypes
        if MODE == 'outside':
            for b in X.comp.bRepBodies:
                b.isLightBulbOn = b.name in SHOW
            out['front34'] = shoot(X, os.path.join(docs, 'HA_v5f_b2_front34.png'), (0.55, 0.85, 0.35), UP)
        elif MODE == 'cut':
            hb = X.tbm.copy(X.body('HOUSING_E'))
            X.tbm.booleanOperation(hb, X.wbox(-150, 150, -150, 150, -10, 55.0), B.IntersectionBooleanType)
            tmp.append(X.add(hb, 'RENDER_tmp_HOUSING_cut'))
            keep = DOOR_ASM + INSIDE
            for b in X.comp.bRepBodies:
                b.isLightBulbOn = (b.name in keep) or b.name.startswith('RENDER_tmp_')
            out['cut'] = shoot(X, os.path.join(docs, 'HA_v5f_b2_cut.png'), (0.30, -0.55, 0.78), UP)
        elif MODE == 'open':
            mv = adsk.core.Matrix3D.create(); mv.translation = wvec(0, 0, -7.0)    # -70 mm world z (cm)
            for nm in DOOR_ASM:
                tb = X.tbm.copy(X.body(nm)); X.tbm.transform(tb, mv)
                tmp.append(X.add(tb, 'RENDER_tmp_' + nm))
            for b in X.comp.bRepBodies:
                b.isLightBulbOn = (b.name in ['HOUSING_E', 'SLAB_frame', 'LCD_glass'] + INSIDE) or b.name.startswith('RENDER_tmp_')
            out['under_open'] = shoot(X, os.path.join(docs, 'HA_v5f_b2_under_open.png'), (0.75, 0.55, -0.45), UP)
        else:
            ap = red(X)
            out['red'] = ap is not None
            for nm in ('HOUSING_E', 'SLAB_frame', 'LCD_glass', 'DOOR_F', 'SPK_L', 'KO_K5_LL', 'KO_K5_UL'):
                tb = X.tbm.copy(X.body(nm))
                X.tbm.booleanOperation(tb, X.wbox(-150, 47.5, -150, 150, -10, 250), B.IntersectionBooleanType)
                if tb.volume <= 0:
                    continue
                b = X.add(tb, 'RENDER_tmp_' + nm)
                tmp.append(b)
                if nm.startswith('KO_K5_') and ap is not None:
                    b.appearance = ap
            for b in X.comp.bRepBodies:
                b.isLightBulbOn = b.name.startswith('RENDER_tmp_')
            out['k5_section'] = shoot(X, os.path.join(docs, 'HA_v5f_b2_k5_section.png'), (1.0, 0.0, 0.0), UP, ortho=True)
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
    out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('RENDER_tmp_')]
    out['files'] = {f: os.path.getsize(os.path.join(docs, f)) for f in os.listdir(docs) if f.startswith('HA_v5f_b2_') and '_check' not in f}
    log('v5f_b2j_renders', MODE, out)
    print(json.dumps(out))
