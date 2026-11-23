# Helpers for the scripts that turn version 67 of the Fusion model into version 68:
# screws and printed clamps instead of heat-staked and glued joints.
#
# Loaded into Fusion's Python as the module "v68" (README.md has the loader). It needs the two
# helper libraries of the earlier passes, already loaded as the modules "c3k" and "c3".
# Lengths in mm. World coordinates: x + = the viewer's left, y + toward the screen, z up.
# Nothing in this file changes the document: every solid here is a temporary body.
import sys, math
import adsk.core, adsk.fusion

k = sys.modules['c3k']
c3 = sys.modules['c3']
G = k.c.setdefault('v68', {})      # name -> the new temporary body of a changed or added part
BACKUP = '_v67'                    # suffix of the hidden copy kept of every changed body


def box(X, sx, x0, x1, y0, y1, z0, z1):
    """A world box. sx = -1 mirrors it to the right-hand side."""
    return X.wbox(sx * x0, sx * x1, y0, y1, z0, z1)


def cyl(X, sx, x, y, z0, z1, r0, r1=None):
    """An upright cylinder, or a cone with radius r0 at z0 and r1 at z1."""
    return X.cyl((sx * x, y, z0), (sx * x, y, z1), r0, r1)


def add(X, t, *tools):
    for q in tools:
        X.uni(t, q)
    return t


def cut(X, t, *tools):
    for q in tools:
        X.dif(t, q)
    return t


def start(X, name):
    """A temporary copy of a model body, to work on."""
    return X.tbm.copy(X.body(name))


def facts(X, name):
    """Volume and lumps of a new body, and what it adds to and takes from the model's body."""
    new = G[name]
    out = {'new': round(X.vol(new), 3), 'lumps': new.lumps.count, 'faces': new.faces.count}
    old = X.body(name)
    if old is not None:
        o = X.tbm.copy(old)
        a = X.tbm.copy(new); X.dif(a, o)
        r = X.tbm.copy(o); X.dif(r, new)
        out['old'] = round(X.vol(o), 3)
        out['added'] = round(X.vol(a), 3) if a.faces.count else 0.0
        out['removed'] = round(X.vol(r), 3) if r.faces.count else 0.0
    return out


def near(X, tb, skip=(), lim=1.5, new=True):
    """The unit's bodies within lim of a temporary body: the distance, or the shared volume if they meet.
    With new=True a part changed in this pass is taken as its new body."""
    q = tb.boundingBox; e = lim / 10.0
    bb = adsk.core.BoundingBox3D.create(k.P3(q.minPoint.x - e, q.minPoint.y - e, q.minPoint.z - e),
                                        k.P3(q.maxPoint.x + e, q.maxPoint.y + e, q.maxPoint.z + e))
    names = [b.name for b in k.current(X, leads=True)]
    names += [n for n in G if n not in names]
    rows = []
    for n in names:
        if n in skip:
            continue
        t = G[n] if (new and n in G) else (k.tcopy(X, n) if X.body(n) is not None else None)
        if t is None or t is tb or not bb.intersects(t.boundingBox):
            continue
        if k.late():
            rows.append((99.0, n + ': not checked, out of time')); continue
        d = X.mm.measureMinimumDistance(tb, t).value * 10.0
        if d < 0.0005:
            rows.append((0.0, '%s shares %.3f mm3' % (n, X.xv(tb, t))))
        elif d < lim:
            rows.append((round(d, 2), n))
    return sorted(rows)


def simplify(pts, eps):
    """Drop points that lie within eps of the line between their neighbours (Douglas-Peucker)."""
    if len(pts) < 3:
        return list(pts)
    a, b = pts[0], pts[-1]
    dx, dy = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dy)
    far, at = 0.0, 0
    for i in range(1, len(pts) - 1):
        p = pts[i]
        d = abs(dx * (p[1] - a[1]) - dy * (p[0] - a[0])) / L if L > 1e-9 else math.hypot(p[0] - a[0], p[1] - a[1])
        if d > far:
            far, at = d, i
    if far <= eps:
        return [a, b]
    return simplify(pts[:at + 1], eps)[:-1] + simplify(pts[at:], eps)


def cutline(X, bodies, axis, val, win, eps=0.03):
    """Outlines of bodies where a world-axis plane cuts them: {name: [[a0, b0, a1, b1, ...], ...]}.
    bodies: {name: model or temporary body}. axis 'x': a = y, b = z; 'y': a = x, b = z; 'z': a = x, b = y."""
    n, e1, e2 = c3.AX[axis]
    o = (val, 0.0, 0.0) if axis == 'x' else (0.0, val, 0.0) if axis == 'y' else (0.0, 0.0, val)
    out = {}
    for name, b in bodies.items():
        rows = []
        for q in c3.section(X, b, o, n, e1, e2, win=win):
            rows.append([round(w, 2) for p in simplify(q, eps) for w in p])
        if rows:
            out[name] = rows
    return out


def picture(X, items, axis, val, win, scale, fname, folder, marks=()):
    """A section picture (PNG) in the given folder on the Mac. items: [(body, (r, g, b), filled)]."""
    c3.OUT = folder
    return c3.wpic(X, items, axis, val, win, scale, fname, marks=marks)
