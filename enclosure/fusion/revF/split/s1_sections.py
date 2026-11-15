# Block 1, read-only: mesh sections of named bodies by world planes, chained and simplified, printed as compact JSON.
import adsk.core, adsk.fusion, sys, time, math, json

NAMES = %NAMES%
PLANES = %PLANES%          # name: [origin(world), normal(world), axis1(world), axis2(world)]
TOL = %TOL%                # cm chordal tolerance of the mesh


def dp(pts, eps):          # Douglas-Peucker on a list of 2D points
    if len(pts) < 3:
        return pts
    a = pts[0]; b = pts[-1]; dx = b[0] - a[0]; dy = b[1] - a[1]; L = math.hypot(dx, dy)
    best = -1.0; bi = 0
    for i in range(1, len(pts) - 1):
        p = pts[i]
        d = abs(dy * (p[0] - a[0]) - dx * (p[1] - a[1])) / L if L > 1e-9 else math.hypot(p[0] - a[0], p[1] - a[1])
        if d > best:
            best = d; bi = i
    if best <= eps:
        return [a, b]
    return dp(pts[:bi + 1], eps)[:-1] + dp(pts[bi:], eps)


def chain(segs):
    key = lambda p: (round(p[0], 3), round(p[1], 3))
    adj = {}
    for i, (p, q) in enumerate(segs):
        adj.setdefault(key(p), []).append((i, 1)); adj.setdefault(key(q), []).append((i, 0))
    used = [False] * len(segs); out = []
    for i in range(len(segs)):
        if used[i]:
            continue
        used[i] = True; line = [segs[i][0], segs[i][1]]
        for end in (1, 0):
            while True:
                p = line[-1] if end == 1 else line[0]
                nxt = None
                for j, w in adj.get(key(p), []):
                    if not used[j]:
                        nxt = (j, w); break
                if nxt is None:
                    break
                j, w = nxt; used[j] = True
                q = segs[j][1] if w == 0 else segs[j][0]
                q = segs[j][1] if key(segs[j][0]) == key(p) else segs[j][0]
                if end == 1:
                    line.append(q)
                else:
                    line.insert(0, q)
        out.append(line)
    return out


def run(_context):
    t0 = time.time()
    k = sys.modules['v5f_k']; X = k.K()
    C, S, H = k.C, k.S, k.H
    res = {}
    for n in NAMES:
        b = X.body(n)
        mc = b.meshManager.createMeshCalculator(); mc.surfaceTolerance = TOL
        ms = mc.calculate(); P = ms.nodeCoordinatesAsDouble; I = ms.nodeIndices
        nn = len(P) // 3; nt = len(I) // 3
        W = []
        for i in range(nn):
            X_, Y_, Z_ = P[3 * i], P[3 * i + 1], P[3 * i + 2]
            W.append((X_ * 10 - k.XC, (Y_ * C - Z_ * S) * 10, H + (Y_ * S + Z_ * C) * 10))
        for pn, (o, nr, a1, a2) in PLANES.items():
            sd = [(w[0] - o[0]) * nr[0] + (w[1] - o[1]) * nr[1] + (w[2] - o[2]) * nr[2] for w in W]
            segs = []
            for t in range(nt):
                ids = (I[3 * t], I[3 * t + 1], I[3 * t + 2]); s = [sd[i] for i in ids]
                if min(s) > 0 or max(s) < 0 or (min(s) == 0 and max(s) == 0):
                    continue
                pts = []
                for a, bb in ((0, 1), (1, 2), (2, 0)):
                    sa, sb = s[a], s[bb]
                    if (sa < 0 < sb) or (sb < 0 < sa) or (sa == 0) :
                        f = 0.0 if sa == 0 else sa / (sa - sb)
                        pa = W[ids[a]]; pb = W[ids[bb]]
                        q = [pa[i] + f * (pb[i] - pa[i]) for i in range(3)]
                        u = sum((q[i] - o[i]) * a1[i] for i in range(3)); v = sum((q[i] - o[i]) * a2[i] for i in range(3))
                        pts.append((u, v))
                if len(pts) >= 2:
                    segs.append((pts[0], pts[1]))
            lines = [dp(l, 0.02) for l in chain(segs)]
            res.setdefault(pn, {})[n] = [[[round(p[0], 2), round(p[1], 2)] for p in l] for l in lines if len(l) >= 2]
    print(json.dumps({'t': round(time.time() - t0, 1), 'res': res}, separators=(',', ':')))
