# Block 9 (the radar's holder): the two calculations that were made outside Fusion. Plain Python, no Fusion call.
# The figures they give are the ones in claude/report-enclosure-audit-fixes-block9-2026-11-26.md, sections 4.3 and 7.
# This file was written at the close from the report's own inputs (the first run of block 9 was not kept as a file) and
# gives the report's figures again.
#
# 1. The arm's press on the touch board (report section 7).
#    The arm is a flat spring 3.6 x 1.2 (z 40.2..43.8, y 1.3..2.5), bending in y. From the pad's middle (x 0.5) to the
#    gusset's toe (x 20.1) it is 19.6 long; the gusset thickens it at 45 deg over the next 1.0, to the root's face
#    (x 21.1). Deflection by the unit load method; E = 2,000 MPa for ABS, ASSUMED (the plan note's figure).
#    Tolerance chain (the tolerance basis' wall faces: 0.10 likely, 0.20 worst, each): the pad lies 21.7 beyond
#    standoffs A and B, and standoff C stands 21.2 from them.
# 2. The lead's free run over the Pi (report section 4.3; architect log 2026-11-26 section 4.B, the third condition).
#    Route R8 (p86_b9_build2.py): from the tie (22.0, -9.8, 49.7) to the J5 plug's end (-37.8, -32.98, 94.07), 89.7 as laid.
#    A lead with spare length in that run is taken to hang as a chain (a catenary) between its two ends; its skin is 1.3
#    from its axis (2.6 across). The Pi cooler's keep-out KO_K7_fan: x -15.75..14.25, y -38.7..-7.6, top at z 35.8.
import math

E = 2000.0                     # MPa, assumed
B = 3.6; H = 1.2               # the arm's section: width along z, thickness along y
L0 = 19.6; GUS = 1.0           # pad's middle to the gusset's toe; the gusset's length
MODELLED = 0.60                # the press as modelled (p87 fits)
LIMIT_LAST, LIMIT_SHORT = 8.2, 13.2   # the rule's limits along the layers, MPa


def arm():
    i0 = B * H ** 3 / 12.0
    flex = L0 ** 3 / (3.0 * E * i0)                       # mm per N, the plain part
    n = 2000; dt = GUS / n                                # the gusset, Simpson's rule
    f = lambda t: (L0 + t) ** 2 / (E * B * (H + t) ** 3 / 12.0)
    s = f(0.0) + f(GUS) + sum((4 if j % 2 else 2) * f(j * dt) for j in range(1, n))
    flex += s * dt / 3.0
    k = 1.0 / flex
    z = B * H ** 2 / 6.0
    per_mm = k * L0 / z                                   # MPa at the gusset's toe per mm of press
    ab = 1.0 + 21.7 / 21.2; c = 21.7 / 21.2               # how A and B, and C, count at the pad
    likely = 0.10 * math.sqrt(ab ** 2 + c ** 2 + 1.0)
    worst = 0.20 * (ab + c + 1.0)
    print('arm: stiffness %.3f N/mm; %.2f MPa at the gusset\'s toe per mm of press' % (k, per_mm))
    print('     chain: A and B count %.2f times, C %.2f times, the pad\'s own face once: likely +-%.2f, worst +-%.2f' % (ab, c, likely, worst))
    root = lambda force: 6.0 * force * 21.7 / (B * 2.2 ** 2)   # the root block 2.2 x 3.6, 21.7 from the pad's middle
    for name, p in (('as modelled', MODELLED), ('likely loose end', MODELLED - likely), ('likely tight end', MODELLED + likely),
                    ('worst tight end', MODELLED + worst), ('worst loose end', MODELLED - worst)):
        if p <= 0:
            print('     %-17s no press: %.2f short of the board' % (name, -p)); continue
        print('     %-17s press %.2f: %.2f N, %.1f MPa at the toe, %.1f MPa in the root block (limits %.1f lasting, %.1f short)'
              % (name, p, k * p, per_mm * p, root(k * p), LIMIT_LAST, LIMIT_SHORT))


def chain(a, b, length, r=1.3, ko=(-15.75, 14.25, -38.7, -7.6, 35.8)):
    """Lowest skin of a chain of the given length between a and b over the keep-out's plan, against its top."""
    d = math.hypot(b[0] - a[0], b[1] - a[1]); v = b[2] - a[2]
    if length <= math.sqrt(d * d + v * v):
        raise ValueError('the lead is shorter than the straight line')
    t = math.sqrt(length ** 2 - v ** 2)
    lo, hi = 1e-3, 1e6                                    # solve 2 a sinh(d / 2a) = t for a
    for _ in range(200):
        m = math.sqrt(lo * hi)
        if 2.0 * m * math.sinh(d / (2.0 * m)) > t:
            lo = m
        else:
            hi = m
    al = lo
    x0 = d / 2.0 - al * math.atanh(v / length)            # where the chain is lowest, from a
    c0 = a[2] - al * math.cosh(-x0 / al)
    best = None
    for j in range(0, 4001):
        x = d * j / 4000.0
        px = a[0] + (b[0] - a[0]) * x / d; py = a[1] + (b[1] - a[1]) * x / d
        z = al * math.cosh((x - x0) / al) + c0
        if ko[0] <= px <= ko[1] and ko[2] <= py <= ko[3]:
            if best is None or z < best[0]:
                best = (z, px, py)
    return best[0] - r - ko[4], best


def lead():
    tie = (22.0, -9.8, 49.7); plug = (-37.8, -32.98, 94.07); bend = (-37.6, -40.6, 92.5)
    run = math.dist(tie, (-24.5, -40.0, 77.5)) + math.dist((-24.5, -40.0, 77.5), bend) + math.dist(bend, plug)
    last = math.dist(bend, plug)
    print('lead: free run from the tie to the J5 plug %.1f as laid; its last piece at the plug %.1f' % (run, last))
    for name, a, b, ln in (('all 15 of spare in the free run', tie, plug, run + 15.0),
                           ('the same, the lead keeping its direction over the last piece at the plug', tie, bend, run + 15.0 - last),
                           ('5 of spare in the free run, 10 behind the radar', tie, plug, run + 5.0)):
        gap, at = chain(a, b, ln)
        print('     %s: the skin %s the keep-out\'s top by %.1f (axis lowest at z %.2f over x %.1f, y %.1f)'
              % (name, 'is above' if gap >= 0 else 'reaches into', abs(gap), at[0], at[1], at[2]))


if __name__ == '__main__':
    arm()
    lead()
