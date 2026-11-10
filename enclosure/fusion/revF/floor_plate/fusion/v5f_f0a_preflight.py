# rev F f0a (2026-11-09): floor plate pass, block 0 preflight - read-only.
#   Document state (open documents, version, latest version, recent version descriptions, modified flag), AUD_* bodies,
#   every body (name, visible, cm3, lumps, conservative world bbox from the 8 design-AABB corners, x_rel), duplicate
#   "name (n)" bodies, guard volumes of the printed parts at version 42 (e6). Reads the design without activating it.
#   Writes ~/Documents/HA_panel_renders/fp/f0a_status.json and fp/bodies_now.json.
#   Loader (README lesson 86): exec in its own namespace (this file calls run(None) itself), then a no-op run(); readOnly.
import adsk.core, adsk.fusion, json, math, os, time, traceback
C = math.cos(math.radians(12.0)); S = math.sin(math.radians(12.0)); H = 143.3; XC = -2.55
OUT = os.path.expanduser('~/Documents/HA_panel_renders/fp')
GUARD = {'HOUSING_F_front': 235.9107, 'HOUSING_F_door': 47.0198, 'HOUSING_F_door_e6': 47.2633, 'HOUSING_F_cap': 9.9441,
         'SLAB_frame': 62.9324, 'SPKBOX_L': 25.6082, 'SPKBOX_R': 26.3874, 'MAIN_BRACKET': 6.5563, 'RESP_CARRIER': 10.1214,
         'CRADLE_5807': 2.1898, 'GROMMET_usbc_F': 0.5062, 'BME_HOOD': 0.8029, 'TOUCH_CLIP_L': 0.4896,
         'TOUCH_CLIP_R': 0.4896}


def wpt(x, y, z):                       # design cm -> world mm (x_rel, y, z)
    return (x * 10 - XC, (y * C - z * S) * 10, H + (y * S + z * C) * 10)


def run(_context):
    st = {'t0': time.strftime('%Y-%m-%d %H:%M:%S')}
    t0 = time.time()
    try:
        os.makedirs(OUT, exist_ok=True)
        app = adsk.core.Application.get()
        st['docs'] = [[d.name, d.isModified, d.isSaved] for d in app.documents]
        st['active'] = app.activeDocument.name if app.activeDocument else None
        doc = [d for d in app.documents if d.name == 'HA Panel v5 - tapered'][0]
        df = doc.dataFile
        st['version'] = [df.versionNumber, df.latestVersionNumber]
        try:
            v = df.versions
            st['versions'] = [[v.item(i).versionNumber, v.item(i).description[:240]] for i in range(v.count)
                              if v.item(i).versionNumber >= 40]
        except Exception as e:
            st['versions'] = str(e)[:150]
        st['modified'] = doc.isModified
        des = adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType'))
        st['designType'] = des.designType
        root = des.rootComponent
        st['occurrences'] = root.allOccurrences.count
        rows = []
        for b in root.bRepBodies:
            bb = b.boundingBox
            pts = [wpt(x, y, z) for x in (bb.minPoint.x, bb.maxPoint.x) for y in (bb.minPoint.y, bb.maxPoint.y)
                   for z in (bb.minPoint.z, bb.maxPoint.z)]
            rows.append({'name': b.name, 'vis': b.isLightBulbOn, 'cm3': round(b.volume, 4), 'lumps': b.lumps.count,
                         'lo': [round(min(p[k] for p in pts), 1) for k in range(3)],
                         'hi': [round(max(p[k] for p in pts), 1) for k in range(3)]})
        json.dump(rows, open(os.path.join(OUT, 'bodies_now.json'), 'w'), indent=0)
        names = [r['name'] for r in rows]
        st['n_bodies'] = len(rows)
        st['n_visible'] = sum(1 for r in rows if r['vis'])
        st['AUD'] = [[r['name'], r['vis'], r['cm3']] for r in rows if r['name'].upper().startswith('AUD')]
        st['dup_named'] = sorted(n for n in names if n.endswith(')'))
        st['dup_exact'] = sorted(set(n for n in names if names.count(n) > 1))
        byname = {}
        for r in rows:
            byname.setdefault(r['name'], r)
        st['guard'] = {k: [byname[k]['cm3'] if k in byname else None, v,
                           bool(k in byname and abs(byname[k]['cm3'] - v) <= 0.0005)] for k, v in GUARD.items()}
        st['guard_ok'] = all(g[2] for g in st['guard'].values())
        st['visible'] = sorted([r['name'], r['cm3']] for r in rows if r['vis'])
        st['sketches'] = root.sketches.count
        st['planes'] = root.constructionPlanes.count
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    st['t_s'] = round(time.time() - t0, 1)
    json.dump(st, open(os.path.join(OUT, 'f0a_status.json'), 'w'), indent=1)
    print(json.dumps({k: st.get(k) for k in ('version', 'modified', 'docs', 'n_bodies', 'n_visible', 'AUD', 'dup_named',
                                             'dup_exact', 'guard_ok', 'FAIL', 't_s')}))


run(None)
