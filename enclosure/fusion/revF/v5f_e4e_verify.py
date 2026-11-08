# rev F e4e (2026-11-08): read-only - version and description of "HA Panel v5 - tapered" after e4d, the carrier and cradle
#   (new and hidden old copies): volume, lumps, visibility, D1.6 and D3.2 bores; the STEP files' size and time. Read without
#   activating the design. Writes m2_e4/e4e_status.json.
import adsk.core, adsk.fusion, json, math, os, time, traceback
OUT = os.path.expanduser('~/Documents/HA_panel_renders/m2_e4/e4e_status.json')
NAMES = ('RESP_CARRIER', 'CRADLE_5807', 'RESP_CARRIER_e4', 'CRADLE_5807_e4')


def run(_context):
    st = {'t0': time.strftime('%H:%M:%S')}
    try:
        app = adsk.core.Application.get()
        st['active'] = app.activeDocument.name
        doc = [d for d in app.documents if d.name == 'HA Panel v5 - tapered'][0]
        df = doc.dataFile
        st['version'] = [df.versionNumber, df.latestVersionNumber]
        try:
            v = df.versions
            st['last_versions'] = [[v.item(i).versionNumber, v.item(i).description[:120]] for i in range(min(v.count, 2))]
        except Exception as e:
            st['last_versions'] = str(e)[:120]
        st['modified'] = doc.isModified
        des = adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
        rows = {}
        for b in des.rootComponent.bRepBodies:
            if b.name in NAMES:
                n = {}
                for f in b.faces:
                    if f.geometry.objectType == adsk.core.Cylinder.classType():
                        r = round(adsk.core.Cylinder.cast(f.geometry).radius * 10, 2)
                        n[r] = n.get(r, 0) + 1
                rows[b.name] = {'vol': round(b.volume, 4), 'lumps': b.lumps.count, 'visible': b.isLightBulbOn,
                                'faces': b.faces.count, 'r0.8': n.get(0.8, 0), 'r1.6': n.get(1.6, 0)}
        st['bodies'] = rows
        st['n_bodies'] = des.rootComponent.bRepBodies.count
        st['step'] = {t: [os.path.getsize(p), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(p)))]
                      for t, p in (('resp_carrier', os.path.expanduser('~/Documents/HA_v5f_resp_carrier.step')),
                                   ('cradle_5807', os.path.expanduser('~/Documents/HA_v5f_cradle_5807.step')),
                                   ('f3d', os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-e4.f3d')))}
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    json.dump(st, open(OUT, 'w'), indent=1)
    print(json.dumps(st))


run(None)
