# change3/c3_lib.py - helpers of the FDM fix pass (2026-11-18, brief claude/brief-enclosure-fdm-fixes-2026-11-18.md).
# Exec'd into sys.modules['c3'] (loader: c3_calls.py); k = sys.modules['c3k'] = v5f_k_lib.py (blob ba85884) with its own cache 'c3_cache'.
# World mm: x + = viewer's left, y + toward the screen, z up. Nothing here changes the document: sections, face lists, temporary bodies only.
import adsk.core, adsk.fusion, sys, os, math, time, zlib, struct
k = sys.modules['c3k']
OUT = os.path.expanduser('~/Documents/HA_panel_renders/fdm-fixes')
G = k.c.setdefault('g22', {})                           # name -> the new temporary body
ST = adsk.core.SurfaceTypes
TN = {ST.PlaneSurfaceType: 'pl', ST.CylinderSurfaceType: 'cy', ST.ConeSurfaceType: 'co', ST.TorusSurfaceType: 'to', ST.SphereSurfaceType: 'sp'}


# ---------- small solids ----------
def W3(a, b):                                           # design vector from world point a to world point b
    return k.Wp(*a).vectorTo(k.Wp(*b))


def obox_w(X, c, u, v, L, Wd, Ht):                      # box centred at world c: L along u, Wd along v, Ht along u x v (world vectors)
    U = W3(c, [c[i] + u[i] for i in range(3)]); V = W3(c, [c[i] + v[i] for i in range(3)]); U.normalize(); V.normalize()
    return X.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(k.Wp(*c), U, V, L / 10.0, Wd / 10.0, Ht / 10.0))


def cone_w(X, p0, r0, p1, r1):
    return X.tbm.createCylinderOrCone(k.Wp(*p0), r0 / 10.0, k.Wp(*p1), r1 / 10.0)


def tube(X, p0, p1, r_out, r_in):
    t = X.cyl(p0, p1, r_out)
    e = [(p1[i] - p0[i]) for i in range(3)]; n = math.sqrt(sum(q * q for q in e)); e = [q / n for q in e]
    X.dif(t, X.cyl([p0[i] - e[i] for i in range(3)], [p1[i] + e[i] for i in range(3)], r_in))
    return t


def skin(X):                                            # the cloth reference as a temporary body
    if 'skin_ref' not in k.c:
        k.c['skin_ref'] = X.tbm.copy(X.body('REF_F_outer'))
    return k.c['skin_ref']


# ---------- faces of a body in a world box ----------
def inbox(p, box):
    return box[0] <= p[0] <= box[1] and box[2] <= p[1] <= box[3] and box[4] <= p[2] <= box[5]


def flist(X, b, box, amin=0.05, kinds=None):
    dbb = X.wbox(*box).boundingBox; rows = []
    for i, f in enumerate(b.faces):
        if not dbb.intersects(f.boundingBox):
            continue
        p = k.W(f.pointOnFace); vs = [k.W(v.geometry) for v in f.vertices]
        if not (inbox(p, box) or any(inbox(v, box) for v in vs)):
            continue
        ar = f.area * 100.0
        if ar < amin:
            continue
        g = f.geometry; t = TN.get(g.surfaceType, 'nu')
        if kinds and t not in kinds:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
        ext = [round(fn(v[j] for v in vs), 2) for j in range(3) for fn in (min, max)] if vs else None
        row = {'i': i, 't': t, 'A': round(ar, 2), 'p': k.r2(p), 'n': k.r2(k.wv(nv), 3), 'ext': ext}
        if t in ('cy', 'co'):
            row['r'] = round(g.radius * 10.0, 3); row['ax'] = k.r2(k.unit(k.wv(g.axis)), 3); row['o'] = k.r2(k.W(g.origin))
            if t == 'co':
                row['ha'] = round(math.degrees(g.halfAngle), 2)
        if t == 'to':
            row['r'] = (round(g.majorRadius * 10.0, 3), round(g.minorRadius * 10.0, 3)); row['ax'] = k.r2(k.unit(k.wv(g.axis)), 3); row['o'] = k.r2(k.W(g.origin))
        rows.append(row)
    return rows


def fshow(rows, key=None):
    for r in sorted(rows, key=key or (lambda r: -r['A'])):
        s = '%4d %s A%8.2f p%s n%s' % (r['i'], r['t'], r['A'], r['p'], r['n'])
        if 'r' in r:
            s += ' r%s ax%s o%s' % (r['r'], r['ax'], r['o'])
        if 'ha' in r:
            s += ' ha%s' % r['ha']
        print(s + ' ext%s' % r['ext'])


# ---------- plane sections ----------
def section(X, body, o, n, e1, e2, tol=0.02, win=None):  # polylines [(a, b), ...] in the plane through world o: a along e1, b along e2 (mm from o)
    pl = adsk.core.Plane.create(k.Wp(*o), k.dv(k.unit(n)))
    try:
        w = X.tbm.planeIntersection(body, pl)
    except RuntimeError:
        return []
    edges = []
    if w.wires.count:
        for wi in w.wires:
            edges += [e for e in wi.edges]
    else:
        edges = [e for e in w.edges]
    out = []
    for e in edges:
        ev = e.evaluator
        ok, t0, t1 = ev.getParameterExtents()
        ok, pts = ev.getStrokes(t0, t1, tol / 10.0)
        q = []
        for p in pts:
            wp = k.W(p); d = (wp[0] - o[0], wp[1] - o[1], wp[2] - o[2])
            q.append((d[0] * e1[0] + d[1] * e1[1] + d[2] * e1[2], d[0] * e2[0] + d[1] * e2[1] + d[2] * e2[2]))
        if not q:
            continue
        if win is not None:
            a0 = min(a for a, c in q); a1 = max(a for a, c in q); c0 = min(c for a, c in q); c1 = max(c for a, c in q)
            if a1 < win[0] or a0 > win[1] or c1 < win[2] or c0 > win[3]:
                continue
        out.append(q)
    return out


FONT = {'0': '111101101101111', '1': '010110010010111', '2': '111001111100111', '3': '111001111001111', '4': '101101111001001', '5': '111100111001111',
        '6': '111100111101111', '7': '111001001001001', '8': '111101111101111', '9': '111101111001111', '-': '000000111000000', '.': '000000000000010',
        ' ': '000000000000000'}


class Img:                                              # a white RGB bitmap over a window (a0, a1, b0, b1) in mm at s pixels per mm; b up
    def __init__(self, win, s):
        self.a0, self.a1, self.b0, self.b1 = win; self.s = float(s)
        self.w = int(round((self.a1 - self.a0) * s)) + 1; self.h = int(round((self.b1 - self.b0) * s)) + 1
        self.px = bytearray(b'\xff' * (self.w * self.h * 3))

    def xy(self, a, b):
        return (a - self.a0) * self.s, (self.b1 - b) * self.s

    def dot(self, x, y, col):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3; self.px[i:i + 3] = bytes(col)

    def seg(self, p, q, col, wide=True):
        x0, y0 = self.xy(*p); x1, y1 = self.xy(*q)
        if max(x0, x1) < 0 or min(x0, x1) > self.w or max(y0, y1) < 0 or min(y0, y1) > self.h:
            return
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        if n > 20000:
            n = 20000
        for i in range(n + 1):
            t = i / float(n); x = int(round(x0 + (x1 - x0) * t)); y = int(round(y0 + (y1 - y0) * t))
            self.dot(x, y, col)
            if wide:
                self.dot(x + 1, y, col); self.dot(x, y + 1, col)

    def outline(self, polys, col, wide=True):
        for q in polys:
            for i in range(len(q) - 1):
                self.seg(q[i], q[i + 1], col, wide)

    def fill(self, polys, col):                         # even-odd scan-line fill of closed section curves
        rows = {}
        for q in polys:
            for i in range(len(q) - 1):
                x0, y0 = self.xy(*q[i]); x1, y1 = self.xy(*q[i + 1])
                if y0 == y1:
                    continue
                if y0 > y1:
                    x0, y0, x1, y1 = x1, y1, x0, y0
                r0 = max(0, int(math.ceil(y0))); r1 = min(self.h - 1, int(math.ceil(y1)) - 1)
                for r in range(r0, r1 + 1):
                    rows.setdefault(r, []).append(x0 + (r - y0) * (x1 - x0) / (y1 - y0))
        cb = bytes(col)
        for r, xs in rows.items():
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                ia = max(0, int(math.ceil(xs[j]))); ib = min(self.w - 1, int(math.floor(xs[j + 1])))
                if ib >= ia:
                    o = (r * self.w + ia) * 3; self.px[o:o + 3 * (ib - ia + 1)] = cb * (ib - ia + 1)

    def text(self, x, y, s, col, sc=2):
        for ch in s:
            g = FONT.get(ch, FONT[' '])
            for j in range(15):
                if g[j] == '1':
                    for dx in range(sc):
                        for dy in range(sc):
                            self.dot(x + (j % 3) * sc + dx, y + (j // 3) * sc + dy, col)
            x += 4 * sc

    def grid(self, step, major=5):
        i0 = int(math.ceil(self.a0 / step - 1e-9)); i1 = int(math.floor(self.a1 / step + 1e-9))
        for i in range(i0, i1 + 1):
            a = i * step; col = (150, 150, 150) if i % major == 0 else (222, 222, 222)
            self.seg((a, self.b0), (a, self.b1), col, False)
            if i % major == 0:
                x, y = self.xy(a, self.b0); self.text(int(x) + 3, self.h - 14, ('%g' % a), (90, 90, 90))
        j0 = int(math.ceil(self.b0 / step - 1e-9)); j1 = int(math.floor(self.b1 / step + 1e-9))
        for j in range(j0, j1 + 1):
            b = j * step; col = (150, 150, 150) if j % major == 0 else (222, 222, 222)
            self.seg((self.a0, b), (self.a1, b), col, False)
            if j % major == 0:
                x, y = self.xy(self.a0, b); self.text(3, int(y) + 3, ('%g' % b), (90, 90, 90))

    def cross(self, a, b, col, r=6):
        x, y = self.xy(a, b); x = int(round(x)); y = int(round(y))
        for d in range(-r, r + 1):
            self.dot(x + d, y, col); self.dot(x, y + d, col)

    def save(self, fname):
        if not os.path.isdir(OUT):
            os.makedirs(OUT)
        raw = b''.join(b'\x00' + bytes(self.px[r * self.w * 3:(r + 1) * self.w * 3]) for r in range(self.h))

        def chunk(tag, body):
            return struct.pack('>I', len(body)) + tag + body + struct.pack('>I', zlib.crc32(tag + body) & 0xffffffff)
        data = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', self.w, self.h, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b'')
        p = os.path.join(OUT, fname)
        with open(p, 'wb') as f:
            f.write(data)
        return p, self.w, self.h, len(data)


def tint(col, f=0.78):
    return tuple(int(255 - (255 - v) * (1.0 - f)) for v in col)


COL = {'shell': (30, 60, 160), 'door': (170, 60, 20), 'box': (20, 120, 60), 'base': (120, 40, 140), 'new': (220, 0, 0), 'lead': (200, 140, 0), 'part': (90, 90, 90),
       'cap': (0, 130, 150), 'plate': (0, 0, 0)}


def secpic(X, items, o, n, e1, e2, win, s, fname, grid=1.0, marks=(), major=5):
    # items: [(body or temporary body, (r, g, b), filled)]; marks: [(a, b)] crosses. Returns the file's path and size.
    im = Img(win, s); secs = []
    for b, col, filled in items:
        ps = section(X, b, o, n, e1, e2, win=win); secs.append((ps, col))
        if filled:
            im.fill(section(X, b, o, n, e1, e2), tint(col))
    im.grid(grid, major)
    for ps, col in secs:
        im.outline(ps, col)
    for m in marks:
        im.cross(m[0], m[1], (255, 0, 255))
    return im.save(fname)


AX = {'x': ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),     # plane x = const: a = world y, b = world z
      'y': ((0.0, 1.0, 0.0), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0)),     # plane y = const: a = world x, b = world z
      'z': ((0.0, 0.0, 1.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0))}     # plane z = const: a = world x, b = world y


def wpic(X, items, axis, val, win, s, fname, grid=1.0, marks=(), major=5):   # a world-axis section with absolute world coordinates on the picture
    n, e1, e2 = AX[axis]
    o = (val, 0.0, 0.0) if axis == 'x' else (0.0, val, 0.0) if axis == 'y' else (0.0, 0.0, val)
    return secpic(X, items, o, n, e1, e2, win, s, fname, grid, marks, major)


# ---------- what a new body adds and removes, and what the added plastic meets (as change2's delta) ----------
def delta(X, name, near=1.5, skip=()):
    new = G[name]; old = k.tcopy(X, name)
    add = X.tbm.copy(new); X.dif(add, old); rem = X.tbm.copy(old); X.dif(rem, new)
    va = X.vol(add) if add.faces.count else 0.0; vr = X.vol(rem) if rem.faces.count else 0.0
    res = {'old': round(X.vol(old), 3), 'new': round(X.vol(new), 3), 'added': round(va, 3), 'removed': round(vr, 3), 'lumps': new.lumps.count, 'faces': new.faces.count}
    hits = {}; close = {}
    if va > 1e-4:
        q = add.boundingBox; e = near / 10.0
        box = adsk.core.BoundingBox3D.create(k.P3(q.minPoint.x - e, q.minPoint.y - e, q.minPoint.z - e), k.P3(q.maxPoint.x + e, q.maxPoint.y + e, q.maxPoint.z + e))
        for o in k.current(X, leads=True):
            if o.name == name or o.name in skip or not box.intersects(o.boundingBox):
                continue
            if k.late():
                close[o.name] = 'not checked (time)'; continue
            t = k.tcopy(X, o.name)
            d = X.mm.measureMinimumDistance(add, t).value * 10.0
            if d < 0.0005:
                hits[o.name] = round(X.xv(add, t), 3)
            elif d < near:
                close[o.name] = round(d, 2)
    k.c[('delta', name)] = (add, rem)
    return res, hits, close


def outside(X, name):                                   # what of a new body lies outside the cloth reference
    t = X.tbm.copy(G[name]); X.dif(t, X.tbm.copy(skin(X)))
    return (round(X.vol(t), 3), [round(l.volume * 1000.0, 3) for l in t.lumps]) if t.faces.count else (0.0, [])


def lumpbox(X, tb):                                     # [[mm3, world box], ...] of a temporary body's lumps
    return k.K.lumps(X, tb) if tb.faces.count else []
