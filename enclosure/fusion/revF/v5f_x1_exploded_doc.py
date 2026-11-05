# rev F exploded view x1 (2026-11-05, Daniel 17:03 "Give me an exploded view in fusion so I can see all the parts"):
#   a SEPARATE Fusion document "HA Panel v5 - exploded view (rev F c2)" in the same project folder; the main model is only
#   read. One component per part group, bodies copied at their true positions, the explode offset carried by the
#   occurrence transform (so each group can be moved back in Fusion). World mm offsets: cap up, display stack forward along
#   the slab normal (0, cos 12°, sin 12°), speakers / boxes sideways, door / grommet / 5807 / main board / BME680 back,
#   Pi back and down, feet down, radar out along its antenna normal. Not included: cloth bodies, leads, keep-outs, tools,
#   references, superseded copies, LCD connector / standoff details. Colours: printed parts blue-grey, cap orange (as in the
#   section pictures), boards green, LCD / speakers / feet dark. Renders HA_v5f_c2_exploded_{rear34,front34}.png.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
DOC_NAME = 'HA Panel v5 - exploded view (rev F c2)'
OUT = os.path.expanduser('~/Documents/HA_panel_renders')
NS = (0.0, C, S)
PRINT, CAPC, PCB, DARK, GLASS = 'x_printed', 'x_cap', 'x_pcb', 'x_dark', 'x_glass'
GROUPS = [
    ('Front shell', ['HOUSING_F_front'], (0.0, 0.0, 0.0), PRINT),
    ('Top cap', ['HOUSING_F_cap'], (0.0, 0.0, 85.0), CAPC),
    ('Cap sensors - VEML6030 + mic strips', ['VEML_env', 'MIC_strip_L_env', 'MIC_strip_R_env'], (0.0, 0.0, 55.0), PCB),
    ('Rear door', ['HOUSING_F_door'], (0.0, -150.0, 0.0), PRINT),
    ('USB-C grommet', ['GROMMET_usbc_F'], (0.0, -185.0, 0.0), PRINT),
    ('5807 cradle + board', ['CRADLE_5807', 'PD_5807_env'], (0.0, -105.0, 0.0), PRINT),
    ('Main board + bracket', ['MAIN_BRACKET', 'MAIN_pcb'], (0.0, -60.0, 0.0), PRINT),
    ('Pi 5 + cooler + GPIO plugs', ['PI5_F', 'PI5_F_cooler', 'GPIO_plugA_env', 'GPIO_plugB_env'], (0.0, -85.0, -35.0), PCB),
    ('BME680', ['BME680_env'], (0.0, -60.0, 0.0), PCB),
    ('Speaker box L', ['SPKBOX_L'], (95.0, 0.0, 0.0), PRINT),
    ('Speaker box R', ['SPKBOX_R'], (-95.0, 0.0, 0.0), PRINT),
    ('Speaker L (DMA45-4)', ['SPK_L'], (95.0, 60.0, 0.0), DARK),
    ('Speaker R (DMA45-4)', ['SPK_R'], (-95.0, 60.0, 0.0), DARK),
    ('Touch PCB', ['TOUCH_PCB'], (0.0, 45.0, 0.0), PCB),
    ('Radar LD2410C', ['LD2410C_env_F'], (-0.857 * 50.0, 0.515 * 50.0, 0.0), PCB),
    ('ReSpeaker Lite + carrier', ['RESP_CARRIER', 'RESP_pcb'], tuple(c * 60.0 for c in NS), PRINT),
    ('LCD module', ['LCD_glass', 'LCD_panel_body', 'LCD_pcb_76x110'], tuple(c * 95.0 for c in NS), GLASS),
    ('Slab frame', ['SLAB_frame'], tuple(c * 135.0 for c in NS), PRINT),
    ('Feet SJ5012', ['FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR'], (0.0, 0.0, -25.0), DARK),
]
COLOURS = {PRINT: (169, 200, 232), CAPC: (244, 177, 131), PCB: (46, 125, 50), DARK: (45, 45, 45), GLASS: (20, 20, 25)}
BODY_COLOUR = {'MAIN_pcb': PCB, 'RESP_pcb': PCB, 'PD_5807_env': PCB, 'PI5_F_cooler': DARK, 'GPIO_plugA_env': DARK,
               'GPIO_plugB_env': DARK, 'LCD_pcb_76x110': PCB}


def wvec_cm(d):                              # world mm offset -> design Vector3D (cm)
    return V3(d[0] / 10, (d[1] * C + d[2] * S) / 10, (-d[1] * S + d[2] * C) / 10)


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        folder = X.doc.dataFile.parentFolder
        src = []
        missing = []
        for (gname, names, off, col) in GROUPS:
            items = []
            for n in names:
                b = X.body(n)
                if b is None:
                    missing.append(n); continue
                items.append((n, X.tbm.copy(b), BODY_COLOUR.get(n, col)))
            src.append((gname, items, off))
        out['missing'] = missing
        app = X.app
        lib = None
        for i in range(app.materialLibraries.count):
            l = app.materialLibraries.item(i)
            if 'Appearance' in l.name:
                lib = l; break
        base = None
        if lib is not None:
            for i in range(lib.appearances.count):
                a = lib.appearances.item(i)
                if 'Plastic' in a.name and 'Matte' in a.name:
                    base = a; break
        out['appearance_base'] = base.name if base else None
        doc2 = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        des2 = adsk.fusion.Design.cast(app.activeProduct)
        des2.designType = adsk.fusion.DesignTypes.DirectDesignType
        root = des2.rootComponent
        apps = {}
        if base is not None:
            for k, rgb in COLOURS.items():
                try:
                    a = des2.appearances.addByCopy(base, k)
                    cp = a.appearanceProperties.itemByName('Color')
                    if cp is None:
                        for j in range(a.appearanceProperties.count):
                            p = a.appearanceProperties.item(j)
                            if p.objectType == adsk.core.ColorProperty.classType():
                                cp = p; break
                    cp.value = adsk.core.Color.create(rgb[0], rgb[1], rgb[2], 255)
                    apps[k] = a
                except Exception as e:
                    out.setdefault('appearance_fail', []).append(k + ': ' + str(e)[:60])
        made = {}
        for (gname, items, off) in src:
            m = adsk.core.Matrix3D.create(); m.translation = wvec_cm(off)
            occ = root.occurrences.addNewComponent(m)
            comp = occ.component; comp.name = gname
            for (n, tb, col) in items:
                b = comp.bRepBodies.add(tb); b.name = n
                if col in apps:
                    b.appearance = apps[col]
            made[gname] = [n for (n, tb, col) in items]
        out['components'] = made
        vp = app.activeViewport
        vp.visualStyle = adsk.core.VisualStyles.ShadedWithVisibleEdgesOnlyVisualStyle
        shots = {}
        for (k, d) in (('rear34', (0.75, -1.0, 0.65)), ('front34', (-0.7, 1.0, 0.55))):
            cam = vp.camera
            cam.cameraType = adsk.core.CameraTypes.PerspectiveCameraType
            tgt = (XC, -40.0, 80.0); n_ = math.sqrt(sum(c * c for c in d)); D = 900.0
            cam.target = Dw(*tgt); cam.eye = Dw(tgt[0] + D * d[0] / n_, tgt[1] + D * d[1] / n_, tgt[2] + D * d[2] / n_)
            cam.upVector = UP; cam.isSmoothTransition = False; cam.isFitView = True
            vp.camera = cam; vp.refresh()
            p = os.path.join(OUT, 'HA_v5f_c2_exploded_%s.png' % k)
            shots[k] = vp.saveAsImageFile(p, 1600, 1200)
        out['shots'] = shots
        cam = vp.camera
        d = (0.75, -1.0, 0.65); tgt = (XC, -40.0, 80.0); n_ = math.sqrt(sum(c * c for c in d)); D = 900.0
        cam.target = Dw(*tgt); cam.eye = Dw(tgt[0] + D * d[0] / n_, tgt[1] + D * d[1] / n_, tgt[2] + D * d[2] / n_)
        cam.upVector = UP; cam.isSmoothTransition = False; cam.isFitView = True; vp.camera = cam
        out['saved'] = doc2.saveAs(DOC_NAME, folder, 'Exploded view of rev F after cap block c2; copies only, the design '
                                   'model is HA Panel v5 - tapered (Claude)', '')
        out['doc'] = doc2.name
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    try:
        log('v5f_x1_exploded_doc', 'run', out)
    except Exception:
        pass
    print(json.dumps(out, separators=(',', ':'))[:4000])
