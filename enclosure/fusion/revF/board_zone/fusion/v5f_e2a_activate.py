# rev F e2a (2026-11-08): activate "HA Panel v5 - tapered" for the main-board rev 2 body update (e2b needs it active).
#   Writes ~/Documents/HA_panel_renders/board_zone/e2a_status.json (before / after, timing). Changes no design.
import adsk.core, adsk.fusion, json, os, time, traceback
OUT = os.path.expanduser('~/Documents/HA_panel_renders/board_zone')


def run(_context):
    app = adsk.core.Application.get()
    st = {'t0': time.strftime('%H:%M:%S'), 'active_before': app.activeDocument.name}
    t0 = time.time()
    try:
        doc = [d for d in app.documents if d.name == 'HA Panel v5 - tapered'][0]
        st['modified_before'] = doc.isModified
        st['version'] = [doc.dataFile.versionNumber, doc.dataFile.latestVersionNumber]
        if app.activeDocument.name != doc.name:
            doc.activate()
        st['active_after'] = app.activeDocument.name
        st['t_s'] = round(time.time() - t0, 1)
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    json.dump(st, open(os.path.join(OUT, 'e2a_status.json'), 'w'))
    print(json.dumps(st))


run(None)
