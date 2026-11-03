# rev F block 0 (2026-11-03): V8 - LCD standoff depth -> LCD screw length (standoffs are M3, see the correction below).
# Imports Daniel's Waveshare STEP (~/Documents/Maker/HA Panel/Datasheets/8inch-dsi-lcd_c_New.stp) into a separate,
# unsaved document, probes the four mounting points along the screw axis, closes the document without saving.
# STEP frame: origin = glass centre, long axis Y (= design x), +Z toward the viewer, glass front Z 4.8 -> d = 4.8 - Z.
# Mounting points: STEP (X +-34, Y +-47.5) = design (x +-47.5, Z ZS +-34).
# Result 2026-11-03: import 10.7 s; standoff D5.5 x 1.5 (Z -2.6..-4.1 = d 7.4..8.9) with a plain D2.6 bore through standoff
# and PCB (+ D4.3 x 0.3 at the PCB front), no thread modelled; LCD panel back on the axis at Z 0.05-0.10 (4.15-4.2 below
# the standoff face). Head seat d 12.8, boss 3.8 -> 6 mm screw tip 2.2 below the boss face (~2.0 clear of the panel);
# 8 mm tip 4.2 -> touches the panel back -> rejected.
# Correction 2026-11-03 11:20: Waveshare's 2D drawing gives the four standoffs as M3 ("4xM3.00 H1.5"; the Pi standoffs are
# "4xM2.50 H8"); the D2.6 bore matches an M3 tap size -> LCD screws are DIN912 M3 x 6 (the "M2.5" in the logs is wrong).
import adsk.core, adsk.fusion, json, math, os, time

LOG = os.path.expanduser('~/Documents/v5f_log.json')
STEP = os.path.expanduser('~/Documents/Maker/HA Panel/Datasheets/8inch-dsi-lcd_c_New.stp')
AXES = [(34, 47.5), (-34, 47.5), (34, -47.5), (-34, -47.5)]   # STEP X, Y (mm)


def segments(body, x, y, z_top, z_bot, step=0.05):
    P3 = adsk.core.Point3D.create
    INS = (adsk.fusion.PointContainment.PointInsidePointContainment,)
    segs, inside, start = [], False, None
    n = int(round((z_top - z_bot) / step))
    for i in range(n + 1):
        z = z_top - i * step
        ins = body.pointContainment(P3(x / 10, y / 10, z / 10)) in INS
        if ins and not inside:
            start, inside = z, True
        if inside and not ins:
            segs.append((round(start, 2), round(z + step, 2)))
            inside = False
    if inside:
        segs.append((round(start, 2), z_bot))
    return segs


def run(_context):
    app = adsk.core.Application.get()
    panel = app.activeDocument
    if panel.name != 'HA Panel v5 - tapered':
        raise RuntimeError('active document is %r' % panel.name)
    t0 = time.time()
    im = app.importManager
    nd = im.importToNewDocument(im.createSTEPImportOptions(STEP))
    des = adsk.fusion.Design.cast(nd.products.itemByProductType('DesignProductType'))
    bodies = {}
    for o in des.rootComponent.allOccurrences:
        for b in o.bRepBodies:
            bodies[o.name.split(':')[0] + '/' + b.name] = b
    pcba = [b for k, b in bodies.items() if k.startswith('101INCH-DSI-PCBA') and b.faces.count > 2000][0]
    out = {'import_s': round(time.time() - t0, 1), 'axes': {}}
    for (X, Y) in AXES:
        cyls = []
        for f in pcba.faces:
            if f.geometry.surfaceType != adsk.core.SurfaceTypes.CylinderSurfaceType:
                continue
            c = adsk.core.Cylinder.cast(f.geometry)
            if abs(abs(c.axis.z) - 1) > 1e-3 or math.hypot(c.origin.x * 10 - X, c.origin.y * 10 - Y) > 0.6:
                continue
            pt = f.pointOnFace
            _, nrm = f.evaluator.getNormalAtPoint(pt)
            radial = adsk.core.Vector3D.create(pt.x - c.origin.x, pt.y - c.origin.y, 0)
            bb = f.boundingBox
            cyls.append({'D': round(c.radius * 20, 3), 'Z': (round(bb.minPoint.z * 10, 2), round(bb.maxPoint.z * 10, 2)),
                         'kind': 'hole' if nrm.dotProduct(radial) < 0 else 'boss'})
        along = {k: segments(b, X, Y, 5.0, -5.0) for k, b in bodies.items()}
        out['axes']['%g,%g' % (X, Y)] = {'cylinders': cyls, 'material_on_axis': {k: v for k, v in along.items() if v}}
    nd.close(False)
    if app.activeDocument != panel:
        panel.activate()
    out['active_after'] = app.activeDocument.name
    out['panel_modified'] = panel.isModified
    arr = json.load(open(LOG)) if os.path.exists(LOG) else []
    arr.append({'t': time.strftime('%Y-%m-%d %H:%M:%S'), 'script': 'v5f_b0_v8_lcd_standoff', 'step': 'V8', 'data': out})
    json.dump(arr, open(LOG, 'w'), indent=1)
    print(json.dumps(out))
