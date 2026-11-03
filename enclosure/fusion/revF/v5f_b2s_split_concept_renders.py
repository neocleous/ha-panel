# rev F block 2s (2026-11-03): concept renders for the removable-back proposal (Daniel 23:41: "if the back was removable
# the unit would be much easier to service and assemble"). Nothing in the design changes: TemporaryBRep copies only,
# deleted after the shots. Split = vertical world plane y -55 (opening arch 159 wide at the floor, closes at z ~159;
# all four LCD-screw key entries at the plane lie inside it, probed in the b2 removable-back study).
#   front shell = HOUSING_E ∩ (y >= -55) (+ DOOR_F standing in for the solid floor), cover = HOUSING_E ∩ (y < -55).
# Views into ~/Documents/HA_panel_renders/:
#   HA_v5f_split_rear34_exploded.png  cover (red) moved 80 mm back, rear 3/4
#   HA_v5f_split_rear_open.png        cover removed, from behind and slightly above: speakers, touch PCB, Pi, LCD lanes (red)
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
YS = -55.0
OUT = os.path.expanduser('~/Documents/HA_panel_renders')


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
    return vp.saveAsImageFile(path, w, h)


def run(_context):
    X = Ctx()
    os.makedirs(OUT, exist_ok=True)
    vis0 = {b.name: b.isLightBulbOn for b in X.comp.bRepBodies}
    out = {}
    tmp = []
    try:
        X.app.activeViewport.visualStyle = adsk.core.VisualStyles.ShadedWithVisibleEdgesOnlyVisualStyle
        B = adsk.fusion.BooleanTypes
        red = X.des.appearances.itemByName('Paint - Enamel Glossy (Red)')
        hb = X.body('HOUSING_E')
        front = X.tbm.copy(hb); X.tbm.booleanOperation(front, X.wbox(-150, 150, YS, 150, -10, 250), B.IntersectionBooleanType)
        cover = X.tbm.copy(hb); X.tbm.booleanOperation(cover, X.wbox(-150, 150, -150, YS, -10, 250), B.IntersectionBooleanType)
        out['front_cm3'] = round(front.volume, 2); out['cover_cm3'] = round(cover.volume, 2)
        mv = adsk.core.Matrix3D.create(); mv.translation = wvec(0, -8.0, 0)       # 80 mm back (cm)
        X.tbm.transform(cover, mv)
        fb = X.add(front, 'RENDER_tmp_front'); tmp.append(fb)
        cb = X.add(cover, 'RENDER_tmp_cover'); tmp.append(cb)
        if red is not None:
            cb.appearance = red
        base = ['SLAB_frame', 'LCD_glass', 'DOOR_F', 'FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR']
        for b in X.comp.bRepBodies:
            b.isLightBulbOn = b.name in base or b.name in ('RENDER_tmp_front', 'RENDER_tmp_cover')
        out['rear34_exploded'] = shoot(X, os.path.join(OUT, 'HA_v5f_split_rear34_exploded.png'), (-0.55, -0.85, 0.35), UP)
        cb.isLightBulbOn = False
        lanes = []
        for nm in ('KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR'):
            t = X.tbm.copy(X.body(nm)); X.tbm.booleanOperation(t, X.wbox(-150, 150, YS, 150, -10, 250), B.IntersectionBooleanType)
            lb = X.add(t, 'RENDER_tmp_' + nm); tmp.append(lb); lanes.append(lb.name)
            if red is not None:
                lb.appearance = red
        inside = ['SPK_L', 'SPK_R', 'TOUCH_PCB', 'PI5_F', 'PI5_F_cooler', 'GPIO_plugA_env', 'GPIO_plugB_env']
        names = [b.name for b in X.comp.bRepBodies]
        for b in X.comp.bRepBodies:
            b.isLightBulbOn = b.name in base + inside + ['RENDER_tmp_front'] + lanes or (b.name.startswith('LCD_') and b.name != 'LCD_glass')
        out['rear_open'] = shoot(X, os.path.join(OUT, 'HA_v5f_split_rear_open.png'), (-0.20, -1.0, 0.30), UP)
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
    out['files'] = {f: os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT)}
    log('v5f_b2s_split_concept_renders', 'renders', out)
    print(json.dumps(out))
