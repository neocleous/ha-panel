# rev F block 4m (2026-11-04), read-only on the panel document: the LCD's 15-pin DSI connector in Daniel's Waveshare STEP.
#   Which side does the FPC enter (± design x)? Imports the STEP into a new unsaved document (as b0 V8), lists the bodies and
#   faces inside the connector's region and closes the document.
#   STEP frame (b0): STEP Y = design x (same sign), STEP X = design Z − ZS (±), d = 4.8 − STEP Z. LCD_DSI_conn_d9.3 (rev D box):
#   x_rel 41.85…46.75 → design x 39.3…44.2 → STEP Y 39.3…44.2; Z −39…−16.6 → STEP X ≈ −12…11; d ≤ 9.3 → STEP Z ≥ −4.5.
import adsk.core, adsk.fusion, json, math, os, time

LOG = os.path.expanduser('~/Documents/v5f_log.json')
STEP = os.path.expanduser('~/Documents/Maker/HA Panel/Datasheets/8inch-dsi-lcd_c_New.stp')
REG = (-16.0, 16.0, 36.0, 48.0, -9.0, -2.0)     # STEP X, Y, Z ranges (mm)


def run(_context):
    app = adsk.core.Application.get()
    panel = app.activeDocument
    if panel.name != 'HA Panel v5 - tapered':
        raise RuntimeError('active document is %r' % panel.name)
    out = {}
    t0 = time.time()
    im = app.importManager
    nd = im.importToNewDocument(im.createSTEPImportOptions(STEP))
    try:
        des = adsk.fusion.Design.cast(nd.products.itemByProductType('DesignProductType'))
        tbm = adsk.fusion.TemporaryBRepManager.get()
        P3 = adsk.core.Point3D.create
        reg = tbm.createBox(adsk.core.OrientedBoundingBox3D.create(P3((REG[0] + REG[1]) / 20, (REG[2] + REG[3]) / 20, (REG[4] + REG[5]) / 20),
                                                                  adsk.core.Vector3D.create(1, 0, 0), adsk.core.Vector3D.create(0, 1, 0),
                                                                  (REG[1] - REG[0]) / 10, (REG[3] - REG[2]) / 10, (REG[5] - REG[4]) / 10))
        res = []
        for o in des.rootComponent.allOccurrences:
            for b in o.bRepBodies:
                bb = b.boundingBox
                if bb.maxPoint.x * 10 < REG[0] or bb.minPoint.x * 10 > REG[1] or bb.maxPoint.y * 10 < REG[2] or bb.minPoint.y * 10 > REG[3] \
                        or bb.maxPoint.z * 10 < REG[4] or bb.minPoint.z * 10 > REG[5]:
                    continue
                t = tbm.copy(b)
                tbm.booleanOperation(t, tbm.copy(reg), adsk.fusion.BooleanTypes.IntersectionBooleanType)
                if t.volume <= 0:
                    continue
                ent = {'body': o.name.split(':')[0] + '/' + b.name, 'faces_total': b.faces.count, 'lumps': []}
                for lp in t.lumps:
                    lb = lp.boundingBox
                    box = [round(lb.minPoint.x * 10, 2), round(lb.maxPoint.x * 10, 2), round(lb.minPoint.y * 10, 2), round(lb.maxPoint.y * 10, 2),
                           round(lb.minPoint.z * 10, 2), round(lb.maxPoint.z * 10, 2)]
                    vol = round(lp.volume * 1000, 2)
                    if vol < 1.0:
                        continue
                    pl = []
                    for sh in lp.shells:
                        for f in sh.faces:
                            if f.geometry.objectType.endswith('Plane'):
                                p = f.pointOnFace; ok, n = f.evaluator.getNormalAtPoint(p)
                                pl.append([round(n.x, 2), round(n.y, 2), round(n.z, 2), round(f.area * 100, 2), round(p.x * 10, 2), round(p.y * 10, 2), round(p.z * 10, 2)])
                    pl.sort(key=lambda r: -r[3])
                    ent['lumps'].append({'box_XYZ': box, 'mm3': vol, 'n_faces': sum(sh.faces.count for sh in lp.shells), 'planar_top12': pl[:12]})
                if ent['lumps']:
                    res.append(ent)
        out['bodies_in_region'] = res
        out['import_s'] = round(time.time() - t0, 1)
    except Exception as e:
        out['FAIL'] = str(e)
    finally:
        nd.close(False)
        if app.activeDocument != panel:
            panel.activate()
    out['active_after'] = app.activeDocument.name
    arr = json.load(open(LOG)) if os.path.exists(LOG) else []
    arr.append({'t': time.strftime('%Y-%m-%d %H:%M:%S'), 'script': 'v5f_b4m_probe_lcd_dsi_conn', 'step': 'probe', 'data': out})
    json.dump(arr, open(LOG, 'w'), indent=1)
    print(json.dumps({'n_bodies': len(out.get('bodies_in_region', [])), 'import_s': out.get('import_s'), 'FAIL': out.get('FAIL'), 'active_after': out['active_after']}))
