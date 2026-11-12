# rev F k2b (2026-11-12): fix pass, block 2 - the base plate. Run through k.step(); the library is the global k.
#   Fix 4  the lowered band (top z 1.8) under the shell's side walls is widened so that the raised field (top z 2.5) stays GAP or more
#          from the wall's inner bottom edge for every position of the plate unit from in place to SMAX behind:
#          tool = the wall's bottom section (z 2.8..3.0, taken down to z 1.8) grown by GAP in plan and swept SMAX toward the screen,
#          limited to the sides (|x| >= XMIN, y YA..YB). The plate's rim below z 1.8 is not touched.
#   Fix 2  the two front foot recesses (13.0 across, 0.5 deep) are filled at (+-80, -11.5) and cut again at (+-80, FOOT_Y);
#          FOOT_FL and FOOT_FR move with them.
#   dry(X) builds on temporary bodies and prints the checks; apply(X) swaps (old bodies -> <name>_v55, hidden).
import math
GAP = 1.2; SMAX = 1.5; YA, YB = -60.0, -3.0; XMIN = 62.0
FOOT_X = 80.0; FOOT_Y = -5.5; FOOT_OLD_Y = -11.5; REC_R = 6.5; REC_D = 0.5
SUF = '_v55'
YS = (-5.0, -15.0, -25.0, -30.0, -35.0, -45.0, -50.0, -54.5)
SH = (0.0, 1.05, 1.3, 1.5)


def wall(X, sx):                                     # the shell's bottom edge on one side
    return k.region(X, 'HOUSING_F_front', 'bot%+d' % sx, (60, 100, -64, 14, 2.6, 3.4) if sx > 0 else (-100, -60, -64, 14, 2.6, 3.4))


def band_tool(X, sx):
    sl = None
    for p in wall(X, sx):
        t = X.cp(p); X.sec(t, X.wbox(sx * 60.0, sx * 100.0, -64.0, 14.0, 2.8, 3.0))
        if X.vol(t) > 0.001:
            sl = t if sl is None else X.uni(sl, t)
    pr = None
    for j in range(7):                               # the section as a prism from z 1.6 to 3.0
        t = X.cp(sl); X.move(t, 0.0, 0.0, -0.2 * j)
        pr = t if pr is None else X.uni(pr, t)
    out = X.cp(pr); s = 0.0
    while s <= SMAX + 1e-6:
        if s > 0:
            t = X.cp(pr); X.move(t, 0.0, s, 0.0); X.uni(out, t)
        for i in range(16):
            a = math.pi / 8.0 * i
            t = X.cp(pr); X.move(t, GAP * math.cos(a), GAP * math.sin(a) + s, 0.0); X.uni(out, t)
        s += 0.5
    X.sec(out, X.wbox(sx * XMIN, sx * 100.0, YA, YB, 1.8, 3.2))
    return out


def plate_new(X):
    new = X.cp(X.body('FLOOR_PLATE')); tools = {}
    for sx in (1, -1):
        tools[sx] = band_tool(X, sx)
        X.dif(new, tools[sx])
    for sx in (1, -1):                               # old recess: plug 0.1 larger and deeper, flush with the underside
        X.uni(new, X.cyl((sx * FOOT_X, FOOT_OLD_Y, 0.0), (sx * FOOT_X, FOOT_OLD_Y, REC_D + 0.1), REC_R + 0.1))
    for sx in (1, -1):
        X.dif(new, X.cyl((sx * FOOT_X, FOOT_Y, -0.5), (sx * FOOT_X, FOOT_Y, REC_D), REC_R))
    return new, tools


def xs(X, plist, y, z, sx):                          # solid stretches along |x| 60..100 at (y, z)
    return [[round(60.0 + a, 2), round(60.0 + b, 2)] for a, b in k.needle_t(X, plist, (sx * 60.0, y, z), (sx * 100.0, y, z))]


def gaps(X, plate_side, sx, ys=YS):                  # the gap table: wall's inner bottom edge to the raised field's edge
    out = {}
    for y in ys:
        a = xs(X, wall(X, sx), y, 2.9, sx)
        row = []
        for s in SH:
            b = xs(X, plate_side, y + s, 2.4, sx)
            row.append(round(a[0][0] - b[-1][1], 2) if a and b else None)
        out[y] = row
    return out


def side(X, tb, sx):                                 # the plate's side as one piece for the needles
    t = X.wbox(sx * 60.0, sx * 100.0, -66.0, 14.0, -0.6, 3.2); X.sec(t, tb)
    return [t]


def dry(X):
    c = k.c; P = X.body('FLOOR_PLATE')
    new, tools = plate_new(X)
    c['k2_plate'] = new
    old = X.cp(P)
    rem = X.cp(old); X.dif(rem, new)
    add = X.cp(new); X.dif(add, old)
    print('plate volume old / new', round(P.volume * 1000.0, 1), round(X.vol(new), 1), 'lumps', new.lumps.count, 'faces', P.faces.count, new.faces.count)
    print('removed:', X.lumps(rem, 6000)[:10])
    print('added:', X.lumps(add, 6000)[:10])
    for sx in (1, -1):
        print('band tool side', sx, 'mm3', round(X.vol(tools[sx]), 1), 'lumps', tools[sx].lumps.count)
        ps = side(X, new, sx)
        g = gaps(X, ps, sx)
        for y in YS:
            print('  gap side %+d y %6.1f: in place / 1.05 / 1.3 / 1.5 behind' % (sx, y), g[y])
        # the new recess: plate left above it, and the old one filled
        pts = [(FOOT_X + dx, FOOT_Y + dy) for dx in (-6.0, 0.0, 6.0) for dy in (-6.0, 0.0, 6.0) if dx * dx + dy * dy <= 36.1]
        zs = [k.needle_t(X, ps, (sx * x, y, -0.5), (sx * x, y, 3.5)) for x, y in pts]
        print('  new recess: solid z over its footprint (from -0.5):', sorted(set(tuple(round(v - 0.5, 2) for v in q[0]) for q in zs if q)), 'points', len(zs))
        print('  old recess centre and rear edge: solid z', [[round(a - 0.5, 2), round(b - 0.5, 2)] for a, b in k.needle_t(X, ps, (sx * FOOT_X, FOOT_OLD_Y - 3.0, -0.5), (sx * FOOT_X, FOOT_OLD_Y - 3.0, 3.5))],
              [[round(a - 0.5, 2), round(b - 0.5, 2)] for a, b in k.needle_t(X, ps, (sx * FOOT_X, FOOT_OLD_Y - 6.3, -0.5), (sx * FOOT_X, FOOT_OLD_Y - 6.3, 3.5))])
    return new


def apply(X):
    c = k.c; out = {}
    nb = X.swap('FLOOR_PLATE', c['k2_plate'], SUF)
    out['FLOOR_PLATE'] = [round(nb.volume * 1000.0, 1), nb.lumps.count, nb.isLightBulbOn]
    for n in ('FOOT_FL', 'FOOT_FR'):
        t = X.cp(X.body(n)); X.move(t, 0.0, FOOT_Y - FOOT_OLD_Y, 0.0)
        fb = X.swap(n, t, SUF)
        out[n] = [round(fb.volume * 1000.0, 1), fb.isLightBulbOn]
    print('applied', out, 'purged', k.purge(['FLOOR_PLATE', 'FOOT_']), 'dups', X.dups(), 'bodies', len(X.names()))
    return out
