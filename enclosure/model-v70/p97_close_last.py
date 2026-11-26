# The close (brief block 10 point 2): the last pass's checks (claude/report-enclosure-screws-block4-2026-11-23.md, checks 1 to
# 13) that no script of this pass repeats, read on the saved version by the last pass's methods (enclosure/model-v68/
# v69_checks.py on docs; c3k.line and K4NS['slide'] at 45a38e4). READ-ONLY but for TMP_ bodies, deleted again.
#   'usb'        check 1 and check 3's step 15: the ReSpeaker's USB cable to what stands round it at home; the left box slid on
#                (K4NS slide, 17 positions) against the plate unit's bodies; the box and its driver to the plug and the cable
#   'hoodscrew'  check 2: the precision driver (MICRO) and a hand (MICROG) straight out of the hood's screw head, everything in
#                but the door; the leads beside it
#   'hoodout'    check 2: the hood lifted 3.5 off its pegs, moved toward the middle (part='across'), then drawn back out through
#                the door opening at 48, 56 and 60 toward the middle (part='back'), display module out: shared volume and nearest
#   'clipkey'    check 2: the 2.0 key's long arm swept from pointing back to straight up on a touch clip's screw (p89's sweep,
#                set to the clip's screw: y -7.05, z 38.0, head's top at x +-38.85, elbow at x +-24.9). side 'L' or 'R'; state
#                'build' (step 22) or 'service' (module in); holder=False leaves the radar's holder and the radar out.
#                The line 'the short arm ... meets' is p89's for the holder's own screw and says nothing here.
#   'dispkeys'   check 2: the display screws' four key lanes, which the model holds as keep-outs KO_K5_* (the key's space with
#                2.0 round it): each against every body and lead within 3, everything in but the door
#   'pilots'     check 7: the wall round every pilot 1.6 across in the cap, the door, the shell and the holder: 12 directions
#                every 0.5 along the pilot, the first solid stretch from the pilot's wall outward
#                (names=(...) reads other bodies, such as the hidden _v69 copies, the same way)
#   'small'      check 6: the supply module (its pins) to the ReSpeaker's bodies at home and with the main board 0.1 out;
#                check 12: the cap's light opening and the sensor board's envelope; check 5: the clamps' faces that look at
#                the strip, now and at version 69, and the strips' envelopes
#   'pliers'     check 2's pliers on the Pi's USB-C plug: the pliers' shape of the last pass is in no file, so what is read
#                instead is what this pass added or removed within 40 of the plug's envelope (each body against its hidden
#                _v69 copy), and how near the added material comes to the plug
# Run: runpy.run_path(D + 'p97_close_last.py')['main'](stage, tag='', **kw)  -> p97_<stage>[_<tag>].txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
P95 = runpy.run_path(D + 'p95_close_checks.py')
dist = P95['dist']; crop = P95['crop']
HN = (0.11394, 0.09756, 0.98869)           # the hood's own up (its pins' axis), as p71 and p95 have it
OUT = (0.0, -0.9781, -0.2079)              # along the screen's normal, away from the viewer
DOOR = ('HOUSING_F_door', 'GROMMET_usbc_F')
MODULE = ('SLAB_frame', 'LCD_', 'RESP_', 'MAIN_')
HOLES = (('upper, viewer\'s left', 70.0, 27.0, 12.8), ('upper, viewer\'s right', -70.0, 27.0, 12.8),
         ('lower, viewer\'s left', 85.0, -82.002, 11.4), ('lower, viewer\'s right', -85.0, -82.002, 11.4))   # p49_holes.txt


def grow(b, e):
    return (b[0] - e, b[1] + e, b[2] - e, b[3] + e, b[4] - e, b[5] + e)


def usb(k, X):
    c = X.body('LEAD_USB_RESP'); cb = k.wbb(X, c)
    print('USB cable LEAD_USB_RESP, box %s' % k.r2(cb))
    for n in ('HOUSING_F_front', 'HOUSING_F_plate', 'SPKBOX_L', 'SPK_L', 'USBA_plug_env', 'FLOOR_PLATE', 'RESP_CARRIER', 'PI5_F', 'RADAR_HOLDER'):
        b = X.body(n)
        t = crop(X, b, grow(cb, 8.0))
        print('   to %-16s %s' % (n, dist(k, X, c, t) if t.faces.count else 'more than 8'))
        o = X.body(n + '_v69')
        if o:
            t0 = crop(X, o, grow(cb, 8.0))
            add = X.tbm.copy(t); X.dif(add, X.tbm.copy(t0)); rem = X.tbm.copy(t0); X.dif(rem, X.tbm.copy(t))
            print('      its _v69 copy: %s; within 8 of the cable\'s box this pass added %.3f and removed %.3f'
                  % (dist(k, X, c, t0), X.vol(add) if add.faces.count else 0.0, X.vol(rem) if rem.faces.count else 0.0))
    for a, b in (('SPKBOX_L', 'USBA_plug_env'), ('SPK_L', 'USBA_plug_env'), ('SPKBOX_L', 'RESP_usbc_plug_env')):
        if X.body(a) and X.body(b):
            pb = k.wbb(X, X.body(b))
            print('   %s to %s: %s' % (a, b, dist(k, X, crop(X, X.body(a), grow(pb, 8.0)), X.body(b))))
    fixed = tuple(n for n in ('FLOOR_PLATE', 'PI5_F', 'PI5_F_cooler', 'PIPWR_a_env', 'CRADLE_5807', 'PD_5807_env', 'USBA_plug_env',
                              'LEAD_USB_RESP', 'SPKBOX_R', 'SPK_R') if X.body(n))
    res = k.K4NS['slide'](X, 'v79s15', fixed=fixed)
    bad = {q: h for q, h in res.items() if h}
    print('step 15, the left box and its driver slid on (K4NS slide): %d positions against %s: %s' % (len(res), list(fixed), bad or 'nothing shared at any'))


def hood_head(k, X):
    S = X.body('SCREWS_M2x6_env'); hb = k.wbb(X, X.body('BME_HOOD'))
    mid = ((hb[0] + hb[1]) / 2, (hb[2] + hb[3]) / 2, (hb[4] + hb[5]) / 2)
    best = None
    for f in S.faces:
        if f.geometry.surfaceType != adsk.core.SurfaceTypes.PlaneSurfaceType or abs(f.area * 100 - math.pi * 1.9 ** 2) > 0.2:
            continue
        p = k.W(f.centroid)
        d = math.sqrt(sum((p[i] - mid[i]) ** 2 for i in range(3)))
        if best is None or d < best[0]:
            ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
            best = (d, p, k.unit(k.wv(nv)))
    return best[1], best[2]


def hoodscrew(k, X):
    o, u = hood_head(k, X)
    print('hood\'s screw: head\'s top at %s, driver along %s' % (k.r2(o), k.r2(u, 4)))
    hard = [b for b in k.current(X, leads=False, kos=False) if b.name not in DOOR + ('SCREWS_M2x6_env',) and not b.name.startswith('FOOT_')]
    leads = [b for b in k.current(X, leads=True, kos=False) if b.name.startswith('LEAD_')]
    print('   everything in but the door (%d bodies, %d leads): %s' % (len(hard), len(leads), k.probe(X, o, u, k.MICRO, k.MICROG, hard, leads, st0=2.0, step=5.0)))
    r = k.line(X, o, u, k.MICRO, hard, st0=2.0, step=5.0)
    print('   tool rows %s' % r['rows'])
    build = [b for b in hard if not b.name.startswith(MODULE) and b.name not in ('HOUSING_F_cap', 'MIC_CLAMP_L', 'MIC_CLAMP_R', 'MIC_strip_L_env', 'MIC_strip_R_env', 'VEML_env')]
    print('   step 18 (no display module, no cap; %d bodies): %s' % (len(build), k.probe(X, o, u, k.MICRO, k.MICROG, build, None, st0=2.0, step=5.0)))


def hoodout(k, X, part='across'):
    hood = X.tbm.copy(X.body('BME_HOOD'))
    o, u = hood_head(k, X)
    gone = DOOR + ('BME_HOOD', 'MAIN_plug_env', 'MAIN_J2_plug_env')
    zone = X.wbox(-95.0, 8.0, -130.0, -12.0, 78.0, 142.0)
    items = []
    for b in k.current(X, leads=False, kos=False):
        n = b.name
        if n in gone or n.startswith(MODULE) or n.startswith('FOOT_'):
            continue
        t = X.tbm.copy(b)
        if not t.boundingBox.intersects(zone.boundingBox):
            continue
        X.sec(t, X.tbm.copy(zone))
        if n == 'SCREWS_M2x6_env' and t.faces.count:
            X.dif(t, X.sph(o, 8.0))                     # the hood's own screw is out
        if t.faces.count:
            items.append((n, t))
    print('hood out, display module out; against %d bodies near its way: %s' % (len(items), [n for n, t in items]))
    across = (0.5, 1, 2, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60)
    back = (5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60)
    pos = [('lift 3.5, across %g' % s, s, 0.0) for s in across] if part == 'across' else [('lift 3.5, across %g, back %g' % (s, b), s, b) for s in (48.0, 56.0, 60.0) for b in back]
    for name, s, b in pos:
        if k.late():
            print('time'); break
        t = X.move(X.tbm.copy(hood), 3.5 * HN[0] + s, 3.5 * HN[1] - b, 3.5 * HN[2])
        q = t.boundingBox; e = 1.2
        bb = adsk.core.BoundingBox3D.create(adsk.core.Point3D.create(q.minPoint.x - e, q.minPoint.y - e, q.minPoint.z - e),
                                            adsk.core.Point3D.create(q.maxPoint.x + e, q.maxPoint.y + e, q.maxPoint.z + e))
        best = None; shared = {}
        for n, p in items:
            if not bb.intersects(p.boundingBox):
                continue
            rr = X.mm.measureMinimumDistance(t, p); dd = rr.value * 10.0
            if dd < 0.0005:
                v = X.xv(t, p)
                if v > 0.0005:
                    shared[n] = round(v, 3)
            if best is None or dd < best[0]:
                best = (round(dd, 2), n, 'on the hood at', k.r2(k.W(rr.positionOne)))
        print('   %-32s shared %s, nearest %s' % (name, shared or '0', best if best else 'more than 12'))


def clipkey(k, X, side='L', state='build', holder=False):
    P89 = runpy.run_path(D + 'p89_b9_ways.py')
    sx = 1.0 if side == 'L' else -1.0
    g = P89['key'].__globals__                 # run_path hands back a copy: the functions read their own globals
    g['M3'] = (-7.05, 38.0); g['HEAD_X'] = 38.85 if sx > 0 else -38.85 - 1.3
    off = () if holder else ('RADAR_HOLDER', 'LD2410C_env_F')
    h0 = g['hard']
    g['hard'] = lambda k_, X_, st, skip=(): h0(k_, X_, st, skip=off)
    print('touch clip %s, its screw at (y -7.05, z 38.0), state %s, holder and radar %s:' % (side, state, 'on' if holder else 'off'))
    P89['key'](k, X, state, xes=(sx * 24.9,), step=5, lo=0, hi=95)


def dispkeys(k, X):
    # The lanes are in the model as keep-outs KO_K5_*: the key's space with 2.0 round it (the record's "+2.45 to the main
    # board's edge" is 0.45 from the keep-out). A first try of this stage walked the screen plate's own four screw holes
    # (p49_holes.txt), which are not the display screws: its output is kept as p97_dispkeys_first.txt.
    kos = [b for b in X.root.bRepBodies if b.name.startswith('KO_K5') and not k.BACK.search(b.name)]
    others = [b for b in k.current(X, leads=True, kos=False) if b.name not in DOOR and not b.name.startswith('FOOT_')]
    print('display screws\' key lanes: %d keep-outs %s; against %d bodies and leads, everything in but the door' % (len(kos), [b.name for b in kos], len(others)))
    for ko in kos:
        if k.late():
            print('time'); break
        kb = k.wbb(X, ko); zone = grow(kb, 4.0); zb = X.wbox(*zone)
        rows = []
        for b in others:
            t = X.tbm.copy(b)
            if not t.boundingBox.intersects(zb.boundingBox):
                continue
            X.sec(t, X.tbm.copy(zb))
            if not t.faces.count:
                continue
            d = dist(k, X, ko, t)
            if d[0] <= 3.0:
                rows.append((d[0], b.name, d[1]))
        rows.sort()
        print('   %s box %s, volume %.3f: %s' % (ko.name, k.r2(kb), ko.volume * 1000, [(r[0], r[1]) for r in rows[:9]]))
        if rows:
            print('      nearest at %s' % (rows[0][2],))


def pilots(k, X, names=('HOUSING_F_cap', 'HOUSING_F_door', 'HOUSING_F_front', 'RADAR_HOLDER')):
    for nm in names:
        b = X.body(nm)
        for h in k.holes_of(b, 0.75, 0.85):
            if h['k'] != 'h' or h['L'] < 1.5:
                continue
            A = h['A']; B = h['B']; Ln = h['L']
            ax = k.unit((B[0] - A[0], B[1] - A[1], B[2] - A[2]))
            ref = (0.0, 0.0, 1.0) if abs(ax[2]) < 0.9 else (1.0, 0.0, 0.0)
            e1 = k.unit((ax[1] * ref[2] - ax[2] * ref[1], ax[2] * ref[0] - ax[0] * ref[2], ax[0] * ref[1] - ax[1] * ref[0]))
            e2 = (ax[1] * e1[2] - ax[2] * e1[1], ax[2] * e1[0] - ax[0] * e1[2], ax[0] * e1[1] - ax[1] * e1[0])
            box = (min(A[0], B[0]) - 8, max(A[0], B[0]) + 8, min(A[1], B[1]) - 8, max(A[1], B[1]) + 8, min(A[2], B[2]) - 8, max(A[2], B[2]) + 8)
            c = crop(X, b, box)
            least = None; opn = 0; rows = []
            s = 0.25
            while s < Ln:
                p0 = (A[0] + ax[0] * s, A[1] + ax[1] * s, A[2] + ax[2] * s)
                smin = None
                for j in range(12):
                    a = math.radians(30 * j)
                    dr = tuple(e1[i] * math.cos(a) + e2[i] * math.sin(a) for i in range(3))
                    st = k.needle_t(X, [c], p0, (p0[0] + dr[0] * 7, p0[1] + dr[1] * 7, p0[2] + dr[2] * 7), 0.02)
                    st = [q for q in st if q[1] > h['r'] - 0.05]
                    if not st or st[0][0] > h['r'] + 0.15:
                        opn += 1; continue
                    w = round(st[0][1] - max(st[0][0], h['r']), 2)
                    if smin is None or w < smin:
                        smin = w
                    if least is None or w < least[0]:
                        least = (w, round(s, 2), 30 * j)
                rows.append(smin)
                s += 0.5
            print('%s pilot r %.2f from %s to %s, L %.2f, cov %.2f: least wall %s (wall, along, direction); rays open or not at the wall %d of %d; per station %s'
                  % (nm, h['r'], k.r2(A), k.r2(B), Ln, h['cov'], least, opn, 12 * len(rows), rows))


def small(k, X):
    ps = X.body('MAIN_PS1'); pb = k.wbb(X, ps)
    for n in ('RESP_top_env', 'RESP_pcb', 'RESP_CARRIER', 'RESP_mic_env'):
        b = X.body(n)
        if not b:
            continue
        t = crop(X, b, grow(pb, 10.0))
        if not t.faces.count:
            print('MAIN_PS1 to %s: more than 10' % n); continue
        d0 = dist(k, X, ps, t)
        mv = X.move(X.tbm.copy(ps), 0.1 * OUT[0], 0.1 * OUT[1], 0.1 * OUT[2])
        print('MAIN_PS1 to %-14s at home %s; main board 0.1 out %s' % (n, d0, dist(k, X, mv, t)[0]))
    cap = X.body('HOUSING_F_cap')
    for h in k.holes_of(cap, 0.9, 1.8):
        if abs(h['A'][0]) < 3.0:
            print('cap, hole on the middle: r %.3f from %s to %s, L %.2f, cov %.2f' % (h['r'], k.r2(h['A'], 3), k.r2(h['B'], 3), h['L'], h['cov']))
    for n in ('VEML_env', 'VEML_env_v67'):
        if X.body(n):
            print('%s box %s, volume %.3f' % (n, k.r2(k.wbb(X, X.body(n))), X.body(n).volume * 1000))
    for n in ('MIC_CLAMP_L', 'MIC_CLAMP_L_v69', 'MIC_strip_L_env', 'MIC_strip_L_env_v69'):
        b = X.body(n)
        if not b:
            continue
        print('%s box %s' % (n, k.r2(k.wbb(X, b))))
        if 'CLAMP' not in n:
            continue
        for f in b.faces:
            if f.geometry.surfaceType != adsk.core.SurfaceTypes.PlaneSurfaceType or f.area * 100 < 0.5:
                continue
            ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); w = k.wv(nv)
            if w[2] < 0.999:
                continue
            pts = [k.W(v.geometry) for v in f.vertices]
            if not pts:
                continue
            print('   faces up: z %.2f, %.2f mm2, x %.2f..%.2f, y %.2f..%.2f' % (pts[0][2], f.area * 100, min(p[0] for p in pts), max(p[0] for p in pts), min(p[1] for p in pts), max(p[1] for p in pts)))


def pliers(k, X):
    plug = X.body('PIPWR_a_env'); pb = k.wbb(X, plug)
    zone = grow(pb, 40.0)
    print('PIPWR_a_env box %s; zone %s' % (k.r2(pb), k.r2(zone)))
    names = X.names()
    for n in sorted(names):
        if not n.endswith('_v69') or n[:-4] not in names:
            continue
        new = crop(X, X.body(n[:-4]), zone); old = crop(X, X.body(n), zone)
        if not new.faces.count and not old.faces.count:
            continue
        add = X.tbm.copy(new) if new.faces.count else None
        if add and old.faces.count:
            X.dif(add, X.tbm.copy(old))
        rem = X.tbm.copy(old) if old.faces.count else None
        if rem and new.faces.count:
            X.dif(rem, X.tbm.copy(new))
        va = X.vol(add) if add and add.faces.count else 0.0; vr = X.vol(rem) if rem and rem.faces.count else 0.0
        if va < 0.001 and vr < 0.001:
            print('%-22s in the zone: unchanged' % n[:-4]); continue
        da = dist(k, X, add, plug) if va >= 0.001 else None
        dn = dist(k, X, new, plug)[0] if new.faces.count else None; do = dist(k, X, old, plug)[0] if old.faces.count else None
        print('%-22s in the zone: added %.3f, removed %.3f; added material to the plug %s; body to the plug %s (version 69: %s)' % (n[:-4], va, vr, da, dn, do))
    for n in ('RADAR_HOLDER',):
        print('%s to the plug: %s' % (n, dist(k, X, X.body(n), plug)))


def _main(stage, kw):
    k = L['load'](); X = k.K(); k.budget(74)
    print(L['stamp'](), 'before', X.state())
    {'usb': usb, 'hoodscrew': hoodscrew, 'hoodout': hoodout, 'clipkey': clipkey, 'dispkeys': dispkeys, 'pilots': pilots, 'small': small, 'pliers': pliers}[stage](k, X, **kw)
    for b in [b for b in X.root.bRepBodies if b.name.startswith('TMP_')]:
        b.deleteMe()
    print(L['stamp'](), 'after', X.state())


def main(stage, tag='', **kw):
    L['out']('p97_%s%s.txt' % (stage, ('_' + tag) if tag else ''), _main, stage, kw)
