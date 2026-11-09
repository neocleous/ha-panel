# rev F e5f (2026-11-09): read-only - version and description of "HA Panel v5 - tapered" after e5e, the new J10 leads and
#   their hidden old copies (volume, lumps, visibility), the f3d's size and time. Read without activating the design.
#   Writes e5/e5f_status.json. Load with a no-op run() after the exec: the MCP wrapper calls run(context) itself and rolls a
#   script back when that call fails.
import adsk.core, adsk.fusion, json, math, os, time, traceback
OUT = os.path.expanduser('~/Documents/HA_panel_renders/e5/e5f_status.json')
NAMES = ('LEAD_BME680', 'LEAD_VEML', 'LEAD_BME680_e5', 'LEAD_VEML_e5', 'HOUSING_F_front', 'HOUSING_F_cap', 'MAIN_BRACKET',
         'RESP_CARRIER', 'CRADLE_5807')


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
            st['last_versions'] = [[v.item(i).versionNumber, v.item(i).description[:200]] for i in range(v.count)
                                   if v.item(i).versionNumber >= 40]
        except Exception as e:
            st['last_versions'] = str(e)[:120]
        st['modified'] = doc.isModified
        des = adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
        st['bodies'] = {b.name: {'cm3': round(b.volume, 4), 'lumps': b.lumps.count, 'visible': b.isLightBulbOn}
                        for b in des.rootComponent.bRepBodies if b.name in NAMES}
        st['n_bodies'] = des.rootComponent.bRepBodies.count
        p = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-e5.f3d')
        st['f3d'] = [os.path.getsize(p), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(p)))]
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    json.dump(st, open(OUT, 'w'), indent=1)
    print(json.dumps(st))


run(None)
