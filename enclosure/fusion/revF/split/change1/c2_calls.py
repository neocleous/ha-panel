# change1/c2_calls.py - change pass after the split's audit (2026-11-15), block 2: the checks on version 65 (g20). All read-only.
# Before the first check: k.purge(['SPKBOX_', 'HOUSING_F_front', 'HOUSING_F_plate', 'FLOOR_PLATE', 'FOOT_', 'KO_K5']) and sys.modules['cp1a'].R.clear()
# (lesson 197), then k.tiles() for the four big bodies (7.8 s for the new shell).
import adsk.core, adsk.fusion, sys, time, math

# 1. F44: c0_calls.f44_reproduce on the new boxes, plus bisections for the continuous values
#    left: floor s -0.70 (0.693 below the lug's face), end gap 0.108 (0.12 at 0.02 steps); right: -1.04 (0.688), 0.104 (0.12)
#    lug's top edge to the plate 0.292 both; pull until it touches 0.303 (0.32 at 0.02 steps): the floor bears first

# 2. F45: lib_entry on crops of the new boxes, var 'g20': fixed() and sim2() for e -0.50..+0.50 in 0.05 (results equal to variant B)


def f46(_context):
    k = sys.modules['cp1k']; X = k.K(); k.budget(60)
    P = k.tcopy(X, 'HOUSING_F_plate')
    for sx in (1.0, -1.0):
        x0 = 85.0 * sx
        sh = k.region(X, 'HOUSING_F_front', 'peg%+d' % sx, (x0 - 9.0, x0 + 9.0, 10.0, 21.0, -92.0, -72.0), 'S')
        for dx, du in ((1, 0), (-1, 0), (0, 1), (0, -1)):            # wall round the insert hole at mid-peg: [2.0, 3.6] in all four
            print(k.needle_t(X, sh, k.W(k.Dp(x0, 12.2, -82.0)), k.W(k.Dp(x0 + dx * 6.0, 12.2, -82.0 + du * 6.0))))
        peg = []
        for p in sh:
            t = X.cp(p); X.sec(t, X.dbox(x0 - 4.0, x0 + 4.0, 11.0, 12.79, -86.0, -78.0))
            if X.vol(t) > 0.001:
                peg.append(t)
        print(min(X.mm.measureMinimumDistance(t, P).value * 10.0 for t in peg))                          # 0.125 both
        print(k.needle_t(X, [P], k.W(k.Dp(x0 - 8.0, 12.2, -82.0)), k.W(k.Dp(x0 + 8.0, 12.2, -82.0))))     # pocket 7.44 / slot 8.95 along x
        print(k.needle_t(X, [P], k.W(k.Dp(x0, 12.2, -90.0)), k.W(k.Dp(x0, 12.2, -74.0))))                # 7.45 along up
    shs = k.region(X, 'HOUSING_F_front', 'front_band', (-102.0, 102.0, 10.0, 21.0, -95.0, 40.0), 'S')
    worst = 0.0
    for i in range(61):                                # the plate dropped onto the pegs along the normal, 3.0 out to home: 0.0000 mm3
        t = X.tbm.copy(P); X.move_n(t, round(3.0 - 0.05 * i, 2))
        worst = max(worst, sum(X.xv(t, q) for q in shs))
    gaps = []
    for q in shs:                                      # step 19's slit with the four posts left out: 0.2 (nearest x -89.47, up -80.93)
        t = X.cp(q)
        for (xx, uu) in ((70.0, 27.0), (-70.0, 27.0), (85.0, -82.0), (-85.0, -82.0)):
            X.dif(t, X.cyld(xx, uu, 4.6, 10.0, 22.0))
        if X.vol(t) > 0.001:
            gaps.append(X.mm.measureMinimumDistance(t, P).value * 10.0)
    print(worst, min(gaps))


# 4. Step 20: c0_calls.window_reproduce on the new bodies (cp1a.R cleared): tongues 0 / 0.05 / 0.10; heads touch at exactly 1.15 (h 6.5-8, 42-43.5),
#    overlap 0.0005 mm3 at 1.14, 0.01 at 1.16; boxes' backs 0.000 to h 22, 0.185 at 25. Inserts past the boxes and the noses:
def step20(_context):
    k = sys.modules['cp1k']; a = sys.modules['cp1a']; e = sys.modules['cp1e']; X = k.K()
    ins = e.inserts(X)
    for var, nb in (('g20', ''), ('v64', '_v64')):
        boxes = {'left': k.tcopy(X, 'SPKBOX_L' + nb), 'right': k.tcopy(X, 'SPKBOX_R' + nb)}
        for b in (1.15, 1.30, 1.50):
            for h in (0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 15.0, 20.0, 30.0):
                for s in ('left', 'right'):
                    t = X.tbm.copy(ins[s]); X.move(t, 0.0, b, h)
                    X.mm.measureMinimumDistance(t, boxes[s])
    # g20 least 0.175 / 0.325 / 0.525 at b 1.15 / 1.30 / 1.50 (h 3-4); at h 0: 0.78 / 0.75 (b 1.15), 1.03 / 1.00 (b 1.50). v64: 0.53 / 0.50, 0.75 / 0.72
    for sx in (1.0, -1.0):                             # noses over the lip, shell at seat height slid from 1.5 forward to home
        nose = a.crop(X, 'FLOOR_PLATE', 'nose%+d' % sx, (sx * 22.0, sx * 38.0, -1.0, 4.0, 4.2, 7.0))
        lip = a.crop(X, 'HOUSING_F_front', 'lip%+d' % sx, (sx * 22.0, sx * 38.0, -5.0, 5.0, 0.5, 4.3))
        for b in (1.5, 1.4, 1.3, 1.2, 1.1, 1.0, 0.9, 0.8, 0.6, 0.4, 0.2, 0.0):
            min(X.mm.measureMinimumDistance(a.mv(X, p, (0.0, -b, 0.0)), q).value * 10.0 for p in nose for q in lip)
    # 0.768 at 1.5, 0.46 at 1.0, 0.30 from 0.6 to 0.2 (over the lip), both sides


# 5. F50: each KO_K5_* start disc centred at (x, d 15.8, up) of its head's top; that point 0.0000 from the axis, 0.0013 at 100 along the key's lane.


def feet(_context):                                   # 6. the constraints of change 5
    k = sys.modules['cp1k']; X = k.K(); k.budget(60)
    tiles = k.parts(X, 'FLOOR_PLATE')
    for sx in (1.0, -1.0):
        C = X.cyl((30.0 * sx, -70.6, 0.5), (30.0 * sx, -70.6, 2.5), 6.5)                       # 2.0 of plate over the recess: 0.00000 of 265.46 missing
        print(X.vol(C) - sum(X.xv(C, t) for t in tiles))
        ring = X.cyl((30.0 * sx, -70.6, 0.0), (30.0 * sx, -70.6, 0.5), 6.6); X.dif(ring, X.cyl((30.0 * sx, -70.6, -0.1), (30.0 * sx, -70.6, 0.6), 6.5))
        print(X.vol(ring) - sum(X.xv(ring, t) for t in tiles))                                   # 0.1 ring round the mouth: 0.00058 at the blend
    # the limit (block 1): bisection with a column 13 x 2.5 less the old recess: y -70.678 at x +30 and -70.677 at x -30; x 25..34 scanned:
    #   deepest y in the flat -66.81 (x 25, a counterbore) ... -70.85 (x 29) ... -70.68 (x 30) ... -69.89 (x 34)
    # counterbores (k.holes_of r 3.2-3.3): door (19, -74.5), (-19, -77), (+-50, -67); box floors (51, -14), (-51, -14), (64, -45), (-72, -38)
    #   rear left foot edge to (19, -74.5): 2.07 (was 2.70); rear right to (-19, -77): 3.13 (4.00); front 20.62; recess edges 1.92 / 2.98
    # nearest: intake holes 5.42, Pi posts' holes 10.27 / 11.37, cradle posts 13 or more, anchor (55.2..61.8, -58.5..-54.5) 21.45
    cur = k.current(X, leads=False)
    old = [X.body(b.name + '_v64') if b.name in ('FOOT_RL', 'FOOT_RR', 'FLOOR_PLATE') else b for b in cur]
    for bodies in (old, cur):
        for (x, y) in ((19.0, -74.5), (-19.0, -77.0), (50.0, -67.0), (-50.0, -67.0)):
            print(k.line(X, (x, y, -0.65), (0.0, 0.0, -1.0), k.KEY20, bodies, st0=2.0, step=1.0, head=7.0))
    # the 2.0 key from below: head +2.83 (the plate) at all four, before and after; beyond: feet 7.0 / 7.99 -> 6.56 / 7.32, outer pair 8.04


def matrix(_context):                                 # 7. every body against every other; call until left == 0 (four calls)
    k = sys.modules['cp1k']; X = k.K(); ns = k.K4NS     # v5f_k4a_unit_checks.py (blob f5583bf) exec'd with k = cp1k
    k.budget(40.0)
    res, left, n = ns['matrix'](X, 'g20')
    if left == 0:
        ref = sys.modules['r32'].k4['k'].c[('k4m', 'v64')]          # the split pass's measured version 64 table, still in Fusion's memory
        sym = lambda d: {tuple(sorted(q)): v for q, v in d.items() if v}
        A = sym(ref); B = sym(res)
        print(len(A), len(B), {q: B[q] for q in B if q not in A}, {q: A[q] for q in A if q not in B},
              {q: (A[q], B[q]) for q in A if q in B and abs(A[q] - B[q]) > 0.05})
    # 96 bodies, 4560 pairs, 76 not zero = version 64's 76; none new, none gone; changed: door x KO_K5_UL 166.388 -> 164.034, UR 145.934 -> 124.984,
    # LL 103.243 -> 103.160, LR 100.911 -> 100.775 (key paths through the door opening; the door is off when the key is used)


# 8. volumes (BRepBody.volume x 1000): only the five changed parts differ (README table); door, cap, slab frame, carrier, cradle, clips, hood, grommet equal.
