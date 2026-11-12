# rev F m lib (2026-11-12): ribbon pass - flat leads as strips (brief claude/brief-enclosure-ribbon-pass-2026-11-12.md).
# Loaded into sys.modules['v5f_m'] inside Fusion from the repo's raw URL by commit, sha256 checked; it uses the fix pass's library
# v5f_k_lib.py, already loaded as sys.modules['v5f_k'] (frames, temporary solids, slabs of the big bodies).
# World mm throughout: x = x_rel (+x = viewer's left), y + toward the screen, z up from the plate's underside.
# A flat lead is a Strip: a frame (P point, d heading, w width direction; n = d x w is the normal of its face A) moved by
#   S(L)                 straight
#   B(deg, R)            bend through the thickness about the width axis, centre-line radius R; deg > 0 turns toward +n
#   F(theta, turn, side) fold: crease through P at theta to the heading; the heading turns by 2 theta toward turn * w; the strip is
#                        turned over (face A looks the other way) and goes on one layer further toward side * n (old n)
#   T(deg, L)            twist about the heading over the length L
# Every piece is a temporary solid; nothing here changes the design except put()/lead() at the end of the file.
import adsk.core, adsk.fusion, math, sys, time
k = sys.modules['v5f_k']
c = {}                                               # caches and results, kept between connector calls
EPS = 0.02
HALF = 400.0


def add(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def mul(a, s): return (a[0] * s, a[1] * s, a[2] * s)
def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def unit(a): return k.unit(a)
def lin(a, s, b, t): return (a[0] * s + b[0] * t, a[1] * s + b[1] * t, a[2] * s + b[2] * t)
def bdir(u, v, w): return unit(sub(k.B2W(u, v, w), k.B2W(0.0, 0.0, 0.0)))        # a board-frame direction as a world direction
def r2(q, n=2): return [round(v, n) for v in q]


class Strip:
    def __init__(self, X, P, d, w, W, t, name=''):
        self.X = X; self.P = tuple(P); self.d = unit(d)
        self.w = unit(sub(w, mul(self.d, dot(w, self.d))))
        self.W = W; self.t = t; self.name = name
        self.pieces = []                             # [label, temporary body]
        self.L = 0.0                                 # centre-line length so far
        self.log = []                                # [label, op, length at its start, P, d, w]
        self.i = 0
        self.clip = None                             # (P, m, crease) of a fold whose crease still has to cut the next piece

    @property
    def n(self): return cross(self.d, self.w)

    def _lab(self, lab, op):
        self.i += 1
        lab = lab or '%s%d' % (op, self.i)
        self.log.append([lab, op, round(self.L, 2), r2(self.P), r2(self.d, 4), r2(self.w, 4)])
        return lab

    def _box(self, P0, d, w, L, W, t):               # box from P0 along d, width along w, thickness along d x w, centred on the line
        return self.X.obox(add(P0, mul(d, L / 2.0)), d, w, L, W, t)

    def _half(self, P0, m, cdir):                    # the half-space (x - P0) . m <= 0 as a big box; cdir a unit vector square to m
        return self.X.obox(sub(P0, mul(m, HALF / 2.0)), m, cdir, HALF, HALF, HALF)

    def _add(self, lab, tb):                         # a piece; the first piece after a fold is cut at the crease
        if self.clip is not None:
            self.X.sec(tb, self._half(*self.clip)); self.clip = None
        self.pieces.append([lab, tb])

    def S(self, L, lab=None):
        lab = self._lab(lab, 'S')
        if L > 1e-6:
            self._add(lab, self._box(sub(self.P, mul(self.d, EPS)), self.d, self.w, L + 2 * EPS, self.W, self.t))
        self.P = add(self.P, mul(self.d, L)); self.L += L
        return self

    def B(self, deg, R, lab=None):
        if abs(deg) > 180.0 + 1e-9:
            h = deg / 2.0
            return self.B(h, R, lab).B(deg - h, R, lab)
        lab = self._lab(lab, 'B')
        X = self.X; sg = 1.0 if deg > 0 else -1.0; a = math.radians(abs(deg))
        d = self.d; n = self.n; w = self.w
        C = add(self.P, mul(n, sg * R))
        d1 = lin(d, math.cos(a), n, sg * math.sin(a))
        n1 = lin(n, math.cos(a), d, -sg * math.sin(a))
        hw = self.W / 2.0
        ring = X.cyl(sub(C, mul(w, hw)), add(C, mul(w, hw)), R + self.t / 2.0)
        if R - self.t / 2.0 > 0.01:
            X.dif(ring, X.cyl(sub(C, mul(w, hw + 0.3)), add(C, mul(w, hw + 0.3)), R - self.t / 2.0))
        X.sec(ring, self._half(C, mul(d, -1.0), w))               # (x - C) . d >= 0
        if abs(deg) < 180.0 - 1e-6:
            X.sec(ring, self._half(C, d1, w))                     # (x - C) . d1 <= 0
        self._add(lab, ring)
        self.P = sub(C, mul(n1, sg * R)); self.d = unit(d1); self.L += R * a
        return self

    def F(self, theta, turn, side, gap=None, lab=None):
        lab = self._lab(lab, 'F')
        X = self.X; th = math.radians(theta); gap = self.t if gap is None else gap
        d = self.d; w = self.w; n = self.n; hw = self.W / 2.0
        cd = unit(lin(d, math.cos(th), w, turn * math.sin(th)))    # the crease
        m = unit(lin(d, math.sin(th), w, -turn * math.cos(th)))    # in the strip's plane, square to the crease, forward
        e = hw / math.tan(th)
        if self.pieces:                              # the piece before the fold ends at the crease too
            X.sec(self.pieces[-1][1], self._half(self.P, m, cd))
        fin = self._box(sub(self.P, mul(d, EPS)), d, w, e + EPS, self.W, self.t)
        X.sec(fin, self._half(self.P, m, cd))
        self._add(lab + '.in', fin)
        d1 = sub(mul(cd, 2.0 * dot(d, cd)), d); w1 = sub(mul(cd, 2.0 * dot(w, cd)), w)
        off = self.t + gap
        P1 = add(self.P, mul(n, side * off))
        fout = self._box(sub(P1, mul(d1, e)), d1, w1, e + EPS, self.W, self.t)
        X.sec(fout, self._half(P1, m, cd))
        self.pieces.append([lab + '.out', fout])
        self.clip = (P1, m, cd)
        mid = add(self.P, mul(n, side * off / 2.0)); hl = hw / math.sin(th)
        self.pieces.append([lab + '.roll', X.cyl(sub(mid, mul(cd, hl)), add(mid, mul(cd, hl)), (off + self.t) / 2.0)])
        self.P = P1; self.d = unit(d1); self.w = unit(w1); self.L += math.pi * off / 2.0
        return self

    def T(self, deg, L, nseg=12, lab=None):
        lab = self._lab(lab, 'T')
        w0 = self.w; n0 = self.n; d = self.d; q = L / nseg
        for i in range(nseg):
            a = math.radians(deg * (i + 0.5) / nseg)
            wi = lin(w0, math.cos(a), n0, math.sin(a))
            self._add('%s.%d' % (lab, i), self._box(add(self.P, mul(d, i * q - EPS)), d, wi, q + 2 * EPS, self.W, self.t))
        a = math.radians(deg)
        self.w = unit(lin(w0, math.cos(a), n0, math.sin(a)))
        self.P = add(self.P, mul(d, L)); self.L += L
        return self

    def width(self, W):
        self.W = W; return self

    def end(self, lab='end'):
        self._lab(lab, 'end'); return self

    def frame(self):
        return {'P': r2(self.P), 'd': r2(self.d, 4), 'w': r2(self.w, 4), 'n': r2(self.n, 4), 'L': round(self.L, 2),
                'B': r2(k.W2B(*self.P))}

    def solid(self):                                 # one temporary body of all pieces (union in balanced pairs)
        X = self.X; segs = [X.cp(p) for q, p in self.pieces]
        while len(segs) > 1:
            nxt = []
            for i in range(0, len(segs) - 1, 2):
                nxt.append(X.uni(segs[i], segs[i + 1]))
            if len(segs) % 2:
                nxt.append(segs[-1])
            segs = nxt
        return segs[0]


# ---------- obstacles ----------
BIGBOX = (-12.0, 112.0, -100.0, 30.0, -6.0, 190.0)   # world crop of the big bodies: the left-speaker half and the middle


def crops(X, name, budget=True):                     # cached crop of a big body to BIGBOX: list of temporary pieces, or None if out of time.
    for q in c:                                      # Keyed by name only: reading a big body's volume costs up to 12 s a call, and no
        if isinstance(q, tuple) and q[0] == 'mcrop' and q[1] == name:      # printed part changes in this pass (block 3 compares the volumes)
            return c[q]
    if budget and k.late():
        return None
    c[('mcrop', name)] = k.region(X, name, 'm_big', BIGBOX)
    return c[('mcrop', name)]


def obstacles(X, skip=(), leads=True):               # [(name, [bodies])]: model bodies, big ones as cached crops; None if a crop is still to be made
    out = []
    for b in k.current(X, leads=leads):
        if b.name in skip:
            continue
        if b.name in k.BIG:
            p = crops(X, b.name)
            if p is None:
                return None
            out.append((b.name, p))
        else:
            out.append((b.name, [b]))
    return out


def bb6(b):
    q = b.boundingBox; return (q.minPoint.x, q.minPoint.y, q.minPoint.z, q.maxPoint.x, q.maxPoint.y, q.maxPoint.z)


def bgap(p, q):                                      # distance between two design-frame boxes, mm
    dx = max(q[0] - p[3], p[0] - q[3], 0.0); dy = max(q[1] - p[4], p[1] - q[4], 0.0); dz = max(q[2] - p[5], p[2] - q[5], 0.0)
    return math.sqrt(dx * dx + dy * dy + dz * dz) * 10.0


def clear(X, pieces, obs, lim=3.0, vols=True):       # {obstacle: [mm, piece label, mm3 where they touch, world point on the piece]} within lim
    out = {}
    boxes = [(lab, p, bb6(p)) for lab, p in pieces]
    for name, bodies in obs:
        best = None
        for b in bodies:
            qb = bb6(b)
            for lab, p, qp in boxes:
                if bgap(qp, qb) > lim:
                    continue
                r = X.mm.measureMinimumDistance(p, b); g = r.value * 10.0
                if best is None or g < best[0]:
                    best = [round(g, 2), lab, 0.0, r2(k.W(r.positionOne), 1)]
        if best is None or best[0] > lim:
            continue
        if best[0] < 0.005 and vols:
            v = 0.0
            for b in bodies:
                tb = b if b.isTemporary else k.tcopy(X, b.name)
                for lab, p, qp in boxes:
                    if bgap(qp, bb6(b)) < 0.01:
                        v += X.xv(p, tb)
            best[2] = round(v, 2)
        out[name] = best
    return out


def table(res, n=14):                                # nearest first, compact text
    rows = sorted(res.items(), key=lambda t: (t[1][0], -t[1][2]))
    return ' | '.join('%s %.2f%s@%s' % (k.sn(q), v[0], (' (%.2f mm3)' % v[2]) if v[2] else '', v[1]) for q, v in rows[:n])


def scan(X, p0, p1, obs, minlen=0.0):                # solid stretches of a thin bar between two world points: [[t0, t1, name], ...]
    out = []
    for name, bodies in obs:
        ps = [b if b.isTemporary else k.tcopy(X, b.name) for b in bodies]
        for s in k.needle_t(X, ps, p0, p1):
            if s[1] - s[0] >= minlen:
                out.append([s[0], s[1], k.sn(name)])
    return sorted(out)


def free(X, p0, p1, obs):                            # free stretches along the bar, as text, with what bounds them
    L = math.sqrt(sum((p1[i] - p0[i]) ** 2 for i in range(3)))
    sol = scan(X, p0, p1, obs); out = []; t = 0.0; last = 'start'
    for a, b, nm in sol:
        if a > t + 0.05:
            out.append('%.1f..%.1f (%s|%s)' % (t, a, last, nm))
        if b > t:
            t = b; last = nm
    if t < L - 0.05:
        out.append('%.1f..%.1f (%s|end)' % (t, L, last))
    return ' '.join(out)


# ---------- model changes (the only ones in this file) ----------
def put(X, tb, name, colour=None, show=True):        # a temporary body into the model as a template AUD_<name>
    old = X.body('AUD_' + name)
    if old is not None:
        old.deleteMe()
    b = X.root.bRepBodies.add(tb); b.name = 'AUD_' + name
    if colour:
        a = X.des.appearances.itemByName(colour)
        if a is not None:
            b.appearance = a
    b.isLightBulbOn = show
    return b


def lead(X, name, tb, suffix='_v60', like=None):     # a lead or envelope replaced: the present body -> name + suffix (hidden); a body of this pass is replaced
    old = X.body(name)
    if old is None:
        b = X.add(tb, name, like=X.body(like) if like else None, show=False)
    elif X.body(name + suffix) is None:
        b = X.swap(name, tb, suffix, show=False)
    else:
        old.name = name + '_out'
        b = X.add(tb, name, like=old, show=False)
        old.deleteMe()
    return b


# ---------- the ADT-Link plugs, from the tables of claude/usb-cable-choice-2026-11-12.md (not from the maker's models) ----------
UC = {'face': 42.78, 'v': 7.21, 'w': -7.29}          # the ReSpeaker socket's face (u) and the plug's centre line, read from the model at version 60


def usbc(X, g=0.0, bt=1.6):                          # USB-C end (T2G) as labelled boxes in the board frame; g = how far the sleeve's face stands off the
    u0 = UC['face'] + g; v = UC['v']; w = UC['w']    # socket's face; bt = the plug's board thickness (model 0.8, drawing 1.6: the larger is allowed for)
    dx = bt - 0.8                                    # every face behind the board moves with its thickness
    def bx(a0, a1, hv, c0, c1):                      # along the plug a0..a1 (from the sleeve's face, + away from the ReSpeaker), half width hv, across c0..c1 (+ toward the door)
        return X.bbox(u0 + a0, u0 + a1, v - hv, v + hv, w + c0, w + c1)
    return [['shell', bx(-7.12, 1.00, 4.125, -1.20, 1.20)],
            ['flange', bx(1.00, 1.50, 4.125, -1.44, 1.44)],
            ['board', bx(1.50, 1.50 + bt, 4.50, -1.91, 3.60)],
            ['board2', bx(1.50, 1.50 + bt, 3.50, 3.55, 10.60)],
            ['sleeve_wide', bx(0.50, 2.60 + dx, 4.70, 2.16, 4.80)],
            ['sleeve_mid', bx(0.00, 2.60 + dx, 3.70, 4.75, 11.60)],
            ['sleeve_narrow', bx(0.00, 1.80, 2.70, 11.55, 18.96)],
            ['cable_on_board', bx(0.06, 1.50, 2.625, 2.16, 18.96)]]


def usbc_start(g=0.0):                               # the cable where it leaves the sleeve: world point, heading (toward the door), width direction (up the board)
    return k.B2W(UC['face'] + g + 0.06 + 0.72, UC['v'], UC['w'] + 18.96), bdir(0, 0, 1), bdir(0, 1, 0)


def join(X, pieces):                                 # labelled boxes as one temporary body
    t = X.cp(pieces[0][1])
    for q, p in pieces[1:]:
        X.uni(t, p)
    return t
