# Section outlines for pictures (READ-ONLY). Each body (a model body by name, or 'c:<key>' for a temporary body kept in k.c) is
# cropped to a world box, cut by a world plane with TemporaryBRepManager.planeIntersection, and its edges stroked to polylines in
# the plane's own 2D frame (u along 'uax', v = normal x u), in mm. Written to p65_<tag>.json for drawing in the container.
# Run: runpy.run_path(D + 'p65_section.py')['main'](tag, origin, normal, uax, names, box)
import runpy, json
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def _main(tag, origin, normal, uax, names, box):
    k = L['load'](); X = k.K(); k.budget(75)
    print(L['stamp'](), 'before', X.state())
    n = k.unit(normal); u = k.unit(uax); v = (n[1] * u[2] - n[2] * u[1], n[2] * u[0] - n[0] * u[2], n[0] * u[1] - n[1] * u[0])
    pl = adsk.core.Plane.create(k.Wp(*origin), k.dv(n))
    out = {'tag': tag, 'origin': origin, 'normal': n, 'u': u, 'v': v, 'box': box, 'bodies': {}}
    for nm in names:
        src = k.c[nm[2:]] if nm.startswith('c:') else X.body(nm)
        if src is None:
            print('no body', nm); continue
        t = X.tbm.copy(src); c = X.wbox(*box)
        if not t.boundingBox.intersects(c.boundingBox):
            continue
        X.sec(t, c)
        if not t.faces.count:
            continue
        try:
            w = X.tbm.planeIntersection(t, pl)
        except Exception as e:
            print('%s: %s' % (nm, e)); continue
        if w is None:
            continue
        lines = []
        for e in w.edges:
            ev = e.evaluator; ok, a, b = ev.getParameterExtents()
            ok, pts = ev.getStrokes(a, b, 0.002)
            row = []
            for p in pts:
                q = k.W(p); d = (q[0] - origin[0], q[1] - origin[1], q[2] - origin[2])
                row.append((round(sum(d[i] * u[i] for i in range(3)), 3), round(sum(d[i] * v[i] for i in range(3)), 3)))
            lines.append(row)
        out['bodies'][nm] = lines
        print('%-24s %d edges' % (nm, len(lines)))
    json.dump(out, open(D + 'p65_%s.json' % tag, 'w'))
    print(L['stamp'](), 'after', X.state())


def main(tag, origin, normal, uax, names, box):
    L['out']('p65_%s.txt' % tag, _main, tag, origin, normal, uax, names, box)
