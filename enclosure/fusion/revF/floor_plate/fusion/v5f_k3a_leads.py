# rev F k3a (2026-11-12): fix pass, block 3 - leads. Run through k.step(); the library is the global k, the picture helpers pc.
#   A lead is a chain of cylinders and spheres through its nodes, as in v5f_h3b_leads.py. Node frames: B = board frame (u, v, w),
#   S = slab (x_rel, depth, Zd), W = world (x_rel, y, z). Routes are data: k.c['routes'] = {name: [radius, [nodes]]}.
#   trial() adds a route as a hidden template AUD_<name>; near() lists what stands within a distance of a model body;
#   commit() makes the template the lead (the present LEAD_<name> -> LEAD_<name>_v55, hidden; a lead of this pass is replaced).
import math


def pt(n):
    return k.Bp(n[1], n[2], n[3]) if n[0] == 'B' else (k.Dp(n[1], n[2], n[3]) if n[0] == 'S' else k.Wp(n[1], n[2], n[3]))


def wn(n):                                           # a node as a world node
    q = k.W(pt(n)); return ['W', round(q[0], 2), round(q[1], 2), round(q[2], 2)]


def length(nodes):
    ps = [pt(n) for n in nodes]
    return sum(ps[i].distanceTo(ps[i + 1]) for i in range(len(ps) - 1)) * 10.0


def arc(c, e1, e2, rad, a0, a1, n):                  # world nodes on an arc about c in the plane of the unit vectors e1, e2; angles in degrees
    out = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / float(n))
        out.append(['W'] + [round(c[j] + rad * (math.cos(a) * e1[j] + math.sin(a) * e2[j]), 2) for j in range(3)])
    return out


def rope(X, r, nodes):
    ps = [pt(n) for n in nodes]; segs = []
    for i in range(len(ps) - 1):
        if ps[i].distanceTo(ps[i + 1]) < 1e-4:
            continue
        t = X.tbm.createCylinderOrCone(ps[i], r / 10.0, ps[i + 1], r / 10.0)
        if i > 0:
            X.uni(t, X.tbm.createSphere(ps[i], (r + 0.05) / 10.0))
        segs.append(t)
    while len(segs) > 1:                             # union in balanced pairs
        nxt = []
        for i in range(0, len(segs) - 1, 2):
            nxt.append(X.uni(segs[i], segs[i + 1]))
        if len(segs) % 2:
            nxt.append(segs[-1])
        segs = nxt
    return segs[0]


def trial(X, name, colour='red'):                    # the route k.c['routes'][name] as a hidden template
    r, nodes = k.c['routes'][name]
    old = X.body('AUD_' + name)
    if old is not None:
        old.deleteMe()
    b = pc['aud'](X, rope(X, r, nodes), name, colour)
    b.isLightBulbOn = False
    return b, round(length(nodes), 1)


def near(X, b, others, lim=3.0):                     # [(distance, name)] of model bodies within lim of body b
    q = b.boundingBox; e = lim / 10.0
    box = adsk_box(q.minPoint.x - e, q.minPoint.y - e, q.minPoint.z - e, q.maxPoint.x + e, q.maxPoint.y + e, q.maxPoint.z + e)
    out = []
    for o in others:
        if o.name == b.name or not box.intersects(o.boundingBox):
            continue
        d = X.mm.measureMinimumDistance(b, o).value * 10.0
        if d <= lim:
            out.append((round(d, 2), o.name))
    return sorted(out)


def adsk_box(x0, y0, z0, x1, y1, z1):
    import adsk.core
    return adsk.core.BoundingBox3D.create(k.P3(x0, y0, z0), k.P3(x1, y1, z1))


def overlap(X, b, name):                             # mm3 of a model body b inside the model body named (big bodies through their slabs)
    return k.xvol(X, X.tbm.copy(b), name)


def commit(X, name, suffix='_v55'):                  # AUD_<name> becomes LEAD_<name>
    t = X.body('AUD_' + name)
    if t is None:
        raise RuntimeError('no template for ' + name)
    old = X.body(name)
    like = old or X.body('LEAD_MIC_R')
    if old is not None:
        if X.body(name + suffix) is None:
            X.retire(old, suffix)
        else:
            old.deleteMe()
    t.name = name
    try:
        t.appearance = like.appearance
    except Exception:
        pass
    t.isLightBulbOn = False
    return t
