# rev F f0b (2026-11-09): floor plate pass, block 0 - read-only check after closing without saving and reopening version 42
#   from the hub (Daniel 23:2x: "close and reopen v42"). Version, modified flag, body count, AUD_* bodies, guard volumes of
#   the 14 printed parts (names and visibility for all, volumes only for the guards - f0a's full pass took 200 s).
#   Writes ~/Documents/HA_panel_renders/fp/f0b_status.json. Loader per README lesson 86; readOnly.
import adsk.core, adsk.fusion, json, os, time, traceback
OUT = os.path.expanduser('~/Documents/HA_panel_renders/fp')
GUARD = {'HOUSING_F_front': 235.9107, 'HOUSING_F_door': 47.0198, 'HOUSING_F_door_e6': 47.2633, 'HOUSING_F_cap': 9.9441,
         'SLAB_frame': 62.9324, 'SPKBOX_L': 25.6082, 'SPKBOX_R': 26.3874, 'MAIN_BRACKET': 6.5563, 'RESP_CARRIER': 10.1214,
         'CRADLE_5807': 2.1898, 'GROMMET_usbc_F': 0.5062, 'BME_HOOD': 0.8029, 'TOUCH_CLIP_L': 0.4896,
         'TOUCH_CLIP_R': 0.4896}


def run(_context):
    st = {'t0': time.strftime('%Y-%m-%d %H:%M:%S')}
    t0 = time.time()
    try:
        app = adsk.core.Application.get()
        st['docs'] = [[d.name, d.isModified, d.isSaved] for d in app.documents]
        st['active'] = app.activeDocument.name if app.activeDocument else None
        doc = [d for d in app.documents if d.name == 'HA Panel v5 - tapered'][0]
        st['version'] = [doc.dataFile.versionNumber, doc.dataFile.latestVersionNumber]
        st['modified'] = doc.isModified
        des = adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
        root = des.rootComponent
        names = [b.name for b in root.bRepBodies]
        st['n_bodies'] = len(names)
        st['AUD'] = [n for n in names if n.upper().startswith('AUD')]
        st['visible'] = sorted(b.name for b in root.bRepBodies if b.isLightBulbOn)
        g = {}
        for b in root.bRepBodies:
            if b.name in GUARD and b.name not in g:
                g[b.name] = [round(b.volume, 4), GUARD[b.name], abs(b.volume - GUARD[b.name]) <= 0.0005, b.lumps.count]
        st['guard'] = g
        st['guard_ok'] = len(g) == len(GUARD) and all(v[2] for v in g.values())
        st['modified_after'] = doc.isModified
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    st['t_s'] = round(time.time() - t0, 1)
    json.dump(st, open(os.path.join(OUT, 'f0b_status.json'), 'w'), indent=1)
    print(json.dumps({k: st.get(k) for k in ('version', 'modified', 'modified_after', 'n_bodies', 'AUD', 'guard_ok', 'FAIL', 't_s')}))


run(None)
