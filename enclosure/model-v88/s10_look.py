# Read-only looks used by every block of the pass: faces of a body in a world box (planes, cylinders, cones, with their circular
# edges), needles through bodies, what one body has that another lacks (by y slabs), and world boxes.
# READ-ONLY: temporary bodies only; nothing is created in the document.
# World mm: x + = viewer's left, y + toward the screen, z up.
# Run: L.checked('s10_look.py', sha)['main'](what, tag, **kw)  -> s10_<what>_<tag>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/screw_margins_v88/'
L = runpy.run_path(D + 's00_lib.py')
ST = adsk.core.SurfaceTypes
PLN, CYL, CON = ST.PlaneSurfaceType, ST.CylinderSurfaceType, ST.ConeSurfaceType
CIRC = adsk.core.Curve3DTypes.Circle3DCurveType; ARC = adsk.core.Curve3DTypes.Arc3DCurveType


def facerows(k, body, box, amin=0.0, kinds='pcko'):
    """Rows for the faces of a body whose sample point lies in a world box (x0, x1, y0, y1, z0, z1)."""
    rows = []
    for f in body.faces:
        p = k.W(f.pointOnFace)
        if not (box[0] <= p[0] <= box[1] and box[2] <= p[1] <= box[3] and box[4] <= p[2] <= box[5]):
            continue
        ar = f.area * 100.0
        if ar < amin:
            continue
        g = f.geometry; t = g.surfaceType
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); n = k.wv(nv)
        ws = [k.W(v.geometry) for v in f.vertices]
        ext = [round(fn(w[i] for w in ws), 3) for i in range(3) for fn in (min, max)] if ws else None
        circ = []
        for e in f.edges:
            eg = e.geometry
            if eg.curveType in (CIRC, ARC):
                circ.append(('c' if eg.curveType == CIRC else 'a', k.r2(k.W(eg.center), 3), round(eg.radius * 10.0, 3)))
        if t == PLN and 'p' in kinds:
            rows.append(('plane', k.r2(n, 4), k.r2(p, 3), round(ar, 3), ext, circ))
        elif t == CYL and 'c' in kinds:
            o = k.W(g.origin); a = k.unit(k.wv(g.axis))
            tt = sum((p[i] - o[i]) * a[i] for i in range(3)); rad = [p[i] - (o[i] + tt * a[i]) for i in range(3)]
            kind = 'pin' if sum(rad[i] * n[i] for i in range(3)) > 0 else 'hole'
            rows.append(('cyl ' + kind, round(g.radius * 10.0, 4), k.r2(o, 3), k.r2(a, 4), round(ar, 3), ext, circ))
        elif t == CON and 'k' in kinds:
            o = k.W(g.origin); a = k.unit(k.wv(g.axis))
            rows.append(('cone', round(g.radius * 10.0, 4), round(math.degrees(g.halfAngle), 3), k.r2(o, 3), k.r2(a, 4), k.r2(n, 3), k.r2(p, 3), round(ar, 3), ext, circ))
        elif t not in (PLN, CYL, CON) and 'o' in kinds:
            rows.append(('other %d' % t, k.r2(n, 3), k.r2(p, 3), round(ar, 3), ext, circ))
    return rows


def st_faces(k, X, name, box, amin=0.0, kinds='pcko'):
    b = X.body(name)
    print('%s: %.3f mm3, %d faces; faces with their sample point in %s:' % (name, b.volume * 1000.0, b.faces.count, list(box)))
    for r in sorted(facerows(k, b, box, amin, kinds), key=lambda r: (r[0], str(r[1:3]))):
        print('  ', r)


def st_needles(k, X, names, lines, w=0.02):
    """Solid stretches (mm from the first point) of thin bars through named model bodies."""
    for lab, p0, p1 in lines:
        for n in names:
            st = k.needle(X, n, p0, p1, w)
            print('%-34s %-18s from %s to %s: solid %s' % (lab, n, k.r2(p0, 2), k.r2(p1, 2), st))


def st_diff(k, X, a, b, ys=None, box=None):
    """What body a has that body b lacks, and the other way: volumes, lumps, and (ys) the volume in slabs of y."""
    A = X.body(a); B = X.body(b)
    for lab, p, q in (('%s less %s' % (a, b), A, B), ('%s less %s' % (b, a), B, A)):
        t = X.tbm.copy(p); X.dif(t, X.tbm.copy(q))
        if box is not None:
            X.sec(t, X.wbox(*box))
        print('%s: %.4f mm3 in %d lumps: %s' % (lab, X.vol(t), t.lumps.count if t.faces.count else 0, X.lumps(t)[:20] if t.faces.count else []))
        if ys and t.faces.count:
            for i in range(len(ys) - 1):
                s = X.tbm.copy(t); bb = k.wbb(X, t)
                X.sec(s, X.wbox(bb[0] - 1, bb[1] + 1, ys[i], ys[i + 1], bb[4] - 1, bb[5] + 1))
                if s.faces.count and X.vol(s) > 1e-5:
                    print('   y %7.2f to %7.2f: %9.4f mm3, world box %s' % (ys[i], ys[i + 1], X.vol(s), k.wbb(X, s)))


def st_wbb(k, X, names):
    for n in names:
        b = X.body(n)
        print('%-22s %s' % (n, k.wbb(X, b) if b is not None else None))


def _main(what, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'faces': st_faces, 'needles': st_needles, 'diff': st_diff, 'wbb': st_wbb}[what](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(what, tag='', **kw):
    L['out']('s10_%s%s.txt' % (what, ('_' + tag) if tag else ''), _main, what, **kw)
# END
