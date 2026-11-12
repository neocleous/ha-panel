# rev F j5c (2026-11-12): close, block 5.3 - pictures of the rim with the cloth turned under the shell's and the door's bottom edges
#   (D90), as built: plate rim flush with the body and matte black, its top at z 1.8 in the band under the edges; the edges at z 2.8;
#   the cloth 0.7 thick, its lowest face at z 2.1. They replace the pictures of 2026-11-10 (g2f), which show the cloth cut at z 2.8.
#   Everything shown is a temporary copy (RENDER_tmp_*), as in g2f: black plastic for shell, door, cap, slab frame, plate, grommet and
#   feet; the cloth = the old cloth bodies down to z 2.1 plus a flap under each edge (the wall's own bottom slice z 2.8..3.5 moved
#   down by 0.7: the flap is as wide as the wall everywhere; D90 has 2.0 at the chin and the door - not visible from these eyes);
#   an oak table under the feet. The copies are deleted at the end; visibility, style and camera restored. Nothing is saved.
#   DRY=True (default): only the volumes and what the cloth meets. DRY=False: the pictures.
#   Eyes as g2f: 600 in front of the origin, 350 above the table (150 for the low shot); zooms from the same eye with a narrow lens.
#   Files: fp/close/rim_<shot>.png (1600 x 1200) and _check.jpg (800 x 600).
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_j_lib.py'), encoding='utf-8').read())
DRY = globals().get('DRY', True)
TABLE_Z = globals().get('TABLE_Z', -2.9)
ZC = 2.1
SHOTS = [('front', (0.0, 600.0, 350.0 + TABLE_Z), (0.0, -30.0, 85.0), 0.40),
         ('front34', (385.7, 459.6, 350.0 + TABLE_Z), (0.0, -30.0, 85.0), 0.40),
         ('zoom_front', (0.0, 600.0, 350.0 + TABLE_Z), (0.0, 3.0, 2.0), 0.10),
         ('zoom_front34', (385.7, 459.6, 350.0 + TABLE_Z), (88.0, -2.0, 2.0), 0.10),
         ('zoom_low', (0.0, 600.0, 150.0 + TABLE_Z), (0.0, 3.0, 2.0), 0.10),
         ('zoom_low34', (385.7, 459.6, 150.0 + TABLE_Z), (88.0, -2.0, 2.0), 0.10)]


def find_ap(X, names):
    for nm in names:
        a = X.des.appearances.itemByName(nm)
        if a:
            return a
    for i in range(X.app.materialLibraries.count):
        lib = X.app.materialLibraries.item(i)
        if 'Appearance' not in lib.name:
            continue
        for nm in names:
            try:
                a = lib.appearances.itemByName(nm)
            except Exception:
                a = None
            if a:
                return X.des.appearances.addByCopy(a, nm)
    return None


def cloth(X):
    up = X.wbox(-200, 200, -200, 100, ZC, 260)
    f = X.cp(X.body('RENDER_FABRIC_front')); X.sec(f, up)
    d = X.cp(X.body('RENDER_FABRIC_door')); X.sec(d, up)
    sl = X.wbox(-200, 200, -200, 100, 2.8, 3.5)
    ff = X.cp(sl); X.sec(ff, tcopy(X, 'HOUSING_F_front')); X.move(ff, 0, 0, -0.7)      # the big body is the tool: it is not copied
    fd = X.cp(sl); X.sec(fd, tcopy(X, 'HOUSING_F_door')); X.move(fd, 0, 0, -0.7)
    return f, d, ff, fd


def run(_context):
    st = {'dry': DRY}
    t0 = time.time()
    X = K()
    vp = X.app.activeViewport
    vis0 = {}; made = []; cam0 = vp.camera; style0 = vp.visualStyle
    ap0 = set(a.name for a in X.des.appearances)
    try:
        if any(n.startswith('RENDER_tmp_') for n in X.names()):
            raise RuntimeError('RENDER_tmp_ bodies exist already')
        os.makedirs(S3, exist_ok=True)
        st['bodies before'] = len(X.names())
        f, d, ff, fd = cloth(X)
        P = tcopy(X, 'FLOOR_PLATE')
        st['cloth'] = {'front skin mm3 / lumps / lowest z': [round(X.vol(f), 1), f.lumps.count, wext(f)[4]],
                       'door skin mm3 / lumps / lowest z': [round(X.vol(d), 1), d.lumps.count, wext(d)[4]],
                       'flap under the shell mm3 / z': [round(X.vol(ff), 1), wext(ff)[4], wext(ff)[5]],
                       'flap under the door mm3 / z': [round(X.vol(fd), 1), wext(fd)[4], wext(fd)[5]],
                       'in the plate (skins, flaps) mm3': [round(xvol(X, f, P), 2), round(xvol(X, d, P), 2), round(xvol(X, ff, P), 2), round(xvol(X, fd, P), 2)]}
        # the flaps are as wide as the walls; where a wall is wider than the plate's lowered band the flap would lie in the plate:
        #   that part is taken off (the cloth ends where the plate begins)
        for fl in (ff, fd):
            X.tbm.booleanOperation(fl, P, BT.DifferenceBooleanType)
        st['cloth']['flaps after the plate is taken off mm3'] = [round(X.vol(ff), 1), round(X.vol(fd), 1)]
        st['plate rim: world box'] = wext(X.body('FLOOR_PLATE'))
        st['feet lowest z'] = min(wext(X.body(n))[4] for n in ('FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR'))
        status3('j5c_dry' if DRY else 'j5c', st)
        if not DRY:
            blk = find_ap(X, ('Plastic - Matte (Black)', 'BLK_mock'))
            fab = find_ap(X, ('Fabric (Grey)',))
            oak = find_ap(X, ('Oak - Semigloss', 'Oak', 'Pine'))
            gls = find_ap(X, ('Paint - Enamel Glossy (Black)', 'Glass (Grey)', 'Plastic - Matte (Black)'))
            st['appearances'] = [a.name if a else None for a in (blk, fab, oak, gls)]

            def mk(tb, name, a):
                b = X.root.bRepBodies.add(tb); b.name = name
                if a:
                    b.appearance = a
                b.isLightBulbOn = True
                made.append(b); return b

            mk(f, 'RENDER_tmp_cloth_front', fab); mk(d, 'RENDER_tmp_cloth_door', fab)
            mk(ff, 'RENDER_tmp_flap_front', fab); mk(fd, 'RENDER_tmp_flap_door', fab)
            for n in ('HOUSING_F_front', 'HOUSING_F_door', 'HOUSING_F_cap', 'SLAB_frame', 'GROMMET_usbc_F', 'FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR', 'FLOOR_PLATE'):
                mk(X.cp(X.body(n)), 'RENDER_tmp_' + n, blk)
            mk(X.cp(X.body('LCD_glass')), 'RENDER_tmp_LCD_glass', gls)
            mk(X.wbox(-450, 450, -450, 650, TABLE_Z - 3.0, TABLE_Z), 'RENDER_tmp_table', oak)
            keep = set(b.name for b in made)
            for b in X.root.bRepBodies:
                if b.name in keep:
                    continue
                vis0[b.name + '|' + b.entityToken] = (b, b.isLightBulbOn)
                if b.isLightBulbOn:
                    b.isLightBulbOn = False
            vp.visualStyle = adsk.core.VisualStyles.ShadedVisualStyle
            upv = V3(0, S, C)
            shots = {}
            for nm, eye, tgt, ang in SHOTS:
                for _ in range(2):
                    cam = vp.camera
                    cam.cameraType = adsk.core.CameraTypes.PerspectiveCameraType
                    cam.isSmoothTransition = False
                    cam.isFitView = False
                    cam.target = Wp(*tgt); cam.eye = Wp(*eye); cam.upVector = upv
                    cam.perspectiveAngle = ang
                    vp.camera = cam
                    adsk.doEvents(); vp.refresh()
                p = os.path.join(S3, 'rim_%s.png' % nm)
                ok = vp.saveAsImageFile(p, 1600, 1200)
                vp.saveAsImageFile(p.replace('.png', '_check.jpg'), 800, 600)
                shots[nm] = bool(ok)
            st['shots'] = shots
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-6:]
    try:
        for b in made:
            try:
                b.deleteMe()
            except Exception:
                st.setdefault('cleanup', []).append('delete failed')
        for k, (b, v) in vis0.items():
            try:
                if b.isLightBulbOn != v:
                    b.isLightBulbOn = v
            except Exception:
                st.setdefault('cleanup', []).append('vis ' + k.split('|')[0])
        if not DRY:
            vp.visualStyle = style0
            cam0.isSmoothTransition = False
            vp.camera = cam0
            adsk.doEvents(); vp.refresh()
        for a in list(X.des.appearances):
            if a.name not in ap0:
                try:
                    a.deleteMe()
                except Exception:
                    st.setdefault('cleanup', []).append('appearance kept: ' + a.name)
        st['bodies after'] = len(X.names())
        st['left'] = [n for n in X.names() if n.startswith('RENDER_tmp_')]
    except Exception:
        st['CLEANUP_FAIL'] = traceback.format_exc().splitlines()[-6:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('j5c_dry' if DRY else 'j5c', st)


run(None)
