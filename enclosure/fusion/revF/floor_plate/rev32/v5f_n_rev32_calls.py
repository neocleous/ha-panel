# rev F n (2026-11-14): main board rev 3.2 placed - brief claude/brief-enclosure-rev3-2-placed-2026-11-14.md.
# The connector calls as run, in order. Each function is the body of one call's run(_context); the helpers at the top were typed
# into the calls that use them. Model "HA Panel v5 - tapered": version 62 -> version 63 "rev F WIP 2026-11-14 g18".
# Libraries, loaded by commit from raw.githubusercontent.com with their git blob hashes checked (load() below):
#   v5f_k = v5f_k_lib.py @fafa8fd (blob ba85884, sha256 adc99aca...6d56bb)       frames, temporary solids, slabs of the big bodies
#   v5f_m = v5f_m_lib.py @fafa8fd (blob 62790f5, sha256 6da5a524...d2ede6)       strips, obstacle crops
#   r32a  = enclosure/fusion/audit-asm/followup/aud4_lib.py @2c8c9a0 (blob 181243c, sha256 7b61cb46...72b38a), its two module names
#           sys.modules['aud4k'] / ['aud4m'] pointed at v5f_k / v5f_m: jaws(), PLIERS, service_fixed(), ride_setup(), ride()
#   r32.k4 / r32.k4b / r32.s3 = the namespaces of v5f_k4a_unit_checks.py (12006d28...), v5f_k4b_addenda.py (8607cb4d...),
#           v5f_m3b_unit_checks.py (240be32c...) @fafa8fd: matrix()
# Board frame (u, v, w) of the site document: u toward the left-speaker side, v up the board, w toward the door, w 0 = the main
# board's door-side face (the board's solid is w -1.60 .. -0.09, STEP Z 0 .. 1.51). Lengths mm, volumes mm3.
# Read-only (featureType script, readOnly true) except import32(), apply(), save(), export().
import adsk.core, adsk.fusion, sys, os, time, math, types, hashlib, urllib.request

RAW = 'https://raw.githubusercontent.com/neocleous/ha-panel/%s/%s'
F = 'enclosure/fusion/revF/floor_plate/fusion/'
A = 'fafa8fd642eefa1562c7d54543e09f5ed6784754'
B = '2c8c9a06bab60debced7e31fe4721b55c8cbd77d'
M_STEP = [1, 0, 0, -0.005, 0, 0, -1, -3.11, 0, 1, 0, -2.745, 0, 0, 0, 1]     # STEP (X = u, Y = v, Z 0 = back face) -> design, as v5f_i1b


# ---------- helpers ----------
def blob(src):
    return hashlib.sha1(b'blob %d\0' % len(src) + src).hexdigest()


def fetch(sha, path, want):
    src = urllib.request.urlopen(RAW % (sha, path), timeout=25).read()
    got = blob(src)
    if got != want:
        raise RuntimeError('blob of %s is %s' % (path, got))
    return src.decode('utf-8'), hashlib.sha256(src).hexdigest()


def load_mod(name, sha, path, want, repl=()):
    txt, h = fetch(sha, path, want)
    for a, b in repl:
        if a not in txt:
            raise RuntimeError('not found in %s: %s' % (path, a))
        txt = txt.replace(a, b)
    mod = types.ModuleType(name); sys.modules[name] = mod
    exec(compile(txt, path.split('/')[-1], 'exec'), mod.__dict__)
    return h


def load_ns(sha, path, want, g):
    txt, h = fetch(sha, path, want)
    d = {'__name__': 'r32_' + path.split('/')[-1][:-3]}; d.update(g)
    exec(compile(txt, path.split('/')[-1], 'exec'), d)
    return d, h


def dirA(a4, th, ps):                                # jaws' direction (tips -> hand): th below the screen's normal, handle ps toward the middle
    t = math.radians(th); p = math.radians(ps)     # (elevation / azimuth; reproduces the audit's 0.25 mm3 - see calibrate())
    return a4.wdir((-math.sin(p) * math.cos(t), math.cos(p) * math.cos(t), -math.sin(t)))


def notch(X, f, rr, s0, s1, ue=43.8, w0=-1.7, w1=0.0):
    # the relief as a solid through the board: floor at u f over v 1.5..13.0, arcs of radius rr on the reply's centres (43.0, 1.5) and
    # (43.0, 13.0), side walls at v s0 and s1 from u 43.0 outward. Nominal: (42.0, 1.0, 0.5, 14.0); 0.2 smaller all round: (42.2, 0.8, 0.7, 13.8)
    t = X.bbox(f, ue, 1.5, 13.0, w0, w1)
    X.uni(t, X.bbox(43.0, ue, s0, s1, w0, w1))
    X.uni(t, X.cylb(43.0, 1.5, rr, w0, w1))
    X.uni(t, X.cylb(43.0, 13.0, rr, w0, w1))
    return t


# ---------- block 0 ----------
def state_before(_context):                          # the document as found
    app = adsk.core.Application.get(); doc = app.activeDocument; df = doc.dataFile
    root = adsk.fusion.Design.cast(app.activeProduct).rootComponent
    names = [b.name for b in root.bRepBodies]
    print('version', df.versionNumber, 'latest', df.latestVersionNumber, 'modified', doc.isModified, 'bodies', len(names),
          'visible', sum(1 for b in root.bRepBodies if b.isLightBulbOn), [n for n in names if n.upper().startswith(('AUD_', 'NEW_', 'RENDER_TMP'))])
    # version 62 latest 62, modified True, 391 bodies, 36 visible, no template; the audit's modules aud4, aud4k, aud4m still in memory.
    # Then, through the connector: document close (userConfirmedCloseWithoutSave), document open by the lineage id
    # urn:adsk.wipprod:dm.lineage:OwCt3IsjSrWMOTr8NrG2Bg.


def load(_context):                                  # fresh modules under this pass's names
    load_mod('v5f_k', A, F + 'v5f_k_lib.py', 'ba8588482cd63f378ce5b98547aa702716f4855c')
    load_mod('v5f_m', A, F + 'v5f_m_lib.py', '62790f5aece862608eec414bfd419b2aa47ca04a')
    load_mod('r32a', B, 'enclosure/fusion/audit-asm/followup/aud4_lib.py', '181243c7068e2715b299f519df4a7ac8948c95eb',
             repl=(("sys.modules['aud4k']", "sys.modules['v5f_k']"), ("sys.modules['aud4m']", "sys.modules['v5f_m']")))
    k = sys.modules['v5f_k']
    r = types.ModuleType('r32'); sys.modules['r32'] = r; r.res = {}
    r.k4, h = load_ns(A, F + 'v5f_k4a_unit_checks.py', 'f5583bf9e2a5d8bbbc99d2586242a8dc6d37533e', {'k': k})
    r.k4b, h = load_ns(A, F + 'v5f_k4b_addenda.py', '2aa31a167e38376564b65693748f2133d1b3f5ef', {'k': k, 'k4': r.k4})
    r.s3, h = load_ns(A, F + 'v5f_m3b_unit_checks.py', 'fc44e7970c88ae458f82866f2ab17dd8d6cb8c84', {'k': k, 'k4': r.k4, 'k4b': r.k4b})


def preflight(_context):
    k = sys.modules['v5f_k']; r = sys.modules['r32']
    X = k.K()
    print(X.state())
    cur = k.current(X, leads=True)
    print(len(cur), sum(1 for q in cur if q.name.startswith('LEAD_')), sum(1 for q in cur if q.name.startswith('KO_')))
    r.res['vis0'] = sorted(b.name for b in X.root.bRepBodies if b.isLightBulbOn)
    r.res['vol62'] = {n: [round(X.body(n).volume * 1000.0, 2), X.body(n).lumps.count] for n in
                      ('HOUSING_F_front', 'SPKBOX_L', 'SPKBOX_R', 'RESP_CARRIER', 'FLOOR_PLATE', 'CRADLE_5807', 'HOUSING_F_door', 'HOUSING_F_cap', 'MAIN_pcb')}
    print(r.res['vol62'], k.bbb(X.body('MAIN_pcb')))
    # version 62 of 62, unmodified, 391 bodies, 36 visible, no template, no duplicate name; unit 95 (16 leads, 13 key paths).
    # front shell 200363.57, left box 26051.89, right box 26769.41, carrier 12404.26, base plate 32452.33, cradle 1770.95, door 47019.77,
    # cap 9944.06; MAIN_pcb 7463.47 (161 faces), u -43.5..43.5, v -28.95..28.95, w -1.6..-0.09.


def reply_vs_model(_context):                        # the rev 3.2 reply's figures against version 62 (rev 3.1's board)
    k = sys.modules['v5f_k']
    X = k.K()
    pcb = X.body('MAIN_pcb'); plug = X.body('RESP_usbc_plug_env')
    Bq = lambda p: [round(v, 3) for v in k.Bf(p)]
    def md(a, b):
        q = X.mm.measureMinimumDistance(a, b); return round(q.value * 10.0, 3), Bq(q.positionOne), Bq(q.positionTwo)
    print(k.bbb(plug), md(plug, pcb))
    t = X.tbm.copy(plug); m = adsk.core.Matrix3D.create(); m.translation = k.V3(-0.092, 0, 0); X.tbm.transform(t, m)
    print(X.xv(t, X.tbm.copy(pcb)))
    for n in ('LEAD_DSI', 'LEAD_USB_RESP', 'KO_K5_UL', 'KO_K5_LL'):
        print(n, md(X.body(n), pcb))
    lo = X.tbm.copy(X.body('MAIN_low')); X.sec(lo, X.bbox(36.0, 44.0, -2.0, 16.0, -0.2, 3.0))
    print([[round(w, 3) for w in k.Bf(l.boundingBox.minPoint) + k.Bf(l.boundingBox.maxPoint)] + [round(l.volume * 1000, 3)] for l in lo.lumps])
    # plug u 36.58..47.10, v 2.51..11.91, w -9.20..11.67 (552.03 mm3); plug - board 0.200 from (43.70, 3.51) to (43.50, 3.51): across u.
    # plug 0.92 nearer the socket (sleeve on the socket's face): 8.045 mm3 in the board. Ribbon - board 2.900 at v -16.08 (below the relief);
    # USB cable 11.743 at v 9.84; key paths KO_K5_UL / LL 0.550. MAIN_low next to the relief: R105's body u 40.467..41.267, v 2.245..3.845,
    # w to 0.445 (0.733 from u 42.0); R100's u 40.277..41.077, v 5.665..7.265 (0.923).


def calibrate(_context):                             # the audit's jaws 0.5 nearer against rev 3.1's board: which set-up gives its 0.25 mm3
    k = sys.modules['v5f_k']; a4 = sys.modules['r32a']
    X = k.K(); pcb = X.tbm.copy(X.body('MAIN_pcb'))
    def dirB(th, ps):
        t = math.radians(th); p = math.radians(ps)
        return a4.wdir((-math.sin(p), math.cos(t) * math.cos(p), -math.sin(t) * math.cos(p)))
    for lab, fn in (('A', lambda th, ps: dirA(a4, th, ps)), ('B', dirB)):
        for wt in (0.0, 1.0):
            print(lab, wt, [(th, ps, round(X.xv(a4.jaws(X, fn(th, ps), wtip=wt, shift=-0.5, body=a4.PLIERS), pcb), 3))
                             for th in (30.0, 35.0) for ps in (10.0, 15.0)])
    # A (elevation / azimuth), tips at the board's face (wtip 0): 0.156 / 0.218 / 0.181 / 0.249 mm3 at 30/10, 30/15, 35/10, 35/15 -> 0.249 at
    # 35/15 is the audit's 0.25. B: 0.171 / 0.242 / 0.205 / 0.288. Tips at w 1.0 (the template's default): 0 everywhere. Jaws not moved: 0.
    # Used from here on: A, wtip 0.


def matrix62(_context):                              # the reference: every current body against every other at version 62
    k = sys.modules['v5f_k']; r = sys.modules['r32']
    X = k.K(); k.budget(48)
    res, left, n = r.k4['matrix'](X, 'v62')
    print(n, len(res), left, sum(1 for v in res.values() if v))
    # 95 bodies, 4465 pairs, nothing left, 76 not zero (26 s). With MAIN_pcb: LEAD_GPIO_A1 0.676, LEAD_GPIO_A2 1.850, LEAD_GPIO_B 1.220,
    # MAIN_conn 0.286, MAIN_tall 0.035.


# ---------- block 1 ----------
def import32(_context):                              # the STEP file into temporary bodies through a new document, closed without saving
    r = sys.modules['r32']
    app = adsk.core.Application.get(); panel = app.activeDocument
    d = os.path.expanduser('~/Documents/HA_panel_renders/fp/rev32'); os.makedirs(d, exist_ok=True)
    fn = os.path.join(d, 'main-board-rev3.2.step')
    data = urllib.request.urlopen(RAW % ('07aa6925e9620e71dc4c82d8819b5734ffab70ab', 'hardware/main-board/main-board-rev3.2.step'), timeout=40).read()
    if blob(data) != 'd2663e85e8e91082f187f469f85ae00c548d0abc':
        raise RuntimeError('blob')
    open(fn, 'wb').write(data)
    tbm = adsk.fusion.TemporaryBRepManager.get()
    doc = app.importManager.importToNewDocument(app.importManager.createSTEPImportOptions(fn))
    try:
        root = adsk.fusion.Design.cast(doc.products.itemByProductType('DesignProductType')).rootComponent
        srcs = [(root.name, b) for b in root.bRepBodies] + [(o.fullPathName, b) for o in root.allOccurrences for b in o.bRepBodies]
        items = []
        for path, b in srcs:
            tb = tbm.copy(b); bb = tb.boundingBox
            items.append([path + '/' + b.name, [round(q * 10, 3) for q in (bb.minPoint.x, bb.maxPoint.x, bb.minPoint.y, bb.maxPoint.y, bb.minPoint.z, bb.maxPoint.z)], tb])
        r.res['step32'] = items
    finally:
        doc.close(False)
        if app.activeDocument != panel:
            panel.activate()
    # 3594081 bytes, blob ok, sha256 ff730b1b4242d0dc11f7ed4444c2172be9999570c9d3311a589cba40daa7135c; 140 solids in 112 occurrences;
    # the board solid u -43.5..43.5, v -28.95..28.95, Z 0..1.51, 7433.538 mm3, 167 faces. 4.5 s.


def board(_context):                                 # the board solid placed as rev 3.1's, against rev 3.1 and the reply's corner points
    k = sys.modules['v5f_k']; r = sys.modules['r32']
    X = k.K()
    m = adsk.core.Matrix3D.create(); m.setWithArray(M_STEP)
    nb = X.tbm.copy([i for i in r.res['step32'] if i[1][1] - i[1][0] > 80.0][0][2]); X.tbm.transform(nb, m); r.res['pcb32'] = nb
    old = X.tbm.copy(X.body('MAIN_pcb'))
    print(X.vol(X.dif(X.tbm.copy(old), X.tbm.copy(nb))), X.vol(X.dif(X.tbm.copy(nb), X.tbm.copy(old))))
    for f in nb.faces:                               # planes and cylinders of the relief, board frame
        ws = [k.Bf(v.geometry) for v in f.vertices]
        ext = [round(fn(w[i] for w in ws), 3) for i in range(3) for fn in (min, max)] if ws else None
        if ext and ext[1] >= 41.8 and ext[2] <= 14.6 and ext[3] >= -0.1:
            g = f.geometry
            print('cyl r %.4f at %s' % (g.radius * 10, [round(q, 3) for q in k.Bf(g.origin)][:2]) if g.surfaceType == k.CYL else 'plane', ext, round(f.area * 100, 3))
    PI = adsk.fusion.PointContainment.PointInsidePointContainment
    pts = {'cut': [(42.05, 1.6), (42.05, 4.0), (42.05, 7.25), (42.05, 10.5), (42.05, 12.9), (43.45, 0.55), (43.45, 13.95), (42.30, 0.80), (42.30, 13.70), (43.0, 7.25)],
           'board': [(41.95, 1.6), (41.95, 7.25), (41.95, 12.9), (43.45, 0.45), (43.45, 14.05), (42.27, 0.77), (42.27, 13.73), (42.05, 0.45), (42.05, 14.05)]}
    print([(kind, u, v) for kind, ps in pts.items() for u, v in ps if (nb.pointContainment(k.Bp(u, v, -0.85)) == PI) != (kind == 'board')])
    print([(v, round(38.0 + max(q[1] for q in k.needle_t(X, [nb], k.B2W(38.0, v, -0.85), k.B2W(45.0, v, -0.85))), 3)) for v in
           (0.4, 0.6, 1.5, 2.0, 4.0, 7.25, 10.0, 12.0, 13.0, 13.9, 14.1)])
    # rev 3.1 minus rev 3.2: 29.929 mm3 (19.82 mm2 x 1.51); rev 3.2 minus rev 3.1: 0.0. Faces: floor plane u 42.000, v 1.5..13.0, w -1.6..-0.09
    # (17.365 mm2); cylinders r 1.0000 on (43.0, 1.5) and (43.0, 13.0); side walls v 0.5 and 14.0 from u 43.0 to 43.5; the old edge at u 43.5
    # below v 0.5 and above v 14.0. 19 probes, none wrong. Edge at mid thickness: u 42.000 from v 1.5 to 13.0, 43.5 at v 0.4 and 14.1.


GROUPS = {'J9': (-43.3, -34.7, -29.0, -22.1), 'J1': (-4.3, 4.3, -29.0, -22.1), 'J6': (9.4, 16.3, -29.0, -15.4), 'J2': (16.3, 27.0, -29.6, -19.2),
          'J8': (34.5, 43.0, -29.0, -22.1), 'J5': (-43.3, -36.3, -20.6, -7.1), 'J10': (-32.3, -28.5, -19.8, -8.4), 'J11': (-6.4, 5.0, -14.9, -11.1)}


def group(box):                                      # v5f_i1b's grouping of the STEP solids
    x0, x1, y0, y1, z0, z1 = box; cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    if x1 - x0 > 80.0:
        return 'pcb'
    if z1 > 25.0 or z0 < -2.5:
        return 'PS1'
    for q, (a, b, c, d) in GROUPS.items():
        if a <= cx <= b and c <= cy <= d:
            return 'conn'
    return 'tall' if (z1 > 6.0 or z0 < -1.0) else 'low'


def parts(_context):                                 # the 139 part solids, grouped as before, against the model's part bodies
    k = sys.modules['v5f_k']; r = sys.modules['r32']
    X = k.K(); m = adsk.core.Matrix3D.create(); m.setWithArray(M_STEP); grp = {}
    for path, box, tb in r.res['step32']:
        g = group(box)
        if g == 'pcb':
            continue
        t = X.tbm.copy(tb); X.tbm.transform(t, m)
        grp[g] = t if g not in grp else X.uni(grp[g], t)
    for g, n in {'PS1': 'MAIN_PS1', 'conn': 'MAIN_conn', 'tall': 'MAIN_tall', 'low': 'MAIN_low'}.items():
        mod = X.tbm.copy(X.body(n))
        print(n, X.vol(grp[g]), X.vol(X.dif(X.tbm.copy(mod), X.tbm.copy(grp[g]))), X.vol(X.dif(X.tbm.copy(grp[g]), X.tbm.copy(mod))))
    # 14 / 41 / 16 / 68 solids. MAIN_PS1 16960.937, MAIN_conn 1288.750 (16 lumps), MAIN_tall 5435.497 (10), MAIN_low 524.329 (68):
    # equal to the model's bodies, 0.0000 mm3 both ways, same boxes. So only the board's solid is replaced.


def apply(_context):                                 # model change: MAIN_pcb -> MAIN_pcb_v62 (hidden); rev 3.2's solid as MAIN_pcb
    k = sys.modules['v5f_k']; r = sys.modules['r32']
    X = k.K(); st = X.state()
    if st['version'] != 62 or st['modified'] or st['bodies'] != 391 or st['templates'] or st['dups'] or X.body('MAIN_pcb_v62') is not None:
        raise RuntimeError('unexpected state %s' % st)
    X.swap('MAIN_pcb', X.tbm.copy(r.res['pcb32']), '_v62')
    print(k.purge(['MAIN_pcb']), X.state())
    # MAIN_pcb 7433.538, 167 faces, visible, appearance and material as before; MAIN_pcb_v62 7463.467 hidden. 392 bodies, 36 visible, unit 95.


# ---------- block 2 ----------
def variants(_context):                              # the board at the fab's tolerance (built in two calls; larger() writes both the same way)
    k = sys.modules['v5f_k']; r = sys.modules['r32']
    X = k.K()
    B31 = X.tbm.copy(X.body('MAIN_pcb_v62')); B32 = X.tbm.copy(X.body('MAIN_pcb'))
    Bn = X.dif(X.tbm.copy(B31), notch(X, 42.0, 1.0, 0.5, 14.0))       # the construction checked: must equal rev 3.2
    print(X.vol(X.dif(X.tbm.copy(Bn), X.tbm.copy(B32))), X.vol(X.dif(X.tbm.copy(B32), X.tbm.copy(Bn))))
    Bs = X.dif(X.tbm.copy(B31), notch(X, 42.2, 0.8, 0.7, 13.8))       # relief 0.2 smaller all round ("floor at u +42.2")
    def larger(d):                                   # outline d larger all round: four edges out by d (square corners), relief d smaller; holes as they are
        t = X.tbm.copy(B31); a, b = 43.5 + d, 28.95 + d
        for q in ((43.5, a, -b, b), (-a, -43.5, -b, b), (-a, a, 28.95, b), (-a, a, -b, -28.95)):
            X.uni(t, X.bbox(q[0], q[1], q[2], q[3], -1.6, -0.09))
        return X.dif(t, notch(X, 42.0 + d, 1.0 - d, 0.5 + d, 14.0 - d))
    r.res.update({'B31': B31, 'B32': B32, 'B32s': Bs, 'Bplus1': larger(0.1), 'Bplus': larger(0.2)})
    R105 = X.tbm.copy(X.body('MAIN_low')); X.sec(R105, X.bbox(40.3, 41.4, 2.1, 4.0, -0.2, 0.6)); r.res['R105'] = R105
    # construction: 0.0000 / 0.0000. Volumes: rev 3.1 7463.467, rev 3.2 7433.538, relief 0.2 smaller 7438.167, outline +0.1 7477.688,
    # outline +0.2 7521.972 (u +-43.7, v +-29.15). R105's body 0.537 mm3, u 40.47..41.27, v 2.24..3.84, w -0.01..0.44.


def sleeve_leads(_context):                          # check 1 (the USB-C sleeve) and check 3 (both flat leads)
    k = sys.modules['v5f_k']; r = sys.modules['r32']
    X = k.K()
    def md(a, b):
        q = X.mm.measureMinimumDistance(a, b); return round(q.value * 10.0, 3), [round(v, 2) for v in k.Bf(q.positionTwo)]
    P = X.tbm.copy(X.body('RESP_usbc_plug_env'))
    P0 = X.tbm.copy(P); m = adsk.core.Matrix3D.create(); m.translation = k.V3(-0.092, 0, 0); X.tbm.transform(P0, m)
    for pl, p in (('0.92 off', P), ('on the face', P0)):
        print(pl, [(lab, md(p, r.res[lab]), round(X.xv(p, r.res[lab]), 3)) for lab in ('B31', 'B32', 'B32s')])
    for n in ('LEAD_DSI', 'LEAD_USB_RESP'):
        L = X.body(n)
        print(n, [(lab, md(L, r.res[lab])) for lab in ('B31', 'B32', 'B32s')])
        rows = []
        for v0 in range(-32, 32, 4):                 # the lead beside the board, band by band of v
            c = X.tbm.copy(L); X.sec(c, X.bbox(30.0, 80.0, v0, v0 + 4, -60.0, 80.0))
            if c.faces.count and X.vol(c) > 0.001:
                rows.append((v0, md(c, r.res['B32'])[0], md(c, r.res['B32s'])[0]))
        print(rows)
    # sleeve 0.92 off the socket's face: rev 3.1 0.200, rev 3.2 1.700 (to the floor at v 3.51), relief 0.2 smaller 1.500.
    # sleeve on the socket's face: rev 3.1 8.045 mm3 inside, rev 3.2 0.780 clear, relief 0.2 smaller 0.580 clear.
    # ribbon 2.900 at v -16.08 for all three (2.90 from v -20 to 0; 9.60 at v 0..4, 13.77 at 4..8, 17.59 at 8..12).
    # USB cable 11.743 / 11.871 / 11.843 (11.87 at v 4..12, 26.2 or more below).


def jaws_grid(_context):                             # check 2: the pliers' line of D135, plate unit in place, door off, plug and cable left out
    k = sys.modules['v5f_k']; a4 = sys.modules['r32a']; r = sys.modules['r32']
    X = k.K()
    base = [(n, b) for n, b in a4.service_fixed(X, 0.0, b=0.0) if n != 'MAIN_pcb']
    res = r.res.setdefault('jaws', {})
    for th in (30.0, 32.5, 35.0):
        for ps in (10.0, 12.5, 15.0):
            a = dirA(a4, th, ps)
            for lab, sh in (('seated', 0.0), ('seated, 0.5 nearer', -0.5), ('3.6 out', 3.6), ('7.2 out', 7.2), ('7.2 out, 0.5 nearer', 6.7)):
                tool = a4.jaws(X, a, wtip=0.0, shift=sh, body=a4.PLIERS)
                res[(th, ps, lab)] = (a4.hits(X, tool, base + [('MAIN_pcb', r.res['B32'])], eps=0.005),
                                      X.mm.measureMinimumDistance(tool, r.res['B32']).value * 10.0,
                                      X.mm.measureMinimumDistance(tool, r.res['R105']).value * 10.0)
    # 84 obstacles. Board never touched. Seated: board 0.190..0.306 (0.5 nearer 0.066..0.141), R105's body 2.467..2.557 (1.980..2.062);
    # 3.6 out: board 3.66..3.83; 7.2 out: 7.14..7.37 (0.5 nearer 6.66..6.88), nothing touched.
    # Touched: the ribbon 3.81..10.03 mm3 seated (3.68..13.56 0.5 nearer), 1.23..5.12 at 3.6 out; the Pi power cable's lap at 32.5/15 (0.07),
    # 35/12.5 (4.89) and 35/15 (63.94); 0.5 nearer 0.12 / 11.79 / 77.74.


def jaws_tolerance(_context):                        # the jaws against the board at the fab's tolerance; tips at the face and higher
    k = sys.modules['v5f_k']; a4 = sys.modules['r32a']; r = sys.modules['r32']
    X = k.K()
    for bl in ('B32', 'B32s', 'Bplus1', 'Bplus'):
        for wt in (0.0, 0.25, 0.5, 1.0):
            for lab, sh in (('jaws', 0.0), ('0.5 nearer', -0.5)):
                ds = []; vs = []
                for th in (30.0, 32.5, 35.0):
                    for ps in (10.0, 12.5, 15.0):
                        tool = a4.jaws(X, dirA(a4, th, ps), wtip=wt, shift=sh, body=a4.PLIERS)
                        q = X.mm.measureMinimumDistance(tool, r.res[bl])
                        ds.append((q.value * 10, [round(v, 2) for v in k.Bf(q.positionTwo)])); vs.append(X.xv(tool, r.res[bl]))
                print(bl, wt, lab, min(ds), max(d for d, p in ds), max(vs))
    # Nearest point on the board: its square corner at the relief's lower end (u 43.5, v 0.5, the door-side face), not the floor.
    # tips at the face (w 0):  rev 3.2 0.190..0.306 / 0.5 nearer 0.066..0.141;  relief 0.2 smaller 0.186..0.283 / touch, 0.003 mm3 at most;
    #                          outline +0.1 0.089..0.188 / 0.000..0.055 (0.0001 mm3);  outline +0.2 0.000..0.086 (touch) / touch, 0.0047 mm3 at most.
    # tips 0.25 up:            rev 3.2 0.307..0.405 / 0.213..0.268;  +0.1 0.189..0.280 / 0.132..0.181;  +0.2 0.072..0.154 / 0.051..0.095.
    # tips 0.5 up:             rev 3.2 0.446..0.518 / 0.359..0.394;  +0.1 0.331..0.394 / 0.278..0.308;  +0.2 0.218..0.270 / 0.197..0.222.
    # tips 1.0 up:             rev 3.2 0.741..0.761 / 0.647..0.653;  +0.1 0.630..0.642 / 0.561..0.572;  +0.2 0.521..0.528 / 0.475..0.491.
    # To the floor strip alone (u 40..42.1, v 1.5..13.0), tips at the face: 1.635..1.760 / 1.152..1.268; relief 0.2 smaller 1.442..1.563 / 0.959..1.071.


def ride(_context):                                  # check 4: the audit's ride-in (45 pieces, 23 positions out to 60) with rev 3.2
    k = sys.modules['v5f_k']; a4 = sys.modules['r32a']
    X = k.K(); t0 = time.time()
    a4.ride_setup(X)
    print(a4.ride(X, t0, lim=55.0, tag='ride32'), len(a4.R['ride32']))
    # 1035 results, nothing left, none touching. Nearest: the main board 1.029 to the shell (18 to 22 out), as rev 3.1; the cable's held part
    # 1.223 (0.5 out), the ribbon's 4.650, the plug 7.365 (14 out); the Pi signal and display power leads' parts 0.080 (10 out), as before.


def ride_boards(_context):                           # check 5: the board alone at its tolerance, the same 23 positions
    k = sys.modules['v5f_k']; a4 = sys.modules['r32a']; r = sys.modules['r32']
    X = k.K(); fx = a4.R['ride_fix']
    for lab in ('B31', 'B32', 'Bplus1', 'Bplus'):
        best = None
        for s in a4.STEPS:
            g = a4.mingap(X, a4.mvn(X, r.res[lab], s), fx, 3.0)
            if g is not None and (best is None or g[0] < best[0]):
                best = (g[0], s, g[1])
        print(lab, best)
    # rev 3.1 1.029, rev 3.2 1.029, outline +0.1 0.929, outline +0.2 0.829 (all at 18 out, the LCD opening); nothing touching.


def neighbours(_context):                            # check 5: the board's smallest distance to every body round it (its own parts left out)
    k = sys.modules['v5f_k']; a4 = sys.modules['r32a']; r = sys.modules['r32']
    X = k.K()
    own = ('MAIN_pcb', 'MAIN_conn', 'MAIN_low', 'MAIN_tall', 'MAIN_PS1', 'MAIN_PS1_tol', 'MAIN_plug_env', 'MAIN_J2_plug_env',
           'LEAD_GPIO_A1', 'LEAD_GPIO_A2', 'LEAD_GPIO_B')
    q = r.res['Bplus'].boundingBox; e = 0.4
    box = adsk.core.BoundingBox3D.create(k.P3(q.minPoint.x - e, q.minPoint.y - e, q.minPoint.z - e), k.P3(q.maxPoint.x + e, q.maxPoint.y + e, q.maxPoint.z + e))
    for b in k.current(X, leads=True):
        if b.name in own or not box.intersects(b.boundingBox):
            continue
        ps = a4.crop(X, b.name, ('brd', b.name), (-50.0, 55.0, 20.0, 50.0, -63.0, 9.0), 'S') if b.name in k.BIG else [k.tcopy(X, b.name)]
        if ps:
            print(b.name, [round(min(X.mm.measureMinimumDistance(r.res[lab], p).value for p in ps) * 10, 3) for lab in ('B31', 'B32', 'Bplus1', 'Bplus')])
    # within 3.5 (rev 3.1 / rev 3.2 / +0.1 / +0.2): carrier 0 / 0 / 0 / 0 (the board rests on its posts, nothing overlaps);
    # key paths KO_K5_LR, KO_K5_UR (right-speaker side) 0.45 / 0.45 / 0.35 / 0.25; KO_K5_LL, KO_K5_UL (left) 0.55 / 0.55 / 0.45 / 0.35;
    # ReSpeaker's top envelope 0.56 throughout; display's power lead 1.00 throughout; USB-C plug 0.20 / 1.70 / 1.60 / 1.50;
    # ribbon 2.90 / 2.90 / 2.80 / 2.70.


# ---------- block 3 ----------
def matrix_g18(_context):                            # called twice (72.6 s with the new tag's slabs, then 12.6 s)
    k = sys.modules['v5f_k']; r = sys.modules['r32']
    X = k.K(); k.budget(45)
    res, left, n = r.k4['matrix'](X, 'g18')
    if not left:
        sym = lambda d: {tuple(sorted(q)): v for q, v in d.items() if v}
        a = sym(k.c[('k4m', 'v62')]); b = sym(res)
        print(len(a), len(b), {q: a[q] for q in a if q not in b}, {q: b[q] for q in b if q not in a},
              {q: (a[q], b[q]) for q in a if q in b and abs(a[q] - b[q]) > 0.0005})
    # 95 bodies, 4465 pairs, 76 not zero; against version 62: none gone, none new, none changed.


def volumes(_context):
    k = sys.modules['v5f_k']; r = sys.modules['r32']
    X = k.K()
    for n, (v, l) in r.res['vol62'].items():
        if n != 'MAIN_pcb':
            print(n, round(X.body(n).volume * 1000.0, 2), v, X.body(n).lumps.count == l)
    # all eight equal to version 62 (front shell, both boxes, carrier, base plate, cradle, door, cap), one lump each.


def save(_context):                                  # its own call
    k = sys.modules['v5f_k']; r = sys.modules['r32']
    X = k.K(); st = X.state()
    vis = sorted(b.name for b in X.root.bRepBodies if b.isLightBulbOn)
    if st['templates'] or st['dups'] or st['bodies'] != 392 or st['version'] != 62 or st['visible'] != 36 or vis != r.res['vis0'] \
            or X.body('MAIN_pcb_v62') is None or X.body('MAIN_pcb_v62').isLightBulbOn:
        raise RuntimeError('guard: %s' % st)
    print(X.doc.save('rev F WIP 2026-11-14 g18: main board rev 3.2 placed - relief 1.5 deep in the +u side edge (floor u +42.0 over v +1.5..+13.0, '
                     'corners r 1.0); only the board solid replaced, rev 3.1 board kept hidden as MAIN_pcb_v62; edge, pliers, flat leads, ride-in and '
                     'tolerance checks done; interference as version 62; not for print'))


def export(_context):                                # its own call
    k = sys.modules['v5f_k']
    X = k.K()
    f3d = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-g18.f3d'); new = f3d[:-4] + ' new.f3d'
    em = X.des.exportManager
    ok = em.execute(em.createFusionArchiveExportOptions(new))
    if ok and os.path.exists(new) and os.path.getsize(new) > 50e6:
        os.replace(new, f3d)
    print(ok, os.path.getsize(f3d))
    # True 173086500. Read back in a third call: version 63 of 63, unmodified, 392 bodies, 36 visible, no template, unit 95.
