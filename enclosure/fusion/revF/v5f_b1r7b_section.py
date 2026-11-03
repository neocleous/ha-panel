# rev F block 1r-7b (2026-11-03), read-only: vertical section of HOUSING_E and DOOR_F through the ML door-screw axis
# (XC + 73.96, -45.63) along its rib direction (from the v5f_b1r4 log), for the checkpoint diagram.
# s = distance from the screw axis along the rib direction (toward the wall), z = world height. Window s -9..18, z -4..15.
# Output: SVG path strings, px = 40 + (s + 9) * K, py = 30 + (15 - z) * K, K = 20.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
K = 20.0; S0, S1, Z0, Z1 = -9.0, 18.0, -4.0, 15.0
AX = (XC + 73.96, -45.63)
NAMES = ['HOUSING_E', 'DOOR_F']


def clip(P):
    def cut(P, inside, inter):
        o = []
        for i in range(len(P)):
            a = P[i - 1]; b = P[i]; ia, ib = inside(a), inside(b)
            if ib:
                if not ia: o.append(inter(a, b))
                o.append(b)
            elif ia:
                o.append(inter(a, b))
        return o
    ix = lambda v: (lambda a, b: (v, a[1] + (b[1] - a[1]) * (v - a[0]) / ((b[0] - a[0]) or 1e-12)))
    iz = lambda v: (lambda a, b: (a[0] + (b[0] - a[0]) * (v - a[1]) / ((b[1] - a[1]) or 1e-12), v))
    for f in [(lambda p: p[0] >= S0, ix(S0)), (lambda p: p[0] <= S1, ix(S1)), (lambda p: p[1] >= Z0, iz(Z0)), (lambda p: p[1] <= Z1, iz(Z1))]:
        if not P: break
        P = cut(P, f[0], f[1])
    return P


def rdp(P, eps):
    if len(P) < 3: return P
    a, b = P[0], P[-1]; dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy) or 1e-12
    dmax, idx = 0, 0
    for i in range(1, len(P) - 1):
        d = abs(dy * (P[i][0] - a[0]) - dx * (P[i][1] - a[1])) / L
        if d > dmax: dmax, idx = d, i
    if dmax > eps:
        return rdp(P[:idx + 1], eps)[:-1] + rdp(P[idx:], eps)
    return [a, b]


def run(_context):
    X = Ctx()
    out = {}
    try:
        arr = json.load(open(LOG))
        ent = [e for e in arr if e['script'] == 'v5f_b1r4_bosses' and 'ribs' in e['data'] and 'FAIL' not in e['data']][-1]
        d, deg = ent['data']['ribs']['ML']; a = math.radians(deg)
        out['rib_ML'] = (d, deg)
        ca, sa = math.cos(a), math.sin(a)
        pl = adsk.core.Plane.create(Dw(AX[0], AX[1], 0.0), V3(-sa, ca * C, -ca * S))
        for n in NAMES:
            wb = X.tbm.planeIntersection(X.body(n), pl)
            segs = []
            for e in wb.edges:
                ev = e.evaluator; ok, t0, t1 = ev.getParameterExtents(); ok, pts = ev.getStrokes(t0, t1, 0.0005)
                segs.append([((p.x * 10 - AX[0]) * ca + (wy(p) - AX[1]) * sa, wz(p)) for p in pts])
            loops = []
            while segs:
                cur = segs.pop(0); grown = True
                while grown:
                    grown = False
                    for i, s in enumerate(segs):
                        if math.dist(s[0], cur[-1]) < 0.01: cur += s[1:]; segs.pop(i); grown = True; break
                        if math.dist(s[-1], cur[-1]) < 0.01: cur += s[::-1][1:]; segs.pop(i); grown = True; break
                loops.append(cur)
            paths = []
            for L in loops:
                Cc = clip(L)
                if len(Cc) < 3: continue
                k = max(range(len(Cc)), key=lambda i: math.dist(Cc[0], Cc[i]))
                Cc = rdp(Cc[:k + 1], 0.01)[:-1] + rdp(Cc[k:] + [Cc[0]], 0.01)
                paths.append('M' + ' L'.join('%.1f %.1f' % (40 + (s - S0) * K, 30 + (Z1 - z) * K) for (s, z) in Cc) + ' Z')
            out[n] = paths
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    print(json.dumps(out))
