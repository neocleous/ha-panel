# Block 7, after the change: the ways. READ-ONLY (temporary bodies only).
#   'hood'   the hood off and on: lifted along its pins' axis n by L, then toward the middle by m (level, along the hood's own u,
#            away from the wall); shared volume with the shell (cropped round the hood), the radar's envelope, the BME680 board, the
#            pins' tips; the end piece to the wall's end and the foot over the ledges at home
#   'board'  the touch board (board and parts' envelope) out with its clips off: up 1 (over the two lips behind its lower corners),
#            back b, then up;
#            shared volume with every body of the unit near it (cropped), the board's own lead and keep-out left out
#   'clips'  each clip off its place: along -x from home, 0 to 8, and 0.4 back first (its slot); shared volume with every body near
# Run: runpy.run_path(D + 'p71_b7_ways.py')['main'](stage)  -> p71_<stage>.txt
import runpy, math

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
HN = (0.11394, 0.09756, 0.98869); HP0 = (-69.8829, -39.0603, 110.0342)


def near(k, X, box, skip):
    zone = X.wbox(*box); out = []
    for b in k.current(X, leads=False, kos=False):
        if b.name in skip:
            continue
        t = X.tbm.copy(b)
        if not t.boundingBox.intersects(zone.boundingBox):
            continue
        X.sec(t, X.tbm.copy(zone))
        if t.faces.count:
            out.append((b.name, t))
    return out


def hits(X, movers, fixed, dx, dy, dz):
    h = {}
    for m in movers:
        t = X.move(X.tbm.copy(m), dx, dy, dz)
        for nm, f in fixed:
            v = X.xv(t, f)
            if v > 0.0005:
                h[nm] = round(h.get(nm, 0) + v, 4)
    return h


def hood(k, X):
    n = k.unit(HN); u = (0.7593, 0.6497, 0.0); u = k.unit(u)
    H = X.tbm.copy(X.body('BME_HOOD'))
    fixed = near(k, X, (-95, -45, -62, -15, 85, 125), ('BME_HOOD', 'FOAM_bme_env', 'FOAM_bme_top_env', 'SCREWS_M2x6_env'))
    print('fixed near the hood: %s' % [f[0] for f in fixed])
    for Lf in (0.0, 0.5, 1.0, 1.5, 1.9, 2.0, 2.1, 2.5, 3.0, 3.5, 3.7, 3.8, 4.0):
        print('lift %.1f along the pins: %s' % (Lf, hits(X, [H], fixed, Lf * n[0], Lf * n[1], Lf * n[2]) or 'clear'))
    for Lf in (2.1, 2.5, 3.0, 3.5):
        row = []
        for m in (0.5, 1.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0):
            hh = hits(X, [H], fixed, Lf * n[0] + m * u[0], Lf * n[1] + m * u[1], Lf * n[2] + m * u[2])
            row.append((m, hh or 'clear'))
        print('lift %.1f, then toward the middle: %s' % (Lf, row))
    S = X.body('HOUSING_F_front'); hb = X.body('BME_HOOD')
    t = X.add(X.tbm.copy(hb), 'TMP_h', show=False)
    for lab, hbx, sbx in (('end piece to the wall\'s end', (-59.6, -56.5, -50.2, -46.2, 103.8, 108.4), (-62, -54, -55, -44, 96, 110)),
                          ('foot (side plate\'s lower end) over the ledges', (-78, -59, -48, -26, 91.5, 92.6), (-85, -55, -60, -20, 85, 92.0))):
        a = X.wbox(*hbx); X.sec(a, X.tbm.copy(hb)); b = X.wbox(*sbx); X.sec(b, X.tbm.copy(S))
        if a.faces.count and b.faces.count:
            ta = X.add(a, 'TMP_a', show=False); tb = X.add(b, 'TMP_b', show=False)
            r = X.mm.measureMinimumDistance(ta, tb)
            print('%s: %.3f at %s / %s' % (lab, r.value * 10, k.r2(k.W(r.positionOne)), k.r2(k.W(r.positionTwo))))
            ta.deleteMe(); tb.deleteMe()
    t.deleteMe()


def board(k, X):
    movers = [X.tbm.copy(X.body('TOUCH_PCB')), X.tbm.copy(X.body('TOUCH_components_env'))]
    fixed = near(k, X, (-60, 60, -30, 10, -2, 110), ('TOUCH_PCB', 'TOUCH_components_env', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'SCREWS_M2x6_env'))
    print('fixed near the board: %s' % [f[0] for f in fixed])
    # the board stands on its ledge (z 6.0) with two lips 0.8 tall behind its lower corners (x +-43..45, y 1.7..2.4): up 1.0 first.
    # A hit under 0.01 mm3 against the shell is the board's front face lying on the seat (coplanar faces), not a clash.
    for h in (0.25, 0.5, 1.0):
        print('up %.2f: %s' % (h, hits(X, movers, fixed, 0, 0, h) or 'clear'))
    for b in (0.5, 1.0, 2.0, 3.0, 4.0, 5.0):
        print('up 1, back %.1f: %s' % (b, hits(X, movers, fixed, 0, -b, 1.0) or 'clear'))
    for bb in (3.0, 4.0):
        for h in (2.0, 3.0, 5.0, 10.0, 20.0, 30.0, 40.0):
            print('up 1, back %.0f, up %.1f more: %s' % (bb, h - 1.0, hits(X, movers, fixed, 0, -bb, h) or 'clear'))


def clips(k, X):
    for nm, sx in (('TOUCH_CLIP_L', 1), ('TOUCH_CLIP_R', -1)):
        c = X.tbm.copy(X.body(nm))
        fixed = near(k, X, (sx * 30 - 20, sx * 30 + 20, -20, 10, 20, 56), (nm, 'SCREWS_M2x6_env', 'KO_touch_back'))
        print('%s fixed near: %s' % (nm, [f[0] for f in fixed]))
        for back in (0.0, 0.4):
            for s in (0.0, 0.5, 1.0, 2.0, 4.0, 6.0, 8.0):
                print('   %s %.1f back, %.1f toward the middle: %s' % (nm, back, s, hits(X, [c], fixed, -sx * s, -back, 0) or 'clear'))


def _main(stage):
    k = L['load'](); X = k.K(); k.budget(75)
    print(L['stamp'](), 'before', X.state())
    {'hood': hood, 'board': board, 'clips': clips}[stage](k, X)
    for b in [b for b in X.root.bRepBodies if b.name.startswith('TMP_')]:
        b.deleteMe()
    print(L['stamp'](), 'after', X.state())


def main(stage):
    L['out']('p71_%s.txt' % stage, _main, stage)
