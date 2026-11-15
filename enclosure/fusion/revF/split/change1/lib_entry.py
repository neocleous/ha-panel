# change1/lib_entry.py - change pass after the split's audit (2026-11-15): the box-top inserts' entry into the lugs' pockets (F45),
# the F44 fill and the two lead-in variants compared on copies before the model was changed. Temporary bodies only.
# Exec'd into sys.modules['cp1e']. Needs sys.modules['cp1k'] (v5f_k_lib.py) and sys.modules['cp1x'] (aud5x_lib.py), see c0_calls.load().
# World mm: x = x_rel (+x = viewer's left = left-speaker side), y + toward the screen, z up from the base plate's underside.
# s = mm along a box-top screw line from its point p0 (x.bt_line), + toward the screen; e1 = the horizontal direction square to it.
# e = the shell's (and so the plate's inserts') sideways offset from the unit, world +x. d = how far the shell is still forward of home.
import adsk.core, adsk.fusion, sys, time, math
k = sys.modules['cp1k']; x = sys.modules['cp1x']
R = {}
BOX = {'left': 'SPKBOX_L', 'right': 'SPKBOX_R'}
OLD = {'left': (58.5067, -1.0263, 80.0), 'right': (-58.5067, -1.0263, 80.0)}     # axis of the version 63 pocket (moved with the lug), read from its face
SNEW = {'left': -0.6985, 'right': -1.04375}                                       # the split's own pocket floor, on the line (s_end - 0.1 of s2_split_calls)
SFRONT = {'left': 5.11, 'right': 4.76}                                            # plate's front face on the line (c0 f44_reproduce)


def line(side):
    g, p0, u, sb = x.bt_line(side)
    return g, p0, u, (u[1], -u[0], 0.0)


def P(side, s, lat=0.0):
    g, p0, u, e1 = line(side)
    return tuple(p0[i] + u[i] * s + e1[i] * lat for i in range(3))


def old_off(side):                                    # (s, lateral offset) of the old pocket's axis: left (-0.251, +0.0511), right (-0.603, -0.0117)
    g, p0, u, e1 = line(side); o = OLD[side]
    d = tuple(o[i] - p0[i] for i in range(3))
    return sum(d[i] * u[i] for i in range(3)), sum(d[i] * e1[i] for i in range(3))


def s_face(side):                                     # where the line crosses the lug's front face (y -0.78): left -0.0102, right -0.3554
    g, p0, u, e1 = line(side)
    return (-0.78 - p0[1]) / u[1]


def crop(X, side, src=None):
    g = line(side)[0]
    b = src if src is not None else k.tcopy(X, BOX[side])
    c = X.cp(b); X.sec(c, X.wbox(g * 49.0, g * 68.0, -9.0, 3.0, 70.0, 89.0))
    return c


def fill44(X, side, body):                            # F44: the old 1.0-deep pocket filled up to the split's own floor; both clearance holes cut again
    s0, off = old_off(side)
    sfl = -1.0 if side == 'left' else -1.3497
    X.uni(body, X.cyl(P(side, sfl - 0.02, off), P(side, SNEW[side], off), 2.62))
    for lat in (0.0, off):
        X.dif(body, X.cyl(P(side, -1.6, lat), P(side, SNEW[side] + 0.05, lat), 1.8))
    return body


def leadA(X, side, body, w=0.4):                      # variant A, not used: 45 deg cone round the pocket's own axis, w deep at the line's crossing
    sf = s_face(side)
    X.dif(body, X.cyl(P(side, sf - w), P(side, sf + 1.5), 2.6, 2.6 + w + 1.5))
    return body


def cone_B(X, side, w=0.4):                           # variant B, made: 45 deg countersink about world y (square to the lug's face), w wider than the mouth
    g, p0, u, e1 = line(side)
    s0, off = old_off(side)
    M = P(side, s_face(side), off / 2.0)
    Rf = 2.6 / math.cos(math.radians(10.0)) + abs(off) / 2.0 + w
    cone = X.cyl((M[0], -0.78 + 0.6, M[2]), (M[0], -0.78 - (Rf - 2.5), M[2]), Rf + 0.6, 2.5)
    cap = X.obox(P(side, SNEW[side] + 15.0), u, (0.0, 0.0, 1.0), 30.0, 30.0, 30.0)   # nothing below the pocket's floor plane
    X.sec(cone, cap)
    return cone, Rf, M


def leadB(X, side, body, w=0.4):
    cone, Rf, M = cone_B(X, side, w)
    X.dif(body, cone)
    return body


def inserts(X):                                       # the plate's two box-top inserts (4.6 x 5.7, aud5x), flush with its front face
    if 'ins' not in R:
        R['ins'] = {s: x.insert_body(X, s, SFRONT[s]) for s in ('left', 'right')}
    return R['ins']


def ov(X, lugs, e, d):
    v = 0.0
    for s, ins in inserts(X).items():
        t = X.tbm.copy(ins); X.move(t, e, d, 0.0)
        v += X.xv(t, lugs[s])
    return v


DS = [round(1.2 - 0.05 * i, 2) for i in range(25)]


def fixed(X, var, e0):                                # the audit's way: offset held, 1.2 to home in 0.05: (first d with volume, largest mm3, mm3 at home)
    lugs = R['lugs'][var]
    rows = [(d, round(ov(X, lugs, e0, d), 4)) for d in DS]
    hit = [r for r in rows if r[1] > 0.0005]
    return (hit[0][0] if hit else None, max(r[1] for r in rows), rows[-1][1])


def ov_side(X, lugs, side, e, d):
    t = X.tbm.copy(inserts(X)[side]); X.move(t, e, d, 0.0)
    return X.xv(t, lugs[side]), t


def normal(X, lugs, side, e, d):                      # direction lug -> insert between their nearest points, backed off until they are apart (lesson 196)
    dd = d
    for i in range(30):
        t = X.tbm.copy(inserts(X)[side]); X.move(t, e, dd, 0.0)
        r = X.mm.measureMinimumDistance(t, lugs[side])
        if r.value * 10.0 > 0.0005:
            a = k.W(r.positionOne); b = k.W(r.positionTwo)
            v = tuple(a[i] - b[i] for i in range(3)); n = math.sqrt(sum(q * q for q in v))
            return tuple(q / n for q in v), r.value * 10.0, b
        dd += 0.005
    return None, 0.0, None


def sim2(X, var, e0, step=0.01, eps=0.0005, thmin=25.0):
    # the guided path: the shell slides back in 0.01 steps; at a contact, a face within 25 deg of the motion stops it, anything steeper
    # (the 45 deg lead-in, the 80 deg pocket wall) moves it sideways by what clears, at most tan(angle) x step x 1.3
    lugs = R['lugs'][var]; e = e0; d = 1.2; ev = []
    while d > 1e-9:
        d2 = max(0.0, round(d - step, 4))
        hit = [s for s in ('left', 'right') if ov_side(X, lugs, s, e, d2)[0] > eps]
        if hit:
            s = hit[0]
            n, dist, pt = normal(X, lugs, s, e, d)
            if n is None:
                return ('stops', d2, round(e, 3), s, 'no gap', ev)
            th = math.degrees(math.acos(min(1.0, abs(n[1]))))
            if th < thmin:
                return ('stops', d2, round(e, 3), s, round(th, 1), ev, [round(q, 2) for q in pt])
            sg = 1.0 if n[0] > 0 else -1.0
            mx = step * math.tan(math.radians(min(th, 80.0))) * 1.3 + 0.003
            got = None; j = 1
            while 0.002 * j <= mx:
                e2 = e + sg * 0.002 * j
                if all(ov_side(X, lugs, q, e2, d2)[0] <= eps for q in ('left', 'right')):
                    got = e2; break
                j += 1
            if got is None:
                return ('stops', d2, round(e, 3), s, round(th, 1), ev, 'no shift within %.3f' % mx)
            ev.append((d2, s[0], round(th), round(got, 3))); e = got
        d = d2
    return ('home', 0.0, round(e, 3), len(ev), ev[:1] + ev[-1:])
