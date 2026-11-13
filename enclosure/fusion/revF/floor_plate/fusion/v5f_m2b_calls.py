# rev F m2b (2026-11-13): ribbon pass, block 2 - the connector calls as run, in order. Each function is the body of one call's run().
#   k = sys.modules['v5f_k'], m = sys.modules['v5f_m'] (v5f_m_lib.py, sha256 6da5a524...2ede6), s1 = the namespace of v5f_m1_behind_display.py
#   (sha256 5dfa0880...1f2b45), s2 = the namespace of v5f_m2_rest.py (commit c0c0165, sha256 7c5980f7...cb0cb5) with s1 in its globals.
#   check() and margins() are read-only; the others change the model.
#   Results: version 62 "rev F WIP 2026-11-13 g17 ...", 391 bodies (389 + LEAD_SPK_L_v60 and USBA_plug_env_v60; USBA_cable_env renamed
#   USBA_cable_env_v60 and hidden), 36 visible, 95 bodies in the unit, archive ~/Documents/HA Panel v5 - tapered revF-g17.f3d (173 103 280 bytes).
import adsk.core, adsk.fusion, sys, os, time
REF = {'HOUSING_F_front': 200363.6, 'SPKBOX_L': 26051.9, 'SPKBOX_R': 26769.4, 'RESP_CARRIER': 12404.3, 'FLOOR_PLATE': 32452.3,
       'HOUSING_F_door': 47019.8, 'HOUSING_F_cap': 9944.1}


def check(X, k, m, s2):                              # the four bodies against every current body, against each other, at 288, and the shortest way
    obs = m.obstacles(X, skip=s2['NEW'])
    gap = lambda a, b: round(X.mm.measureMinimumDistance(a, b).value * 10.0, 2)
    sol, cb, rb, pl, sl, Ls = s2['solids'](X)
    for n, tb in sol.items():
        print(n, 'lumps', tb.lumps.count, 'vol', round(tb.volume * 1000.0, 1))
    print('cable L', round(cb.L, 2), 'h', round(cb.h, 2), 'ribbon L', round(rb.L, 2), 'a', round(rb.a, 2), 'spk L', Ls)
    print('CABLE: ' + m.table(m.clear(X, cb.pieces, obs, lim=3.0), 30))
    for lab, p in pl + sl:
        print('usba.%s: %s' % (lab, m.table(m.clear(X, [(lab, p)], obs, lim=3.0), 8)))
    print('SPK: ' + m.table(m.clear(X, [('spk', sol['LEAD_SPK_L'])], obs, lim=3.0), 12))
    print('RIBBON: ' + m.table(m.clear(X, rb.pieces, obs, lim=3.0), 30))
    nm = list(sol)
    for i in range(len(nm)):
        for j in range(i + 1, len(nm)):
            print('  %s - %s %.2f' % (nm[i], nm[j], gap(sol[nm[i]], sol[nm[j]])))
    p88 = dict(s2['P2']); p88['Lc'] = 288.0; c88 = s2['cable'](X, None, p88)
    print('288: h', round(c88.h, 2), m.table(m.clear(X, c88.pieces, obs, lim=3.0), 12))
    cd = s2['cable'](X, None, s2['P2'], None, True)
    print('direct L', round(cd.L, 2))
    m.c['b2'] = {'cable': cb, 'ribbon': rb, 'plug': pl, 'sleeve': sl}
    # results (300 / 200):
    #   cable 300.0 (lanes' straight length 23.39; 20.39 at 288), 1 lump, 2340.6 mm3. Nearest: left box's rear wall 0.64 (all lanes), shell 0.81 and
    #     upper-left display screw's key path 0.95 at the top fold (block 1), lower-left key path 1.29 at the drop, plate's anchor 1.81 under the
    #     roll, shell 1.73 / door 3.13 where the cable goes round the roll, shell 1.80 at lane 1. The same at 288.
    #   USB-A plug 692.1 mm3: shell 0.59 from the Pi (its own port), board 0.49 from the left box (pocket's front wall), bare back wall 2.00 from
    #     the box and 2.46 from the left driver, pin ends 2.02 from the driver, sleeve 0.87 from the box and 2.97 from the Ethernet jack's face.
    #   ribbon 200.0 (arch 3.84 high over the Pi's connector; 185.64 the shortest way), 1 lump, 1286.0 mm3: cooler's envelope 23.97 mm3, its two
    #     connectors 19.46 and 13.89 mm3, display's component blanket 0.10, left speaker plug's envelope 0.30 (its front edge, z 83.9),
    #     LCD board 1.50, Pi power cable's lap 2.26 (arch), main board's tall parts 2.41, fan's keep-out 2.84, ReSpeaker 2.90, main board 2.90.
    #   left speaker lead 83.2 as laid (75.9 before), 671.1 mm3: its own plug's envelope 90.10 mm3 (as before), left box 0.85.
    #   cable - ribbon 5.12, cable - speaker lead 0.66 (where the lead passes between lanes 3 and 4 to the box's wire hole), ribbon - speaker
    #     lead 2.58, cable - its USB-A plug 0.00 (it ends on the sleeve's end), USB-C plug - ribbon 2.59. The shortest way of the cable: 130.08.


def commit(X, k, m, s2):                             # model change
    st = X.state()
    if st['version'] != 61 or st['bodies'] != 389 or st['templates'] or st['modified'] or X.body('LEAD_SPK_L_v60') is not None:
        raise RuntimeError('unexpected state %s' % st)
    names = ('LEAD_USB_RESP', 'LEAD_DSI', 'USBA_plug_env', 'LEAD_SPK_L', 'USBA_cable_env')
    vis = {n: X.body(n).isLightBulbOn for n in names}                    # all five hidden at version 61
    print({n: [round(X.body(n).volume * 1000.0, 1), [round(v, 2) for v in k.wbb(X, X.body(n))]] for n in names[2:]})
    # before: USBA_plug_env 1250.7 mm3, x 45.15..55.15, y -45.0..-22.9, z 10.2..18.2; USBA_cable_env 106.8, x 50..54, y -53.5..-45, z 12.2..16.2;
    #         LEAD_SPK_L 611.8
    print(s2['commit'](X))                           # ({'LEAD_USB_RESP': 2340.6, 'LEAD_DSI': 1286.0, 'USBA_plug_env': 692.1, 'LEAD_SPK_L': 671.1,
    for n in names[:4]:                              #   'USBA_cable_env': 'retired'}, 300.0, 200.0, 83.2)
        X.body(n).isLightBulbOn = vis[n]


def picture(X, k, m, view):                          # templates in colour, a few bodies, an orthographic camera; then the connector's screenshot query
    if 'vis0' not in m.c:
        m.c['vis0'] = [b.name for b in X.root.bRepBodies if b.isLightBulbOn]
    for src, nm, col in (('LEAD_DSI', 'dsi', 'Plastic - Matte (Yellow)'), ('LEAD_USB_RESP', 'usb', 'Paint - Enamel Glossy (Red)'),
                         ('RESP_usbc_plug_env', 'plug', 'Paint - Enamel Glossy (Blue)'), ('USBA_plug_env', 'usba', 'Paint - Enamel Glossy (Blue)'),
                         ('LEAD_SPK_L', 'spk', 'Plastic - Matte (Green)')):
        m.put(X, X.tbm.copy(X.body(src)), nm, col)
    want, T, e, ext = {
        'door': ({'SPKBOX_L', 'PI5_F', 'PI5_F_cooler', 'FLOOR_PLATE', 'MAIN_pcb', 'LCD_pcb_76x110', 'RESP_pcb', 'RESP_CARRIER', 'MAIN_plug_env',
                  'PIPWR_a_env'}, (40.0, -45.0, 58.0), (0.45, -1.0, 0.35), 13.0),                    # block2_leads_from_door.png
        'roll': ({'PI5_F', 'PI5_F_cooler', 'FLOOR_PLATE', 'PIPWR_a_env'}, (48.0, -42.0, 30.0), (1.0, -0.9, 0.45), 8.0),   # block2_roll_and_usba_plug_left_box_hidden.png
    }[view]
    for b in X.root.bRepBodies:
        on = b.name in want or b.name.startswith('AUD_')
        if b.isLightBulbOn != on:
            b.isLightBulbOn = on
    k.cam(X, m.add(T, m.mul(m.unit(e), 500.0)), T, ext=ext, up=(0, 0, 1))
    adsk.doEvents()


def tidy(X, k, m):                                   # templates out, visibility back, the printed parts' volumes against version 60: all seven equal
    X.wipe('AUD_')
    want = set(m.c['vis0'])
    for b in X.root.bRepBodies:
        on = b.name in want
        if b.isLightBulbOn != on:
            b.isLightBulbOn = on
    for q, v in REF.items():
        b = X.body(q)
        print(q, round(b.volume * 1000.0, 1), 'ok' if abs(b.volume * 1000.0 - v) < 0.05 and b.lumps.count == 1 else 'DIFFERS')
    print(X.state(), 'unit', len(k.current(X, leads=True)))           # 391 bodies, 36 visible, unit 95


def save(X, k):                                      # its own call; the version number is read back in a later call (62 of 62, unmodified)
    st = X.state()
    if st['templates'] or st['dups'] or st['bodies'] != 391 or st['version'] != 61 or st['visible'] != 36:
        raise RuntimeError('guard: %s' % st)
    print(X.doc.save('rev F WIP 2026-11-13 g17: ribbon pass block 2 - DSI ribbon to the Pi (200), USB cable at 300 with its spare as a flat roll '
                     'behind the left box, ADT USB-A plug from the sheet, left speaker lead re-laid; block 3 checks not yet run; not for print'))


def export(X, k):                                    # its own call
    f3d = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-g17.f3d'); new = f3d[:-4] + ' new.f3d'
    em = X.des.exportManager
    ok = em.execute(em.createFusionArchiveExportOptions(new))
    if ok and os.path.exists(new) and os.path.getsize(new) > 50e6:
        os.replace(new, f3d)
    print(ok, os.path.getsize(f3d))                  # True 173103280


def margins(X, k, m):                                # read-only: each part of the cable from the drop on, and of the ribbon from its drop on, against
    b2 = m.c['b2']                                   # the shell, the door, the plate, the Pi, the Pi power cable and the key paths, up to 9
    obs = [q for q in m.obstacles(X, skip=('LEAD_DSI', 'LEAD_USB_RESP', 'RESP_usbc_plug_env', 'USBA_plug_env', 'LEAD_SPK_L'))
           if q[0] in ('HOUSING_F_front', 'HOUSING_F_door', 'FLOOR_PLATE', 'PI5_F', 'SPK_L', 'LEAD_PI_POWER', 'PIPWR_a_env', 'KO_K5_LL', 'KO_capkey_SL')]
    for s in (b2['cable'], b2['ribbon']):
        i0 = [i for i, q in enumerate(s.pieces) if q[0] == 'drop'][0]
        for lab, p in s.pieces[i0:]:
            r = m.clear(X, [(lab, p)], obs, lim=9.0, vols=False)
            print('%-26s %s' % (lab, ' '.join('%s %.2f' % (k.sn(q), v[0]) for q, v in sorted(r.items()))))


def run(_context):
    pass
