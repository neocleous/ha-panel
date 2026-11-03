# rev F block 0 (2026-11-03): K13/D20 coupon - 60 x 60 x 2.5 (Daniel 2026-11-03: 2.5 overall -> 1.8 under the cloth),
# 40 x 40 x 0.7 fabric recess field (R1), plate corners R3, 20 x 20 glue-patch zone centred, marked by four L corner
# ticks outside the zone (3 mm legs + 0.8 corner, 0.8 wide, 0.4 deep). Modelled standing on a 60 mm edge (Z up) so the
# export loads in print orientation (Daniel: on edge with a brim). Built in a separate unsaved document, exported to
# ~/Documents/HA_coupon_wall2p5.{3mf,stl}, document closed without saving. Run via Fusion MCP fusion_mcp_execute.
import adsk.core, adsk.fusion, json, os, time

LOG = os.path.expanduser('~/Documents/v5f_log.json')


def log(script, step, data):
    arr = []
    if os.path.exists(LOG):
        with open(LOG) as f:
            arr = json.load(f)
    arr.append({'t': time.strftime('%Y-%m-%d %H:%M:%S'), 'script': script, 'step': step, 'data': data})
    with open(LOG, 'w') as f:
        json.dump(arr, f, indent=1)


def run(_context):
    app = adsk.core.Application.get()
    panel = app.activeDocument
    if panel.name != 'HA Panel v5 - tapered':
        raise RuntimeError('active document is %r' % panel.name)
    P3 = adsk.core.Point3D.create
    V3 = adsk.core.Vector3D.create
    tbm = adsk.fusion.TemporaryBRepManager.get()
    UNION = adsk.fusion.BooleanTypes.UnionBooleanType
    DIFF = adsk.fusion.BooleanTypes.DifferenceBooleanType

    def box(x0, x1, y0, y1, z0, z1):  # mm
        x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
        obb = adsk.core.OrientedBoundingBox3D.create(
            P3((x0 + x1) / 20, (y0 + y1) / 20, (z0 + z1) / 20), V3(1, 0, 0), V3(0, 1, 0),
            (x1 - x0) / 10, (y1 - y0) / 10, (z1 - z0) / 10)
        return tbm.createBox(obb)

    def cyl_y(x, z, r, y0, y1):  # mm, axis along Y
        return tbm.createCylinderOrCone(P3(x / 10, y0 / 10, z / 10), r / 10, P3(x / 10, y1 / 10, z / 10), r / 10)

    def rrect_y(cx, cz, w, h, r, y0, y1):  # rounded rectangle prism, axis along Y
        b = box(cx - w / 2, cx + w / 2, y0, y1, cz - h / 2 + r, cz + h / 2 - r)
        tbm.booleanOperation(b, box(cx - w / 2 + r, cx + w / 2 - r, y0, y1, cz - h / 2, cz + h / 2), UNION)
        for sx in (-1, 1):
            for sz in (-1, 1):
                tbm.booleanOperation(b, cyl_y(cx + sx * (w / 2 - r), cz + sz * (h / 2 - r), r, y0, y1), UNION)
        return b

    T, G = 2.5, 0.7            # plate thickness, fabric recess depth (mm)
    ZC = 30.0                   # plate centre height (standing on its edge, z 0..60)
    plate = rrect_y(0, ZC, 60, 60, 3.0, 0, T)                       # back face y 0, front face y 2.5
    tbm.booleanOperation(plate, rrect_y(0, ZC, 40, 40, 1.0, T - G, T + 0.1), DIFF)   # recess floor at y 1.8
    zone = 10.0                 # glue-patch half size (20 x 20)
    for sx in (-1, 1):
        for sz in (-1, 1):
            cx, cz = sx * zone, ZC + sz * zone
            y0, y1 = T - G - 0.4, T - G + 0.1                            # 0.4 deep into the recess floor
            tbm.booleanOperation(plate, box(cx - 3.0 * sx, cx + 0.8 * sx, y0, y1, cz, cz + 0.8 * sz), DIFF)
            tbm.booleanOperation(plate, box(cx, cx + 0.8 * sx, y0, y1, cz - 3.0 * sz, cz + 0.8 * sz), DIFF)

    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    des = adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
    des.designType = adsk.fusion.DesignTypes.DirectDesignType
    comp = des.rootComponent
    body = comp.bRepBodies.add(plate)
    body.name = 'HA_coupon_wall2p5'

    out = {'volume_mm3': round(body.volume * 1000, 2)}
    bb = body.boundingBox
    out['bbox_mm'] = [round(v * 10, 2) for v in (bb.minPoint.x, bb.maxPoint.x, bb.minPoint.y, bb.maxPoint.y,
                                                bb.minPoint.z, bb.maxPoint.z)]
    INS = (adsk.fusion.PointContainment.PointInsidePointContainment,)

    def inside(x, y, z):
        return body.pointContainment(P3(x / 10, y / 10, z / 10)) in INS

    out['probes'] = {
        'recess_floor_y1.75_in': inside(0, 1.75, ZC), 'recess_y1.85_out': not inside(0, 1.85, ZC),
        'rim_y2.45_in': inside(25, 2.45, ZC), 'back_y0.05_in': inside(0, 0.05, ZC),
        'tick_y1.6_out': not inside(10.4, 1.6, ZC + 10.4), 'under_tick_y1.3_in': inside(10.4, 1.3, ZC + 10.4),
        'zone_centre_y1.6_in': inside(0, 1.6, ZC), 'corner_R3_out': not inside(29.5, 1.0, 0.5),
        'corner_R3_flat_in': inside(26.0, 1.0, 0.5)}
    out['faces'] = body.faces.count

    em = des.exportManager
    docs = os.path.expanduser('~/Documents')
    p3mf = os.path.join(docs, 'HA_coupon_wall2p5.3mf')
    pstl = os.path.join(docs, 'HA_coupon_wall2p5.stl')
    o = em.createC3MFExportOptions(body, p3mf)
    o.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
    out['3mf'] = em.execute(o)
    o = em.createSTLExportOptions(body, pstl)
    o.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
    o.isBinaryFormat = True
    out['stl'] = em.execute(o)
    out['files'] = {p: os.path.getsize(p) for p in (p3mf, pstl) if os.path.exists(p)}

    doc.close(False)
    if app.activeDocument != panel:
        panel.activate()
    out['active_after'] = app.activeDocument.name
    log('v5f_b0_coupon', 'coupon', out)
    print(json.dumps(out))
