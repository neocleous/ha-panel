# rev F g2f (2026-11-10): step 1, block 2 - pictures of the plate's painted rim under the cloth (D74): A = as built (rim flush with the
# cloth's face), B = rim set back 0.7 (the plate without the 0.7 skin under the body surface, so the rim continues the shell's plastic).
# Everything shown is a temporary copy (RENDER_tmp_*): black plastic for shell, door, cap, slab frame, plate and feet, the old cloth bodies
# cut at the shell's bottom edge z 2.8, an oak table top under the feet. The copies are deleted at the end, visibility, style and camera
# restored. Nothing is saved. Eye: 600 mm in front of the origin, 350 above the table (and 150 for the low shot); zoom shots from the same
# eye with a narrow lens. Files: ~/Documents/HA_panel_renders/fp/rim/g2_rim_<A|B>_<shot>.png (1600 x 1200) + _check.jpg (480 x 360).
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
OUT = os.path.join(FP, 'rim')
TABLE_Z = -2.9
SHOTS = [('front', (0.0, 600.0, 350.0 + TABLE_Z), (0.0, -30.0, 85.0), 0.40),
         ('front34', (385.7, 459.6, 350.0 + TABLE_Z), (0.0, -30.0, 85.0), 0.40),
         ('zoom_front', (0.0, 600.0, 350.0 + TABLE_Z), (0.0, 3.0, 2.0), 0.10),
         ('zoom_front34', (385.7, 459.6, 350.0 + TABLE_Z), (88.0, -2.0, 2.0), 0.10),
         ('zoom_low', (0.0, 600.0, 150.0 + TABLE_Z), (0.0, 3.0, 2.0), 0.10)]


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


def run(_context):
    st = {}
    t0 = time.time()
    X = K()
    vp = X.app.activeViewport
    vis0 = {}; made = []; cam0 = vp.camera; style0 = vp.visualStyle
    ap0 = set(a.name for a in X.des.appearances)
    try:
        if any(n.startswith('RENDER_tmp_') for n in X.names()):
            raise RuntimeError('RENDER_tmp_ bodies exist already')
        if not os.path.isdir(OUT):
            os.makedirs(OUT)
        st['bodies before'] = len(X.names())
        blk = find_ap(X, ('Plastic - Matte (Black)', 'BLK_mock'))
        fab = find_ap(X, ('Fabric (Grey)',))
        oak = find_ap(X, ('Oak - Semigloss', 'Oak', 'Pine'))
        gls = find_ap(X, ('Paint - Enamel Glossy (Black)', 'Glass (Grey)', 'Plastic - Matte (Black)'))
        st['appearances'] = [a.name if a else None for a in (blk, fab, oak, gls)]

        def mk(tb, name, a, show=True):
            b = X.root.bRepBodies.add(tb); b.name = name
            if a:
                b.appearance = a
            b.isLightBulbOn = show
            made.append(b); return b

        up = X.wbox(-200, 200, -200, 100, 2.8, 260)
        f = X.cp(X.body('RENDER_FABRIC_front')); X.sec(f, X.cp(up)); mk(f, 'RENDER_tmp_cloth_front', fab)
        d = X.cp(X.body('RENDER_FABRIC_door')); X.sec(d, X.cp(up)); mk(d, 'RENDER_tmp_cloth_door', fab)
        for n in ('HOUSING_F_front', 'HOUSING_F_door', 'HOUSING_F_cap', 'SLAB_frame', 'GROMMET_usbc_F', 'FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR'):
            mk(X.cp(X.body(n)), 'RENDER_tmp_' + n, blk)
        mk(X.cp(X.body('LCD_glass')), 'RENDER_tmp_LCD_glass', gls)
        mk(X.wbox(-450, 450, -450, 650, TABLE_Z - 3.0, TABLE_Z), 'RENDER_tmp_table', oak)
        pa = mk(X.cp(X.body('FLOOR_PLATE')), 'RENDER_tmp_plate_A', blk)
        tb = X.cp(X.body('FLOOR_PLATE')); X.dif(tb, X.cp(X.body('TOOL_outer_skin_0p7')))
        st['plate B mm3'] = [round(X.vol(tb), 1), tb.lumps.count]
        pb = mk(tb, 'RENDER_tmp_plate_B', blk, False)
        st['t_built'] = round(time.time() - t0, 1); status('g2f', st)
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
        for var, on, off in (('A', pa, pb), ('B', pb, pa)):
            on.isLightBulbOn = True; off.isLightBulbOn = False
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
                p = os.path.join(OUT, 'g2_rim_%s_%s.png' % (var, nm))
                ok = vp.saveAsImageFile(p, 1600, 1200)
                vp.saveAsImageFile(p.replace('.png', '_check.jpg'), 480, 360)
                shots['%s_%s' % (var, nm)] = bool(ok)
            st['shots'] = shots; status('g2f', st)
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-6:]
    # clean up whatever happened
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
    status('g2f', st)


run(None)
