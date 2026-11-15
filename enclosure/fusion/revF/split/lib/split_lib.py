# Front shell split pass (2026-11-14) - session helpers, exec'd into sys.modules['split_lib'] inside Fusion.
# Uses sys.modules['v5f_k'] (the fix pass's library, loaded by blob hash). World mm: x = x_rel, y + toward the screen, z up.
import adsk.core, adsk.fusion, sys, time, math, json
k = sys.modules['v5f_k']
c = {}


def dp(pts, eps):
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
        adj.setdefault(key(p), []).append(i); adj.setdefault(key(q), []).append(i)
    used = [False] * len(segs); out = []
    for i in range(len(segs)):
        if used[i]:
            continue
        used[i] = True; line = [segs[i][0], segs[i][1]]
        for end in (1, 0):
            while True:
                p = line[-1] if end == 1 else line[0]
                nxt = None
                for j in adj.get(key(p), []):
                    if not used[j]:
                        nxt = j; break
                if nxt is None:
                    break
                used[nxt] = True
                q = segs[nxt][1] if key(segs[nxt][0]) == key(p) else segs[nxt][0]
                if end == 1:
                    line.append(q)
                else:
                    line.insert(0, q)
        out.append(line)
    return out


def wmesh(body, tol=0.005):                       # world nodes and triangle indices of a body's mesh (cached by name, volume, tol)
    q = ('mesh', body.name, round(body.volume, 6), tol)
    if q in c:
        return c[q]
    mc = body.meshManager.createMeshCalculator(); mc.surfaceTolerance = tol
    ms = mc.calculate(); P = ms.nodeCoordinatesAsDouble; I = list(ms.nodeIndices)
    C, S, H, XC = k.C, k.S, k.H, k.XC
    W = [(P[3 * i] * 10 - XC, (P[3 * i + 1] * C - P[3 * i + 2] * S) * 10, H + (P[3 * i + 1] * S + P[3 * i + 2] * C) * 10) for i in range(len(P) // 3)]
    c[q] = (W, I); return c[q]


def plane_x(x): return [[x, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]]
def plane_z(z): return [[0, 0, z], [0, 0, 1], [1, 0, 0], [0, 1, 0]]
def plane_d(d): return [[0, -d * k.C, k.H - d * k.S], [0, -k.C, -k.S], [1, 0, 0], [0, -k.S, k.C]]     # axes x, in-plane up (design Z)


def section(body, pl, eps=0.05, tol=0.005, box=None):  # polylines of a body's mesh cut by a plane, in the plane's 2D axes
    W, I = wmesh(body, tol)
    o, nr, a1, a2 = pl
    sd = [(w[0] - o[0]) * nr[0] + (w[1] - o[1]) * nr[1] + (w[2] - o[2]) * nr[2] for w in W]
    segs = []
    for t in range(len(I) // 3):
        ids = (I[3 * t], I[3 * t + 1], I[3 * t + 2]); s = [sd[i] for i in ids]
        if min(s) > 0 or max(s) < 0 or (min(s) == 0 and max(s) == 0):
            continue
        pts = []
        for a, b in ((0, 1), (1, 2), (2, 0)):
            sa, sb = s[a], s[b]
            if (sa < 0 < sb) or (sb < 0 < sa) or sa == 0:
                f = 0.0 if sa == 0 else sa / (sa - sb)
                pa = W[ids[a]]; pb = W[ids[b]]
                q = [pa[i] + f * (pb[i] - pa[i]) for i in range(3)]
                u = sum((q[i] - o[i]) * a1[i] for i in range(3)); v = sum((q[i] - o[i]) * a2[i] for i in range(3))
                pts.append((u, v))
        if len(pts) >= 2:
            if box is None or any(box[0] <= p[0] <= box[1] and box[2] <= p[1] <= box[3] for p in pts[:2]):
                segs.append((pts[0], pts[1]))
    return [[[round(p[0], 2), round(p[1], 2)] for p in dp(l, eps)] for l in chain(segs) if len(l) >= 2]


def sections(names, planes, eps=0.05, tol=0.005, box=None):
    X = k.K(); res = {}
    for n in names:
        b = X.body(n)
        if b is None:
            continue
        for pn, pl in planes.items():
            r = section(b, pl, eps, tol, box.get(pn) if isinstance(box, dict) else box)
            if r:
                res.setdefault(pn, {})[n] = r
    return res
