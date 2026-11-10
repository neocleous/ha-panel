# rev F g2f0 (2026-11-10): step 1, block 2 - read-only: appearances of the parts seen from outside and the library names the rim renders can use.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
WANT = ('Matte (Black)', 'Satin (Black)', 'Oak', 'Pine', 'Walnut', 'Maple', 'Bamboo', 'Enamel Glossy (White)', 'Matte (White)', 'Fabric', 'Glass')


def run(_context):
    st = {}
    try:
        X = K()
        ap = {}
        for n in ('HOUSING_F_front', 'HOUSING_F_cap', 'HOUSING_F_door', 'GROMMET_usbc_F', 'SLAB_frame', 'LCD_glass', 'FLOOR_PLATE', 'FOOT_FL',
                  'RENDER_FABRIC_front', 'RENDER_FABRIC_door'):
            b = X.body(n)
            if b is None:
                ap[n] = 'missing'; continue
            try:
                ap[n] = [b.appearance.name, b.isLightBulbOn]
            except Exception:
                ap[n] = ['?', b.isLightBulbOn]
        st['bodies'] = ap
        st['design appearances'] = [a.name for a in X.des.appearances]
        found = {}
        for i in range(X.app.materialLibraries.count):
            lib = X.app.materialLibraries.item(i)
            try:
                names = [a.name for a in lib.appearances]
            except Exception:
                continue
            hit = [n for n in names if any(w in n for w in WANT)]
            if hit:
                found[lib.name] = hit[:60]
        st['library'] = found
        vp = X.app.activeViewport
        cam = vp.camera
        st['viewport'] = {'style': int(vp.visualStyle), 'w': vp.width, 'h': vp.height, 'persp': cam.cameraType == adsk.core.CameraTypes.PerspectiveCameraType,
                          'angle': round(cam.perspectiveAngle, 3)}
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-6:]
    status('g2f0', st)


run(None)
