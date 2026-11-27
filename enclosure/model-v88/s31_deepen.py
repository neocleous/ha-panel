# Blocks 2 and 3: holes made deeper in a printed part. Builds a temporary body and keeps it in the library's cache k.c;
# NOTHING IS PUT INTO THE DOCUMENT here (s21_put.py does that).
# Each hole is found on the part itself: the cylinder face of its radius on the given axis, its exact axis and the centre of its
# floor's edge (so the cut continues the hole's own wall, not a rounded copy of it). The cut is a cylinder of the hole's radius
# from 0.2 before the floor to d beyond it, square-ended: the new floor is square to the axis like the old one.
#   build(part, names, key, extra=None)   the part with the named holes of s30_holes.HOLES deeper -> k.c[key]; per hole the
#                                          depth before and after (read off the faces); what went and what came, by lumps.
#                                          extra(k, X, t): more changes to the temporary body before the holes are cut
#   check(part, key, names)               the new body against the model's: volume, lumps, faces; what of each lies outside the
#                                          cloth reference; flat faces under 0.3 mm2 that the model's body does not have; the
#                                          faces of each hole on the new body; the level faces (square to the print's upright)
#                                          that differ, with their height and the grid
# Run: L.checked('s31_deepen.py', sha)['main'](what, tag, **kw)  -> s31_<what>_<tag>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/screw_margins_v88/'
L = runpy.run_path(D + 's00_lib.py')
ST = adsk.core.SurfaceTypes
CIRC = (adsk.core.Curve3DTypes.Circle3DCurveType, adsk.core.Curve3DTypes.Arc3DCurveType)
# sha256 of s30_holes.py, whose table of holes this script uses; set by main()
S30 = {}


def dot(a, b):
    return sum(a[i] * b[i] for i in range(3))


def hole_geo(k, body, M, F, r):
    """The hole on the body: {'r' cm, 'axis' design unit vector pointing inward, 'mouth', 'floor' design points (centres of the
    outermost and innermost circular edges of its wall), 'depth' mm, 'faces' n}. M, F: world points on its axis, mouth and floor."""
    o = k.unit(tuple(F[i] - M[i] for i in range(3))); best = None; hits = []
    for f in body.faces:
        g = f.geometry
        if g.surfaceType != ST.CylinderSurfaceType or abs(g.radius * 10.0 - r) > 0.06:
            continue
        a = k.unit(k.wv(g.axis))
        if abs(abs(dot(a, o)) - 1.0) > 1e-6:
            continue
        og = k.W(g.origin); dd = [og[i] - M[i] for i in range(3)]; t = dot(dd, o)
        off = math.sqrt(max(dot(dd, dd) - t * t, 0.0))
        if off > 0.3:
            continue
        p = k.W(f.pointOnFace); ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); n = k.wv(nv)
        tt = dot([p[i] - og[i] for i in range(3)], a); rad = [p[i] - (og[i] + tt * a[i]) for i in range(3)]
        if dot(rad, n) > 0:
            continue                                       # a pin, not a hole
        hits.append((off, f))
    if not hits:
        raise RuntimeError('no hole of radius %.2f on the axis through %s' % (r, k.r2(M, 2)))
    off0 = min(h[0] for h in hits); hits = [h for h in hits if h[0] < off0 + 0.01]
    g = hits[0][1].geometry
    ax = g.axis.copy(); ax.normalize()
    if dot(k.wv(ax), o) < 0:
        ax.scaleBy(-1.0)
    cs = []
    for off, f in hits:
        for e in f.edges:
            eg = e.geometry
            if eg.curveType in CIRC and abs(eg.radius - g.radius) < 1e-6:
                c = eg.center; w = k.W(c)
                cs.append((dot([w[i] - M[i] for i in range(3)], o), c))
    cs.sort(key=lambda q: q[0])
    return {'r': g.radius, 'axis': ax, 'mouth': cs[0][1], 'floor': cs[-1][1], 'depth': cs[-1][0] - cs[0][0], 'faces': len(hits), 'off': off0,
            't_mouth': cs[0][0], 't_floor': cs[-1][0]}


def shift(p, ax, mm):
    return adsk.core.Point3D.create(p.x + ax.x * mm / 10.0, p.y + ax.y * mm / 10.0, p.z + ax.z * mm / 10.0)


def deepen(k, X, t, body, M, F, r, d):
    """Cut the hole of the model's body d deeper in the temporary body t. Returns the hole's reading before."""
    h = hole_geo(k, body, M, F, r)
    tool = X.tbm.createCylinderOrCone(shift(h['floor'], h['axis'], -0.2), h['r'], shift(h['floor'], h['axis'], d), h['r'])
    X.dif(t, tool)
    return h


def less(X, a, b):
    t = X.tbm.copy(a); X.dif(t, X.tbm.copy(b))
    return t


def show(k, X, lab, t):
    n = t.lumps.count if t.faces.count else 0
    print('   %s: %.4f mm3 in %d lumps%s' % (lab, X.vol(t) if n else 0.0, n, (': %s' % X.lumps(t)[:12]) if n else ''))


def st_build(k, X, part, names, key, extra=None):
    H = S30['HOLES']
    b = X.body(part); t = X.tbm.copy(b)
    print('%s: the model\'s body %.3f mm3, lumps %d, faces %d' % (part, b.volume * 1000.0, b.lumps.count, b.faces.count))
    if extra is not None:
        extra(k, X, t)
        print('   after the other changes: %.3f mm3, lumps %d, faces %d' % (X.vol(t), t.lumps.count, t.faces.count))
    for nm in names:
        p, M, F, r, d = H[nm]
        if p != part:
            raise RuntimeError('%s is not a hole of %s' % (nm, part))
        h = deepen(k, X, t, b, M, F, r, d)
        h2 = hole_geo(k, t, M, tuple(F[i] + (F[i] - M[i]) * 0.0 for i in range(3)), r)
        print('   %-7s r %.4f, %.3f off the given axis, floor centre %s: %.4f deep -> %.4f deep (%+.4f); wall faces %d -> %d' % (
            nm, h['r'] * 10.0, h['off'], k.r2(k.W(h['floor']), 3), h['depth'], h2['depth'], h2['depth'] - h['depth'], h['faces'], h2['faces']))
    k.c[key] = t
    print('   %s: %.3f mm3 (%+.3f), lumps %d, faces %d' % (key, X.vol(t), X.vol(t) - b.volume * 1000.0, t.lumps.count, t.faces.count))
    show(k, X, 'the model\'s body less %s (what goes)' % key, less(X, b, t))
    show(k, X, '%s less the model\'s body (what comes)' % key, less(X, t, b))


def levels(k, body, up):
    out = {}
    for f in body.faces:
        if f.geometry.surfaceType != ST.PlaneSurfaceType:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); n = k.wv(nv); c = dot(n, up)
        if abs(abs(c) - 1) > 1e-4:
            continue
        p = k.W(f.pointOnFace); key = (round(dot(p, up), 3), 'up' if c > 0 else 'down')
        out[key] = out.get(key, 0.0) + f.area * 100
    return out


def st_check(k, X, part, key, names, ref='REF_F_outer'):
    H = S30['HOLES']; M10 = L['old']('m10')
    b = X.body(part); t = k.c[key]
    print('%s: the model\'s body %.3f mm3, lumps %d, faces %d | %s %.3f mm3, lumps %d, faces %d' % (
        part, b.volume * 1000.0, b.lumps.count, b.faces.count, key, X.vol(t), t.lumps.count, t.faces.count))
    show(k, X, 'what goes', less(X, b, t)); show(k, X, 'what comes', less(X, t, b))
    R = X.body(ref)
    for lab, body in (('the model\'s body', b), (key, t)):
        o = X.tbm.copy(body); X.dif(o, X.tbm.copy(R))
        print('   outside the cloth reference, %s: %.3f mm3 in %d lumps' % (lab, X.vol(o) if o.faces.count else 0.0, o.lumps.count if o.faces.count else 0))
    res = []
    for body in (t, b):
        res.append([(round(f.area * 100.0, 4), tuple(k.r2(k.W(f.pointOnFace), 1))) for f in body.faces if f.area * 100.0 < 0.3])
    was = set(q[1] for q in res[1])
    print('   faces under 0.3 mm2: %s %d, the model\'s body %d; not at a place of the model\'s: %s' % (key, len(res[0]), len(res[1]), [q for q in res[0] if q[1] not in was][:20]))
    for nm in names:
        p, M, F, r, d = H[nm]
        o = k.unit(tuple(F[i] - M[i] for i in range(3)))
        rows = []
        for f in t.faces:
            g = f.geometry; pw = k.W(f.pointOnFace)
            dd = [pw[i] - M[i] for i in range(3)]; tt = dot(dd, o); off = math.sqrt(max(dot(dd, dd) - tt * tt, 0.0))
            if off > r + 0.3 or tt < -1.0 or tt > math.sqrt(dot([F[i] - M[i] for i in range(3)], [F[i] - M[i] for i in range(3)])) + d + 0.5:
                continue
            ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); n = k.wv(nv)
            if g.surfaceType == ST.CylinderSurfaceType:
                ts = sorted(round(dot([k.W(e.geometry.center)[i] - M[i] for i in range(3)], o), 3) for e in f.edges if e.geometry.curveType in CIRC)
                rows.append('cylinder r %.4f, circles at %s from the mouth, %.3f mm2' % (g.radius * 10.0, ts, f.area * 100.0))
            elif g.surfaceType == ST.PlaneSurfaceType:
                rows.append('plane at %.3f from the mouth, normal . inward %.4f, %.3f mm2' % (tt, dot(n, o), f.area * 100.0))
            else:
                rows.append('surface type %d at %.3f from the mouth, %.3f mm2' % (g.surfaceType, tt, f.area * 100.0))
        print('   %-7s faces on its axis in %s: %s' % (nm, key, sorted(rows)))
    up = M10['up_dir'](k, part); lh = M10['PRINT'][part][3]
    a = levels(k, t, up); c = levels(k, b, up); base = None
    print('   level faces (square to the print\'s upright; %s) that differ (height, looks, off the grid of %.2f, mm2 %s / the model\'s):' % (M10['PRINT'][part][0], lh, key))
    n = 0
    for q in sorted(set(a) | set(c)):
        na = a.get(q, 0.0); nc = c.get(q, 0.0)
        if abs(na - nc) < 0.005:
            continue
        w = [up[i] * q[0] for i in range(3)]; h = M10['height'](k, part, w); off = h - round(h / lh) * lh; n += 1
        print('      height %8.3f %-4s off %+.3f   %9.3f / %9.3f' % (h, q[1], off, na, nc))
    if not n:
        print('      none')


def _main(what, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'build': st_build, 'check': st_check}[what](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(what, tag='', s30=None, **kw):
    S30.update(L['checked']('s30_holes.py', s30))
    L['out']('s31_%s%s.txt' % (what, ('_' + tag) if tag else ''), _main, what, **kw)
# END
