# change2/cp2_calls.py - posts / shadow gap / FDM strength / door vents pass (2026-11-17): the connector calls of blocks 2 and 3, in order.
# Each function is the body of one call's run(_context). k = sys.modules['cp2k'] (v5f_k_lib.py, blob ba85884, loaded by cp2_lib.load());
# cp2 = sys.modules['cp2'] holding cp2_lib.py, cp2_posts.py, cp2_vents.py and cp2_fix.py. Only commit_*, save_g21 and export_g21 change the model.
# Block 1 (study, read-only) built the posts, the plate and the three door layouts on temporary copies: k.c['shell_new'], ['plate_new'], ['door_b'].
import adsk.core, adsk.fusion, sys, time, math, os


def reference_matrix(_context):                       # version 65's interference table, before any change (Fusion's memory held none)
    k = sys.modules['cp2k']
    ns = {'k': k, '__name__': 'k4a'}
    exec(compile(k.fetch('d223ad333982c9d219732c7a5079d3d1ebcefde7', 'v5f_k4a_unit_checks.py'), 'v5f_k4a_unit_checks.py', 'exec'), ns); k.K4NS = ns
    X = k.K(); k.budget(55.0)
    res, left, n = ns['matrix'](X, 'v65')             # 96 bodies, 4560 pairs, 76 not zero, left 0 (33 s)


def build(_context):                                  # several calls; results in cp2.G (name -> temporary body)
    k = sys.modules['cp2k']; cp2 = sys.modules['cp2']; X = k.K(); k.budget(60.0)
    cp2.build_cap(X)                                  # +36.197
    cp2.build_base(X)                                 # Pi posts +9.504 each; cradle posts +133.555
    cp2.build_cradle(X)                               # +0.267
    cp2.build_clip(X, 1.0); cp2.build_clip(X, -1.0)   # +81.6 each
    cp2.build_box(X, 1.0); cp2.build_box(X, -1.0)     # pilot tip +3.927, driver columns +85.885, clip block +143.617 / 143.611
    cp2.build_carrier(X)                              # posts +1226.779, bosses +20.944
    cp2.build_door(X)                                 # buttresses +169.512, 167.118, 155.826, 46.331 on the vents-only door (47,034.26)
    cp2.build_shell(X, 'fins')                        # 215.22 removed per side (17.5 s)
    cp2.build_shell(X, 'left')                        # gussets +74.106, 56.461, 53.951 (43.7 s with the regions)
    cp2.build_shell(X, 'right')                       # lumps against the posts-only shell: 54.04, 54.07, 74.07, 74.08, 56.45, 56.46
    cp2.G['HOUSING_F_plate'] = X.tbm.copy(k.c['plate_new'])        # cp2.new_plate(X): border step and pocket / slot (cp2_posts.py)
    for n in cp2.G:
        cp2.delta(X, n, 1.2)                          # added / removed, overlaps of the added plastic, anything within 1.2 (README table)
    cp2.outside(X, 'HOUSING_F_front')                 # (52.779, [26.389, 26.389]); door and cap 0.0


def commit_a(_context):
    k = sys.modules['cp2k']; cp2 = sys.modules['cp2']
    app = adsk.core.Application.get(); X = k.K(); G = cp2.G
    st = X.state()
    done = [n for n in G if X.body(n + '_v65') is not None]
    if not done and (st['version'] != 65 or st['modified'] or st['bodies'] != 408 or st['templates'] or st['dups']):
        raise RuntimeError('unexpected state %s' % st)
    if app.activeDocument != X.doc:
        X.doc.activate()                              # the main document active for the change (my scratch document was)
    X = k.K()
    for n in ('HOUSING_F_front', 'HOUSING_F_plate', 'HOUSING_F_door', 'HOUSING_F_cap'):
        if X.body(n + '_v65') is None:
            X.swap(n, G[n], '_v65')                   # old body hidden as <name>_v65, new one in its place with its appearance and visibility


def commit_b(_context):
    k = sys.modules['cp2k']; cp2 = sys.modules['cp2']; X = k.K(); G = cp2.G
    for n in ('FLOOR_PLATE', 'SPKBOX_L', 'SPKBOX_R', 'RESP_CARRIER', 'CRADLE_5807', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R'):
        if X.body(n + '_v65') is None:
            X.swap(n, G[n], '_v65')
    # state: 419 bodies (408 + 11 hidden _v65), 96 in the unit (16 leads, 13 keep-outs), 37 visible, no AUD_*; backups 4 _v63, 11 _v64, 11 _v65


def matrix(_context):                                 # check 2
    k = sys.modules['cp2k']; X = k.K()
    k.purge(['SPKBOX_', 'HOUSING_F_', 'FLOOR_PLATE', 'RESP_CARRIER', 'CRADLE_5807', 'TOUCH_CLIP_'])     # lesson 197
    k.budget(55.0)
    res, left, n = k.K4NS['matrix'](X, 'g21')
    sym = lambda d: {tuple(sorted(q)): v for q, v in d.items() if v}
    A = sym(k.c[('k4m', 'v65')]); B = sym(res)
    # 96 bodies, 4560 pairs, 76 not zero = version 65's 76; none new, none gone; changed: HOUSING_F_door x KO_capkey_SL 97.399 -> 211.189


def outer_skin(_context):                             # check 1: every changed printed part minus REF_F_outer (k.c['skin_ref'] = its temporary copy)
    k = sys.modules['cp2k']; X = k.K()
    for n in ('HOUSING_F_front', 'HOUSING_F_door', 'HOUSING_F_cap', 'SPKBOX_L', 'SPKBOX_R', 'RESP_CARRIER', 'CRADLE_5807', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R'):
        t = X.cp(X.body(n)); X.dif(t, X.tbm.copy(k.c['skin_ref']))
    # shell 52.779 in two lumps (the pegs, 26.389 each); door, cap, boxes, carrier, clips 0.0;
    # cradle 10.924 (its rear bezel, y -84.6 .. -84.27, z 17.6 .. 26.8): the same for CRADLE_5807_v65


def walls(_context):                                  # the review's fixes measured: material along a line from the hole's axis (k.needle_t)
    k = sys.modules['cp2k']; X = k.K()
    for sx in (1.0, -1.0):
        B = [X.cp(X.body('SPKBOX_L' if sx > 0 else 'SPKBOX_R'))]
        k.needle_t(X, B, (sx * 46.0, -6.95, 38.0), (sx * 46.0, 0.0, 38.0))               # clip hole to the front face [1.25, 3.25]
        k.needle_t(X, B, (sx * 48.5, -6.95, 38.0), (sx * 48.5, -14.0, 38.0))             # to the block's rear [1.25, 3.25]
        k.needle_t(X, B, (sx * 51.0, -14.0, 9.8), (sx * 51.0, -8.0, 9.8))                # floor insert toward the driver hole [2.0, 4.3]
        k.needle_t(X, B, (sx * 88.25, -8.0, 10.25), (sx * (88.25 + 6 * 0.86), -8.0, 10.25 - 6 * 0.52))    # outer columns [2.0, 4.0]
        k.needle_t(X, B, (sx * 52.75, -3.35, 10.25), (sx * 52.75, -3.35, 16.5))          # the bosses under the driver's frame [2.0, 4.0]
        C = [X.cp(X.body('TOUCH_CLIP_L' if sx > 0 else 'TOUCH_CLIP_R'))]
        k.needle_t(X, C, (sx * 42.0, -6.95, 38.0), (sx * 42.0, -14.0, 38.0))             # clip hole to the lug's end [1.7, 3.25]
    k.needle_t(X, [X.cp(X.body('CRADLE_5807'))], (7.75, -81.16, 15.0), (14.0, -81.16, 15.0))             # [0.8, 2.8]
    D = [X.cp(X.body('HOUSING_F_door'))]
    for (bx, by, ux, uy) in ((50.0, -67.0, 0.34, -0.94), (-50.0, -67.0, -0.34, -0.94), (19.0, -74.5, 0.0, -1.0), (-19.0, -77.0, 0.0, -1.0)):
        m = math.hypot(ux, uy)
        k.needle_t(X, D, (bx, by, 6.0), (bx + 12 * ux / m, by + 12 * uy / m, 6.0))       # solid from 2.0 to the outer face: 9.51, 9.51, 9.18, 6.69
    C = [X.cp(X.body('RESP_CARRIER'))]
    for (x, up) in ((-34.5, -5.45), (-28.5, -52.7), (21.7, -2.45), (33.5, -52.7)):
        k.needle_t(X, C, k.W(k.Dp(x, 28.0, up)), k.W(k.Dp(x, 28.0, up - 7.0)))           # upper posts [2.0, 4.45]; lower posts [2.0, 4.0] (were 1.70)
        k.needle_t(X, C, k.W(k.Dp(x, 17.7, up)), k.W(k.Dp(x + 9.0, 17.7, up)))           # root: 5.93; 4.0 at (-34.5, -5.45) toward the microphone's lead
    cur = k.current(X, leads=False); k.budget(60.0)
    k.line(X, (40.5 - 1.65, -6.95, 38.0), (-1.0, 0.0, 0.0), k.KEY20, cur, st0=2.0, step=1.0, head=7.0)    # the left clip's screw: head +2.83, 87 free


def step19(_context):                                 # check 3 (two calls: the regions take 25 s each on a new shell)
    k = sys.modules['cp2k']; X = k.K(); k.budget(65.0)
    P = X.cp(X.body('HOUSING_F_plate'))
    for sx in (1.0, -1.0):
        x0 = 85.0 * sx
        sh = k.region(X, 'HOUSING_F_front', 'peg%+d' % sx, (x0 - 9.0, x0 + 9.0, 10.0, 23.0, -92.0, -72.0), 'S')
        for dx, du in ((1, 0), (-1, 0), (0, 1), (0, -1)):                                 # wall round the insert hole at mid-peg: [2.0, 4.0] in all four
            k.needle_t(X, sh, k.W(k.Dp(x0, 12.2, -82.0)), k.W(k.Dp(x0 + dx * 6.0, 12.2, -82.0 + du * 6.0)))
        # peg to plate 0.125 both; pocket 8.24 along x and up; slot 9.76 along x, 8.25 along up
    k.needle_t(X, [P], k.W(k.Dp(96.5, 5.0, -40.0)), k.W(k.Dp(96.5, 16.0, -40.0)))        # border [4.0, 7.0]: d 9.0 .. 12.0
    k.needle_t(X, [P], k.W(k.Dp(92.0, 5.0, -40.0)), k.W(k.Dp(92.0, 16.0, -40.0)))        # island [4.0, 7.8]: d 9.0 .. 12.8
    shs = k.region(X, 'HOUSING_F_front', 'front_band', (-102.0, 102.0, 10.0, 21.0, -95.0, 40.0), 'S')
    for s in (3.0, 2.0, 1.5, 1.2, 1.0, 0.8, 0.6, 0.4, 0.2, 0.1, 0.05, 0.0):             # the plate dropped onto the pegs along the normal: 0.0 mm3
        t = X.tbm.copy(P); X.move_n(t, s); sum(X.xv(t, q) for q in shs)
    rest = []
    for q in shs:                                     # lands to the plate 0.0; slit with the four posts left out 0.2 (top band, rail)
        t = X.cp(q)
        for (xx, uu, rr) in ((70.0, 27.0, 5.2), (-70.0, 27.0, 5.2), (85.0, -82.0, 6.2), (-85.0, -82.0, 6.2)):
            X.dif(t, X.cyld(xx, uu, rr, 10.0, 13.4))
        rest.append(t)
    # border strip x 95.5 .. 99 to the nearest shell 1.513 both sides; island's edge 0.73 beyond the wall's front tip (up 0 and -40)


def door(_context):                                   # check 5
    k = sys.modules['cp2k']; cp2 = sys.modules['cp2']; X = k.K()
    slits = [X.cyl((-78.1, -37.3, z), (-69.7, -47.9, z), 0.05) for z in (99.0, 104.9)]   # the BME680's two slits as lines
    for nm in ('HOUSING_F_door_v65', 'HOUSING_F_door'):
        for f in X.body(nm).faces:                    # the nearest slot's wall at x -25.5: 48.64 (version 65), 48.62 (new)
            g = f.geometry
            if g.surfaceType == adsk.core.SurfaceTypes.PlaneSurfaceType and abs(abs(g.normal.x) - 1.0) < 1e-4 and abs(g.origin.x * 10.0 - k.XC + 25.5) < 0.01:
                min(X.mm.measureMinimumDistance(f, s).value * 10.0 + 0.05 for s in slits)
    X.xv(cp2.slot_cut(X, cp2.VENTS['b']), X.cp(X.body('HOUSING_F_door')))                # 0.0: nine slots open; area by their outlines 1,508.1 mm2
    # new door minus old: 8 lumps at the four bosses, 3 old slots filled; old minus new: 18 lumps, the nine slots' two ends. Edge, lip, magnets untouched.


def save_g21(_context):
    k = sys.modules['cp2k']; X = k.K(); st = X.state()
    if adsk.core.Application.get().activeDocument != X.doc or st['version'] != 65 or not st['modified'] or st['bodies'] != 419 or st['visible'] != 37 or st['templates']:
        raise RuntimeError('unexpected state %s' % st)
    X.doc.save('rev F WIP 2026-11-17 g21: posts, shadow gap, FDM strength, door vents (D204–D211) — not for print')    # -> version 66


def export_g21(_context):
    des = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    path = os.path.expanduser('~/Documents/HA Panel v5 - tapered revF-g21.f3d')
    em = des.exportManager
    print(em.execute(em.createFusionArchiveExportOptions(path)), os.path.getsize(path))    # True 193745925


def close_scratch(_context):                          # my picture document only: unsaved "Untitled" with the root attribute cp2/scratch
    app = adsk.core.Application.get()
    mine = [app.documents.item(i) for i in range(app.documents.count)]
    mine = [d for d in mine if d.name == 'Untitled' and not d.isSaved and
            adsk.fusion.Design.cast(d.products.itemByProductType('DesignProductType')).rootComponent.attributes.itemByName('cp2', 'scratch')]
    if len(mine) != 1:
        raise RuntimeError('scratch documents found: %d' % len(mine))
    mine[0].close(False)                              # Daniel's "Untitled" (51 bodies, no attribute) is left as it is
