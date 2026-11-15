# aud5x_lib.py - assembly audit of the front shell split (2026-11-15). Model "HA Panel v5 - tapered" version 64, READ-ONLY.
# Exec'd into sys.modules['aud5x'] inside Fusion. Uses, loaded unchanged from docs commit 907fa63 by git blob hash:
#   aud5k = enclosure/fusion/revF/floor_plate/fusion/v5f_k_lib.py (blob ba85884): frames, temporary solids, tool sections IRON, KEY20, KEY25
#   aud5m = .../v5f_m_lib.py (blob 62790f5), its k pointed at aud5k
#   aud5  = enclosure/fusion/audit-asm/followup/aud4_lib.py (blob 181243c), its k/m pointed at aud5k/aud5m: finger(), reach(), jaws(),
#           PLIERS, service_fixed(), ride_setup(), ride(), crop(), tl(), items(), mingap()
# Fresh module names, so no cache of an earlier session is used (lesson 181).
# World mm: x = x_rel (+x = viewer's left = left-speaker side), y + toward the screen, z up from the plate's underside.
# Slab frame (x, d, up): d = depth behind the glass. Nothing here changes the design: temporary bodies and measurements only.
import adsk.core, adsk.fusion, math, sys, time
k = sys.modules['aud5k']; a5 = sys.modules['aud5']
R = a5.R


def bb6(b):
    q = b.boundingBox; return (q.minPoint.x, q.minPoint.y, q.minPoint.z, q.maxPoint.x, q.maxPoint.y, q.maxPoint.z)


def body_items(X, names, crops=()):                   # [(label, temporary body, design box)]: small bodies as cached copies, crops by key
    out = []
    for n in names:
        if X.body(n) is None:
            raise RuntimeError('no body ' + n)
        t = k.tcopy(X, n)
        out.append((n, t, bb6(t)))
    for key in crops:
        out += [(key, t, bb6(t)) for t in R[('crop', key)]]
    return out


def line(X, o, u, secs, its, st0=2.0, step=1.0, rng=12.0, head=7.0, t0=None, lim=None):
    # a tool on its axis from its working end o (world) along u: margin = smallest distance to each obstacle less the tool's radius there.
    # 'head' = the first 'head' mm (the joint's own seat); 'beyond' = the rest. As aud3x_lib.line (recheck, 2026-11-12).
    u = k.unit(u); total = sum(L for d, L in secs); best = {}; hb = {}; s = st0
    while s <= total + 1e-6:
        if t0 is not None and time.time() - t0 > lim:
            raise RuntimeError('time limit in line()')
        r = k.rad_at(secs, s); p = k.Wp(o[0] + u[0] * s, o[1] + u[1] * s, o[2] + u[2] * s)
        for lab, b, q in its:
            if k.pbox(p, q) * 10.0 > r + rng:
                continue
            mg = X.mm.measureMinimumDistance(p, b).value * 10.0 - r
            tgt = hb if s <= head else best
            if lab not in tgt or mg < tgt[lab][0]:
                tgt[lab] = (mg, s)
        s += step
    rows = sorted((round(v[0], 2), round(v[1], 1), q) for q, v in best.items())
    hrows = sorted((round(v[0], 2), round(v[1], 1), q) for q, v in hb.items())
    return {'min': rows[0] if rows else None, 'rows': rows[:5], 'head': hrows[0] if hrows else None, 'hrows': hrows[:3]}


def fmt(r, n=3):
    return 'head %s | beyond %s' % ('>12' if r['head'] is None else ' '.join('%+.2f@%g %s' % t for t in r['hrows'][:2]),
                                    '>12' if r['min'] is None else ' '.join('%+.2f@%g %s' % t for t in r['rows'][:n]))


def turn(u, toward, deg):                             # u turned by deg toward 'toward' (both world)
    return k.tilt(u, toward, deg)


# ---------- box-top screws (D146) ----------
# A point on each 10 deg screw line (z 80) and the line's unit direction toward the screen; seat positions s (mm along the line from p0):
# version 63 (old lugs): left -6.62, right -6.964 (recheck: mouth y -3.9, tab 3.43 to the seat); version 64: + 3.168 (lugs moved, D146).
BT_LINES = {'left': (1.0, (58.5, -0.77, 80.0), -6.62), 'right': (-1.0, (-58.6, -0.43, 80.0), -6.964)}
HEAD_H = 1.65                                          # ISO 7380-1 M3 button head height


def bt_line(side):
    g, p0, sb = BT_LINES[side]
    return g, p0, (g * 0.17365, 0.98481, 0.0), sb


def bt_point(side, s):
    g, p0, u, sb = bt_line(side)
    return (p0[0] + u[0] * s, p0[1] + u[1] * s, p0[2] + u[2] * s)


def bt_head_top(side, shift=3.168):                   # world point of the button head's top on the line
    g, p0, u, sb = bt_line(side)
    return bt_point(side, sb + shift - HEAD_H)


def bt_key_dir(side, ph):                             # from the head toward the door, ph deg toward the middle (10 = along the screw line)
    g = BT_LINES[side][0]
    return (-g * math.sin(math.radians(ph)), -math.cos(math.radians(ph)), 0.0)


# ---------- the plate's two box-top inserts (Ruthex M3 x 5.7, 4.6 across by the maker's table; not a body of the model) ----------
INS_D, INS_L = 4.6, 5.7


def plate_front_s(X, side):                           # where the screw line leaves the plate's front face: s along the line (needle)
    g, p0, u, sb = bt_line(side)
    a = bt_point(side, -20.0); b = bt_point(side, 20.0)
    st = k.needle_t(X, [k.tcopy(X, 'HOUSING_F_plate')], a, b)
    return [[round(q[0] - 20.0, 3), round(q[1] - 20.0, 3)] for q in st]


def insert_body(X, side, s_front, dia=INS_D, L=INS_L):   # the insert as a cylinder on the line, its front end at s_front
    a = bt_point(side, s_front - L); b = bt_point(side, s_front)
    return X.cyl(a, b, dia / 2.0)
