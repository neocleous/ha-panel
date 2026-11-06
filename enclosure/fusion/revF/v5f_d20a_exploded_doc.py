# rev F d20a (2026-11-06, Daniel 23:20 "Create an exploded view of the model in fusion so I can inspect the parts"): the 14
#   printed parts as of d19 (the bracket's two halves separate) copied into a new direct-design document, one component per
#   print, in the WORLD frame (z up, x centred: x_rel), each component moved by d18a's explode offset (its occurrence
#   transform, so a part goes back to its fitted place by zeroing that transform). Colours as d18a (housing / structure /
#   fittings), the source bodies' materials copied where they exist. Saved next to the design model as SAVE_NAME and left open;
#   the design model is only read. Writes ~/Documents/HA_panel_renders/d_data/data/d20a_exploded_doc.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py'), encoding='utf-8').read())
import traceback
OUTJ = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d20a_exploded_doc.json')
SAVE_NAME = 'HA Panel v5 - exploded prints (d19)'
GUARD = {'HOUSING_F_front': 235.2269, 'HOUSING_F_door': 47.2694, 'HOUSING_F_cap': 9.9591, 'SLAB_frame': 62.9324,
         'SPKBOX_L': 25.6082, 'SPKBOX_R': 26.3874, 'MAIN_BRACKET': 6.5563, 'RESP_CARRIER': 10.0716, 'CRADLE_5807': 2.1775,
         'GROMMET_usbc_F': 0.5062, 'TOUCH_CLIP_L': 0.4896, 'TOUCH_CLIP_R': 0.4896, 'BME_HOOD': 0.8029}
NS = (0.0, C, S)                                             # slab normal (world)
HOUS, STRU, FITT = 'p_housing', 'p_structure', 'p_fitting'
COLOURS = {HOUS: (169, 200, 232), STRU: (226, 194, 144), FITT: (244, 160, 100)}
PRINTS = [                                                    # (label, body, lump side, world offset mm, colour) - d18a's
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
VIEW_DIR = (-0.966, -0.259, 0.7)                              # d18a's view: 15° behind the right side, 35° up


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        for k, v in GUARD.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard %s %s (expected %s)' % (k, None if b is None else round(b.volume, 4), v))
        for d_ in X.app.documents:
            if d_.name.startswith(SAVE_NAME):
                raise RuntimeError('a document named %r is open already' % d_.name)
        folder = X.doc.dataFile.parentFolder
        M = adsk.core.Matrix3D.create()                       # design frame -> world frame, x centred (x_rel)
        M.setCell(1, 1, C); M.setCell(1, 2, -S); M.setCell(2, 1, S); M.setCell(2, 2, C); M.setCell(2, 3, H / 10)
        M.setCell(0, 3, -XC / 10)
        src = []
        for (lab, n, side, off, col) in PRINTS:
            ob = X.body(n); t = X.tbm.copy(ob)
            if side is not None:
                pick = None
                for L in t.lumps:
                    q = X.tbm.copy(L)
                    bb = wbb(X, q)
                    if (bb[0] + bb[1]) * side > 0:
                        pick = q
                t = pick
            X.tbm.transform(t, M)
            src.append((lab, t, off, col, round(t.volume, 4), ob.material))
        app = X.app; base = None
        for i in range(app.materialLibraries.count):
            l = app.materialLibraries.item(i)
            if 'Appearance' in l.name:
                for j in range(l.appearances.count):
                    a = l.appearances.item(j)
                    if 'Plastic' in a.name and 'Matte' in a.name:
                        base = a; break
                break
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
        mats = {}; parts = []
        for (lab, t, off, col, v, mat) in src:
            occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
            comp = occ.component; comp.name = lab
            b = comp.bRepBodies.add(t); b.name = lab
            if mat is not None:
                try:
                    if mat.name not in mats:
                        mats[mat.name] = des2.materials.addByCopy(mat, mat.name)
                    b.material = mats[mat.name]
                except Exception as e:
                    out.setdefault('material_fail', {})[lab] = str(e)[:80]
            if col in apps:
                b.appearance = apps[col]
            tr = adsk.core.Matrix3D.create(); tr.translation = adsk.core.Vector3D.create(off[0] / 10, off[1] / 10, off[2] / 10)
            try:
                occ.transform2 = tr
            except Exception:
                occ.transform = tr
            parts.append([lab, round(b.volume, 4), v, [round(c, 1) for c in off]])
        out['parts'] = parts
        out['volumes_match'] = all(abs(p[1] - p[2]) < 0.0005 for p in parts)
        out['materials'] = sorted(mats)
        vp = app.activeViewport
        vp.visualStyle = adsk.core.VisualStyles.ShadedWithVisibleEdgesOnlyVisualStyle
        cam = vp.camera
        cam.cameraType = adsk.core.CameraTypes.PerspectiveCameraType
        tg = (0.0, -11.0, 12.0); n_ = math.sqrt(sum(c * c for c in VIEW_DIR))
        cam.target = adsk.core.Point3D.create(*tg)
        cam.eye = adsk.core.Point3D.create(*(tg[i] + 160.0 * VIEW_DIR[i] / n_ for i in range(3)))
        cam.upVector = adsk.core.Vector3D.create(0, 0, 1); cam.isSmoothTransition = False; cam.isFitView = True
        vp.camera = cam; vp.refresh()
        out['saved'] = doc2.saveAs(SAVE_NAME, folder, 'rev F d19: the 14 prints exploded (components, world frame, z up); '
                                   'zero an occurrence transform to put a part back', '')
        out['doc'] = app.activeDocument.name
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    try:
        os.makedirs(os.path.dirname(OUTJ), exist_ok=True)
        json.dump(out, open(OUTJ, 'w'))
    except Exception:
        pass
    log('v5f_d20a_exploded_doc', 'run', out)
    print(json.dumps(out, separators=(',', ':')))
