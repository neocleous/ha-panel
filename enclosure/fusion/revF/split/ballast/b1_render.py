"""Ballast pass, block 1: the options drawn in a scratch document (never in the model of record).
Three connector calls: open() builds the scene from temporary copies and draws the weights as extrusions of their outlines
(results/cand_pts.json, embedded below); shot() saves the picture; close() closes the scratch document without saving and
activates the model again. Never call the cp2k library while the scratch document is active (lesson 202)."""
import adsk.core, adsk.fusion, sys, time, json, os, types

PTS = json.loads('{"rear":[[6.81,-66.24],[6.92,-61.5],[8.6,-60.21],[41.82,-60.19],[42.84,-56.89],[46.19,-55.9],[47.44,-56.32],[49.04,-57.9],[51.58,-58.31],[52.49,-59.79],[52.41,-61.11],[51.76,-62.08],[47.95,-62.99],[46.15,-64.66],[44.92,-66.88],[44.89,-71.76],[44.02,-73.22],[36.67,-75.32],[26.17,-77.15],[24.57,-76.45],[24.05,-74.29],[22.69,-71.94],[20.45,-70.24],[17.26,-70.36],[14.17,-73.22],[12.13,-73.06],[10.35,-69.51],[7.55,-67.61]],"left":[[46.3,-20.75],[46.73,-19.5],[47.66,-18.85],[51.38,-19.28],[54.01,-18.36],[55.77,-16.28],[56.25,-14.66],[55.85,-11.87],[54.01,-9.64],[51.34,-8.71],[48.03,-9.23],[46.73,-8.5],[46.31,-7.44],[46.39,-5.42],[47.91,-4.04],[69.82,-4.09],[71.02,-5.12],[71.87,-8.87],[73.75,-11.69],[75.89,-13.28],[79.1,-14.25],[81.72,-14.13],[84.18,-13.24],[86.22,-11.72],[88.91,-8.56],[90.6,-8.7],[91.53,-9.89],[90.49,-18.16],[88.49,-25.87],[86.57,-26.62],[83.72,-24.99],[80.9,-24.81],[78.4,-26.11],[76.95,-28.41],[76.71,-30.19],[77.57,-32.9],[79.61,-34.73],[83.26,-35.69],[84.03,-37.6],[79.5,-45.6],[75.35,-50.98],[74.2,-51.66],[69.38,-51.69],[68.02,-50.96],[67.62,-49.28],[69.25,-45.66],[68.9,-42.98],[67.08,-40.68],[64.3,-39.71],[61.4,-40.4],[59.58,-42.09],[58.95,-43.41],[58.88,-46.37],[60.45,-49.5],[59.57,-51.36],[58.46,-51.7],[48.3,-51.7],[46.75,-50.97],[46.3,-49.7]],"right":[[-91.6,-10.64],[-90.92,-8.9],[-89.1,-8.48],[-88.12,-9.08],[-86.22,-11.72],[-84.15,-13.26],[-80.9,-14.25],[-78.28,-14.13],[-75.14,-12.84],[-73.2,-11.08],[-71.87,-8.87],[-71.1,-5.31],[-70.37,-4.36],[-64.7,-4.0],[-63.43,-4.45],[-62.71,-5.8],[-62.3,-14.0],[-59.59,-21.45],[-60.63,-23.07],[-64.28,-23.9],[-64.3,-33.45],[-64.76,-34.72],[-66.51,-35.44],[-70.32,-32.98],[-75.84,-33.02],[-76.76,-31.82],[-77.18,-27.8],[-78.8,-25.79],[-80.21,-25.01],[-83.13,-24.82],[-86.63,-26.59],[-88.24,-26.11],[-90.21,-19.59]]}')
WEIGHTS = [('W_rear', 'rear', 2.5, 10.0, (42, 120, 214)), ('W_left', 'left', 0.9, 2.5, (235, 104, 52)), ('W_right', 'right', 0.9, 2.5, (235, 104, 52))]
OUT = os.path.expanduser('~/Documents/HA_panel_renders/ballast')
app = adsk.core.Application.get()
st = {'main': None, 'doc': None}

def grab(X, k, items):
    return [(lab, [X.tbm.copy(X.body(src))], rgb, op) for lab, src, rgb, op in items]

def base_app():
    for i in range(app.materialLibraries.count):
        L = app.materialLibraries.item(i)
        if 'Appearance' in L.name:
            for nm in ('Paint - Enamel Glossy (Yellow)', 'Plastic - Matte (Yellow)'):
                a = L.appearances.itemByName(nm)
                if a:
                    return a
            for j in range(L.appearances.count):
                a = L.appearances.item(j)
                if a.name.startswith('Paint - Enamel'):
                    return a
    raise RuntimeError('no base appearance')

def colour(des, rgb):
    key = 'bal_%d_%d_%d' % tuple(rgb)
    a = des.appearances.itemByName(key)
    if a:
        return a
    a = des.appearances.addByCopy(base_app(), key)
    adsk.core.ColorProperty.cast(a.appearanceProperties.itemByName('Color')).value = adsk.core.Color.create(rgb[0], rgb[1], rgb[2], 255)
    return a

def design():
    return adsk.fusion.Design.cast(st['doc'].products.itemByProductType('DesignProductType'))

def open_scene(_context=None):
    k = sys.modules['cp2k']; X = k.K()
    grey, lead = (200, 199, 194), (80, 80, 90)
    items = [('FLOOR_PLATE', 'FLOOR_PLATE', grey, 1.0), ('SPKBOX_L', 'SPKBOX_L', (170, 178, 190), 0.22), ('SPKBOX_R', 'SPKBOX_R', (170, 178, 190), 0.22),
             ('PI5_F', 'PI5_F', (60, 120, 80), 1.0), ('PI5_F_cooler', 'PI5_F_cooler', (110, 110, 115), 0.8),
             ('CRADLE_5807', 'CRADLE_5807', (150, 150, 150), 1.0), ('PD_5807_env', 'PD_5807_env', (120, 120, 120), 0.6),
             ('PIPWR_a_env', 'PIPWR_a_env', (140, 140, 150), 0.45), ('USBA_plug_env', 'USBA_plug_env', (140, 140, 150), 0.6),
             ('LEAD_USB_RESP', 'LEAD_USB_RESP', lead, 1.0), ('LEAD_SPK_L', 'LEAD_SPK_L', lead, 1.0), ('LEAD_SPK_R', 'LEAD_SPK_R', lead, 1.0)]
    items += [(n, n, (40, 40, 40), 1.0) for n in ('FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR')]
    got = grab(X, k, items)                                   # every copy taken while the model is still active
    st['main'] = app.activeDocument
    st['doc'] = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    des = adsk.fusion.Design.cast(app.activeProduct)
    des.designType = adsk.fusion.DesignTypes.DirectDesignType
    root = des.rootComponent
    for lab, bodies, rgb, op in got:
        a = colour(des, rgb)
        for tb in bodies:
            b = root.bRepBodies.add(tb); b.name = lab; b.appearance = a
            if op < 1.0:
                b.opacity = op
    nrm = k.dv((0.0, 0.0, 1.0)); made = {}
    for name, key, z0, t, rgb in WEIGHTS:
        pi = root.constructionPlanes.createInput()
        pi.setByPlane(adsk.core.Plane.create(k.Wp(0.0, 0.0, z0), nrm))          # direct design only
        cp = root.constructionPlanes.add(pi)
        sk = root.sketches.add(cp)
        P = [sk.modelToSketchSpace(k.Wp(x, y, z0)) for x, y in PTS[key]]
        for i in range(len(P)):
            sk.sketchCurves.sketchLines.addByTwoPoints(P[i], P[(i + 1) % len(P)])
        prof = max([sk.profiles.item(i) for i in range(sk.profiles.count)], key=lambda p: p.areaProperties().area)
        ei = root.features.extrudeFeatures.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        ei.setDistanceExtent(False, adsk.core.ValueInput.createByReal(t / 10.0))
        b = root.features.extrudeFeatures.add(ei).bodies.item(0); b.name = name; b.appearance = colour(des, rgb)
        made[name] = b; sk.isVisible = False; cp.isLightBulbOn = False
    plate = [b for b in root.bRepBodies if b.name == 'FLOOR_PLATE'][0]
    tools = adsk.core.ObjectCollection.create(); tools.add(made['W_left']); tools.add(made['W_right'])
    ci = root.features.combineFeatures.createInput(plate, tools)
    ci.operation = adsk.fusion.FeatureOperations.CutFeatureOperation; ci.isKeepToolBodies = True
    root.features.combineFeatures.add(ci)                    # the pockets under the boxes, for the picture only
    print({n: round(b.volume * 1000.0, 1) for n, b in made.items()})   # 5,542.6 / 3,655.3 / 1,401.3 mm3 in the run

def shot(_context=None):
    k = sys.modules['cp2k']; vp = app.activeViewport; cam = vp.camera
    cam.isSmoothTransition = False; cam.cameraType = adsk.core.CameraTypes.PerspectiveCameraType
    cam.eye = k.Wp(215.0, -330.0, 255.0); cam.target = k.Wp(0.0, -33.0, 4.0); cam.upVector = k.dv((0.0, 0.0, 1.0))
    vp.camera = cam; vp.refresh(); adsk.doEvents()
    o = adsk.core.SaveImageFileOptions.create(os.path.join(OUT, 'ballast_3_rear34_raw.png'))
    o.width = 1600; o.height = 1200; o.isAntiAliased = True; o.isBackgroundTransparent = False
    print(vp.saveAsImageFileWithOptions(o))

def close(_context=None):
    if st['doc'] is not None:
        st['doc'].close(False); st['doc'] = None
    if st['main'] is not None:
        st['main'].activate()

run = open_scene
