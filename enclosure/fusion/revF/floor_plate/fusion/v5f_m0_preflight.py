# rev F m0 (2026-11-12): ribbon pass, block 0 - preflight (brief claude/brief-enclosure-ribbon-pass-2026-11-12.md).
#   Read-only. Each function below is the body of one connector call (featureType script, readOnly true), as run.
#   Between a() and b() the document was closed without saving and opened again through the connector
#   (document close with userConfirmedCloseWithoutSave, then document open by the lineage id).
#   The library v5f_k_lib.py was still in Fusion's memory as sys.modules['v5f_k'] (sha256 adc99aca...6d56bb), with its caches.
#   Results (2026-11-12 23:2x):
#     a  version 60 of 60, modified True, 386 bodies, 36 visible, no AUD_* body; ~/Documents/HA_panel_renders/adt-link/ does not exist
#     b  version 60 of 60, modified False, 386 bodies, 96 the unit (16 leads, 13 key paths), 36 visible, no AUD_*, no duplicate name;
#        volumes front shell 200363.6, left box 26051.9, right box 26769.4, carrier 12404.3, base plate 32452.3, door 47019.8, cap 9944.1
#     c  board frame: RESP_usbc_plug_env u 42.78..74.78, v 1.01..13.41, w -10.59..-3.99; RESP_top_env ends u 42.78 (the socket's face);
#        MAIN_pcb u -43.5..43.5, w -1.6..-0.09 (a full rectangle at v -6..22); KO_K5_UL u 44.05..51.05, v 5.49..37.19, w -17.38..39.96;
#        KO_K5_LL u 44.05..51.05, v -37.15..11.45, w -17.38..76.21; LCD_DSI_conn u 39.35..44.25, v -11.48..11.32, w -25.3..-23.4;
#        world: USBA_plug_env x 45.15..55.15, y -45.0..-22.9, z 10.2..18.2 (1250.7 mm3, 8 faces); USBA_cable_env x 50..54, y -53.5..-45, z 12.2..16.2
#     d  no file or folder named like the maker's models (ut2g, ut1g, ust2, adt-link, us1c, us3k, us3j) within four levels of ~/Documents
import adsk.core, adsk.fusion, sys, os, time


def a(_context):                                     # state before closing; the maker's models
    app = adsk.core.Application.get()
    doc = app.activeDocument; df = doc.dataFile
    root = adsk.fusion.Design.cast(app.activeProduct).rootComponent
    names = [b.name for b in root.bRepBodies]
    print('doc', doc.name, '| version', df.versionNumber, 'latest', df.latestVersionNumber, '| modified', doc.isModified, '| bodies', len(names),
          '| visible', sum(1 for b in root.bRepBodies if b.isLightBulbOn))
    print('AUD/NEW/RENDER_TMP:', [n for n in names if n.upper().startswith(('AUD_', 'NEW_', 'RENDER_TMP'))])
    print('modules:', sorted(m for m in sys.modules if m.startswith(('v5f', 'aud'))))
    d = os.path.expanduser('~/Documents/HA_panel_renders/adt-link')
    print('adt-link dir exists:', os.path.isdir(d))
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            print('  ', f, os.path.getsize(os.path.join(d, f)))


def b(_context):                                     # state after reopening version 60; the unit's bodies; the printed parts' volumes
    k = sys.modules['v5f_k']
    X = k.K(); k.budget(40)
    print('state', X.state())
    print('description:', X.doc.dataFile.description)
    cur = k.current(X, leads=True)
    print('unit bodies', len(cur), '| leads', sum(1 for q in cur if q.name.startswith('LEAD_')), '| KO', sum(1 for q in cur if q.name.startswith('KO_')))
    for n in ('HOUSING_F_front', 'SPKBOX_L', 'SPKBOX_R', 'RESP_CARRIER', 'FLOOR_PLATE', 'HOUSING_F_door', 'HOUSING_F_cap'):
        q = X.body(n)
        print('vol', n, round(q.volume * 1000.0, 1), 'lumps', q.lumps.count)


def c(_context):                                     # what stands round the ReSpeaker's USB socket (board frame) and the USB-A plug at the Pi (world)
    k = sys.modules['v5f_k']
    X = k.K(); k.budget(45)

    def bl(name, box, n=12):                         # lumps of a body inside a board-frame box, as board-frame boxes + mm3
        if X.body(name) is None:
            return 'no body'
        t = X.bbox(*box)
        X.tbm.booleanOperation(t, k.tcopy(X, name), k.BT.IntersectionBooleanType)
        out = []
        for l in t.lumps:
            q = l.boundingBox; p0 = k.Bf(q.minPoint); p1 = k.Bf(q.maxPoint)
            out.append([round(v, 2) for v in (p0[0], p1[0], p0[1], p1[1], p1[2], p0[2])] + [round(l.volume * 1000.0, 1)])
        return sorted(out)[:n]
    R = (30.0, 60.0, -6.0, 22.0, -30.0, 40.0)
    for n in ('RESP_pcb', 'RESP_top_env', 'RESP_usbc_plug_env', 'RESP_mic_env', 'RESP_CARRIER', 'MAIN_pcb', 'MAIN_conn', 'MAIN_low', 'MAIN_tall',
              'MAIN_plug_env', 'KO_K5_UL', 'LEAD_MIC_L', 'LEAD_DSI', 'LEAD_LCD_5V'):
        print(n, bl(n, R))
    for n in ('RESP_usbc_plug_env', 'RESP_pcb', 'MAIN_pcb', 'KO_K5_UL', 'KO_K5_LL', 'LCD_DSI_conn_d9.3', 'RESP_CARRIER'):
        print('bbb', n, k.bbb(X.body(n)))
    for n in ('USBA_plug_env', 'USBA_cable_env'):
        q = X.body(n)
        print('wbb', n, k.wbb(X, q), 'vol', round(q.volume * 1000.0, 1), 'lumps', q.lumps.count, 'faces', q.faces.count)


def d(_context):                                     # the maker's models anywhere under ~/Documents (four levels, 20 s)
    t0 = time.time()
    root = os.path.expanduser('~/Documents'); hits = []
    for dp, dn, fn in os.walk(root):
        if dp[len(root):].count(os.sep) >= 4:
            dn[:] = []
        dn[:] = [q for q in dn if not q.startswith('.') and not q.endswith(('.app', '.photoslibrary'))]
        for f in fn + dn:
            if any(q in f.lower() for q in ('ut2g', 'ut1g', 'ust2', 'adt-link', 'adtlink', 'adt_link', 'us1c', 'us3k', 'us3j')):
                hits.append(os.path.join(dp, f)[len(root):])
        if time.time() - t0 > 20:
            print('stopped on time'); break
    print('hits', hits)


def run(_context):                                   # the connector calls run(); nothing happens when this file is loaded as a whole
    pass
