# aud3x_lib.py - assembly audit, re-check after the fix pass (2026-11-12, model version 60).
# Loaded into sys.modules['aud3x'] inside Fusion. It uses the fix pass's library v5f_k_lib.py, loaded unchanged as sys.modules['aud3']
# (frames, temporary solids, slabs of the big bodies, tool shapes). Read-only: temporary bodies, distances, point containment.
# Nothing here changes the design. World mm: x = x_rel (+x = viewer's left), y + toward the screen, z up from the plate's underside.
import adsk.core, adsk.fusion, math, sys, time
k = sys.modules['aud3']
P3 = adsk.core.Point3D.create; V3 = adsk.core.Vector3D.create
R = {}; T = {}; RES = {}


def bb6(b):
    q = b.boundingBox; return (q.minPoint.x, q.minPoint.y, q.minPoint.z, q.maxPoint.x, q.maxPoint.y, q.maxPoint.z)


def tl(X, name):                                  # temporary pieces of a model body (big bodies: the cached slabs), looked up once
    if name not in T:
        T[name] = list(k.parts(X, name))
    return T[name]


def crop(X, name, key, box, frame='W'):           # crop of a body to a world ('W'), slab ('S') or board ('B') box; cached under key
    if key in R:
        return R[key]
    out = []
    for p in tl(X, name):
        bx = X.wbox(*box) if frame == 'W' else (X.dbox(*box) if frame == 'S' else X.bbox(*box))
        if not bx.boundingBox.intersects(p.boundingBox):
            continue
        X.tbm.booleanOperation(bx, p, k.BT.IntersectionBooleanType)
        if X.vol(bx) > 0.001:
            out.append(bx)
    R[key] = out; return out


def items(X, names=(), crops=(), temps=()):       # obstacles as (label, body, box): model bodies by name or group, cached crops, labelled temporary bodies
    out = []
    for n in names:
        for b in (k.st(X, n) if n in k.ST else k.present(X, [n])):
            if b.name in k.BIG:
                raise RuntimeError('use a crop for ' + b.name)
            out.append((k.sn(b.name), b, bb6(b)))
    for key in crops:
        out += [(key, t, bb6(t)) for t in R[key]]
    out += [(lab, t, bb6(t)) for lab, t in temps]
    return out


def line(X, o, u, secs, its, st0=2.0, step=1.0, rng=12.0, head=7.0):   # tool on its axis from its working end o along u: margin = distance - tool radius
    u = k.unit(u); total = sum(L for d, L in secs); best = {}; hb = {}; s = st0
    while s <= total + 1e-6:
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
    return {'min': rows[0] if rows else None, 'rows': rows[:4], 'head': hrows[0] if hrows else None}


def fmt(r):
    return 'head %s | beyond %s' % ('>12' if r['head'] is None else '%+.2f %s' % (r['head'][0], r['head'][2]),
                                    '>12' if r['min'] is None else ' '.join('%+.2f@%g %s' % t for t in r['rows'][:3]))


def mv(X, tb, d):                                 # a moved copy of a temporary body (world mm)
    t = X.tbm.copy(tb); return X.move(t, d[0], d[1], d[2])


def mvn(X, tb, out):                              # a copy moved along the slab normal toward the viewer
    t = X.tbm.copy(tb); return X.move_n(t, out)


def clash(X, movers, fixed, eps=0.002):           # {(mover, fixed): mm3}; movers [(label, body)], fixed [(label, body, box)]
    out = {}
    for ml, mb in movers:
        for fl, fb, q in fixed:
            if not mb.boundingBox.intersects(fb.boundingBox):
                continue
            v = X.xv(mb, fb)
            if abs(v) > eps:
                out[(ml, fl)] = round(out.get((ml, fl), 0.0) + v, 3)
    return out


def where(X, a, b, n=3):                          # the largest lumps common to two temporary bodies: [mm3, world box]
    t = X.tbm.copy(a); X.tbm.booleanOperation(t, b, k.BT.IntersectionBooleanType)
    return X.lumps(t)[:n]


def gap(X, a, b):                                 # smallest distance between two bodies and its two points (world)
    r = X.mm.measureMinimumDistance(a, b)
    return round(r.value * 10.0, 3), k.r2(k.W(r.positionOne)), k.r2(k.W(r.positionTwo))


def finger(X, tip, a, r=8.0, L=60.0):             # rounded fingertip: tip (world), a = direction from the tip back along the finger (world)
    a = k.unit(a); cc = k.along(tip, a, r); end = k.along(tip, a, L)
    t = X.cyl(cc, end, r); return X.uni(t, X.sph(cc, r))


def rod(X, a, b, r):                              # capsule between two world points
    t = X.cyl(a, b, r); X.uni(t, X.sph(a, r)); return X.uni(t, X.sph(b, r))


def wb(X, tb):                                    # world box of a temporary body [x0, x1, y0, y1, z0, z1]
    t = X.tbm.copy(tb); m = adsk.core.Matrix3D.create()
    m.setWithArray([1, 0, 0, -k.XC / 10.0, 0, k.C, -k.S, 0, 0, k.S, k.C, k.H / 10.0, 0, 0, 0, 1]); X.tbm.transform(t, m)
    q = t.boundingBox
    return [round(v * 10, 2) for v in (q.minPoint.x, q.maxPoint.x, q.minPoint.y, q.maxPoint.y, q.minPoint.z, q.maxPoint.z)]


def wbn(X, name):                                 # world box of a model body through its temporary pieces
    bs = [wb(X, t) for t in tl(X, name)]
    return [min(b[0] for b in bs), max(b[1] for b in bs), min(b[2] for b in bs), max(b[3] for b in bs), min(b[4] for b in bs), max(b[5] for b in bs)]


def solid(X, pieces, p):                          # is a world point inside one of the temporary pieces
    q = k.Wp(*p)
    for t in pieces:
        if t.pointContainment(q) in (adsk.fusion.PointContainment.PointInsidePointContainment, adsk.fusion.PointContainment.PointOnPointContainment):
            return True
    return False


def left(t0, lim=50.0): return lim - (time.time() - t0)
