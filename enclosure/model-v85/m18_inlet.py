# Block 3 (D489): the inlet board's two M2 x 6, flat-headed on the board's holes of 2.5, drawn into SCREWS_M2x6_env, and read.
# World mm. The screws drawn as the body's nine (../model-v80/d41_build4.py: head 3.8 across with a rim 0.3 high and a 90 deg
# cone of 0.9 to the shank 2.0 across, 6.0 long over all), the cone seated on the rim of the board's hole, 2.5 across (record:
# fastener schedule of 2026-11-06), on the board's top face as the model has it (PD_5807_env, read here), axes on the cradle's
# two pilots (read here). NOTHING IS PUT INTO THE DOCUMENT here (m16_put.py does that).
#   read    along each pilot's axis: the solid stretches of every body near it, from z 30 down to z 0; the cradle's faces near the
#           pilot's top (a chamfer?); the board envelope's world box
#   build   the two screws, added to a copy of SCREWS_M2x6_env (from SCREWS_M2x6_env_v85 if it exists) -> k.c['bm_m2']
#   check   each new screw: head top, tip, the thread in the cradle (from the pilot's top), the tip to the pilot's far end and to the
#           next body beyond; what it shares with every body of the unit, what stands within 2.0 of it (head and shank apart);
#           the driver's way: a bar 150 long above the head, 4.2, 6.0 and 8.0 across: the bodies it shares with
# Run: L.checked('m18_inlet.py', sha)['main'](stage, tag, **kw)  -> m18_<stage>_<tag>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/box_margins_v85/'
L = runpy.run_path(D + 'm00_lib.py')
AXES = ((-7.49, -81.16), (7.75, -81.16))        # the cradle's two pilots, 1.6 across, upright, z 14.5 to 20.2 (m10_holes_a.txt)
HOLE_R = 1.25; R_SH = 1.0; R_HD = 1.9; H_RIM = 0.3; H_CONE = 0.9; LEN = 6.0


def near_names(k, X, box, skip=()):
    out = []
    for b in k.current(X, leads=True, kos=False):
        if b.name in skip:
            continue
        q = k.wbb(X, b)
        if q[1] < box[0] or q[0] > box[1] or q[3] < box[2] or q[2] > box[3] or q[5] < box[4] or q[4] > box[5]:
            continue
        out.append(b.name)
    return out


def st_read(k, X):
    k.budget(70)
    print('PD_5807_env world box %s; CRADLE_5807 %s' % (k.wbb(X, X.body('PD_5807_env')), k.wbb(X, X.body('CRADLE_5807'))))
    for x, y in AXES:
        names = near_names(k, X, (x - 2, x + 2, y - 2, y + 2, 0.0, 40.0))
        print('axis (%.2f, %.2f): bodies near it %s' % (x, y, names))
        for n in names:
            for dx in (0.0, 1.45):
                st = k.needle_t(X, k.parts(X, n), (x + dx, y, 40.0), (x + dx, y, 0.0), 0.02)
                if st:
                    print('   %-22s %s: solid z %s' % (n, 'on the axis' if dx == 0 else '1.45 off it', [(round(40.0 - b, 2), round(40.0 - a, 2)) for a, b in st]))
        for r in k.faces(X, X.body('CRADLE_5807'), (x - 3, x + 3, y - 3, y + 3, 18.0, 22.0), kinds=('p', 'c'), amin=0.05):
            print('   cradle face %s' % (r,))
        for f in X.body('CRADLE_5807').faces:
            if f.geometry.surfaceType == adsk.core.SurfaceTypes.ConeSurfaceType:
                p = k.W(f.pointOnFace)
                if abs(p[0] - x) < 3 and abs(p[1] - y) < 3:
                    ws = [k.W(v.geometry) for v in f.vertices]
                    print('   cradle cone face at %s, %.3f mm2, z %s' % (k.r2(p, 2), f.area * 100, [round(min(w[2] for w in ws), 3), round(max(w[2] for w in ws), 3)] if ws else None))


def screw(k, X, x, y, zb):
    zc0 = zb - (HOLE_R - R_SH); zc1 = zc0 + H_CONE; ztop = zc1 + H_RIM; ztip = ztop - LEN
    s = X.cyl((x, y, ztip), (x, y, zc0), R_SH)
    X.uni(s, X.cyl((x, y, zc0), (x, y, zc1), R_SH, R_HD))
    X.uni(s, X.cyl((x, y, zc1), (x, y, ztop), R_HD))
    return s, ztip, ztop


def board_top(k, X, x, y):
    st = k.needle_t(X, k.parts(X, 'PD_5807_env'), (x, y, 40.0), (x, y, 0.0), 0.02)
    return [(round(40.0 - b, 3), round(40.0 - a, 3)) for a, b in st]


def st_build(k, X, zb=None):
    src = X.body('SCREWS_M2x6_env_v85') or X.body('SCREWS_M2x6_env')
    t = X.tbm.copy(src)
    for x, y in AXES:
        bt = board_top(k, X, x, y)
        z = zb if zb is not None else max(b for a, b in bt)
        s, ztip, ztop = screw(k, X, x, y, z)
        print('screw at (%.2f, %.2f): the board envelope on the axis %s; seated on z %.3f: head top z %.3f, tip z %.3f; %.3f mm3' % (x, y, bt, z, ztop, ztip, X.vol(s)))
        X.uni(t, s)
    k.c['bm_m2'] = t
    print('bm_m2 %.3f mm3, lumps %d | built from %s %.3f, lumps %d' % (X.vol(t), t.lumps.count, src.name, src.volume * 1000, src.lumps.count))


def st_check(k, X, src='model'):
    k.budget(72)
    S = k.c['bm_m2'] if src == 'cache' else X.tbm.copy(X.body('SCREWS_M2x6_env'))
    C = X.body('CRADLE_5807')
    for x, y in AXES:
        lump = None
        for lp in S.lumps:
            t = X.tbm.copy(lp); bb = k.wbb(X, t)
            if bb[0] - 0.1 <= x <= bb[1] + 0.1 and bb[2] - 0.1 <= y <= bb[3] + 0.1:
                lump = t; lb = bb
        if lump is None:
            print('(%.2f, %.2f): NO SCREW' % (x, y)); continue
        ztip, ztop = lb[4], lb[5]
        cr = k.needle_t(X, k.parts(X, 'CRADLE_5807'), (x, y, 30.0), (x, y, 0.0), 0.02)
        crz = [(round(30.0 - b, 3), round(30.0 - a, 3)) for a, b in cr]
        ring = k.needle_t(X, k.parts(X, 'CRADLE_5807'), (x + 0.85, y, 30.0), (x + 0.85, y, 0.0), 0.02)
        ringz = [(round(30.0 - b, 3), round(30.0 - a, 3)) for a, b in ring]
        print('screw at (%.2f, %.2f): %.3f mm3; head top z %.3f, tip z %.3f' % (x, y, X.vol(lump), ztop, ztip))
        print('   the cradle on the axis: solid z %s; at 0.85 off it (the pilot\'s wall): solid z %s' % (crz, ringz))
        print('   the bodies on the axis below the tip:')
        for n in near_names(k, X, (x - 1, x + 1, y - 1, y + 1, ztip - 20.0, ztip), skip=('SCREWS_M2x6_env',)):
            st = k.needle_t(X, k.parts(X, n), (x, y, ztip), (x, y, ztip - 20.0), 0.02)
            if st:
                print('      %-22s from the tip down: %s' % (n, st))
        sh = []; nr = []
        for n in near_names(k, X, (lb[0] - 2.5, lb[1] + 2.5, lb[2] - 2.5, lb[3] + 2.5, lb[4] - 2.5, lb[5] + 2.5), skip=('SCREWS_M2x6_env',)):
            v = sum(X.xv(X.tbm.copy(lump), p) for p in k.parts(X, n))
            if v > 0.0005:
                sh.append('%s %.4f' % (n, v))
            dd = min(X.mm.measureMinimumDistance(X.tbm.copy(lump), p).value * 10 for p in k.parts(X, n))
            if dd < 2.0:
                nr.append('%s %.3f' % (n, dd))
        print('   shares with: %s' % (', '.join(sh) or 'nothing'))
        print('   within 2.0: %s' % (', '.join(nr) or 'nothing'))
        hd = X.cyl((x, y, ztop - 1.2), (x, y, ztop), R_HD)
        for n in near_names(k, X, (x - 4.5, x + 4.5, y - 4.5, y + 4.5, ztop - 3.5, ztop + 2.5), skip=('SCREWS_M2x6_env',)):
            dd = min(X.mm.measureMinimumDistance(hd, p).value * 10 for p in k.parts(X, n))
            if dd < 2.5:
                print('   round the head (3.8 across, 1.2 high): %-22s %.3f' % (n, dd))
        for r in (2.1, 3.0, 4.0):
            hit = []
            for n in near_names(k, X, (x - r, x + r, y - r, y + r, ztop, ztop + 150.0), skip=('SCREWS_M2x6_env',)):
                v = 0.0; zs = []
                for p in k.parts(X, n):
                    c = X.cyl((x, y, ztop + 0.05), (x, y, ztop + 150.0), r); X.sec(c, X.tbm.copy(p))
                    if c.faces.count and X.vol(c) > 1e-4:
                        v += X.vol(c); zs += [k.W(vx.geometry)[2] for vx in c.vertices]
                if v > 1e-4:
                    hit.append('%s %.2f (z %.1f..%.1f)' % (n, v, min(zs), max(zs)) if zs else '%s %.2f' % (n, v))
            print('   driver\'s way, a bar %.1f across above the head, 150 long: %s' % (2 * r, ', '.join(hit) or 'free'))
        if k.late():
            print('time'); return


def _main(stage, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'read': st_read, 'build': st_build, 'check': st_check}[stage](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(stage, tag='', **kw):
    L['out']('m18_%s%s.txt' % (stage, ('_' + tag) if tag else ''), _main, stage, **kw)
# END
