# rev F e1a (2026-11-07): main board outline question - read-only body list of "HA Panel v5 - tapered" without activating it.
#   Writes ~/Documents/HA_panel_renders/board_zone/bodies.json: name, visible, volume cm3, world bbox (x_rel, y, z; 8 corners of
#   the design AABB, so conservative), for every body in the root component.
import adsk.core, adsk.fusion, json, math, os, time, traceback
C = math.cos(math.radians(12.0)); S = math.sin(math.radians(12.0)); H = 143.3; XC = -2.55
OUT = os.path.expanduser('~/Documents/HA_panel_renders/board_zone')


def wpt(x, y, z):                       # design cm -> world mm (x_rel, y, z)
    return (x * 10 - XC, (y * C - z * S) * 10, H + (y * S + z * C) * 10)


def find_design():
    app = adsk.core.Application.get()
    for i in range(app.documents.count):
        d = app.documents.item(i)
        if d.name == 'HA Panel v5 - tapered':
            return d, adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType'))
    raise RuntimeError('design document not open')


def run(_context):
    out = {'t0': time.strftime('%H:%M:%S')}
    try:
        os.makedirs(OUT, exist_ok=True)
        doc, des = find_design()
        out['doc'] = {'modified': doc.isModified, 'version': doc.dataFile.versionNumber, 'latest': doc.dataFile.latestVersionNumber}
        comp = des.rootComponent
        rows = []
        for b in comp.bRepBodies:
            bb = b.boundingBox
            pts = [wpt(x, y, z) for x in (bb.minPoint.x, bb.maxPoint.x) for y in (bb.minPoint.y, bb.maxPoint.y)
                   for z in (bb.minPoint.z, bb.maxPoint.z)]
            lo = [round(min(p[k] for p in pts), 2) for k in range(3)]
            hi = [round(max(p[k] for p in pts), 2) for k in range(3)]
            rows.append({'name': b.name, 'vis': b.isLightBulbOn, 'vol': round(b.volume, 4), 'lo': lo, 'hi': hi,
                         'lumps': b.lumps.count})
        json.dump(rows, open(os.path.join(OUT, 'bodies.json'), 'w'), indent=0)
        out['n'] = len(rows)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    json.dump(out, open(os.path.join(OUT, 'e1a_status.json'), 'w'))
    print(json.dumps(out))


run(None)
