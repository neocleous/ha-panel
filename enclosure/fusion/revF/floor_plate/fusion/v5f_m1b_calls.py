# rev F m1b (2026-11-12/13): ribbon pass, block 1 - the connector calls as run, in order. Each function is the body of one call's run().
#   k = sys.modules['v5f_k'], m = sys.modules['v5f_m'] (v5f_m_lib.py, commit 2063356 then ca0cfee), s1 = the namespace of
#   v5f_m1_behind_display.py (commit ca0cfee, sha256 5dfa0880...1f2b45). check() and near() are read-only; the others change the model.
#   Results: version 61 "rev F WIP 2026-11-12 g16 ...", 389 bodies (386 + the three *_v60 backups), 36 visible, archive
#   ~/Documents/HA Panel v5 - tapered revF-g16.f3d (172 751 785 bytes).
import adsk.core, adsk.fusion, sys, os, time
SKIP = ('LEAD_DSI', 'LEAD_USB_RESP', 'RESP_usbc_plug_env')
REF = {'HOUSING_F_front': 200363.6, 'SPKBOX_L': 26051.9, 'SPKBOX_R': 26769.4, 'RESP_CARRIER': 12404.3, 'FLOOR_PLATE': 32452.3,
       'HOUSING_F_door': 47019.8, 'HOUSING_F_cap': 9944.1}


def check(X, k, m, s1):                              # the three new bodies against every current body of version 60; the sheet's reference (g = 0)
    obs = m.obstacles(X, skip=SKIP)
    sol, pl, cb, rb = s1['solids'](X)
    for n, tb in sol.items():
        print(n, 'lumps', tb.lumps.count, 'vol', round(tb.volume * 1000.0, 1))
    for lab, p in pl:
        print('plug.%s: %s' % (lab, m.table(m.clear(X, [(lab, p)], obs, lim=1.5), 6)))
    print('CABLE: ' + m.table(m.clear(X, cb.pieces, obs, lim=3.0), 16))
    print('RIBBON: ' + m.table(m.clear(X, rb.pieces, obs, lim=3.0), 24))
    pv0 = dict(s1['PV']); pv0['g'] = 0.0
    for lab, p in s1['plug'](X, pv0):
        print('g=0 plug.%s: %s' % (lab, m.table(m.clear(X, [(lab, p)], obs, lim=1.5), 6)))
    m.c['b1'] = {'plug': pl, 'cable': cb, 'ribbon': rb}
    # results: plug sleeve 0.20 and its cable 0.26 from the main board's side edge (g 0.92); at g = 0 they are 8.05 and 5.23 mm3 inside it.
    #          cable: shell 0.81 and upper-left display screw's key path 0.95 at the fold, door 2.21. ribbon: its own connector 19.46 mm3,
    #          left speaker plug's envelope 0.63 at the drop, main board's tall parts 2.41, ReSpeaker 2.90, board 2.90.


def commit(X, k, m, s1):                             # model change
    st = X.state()
    if st['version'] != 60 or st['bodies'] != 386 or st['templates'] or X.body('LEAD_DSI_v60') is not None:
        raise RuntimeError('unexpected state %s' % st)
    print(s1['commit'](X))                           # {'RESP_usbc_plug_env': 552.0, 'LEAD_USB_RESP': 284.3, 'LEAD_DSI': 588.3} mm3
    X.body('RESP_usbc_plug_env').isLightBulbOn = True


def picture(X, k, m, view):                          # templates in colour, the display module's boards, an orthographic camera; then the connector's screenshot query
    if 'vis0' not in m.c:
        m.c['vis0'] = [b.name for b in X.root.bRepBodies if b.isLightBulbOn]
    for src, nm, col in (('LEAD_DSI', 'dsi', 'Plastic - Matte (Yellow)'), ('LEAD_USB_RESP', 'usb', 'Paint - Enamel Glossy (Red)'),
                         ('RESP_usbc_plug_env', 'plug', 'Paint - Enamel Glossy (Blue)')):
        m.put(X, X.tbm.copy(X.body(src)), nm, col)
    want = {'LCD_pcb_76x110', 'LCD_DSI_conn_d9.3', 'RESP_CARRIER', 'RESP_pcb', 'RESP_top_env', 'MAIN_pcb', 'MAIN_low', 'MAIN_tall', 'MAIN_conn', 'MAIN_PS1'}
    for b in X.root.bRepBodies:
        on = b.name in want or b.name.startswith('AUD_')
        if b.isLightBulbOn != on:
            b.isLightBulbOn = on
    V = {'door': ((42.0, -3.0, 4.0), (0.55, 0.45, 1.0), 7.5, (0, 1, 0)),          # board-frame target, direction to the eye, extents, up
         'side': ((44.0, -3.0, 3.0), (1.0, 0.12, 0.10), 7.0, (0, 1, 0)),
         'above': ((42.0, 0.0, 2.0), (0.0, 1.0, 0.0), 6.5, (0, 0, -1))}[view]
    T = k.B2W(*V[0])
    e = m.unit(m.lin(m.lin(m.bdir(1, 0, 0), V[1][0], m.bdir(0, 1, 0), V[1][1]), 1.0, m.bdir(0, 0, 1), V[1][2]))
    k.cam(X, m.add(T, m.mul(e, 400.0)), T, ext=V[2], up=m.bdir(*V[3]))
    adsk.doEvents()


def near(X, k, m):                                   # distances up to 12 for the report, by part of each lead (table in the block 1 report)
    b1 = m.c['b1']; obs = m.obstacles(X, skip=SKIP)
    for lab, pieces in (('plug', b1['plug']), ('cable', b1['cable'].pieces), ('ribbon', b1['ribbon'].pieces)):
        r = m.clear(X, pieces, obs, lim=12.0, vols=False)
        print(lab, ' | '.join('%s %.2f@%s' % (k.sn(q), v[0], v[1]) for q, v in sorted(r.items(), key=lambda t: t[1][0])))


def tidy(X, k, m):                                   # templates out, visibility back, the printed parts' volumes against version 60
    X.wipe('AUD_')
    want = set(m.c['vis0'])
    for b in X.root.bRepBodies:
        on = b.name in want
        if b.isLightBulbOn != on:
            b.isLightBulbOn = on
    for q, v in REF.items():
        b = X.body(q)
        print(q, round(b.volume * 1000.0, 1), 'ok' if abs(b.volume * 1000.0 - v) < 0.05 and b.lumps.count == 1 else 'DIFFERS')


def save(X, k, version):                             # its own call; the version number is read back in a later call
    st = X.state()
    if st['templates'] or st['dups'] or st['bodies'] != 389 or st['version'] != 60:
        raise RuntimeError('guard: %s' % st)
    print(X.doc.save(version))


def export(X, k):                                    # its own call
    f3d = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-g16.f3d'); new = f3d[:-4] + ' new.f3d'
    em = X.des.exportManager
    ok = em.execute(em.createFusionArchiveExportOptions(new))
    if ok and os.path.exists(new) and os.path.getsize(new) > 50e6:
        os.replace(new, f3d)
    print(ok, os.path.getsize(f3d))


def run(_context):
    pass
