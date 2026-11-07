# rev F e2e (2026-11-08): read-only - version and description of "HA Panel v5 - tapered" after e2d, the main-board
#   bodies' volumes and positions, read without activating the design. Writes board_zone/e2e_status.json.
import adsk.core, adsk.fusion, json, math, os, time, traceback
C = math.cos(math.radians(12.0)); S = math.sin(math.radians(12.0)); H = 143.3; XC = -2.55
OUT = os.path.expanduser('~/Documents/HA_panel_renders/board_zone/e2e_status.json')


def run(_context):
    st = {'t0': time.strftime('%H:%M:%S')}
    try:
        app = adsk.core.Application.get()
        doc = [d for d in app.documents if d.name == 'HA Panel v5 - tapered'][0]
        df = doc.dataFile
        st['version'] = [df.versionNumber, df.latestVersionNumber]
        try:
            st['description'] = df.description
        except Exception:
            st['description'] = None
        try:
            v = df.versions
            st['last_versions'] = [[v.item(i).versionNumber, v.item(i).description[:80]] for i in range(min(v.count, 3))]
        except Exception as e:
            st['last_versions'] = str(e)[:120]
        st['modified'] = doc.isModified
        des = adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
        rows = {}
        for b in des.rootComponent.bRepBodies:
            if b.name.startswith('MAIN_'):
                bb = b.boundingBox
                rows[b.name] = [round(b.volume, 4), b.isLightBulbOn, round(bb.minPoint.x * 10 - XC, 2), round(bb.maxPoint.x * 10 - XC, 2)]
        st['main'] = rows
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    json.dump(st, open(OUT, 'w'), indent=1)
    print(json.dumps(st))


run(None)
