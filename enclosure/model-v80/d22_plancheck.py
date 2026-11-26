# Block 1: the plan's temporary bodies (d20, kept in k.c) checked against each other and against the model. READ-ONLY.
#   today     the driver as measured (d20's body) against the model as it stands: what it shares with the boxes and the shell at
#             home, and whether its ring passes the shell on the shell's way down (the plate unit b behind, h below its place)
#   plan      the same against the plan's boxes and shell; the ring's room at home (all round, in front) by grown copies
#   way       the ring and the flange on the shell's way down over the window (b 0.95 to 1.60) and 0.25 to either side, against
#             the plan's shell; then with the ring grown by g all round and in front, to give its least room on the way
#   chamber   each box's chamber, the model's and the plan's: the air behind the front face's plane, and that air less the
#             driver's body in it (the record's 'lower' figure), with the model's driver and with the driver as measured
# Run: runpy.run_path(D + 'd22_plancheck.py')['main'](stage)  -> d22_<stage>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
L = runpy.run_path(D + 'v80_lib.py')
B20 = runpy.run_path(D + 'd20_build.py')
AX = 70.5; AZ = 28.0
PCIN = adsk.fusion.PointContainment.PointInsidePointContainment


def need(k, *keys):
    for q in keys:
        if k.c.get(q) is None:
            raise RuntimeError('missing ' + q + ': run d20_build first')


def ring(X, sx, g=0.0, top=0.0):
    return X.cyl((sx * AX, 0.01, AZ), (sx * AX, 2.0 + top, AZ), 18.0 + g)


def flange(X, sx):
    return X.wbox(sx * AX - 23.0, sx * AX + 23.0, -3.8, 0.0, AZ - 23.0, AZ + 23.0)


def bay(X, src, sx):
    a, b = sorted((sx * 40.0, sx * 100.0))
    return L['crop'](X, src, (a, b, -6.0, 8.0, 0.0, 60.0))


def walk(k, X, sh, sx, bs, ss, hs, g=0.0, top=0.0, with_flange=True):
    """First lift at which the ring (and the flange) meet the shell, per (b, s); None if clear at every lift."""
    out = {}
    r0 = ring(X, sx, g, top); f0 = flange(X, sx) if with_flange else None
    for b in bs:
        for s in ss:
            hit = None
            for h in hs:
                v = X.xv(X.move(X.tbm.copy(r0), s, -b, -h), sh)
                vf = X.xv(X.move(X.tbm.copy(f0), s, -b, -h), sh) if f0 is not None else 0.0
                if v > 0.0005 or vf > 0.0005:
                    hit = (h, round(v, 3), round(vf, 3)); break
            out[(b, s)] = hit
    return out


def show(res, what):
    bad = {q: v for q, v in res.items() if v}
    print('   %s: %d positions of (behind, to the side) walked; %s' % (what, len(res), ('MEETS at %s' % bad) if bad else 'clear at every lift'))


HS = [0.5 * i for i in range(0, 121)]                    # lifts 0 to 60
BS = (0.95, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6)


def st_today(k, X):
    need(k, 'ds_spk_L', 'ds_spk_R')
    k.budget(75)
    for sx, s in ((1, 'L'), (-1, 'R')):
        d = k.c['ds_spk_' + s]
        t = X.tbm.copy(d); X.sec(t, X.tbm.copy(X.body('SPKBOX_' + s)))
        print('the driver as measured, in SPKBOX_%s as it stands: shares %.3f mm3 in %d lumps %s' % (s, X.vol(t), t.lumps.count, [q for q in X.lumps(t)][:4]))
        sh = bay(X, 'HOUSING_F_front', sx)
        print('   its ring against the shell as it stands, at home: shares %.3f' % X.xv(ring(X, sx), sh))
        res = walk(k, X, sh, sx, BS, (0.0,), HS, with_flange=False)
        for q, v in sorted(res.items()):
            print('   ring on the way, %.2f behind: %s' % (q[0], ('meets from lift %.1f (%.3f mm3)' % (v[0], v[1])) if v else 'clear'))
        if k.late():
            print('time'); return


def st_plan(k, X):
    need(k, 'ds_spk_L', 'ds_spk_R', 'ds_box_L', 'ds_box_R', 'ds_shell', 'ds_foam_L', 'ds_heads', 'ds_clip_L')
    for sx, s in ((1, 'L'), (-1, 'R')):
        d = k.c['ds_spk_' + s]; bx = k.c['ds_box_' + s]; fo = k.c['ds_foam_' + s]
        sh = bay(X, k.c['ds_shell'], sx)
        print('side %s: driver in the plan\'s box %.4f; foam in box %.4f; foam in driver %.4f; driver in shell %.4f; heads in driver %.4f; heads in shell %.4f' % (
            s, X.xv(d, bx), X.xv(fo, bx), X.xv(fo, d), X.xv(d, sh), X.xv(k.c['ds_heads'], d), X.xv(k.c['ds_heads'], sh)))
        fl = flange(X, sx)
        print('   seat: the flange pushed 0.05 forward shares %.4f with the shell: contact %.1f mm2' % (X.xv(X.move(X.tbm.copy(fl), 0, 0.05, 0), sh), X.xv(X.move(X.tbm.copy(fl), 0, 0.05, 0), sh) / 0.05))
        for g in (0.5, 0.9, 1.0, 1.1, 1.9, 2.0, 2.1):
            print('   ring grown %.1f all round (not forward): shares %.4f with the shell' % (g, X.xv(ring(X, sx, g), sh)))
        for tp in (2.2, 2.29, 2.31, 2.4):
            print('   ring grown %.2f forward: shares %.4f' % (tp, X.xv(ring(X, sx, 0.0, tp), sh)))
        cl = k.c['ds_clip_' + s]
        print('   clip in box %.4f; clip in the model\'s shell %.4f; clip in touch board %.4f; clip pushed 0.39 back in box %.4f; 0.41 back %.4f' % (
            X.xv(cl, bx), X.xv(cl, sh), X.xv(cl, X.tbm.copy(X.body('TOUCH_PCB'))), X.xv(X.move(X.tbm.copy(cl), 0, -0.39, 0), bx), X.xv(X.move(X.tbm.copy(cl), 0, -0.41, 0), bx)))
        for g in (0.25, 0.3, 0.35):
            m = X.cyl((sx * AX, -28.8, AZ), (sx * AX, -18.8, AZ), 16.0 + g)
            print('   magnet grown %.2f: shares %.4f with the box' % (g, X.xv(m, bx)))
    pl = X.tbm.copy(X.body('USBA_plug_env'))
    for g in (0.45, 0.5, 3.0, 3.2, 3.3):
        gb = k.wbb(X, X.body('USBA_plug_env'))
        t = X.wbox(gb[0] - g, gb[1] + g, gb[2] - g, gb[3] + g, gb[4] - g, gb[5] + g)
        print('USB-A plug\'s box grown %.2f: shares %.4f with the plan\'s left box (model\'s box: %.4f)' % (g, X.xv(t, k.c['ds_box_L']), X.xv(t, X.tbm.copy(X.body('SPKBOX_L')))))


def st_way(k, X):
    need(k, 'ds_shell')
    k.budget(78)
    for sx, s in ((1, 'L'), (-1, 'R')):
        sh = bay(X, k.c['ds_shell'], sx)
        show(walk(k, X, sh, sx, BS, (-0.25, 0.0, 0.25), HS), 'side %s, ring and flange as drawn' % s)
        for g in (0.4, 0.5, 0.7, 0.8):
            show(walk(k, X, sh, sx, (0.95, 1.6), (-0.25, 0.25), HS[::2], g=0.0, top=g, with_flange=False), 'side %s, ring %.1f taller' % (s, g))
        for g in (0.4, 0.5, 0.6):
            show(walk(k, X, sh, sx, (0.95, 1.6), (-0.25, 0.25), HS[::2], g=g, top=0.0, with_flange=False), 'side %s, ring %.1f wider all round' % (s, g))
        if k.late():
            print('time'); return


def chamber(k, X, bx, sx, yface, ystop, zmax):
    """The air of a box behind its front face's plane (the opening closed there), as the record's method closes it at y -3.7."""
    x0, x1 = sorted((sx * 40.0, sx * 101.0))
    A = X.wbox(x0, x1, -60.0, 3.0, 1.0, 92.0)
    X.dif(A, X.tbm.copy(bx))
    X.dif(A, X.wbox(x0, x1, yface, ystop, 1.0, zmax))
    X.dif(A, X.cyl((sx * 62.0, -53.5, 30.0), (sx * 62.0, -49.0, 30.0), 2.2))
    pc = k.Wp(sx * AX, -30.0, 62.0)
    for lump in A.lumps:
        if lump.pointContainment(pc) == PCIN:
            t = X.tbm.copy(lump); bb = k.wbb(X, t)
            return t, bb, A.lumps.count
    return None, None, A.lumps.count


def st_chamber(k, X):
    need(k, 'ds_spk_L', 'ds_spk_R', 'ds_box_L', 'ds_box_R')
    for sx, s in ((1, 'L'), (-1, 'R')):
        for tag, bx, yf, ys, zm, drv in (('model, version 79', X.tbm.copy(X.body('SPKBOX_' + s)), -3.7, -3.0, 92.0, X.tbm.copy(X.body('SPK_' + s))),
                                         ('plan', k.c['ds_box_' + s], -5.0, -4.0, 52.2, None)):
            a, bb, n = chamber(k, X, bx, sx, yf, ys, zm)
            if a is None:
                print('SPKBOX_%s, %s: no chamber lump (%d lumps)' % (s, tag, n)); continue
            va = X.vol(a) / 1000.0
            row = 'SPKBOX_%s, %s: air %.3f cm3 (box %s, %d lumps)' % (s, tag, va, bb, n)
            if drv is not None:
                row += '; less the model\'s driver in it: %.3f' % (va - X.xv(drv, a) / 1000.0)
            dm = k.c['ds_spk_' + s]
            if tag == 'plan':
                old = X.tbm.copy(X.body('SPK_' + s)); X.move(old, 0.0, -0.8, 0.0)       # the model's driver with its flange's back at y -3.8
                row += '; less the model\'s driver set 0.8 back: %.3f' % (va - X.xv(old, a) / 1000.0)
            row += '; less the driver as measured: %.3f' % (va - X.xv(dm, a) / 1000.0)
            print(row)


def _main(stage):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'today': st_today, 'plan': st_plan, 'way': st_way, 'chamber': st_chamber}[stage](k, X)
    print(L['stamp'](), 'after', X.state())


def main(stage):
    L['out']('d22_%s.txt' % stage, _main, stage)
# END
