# rev F d18a (2026-11-06, Daniel 21:33 "Give an exploded view of the individual prints"): the 14 printed parts as of d17 (the
#   bracket's two halves are separate prints), copied into a temporary direct-design document (closed unsaved; the design model
#   is only read), exploded along the panel's y axis in assembly order (slab and carrier forward along the slab normal; boxes,
#   cradle, bracket, door, grommet back; cap and BME680 hood up; touch clips forward), offsets chosen with a bounding-box
#   occlusion check so no print hides another from the right-rear-above view. Rendered at twice the viewport size, plus each
#   print's centroid in image pixels for the labels -> ~/Documents/HA_panel_renders/HA_v5f_d17_prints_<view>_raw.png and
#   d_data/data/d18a_exploded.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py'), encoding='utf-8').read())
import traceback
OUT = os.path.expanduser('~/Documents/HA_panel_renders')
OUTJ = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d18a_exploded.json')
GUARD = {'HOUSING_F_front': 235.2269, 'HOUSING_F_door': 47.2694, 'HOUSING_F_cap': 9.9591, 'SLAB_frame': 62.9324,
         'SPKBOX_L': 25.6082, 'SPKBOX_R': 26.3874, 'MAIN_BRACKET': 6.2403, 'RESP_CARRIER': 10.0716, 'CRADLE_5807': 2.1775,
         'GROMMET_usbc_F': 0.5062, 'TOUCH_CLIP_L': 0.4896, 'TOUCH_CLIP_R': 0.4896, 'BME_HOOD': 0.8029}
NS = (0.0, C, S)                                             # slab normal (world)
HOUS, STRU, FITT = 'p_housing', 'p_structure', 'p_fitting'
COLOURS = {HOUS: (169, 200, 232), STRU: (226, 194, 144), FITT: (244, 160, 100)}
PRINTS = [                                                    # (label, body, lump side, world offset mm, colour)
    ('Front shell', 'HOUSING_F_front', None, (0.0, 0.0, 0.0), HOUS),
    ('Top cap', 'HOUSING_F_cap', None, (0.0, 0.0, 90.0), HOUS),
    ('Slab frame', 'SLAB_frame', None, tuple(c * 182.0 for c in NS), HOUS),
    ('ReSpeaker carrier', 'RESP_CARRIER', None, tuple(c * 97.5 for c in NS), FITT),
    ('Touch clip L', 'TOUCH_CLIP_L', None, (0.0, 58.5, -15.0), FITT),
    ('Touch clip R', 'TOUCH_CLIP_R', None, (0.0, 58.5, -15.0), FITT),
    ('BME680 hood', 'BME_HOOD', None, (0.0, 0.0, 115.0), FITT),
    ('Speaker box L', 'SPKBOX_L', None, (40.0, -143.0, 0.0), STRU),
    ('Speaker box R', 'SPKBOX_R', None, (0.0, -143.0, 0.0), STRU),
    ('5807 cradle', 'CRADLE_5807', None, (0.0, -195.0, 0.0), FITT),
    ('Bracket, left half', 'MAIN_BRACKET', 1, (0.0, -253.5, 20.0), STRU),
    ('Bracket, right half', 'MAIN_BRACKET', -1, (0.0, -253.5, 20.0), STRU),
    ('Rear door', 'HOUSING_F_door', None, (0.0, -318.5, 0.0), HOUS),
    ('USB-C grommet', 'GROMMET_usbc_F', None, (0.0, -370.5, 0.0), FITT),
]
PART_DIRS = {'Rear door': (0.8, -0.9, 0.75), 'USB-C grommet': (0.8, -0.9, 0.75), '5807 cradle': (0.8, -0.9, 0.75),
             'Top cap': (-0.6, 0.7, 1.2)}                             # rear parts from behind; the cap from higher up
VIEWS = (('side', (-0.966, -0.259, 0.7)),)                   # 15° behind the right side, 35° up
TGT, DIST = (0.0, -110.0, 120.0), 1600.0                 # look-at (x_rel, y, z) and eye distance (mm)


def run(_context):
    X = Ctx(); out = {}; t0 = time.time(); doc2 = None
    try:
        for k, v in GUARD.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard %s %s (expected %s)' % (k, None if b is None else round(b.volume, 4), v))
        src = []
        for (lab, n, side, off, col) in PRINTS:
            t = tb_copy(X, n)
            if side is not None:
                pick = None
                for L in t.lumps:
                    q = X.tbm.copy(L)
                    if (wbb(X, q)[0] + wbb(X, q)[1]) * side > 0:
                        pick = q
                t = pick
            mvw(X, t, *off)
            src.append((lab, n, t, col, round(t.volume, 4)))
        app = X.app; lib = None; base = None
        for i in range(app.materialLibraries.count):
            l = app.materialLibraries.item(i)
            if 'Appearance' in l.name:
                lib = l; break
        if lib is not None:
            for i in range(lib.appearances.count):
                a = lib.appearances.item(i)
                if 'Plastic' in a.name and 'Matte' in a.name:
                    base = a; break
        doc2 = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        des2 = adsk.fusion.Design.cast(app.activeProduct)
        des2.designType = adsk.fusion.DesignTypes.DirectDesignType
        root = des2.rootComponent
        apps = {}
        if base is not None:
            for k, rgb in COLOURS.items():
                a = des2.appearances.addByCopy(base, k)
                cp = a.appearanceProperties.itemByName('Color')
                if cp is None:
                    for j in range(a.appearanceProperties.count):
                        p = a.appearanceProperties.item(j)
                        if p.objectType == adsk.core.ColorProperty.classType():
                            cp = p; break
                cp.value = adsk.core.Color.create(rgb[0], rgb[1], rgb[2], 255)
                apps[k] = a
        bodies = []
        for (lab, n, t, col, v) in src:
            b = root.bRepBodies.add(t); b.name = lab
            if col in apps:
                b.appearance = apps[col]
            bodies.append((lab, b, v))
        vp = app.activeViewport
        vp.visualStyle = adsk.core.VisualStyles.ShadedWithVisibleEdgesOnlyVisualStyle
        out['viewport'] = [vp.width, vp.height]
        views = {}
        for (k, d) in VIEWS:
            cam = vp.camera
            cam.cameraType = adsk.core.CameraTypes.PerspectiveCameraType
            tgt = (XC + TGT[0], TGT[1], TGT[2]); n_ = math.sqrt(sum(c * c for c in d)); D = DIST
            cam.target = Dw(*tgt); cam.eye = Dw(tgt[0] + D * d[0] / n_, tgt[1] + D * d[1] / n_, tgt[2] + D * d[2] / n_)
            cam.upVector = UP; cam.isSmoothTransition = False; cam.isFitView = True
            vp.camera = cam; vp.refresh()
            pts = {}
            for (lab, b, v) in bodies:
                c = b.physicalProperties.centerOfMass
                p2 = vp.modelToViewSpace(c)
                bb = b.boundingBox; mn, mx = bb.minPoint, bb.maxPoint
                cs = [vp.modelToViewSpace(P3(x_, y_, z_)) for x_ in (mn.x, mx.x) for y_ in (mn.y, mx.y) for z_ in (mn.z, mx.z)]
                pts[lab] = [round(p2.x, 1), round(p2.y, 1), v, [round(min(q.x for q in cs), 1), round(min(q.y for q in cs), 1),
                                                                round(max(q.x for q in cs), 1), round(max(q.y for q in cs), 1)]]
            path = os.path.join(OUT, 'HA_v5f_d17_prints_%s_raw.png' % k)
            ok = vp.saveAsImageFile(path, 2 * vp.width, 2 * vp.height)
            views[k] = {'ok': ok, 'path': path, 'pts': pts}
        out['views'] = views
        singles = {}
        for (lab, b, v) in bodies:
            for (lab2, b2, v2) in bodies:
                b2.isLightBulbOn = (lab2 == lab)
            bb = b.boundingBox
            c = P3((bb.minPoint.x + bb.maxPoint.x) / 2, (bb.minPoint.y + bb.maxPoint.y) / 2, (bb.minPoint.z + bb.maxPoint.z) / 2)
            d = PART_DIRS.get(lab, (-0.8, 0.9, 0.75)); dv = wv(d); dv.normalize()
            cam = vp.camera
            cam.cameraType = adsk.core.CameraTypes.PerspectiveCameraType
            cam.target = c; cam.eye = P3(c.x + dv.x * 120, c.y + dv.y * 120, c.z + dv.z * 120)
            cam.upVector = UP; cam.isSmoothTransition = False; cam.isFitView = True
            vp.camera = cam; vp.refresh()
            path = os.path.join(OUT, 'd18_parts', 'part_%02d.png' % len(singles))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            singles[lab] = {'path': path, 'ok': vp.saveAsImageFile(path, vp.width, vp.height), 'cm3': v}
        for (lab2, b2, v2) in bodies:
            b2.isLightBulbOn = True
        out['singles'] = singles
        out['n_prints'] = len(bodies)
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    try:
        if doc2 is not None:
            doc2.close(False)
        for d_ in X.app.documents:
            if d_.name == 'HA Panel v5 - tapered':
                d_.activate(); break
        out['active_after'] = X.app.activeDocument.name
    except Exception as e:
        out['close_fail'] = str(e)[:100]
    try:
        os.makedirs(os.path.dirname(OUTJ), exist_ok=True)
        json.dump(out, open(OUTJ, 'w'))
    except Exception:
        pass
    log('v5f_d18a_exploded_prints', 'run', {k: v for k, v in out.items() if k != 'views'})
    print(json.dumps({k: v for k, v in out.items() if k != 'views'}, separators=(',', ':')))
