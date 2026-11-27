# Section outlines for pictures (READ-ONLY), after ../model-v70/p65_section.py. Each body (a model body by name, or 'c:<key>'
# for a temporary body kept in k.c) is cropped to a world box, cut by a world plane (TemporaryBRepManager.planeIntersection),
# and its cut edges stroked to polylines in the plane's own frame (u along 'uax', v = normal x u), in mm, rounded to 0.01.
# Written to d23_<tag>.json and printed in one line for drawing outside Fusion (d24_draw.py).
# Run: runpy.run_path(D + 'd23_section.py')['main'](tag, origin, normal, uax, names, box)
import runpy, json
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
L = runpy.run_path(D + 'v80_lib.py')


def thin(row):
    out = []
    for p in row:
        if out and abs(p[0] - out[-1][0]) < 0.005 and abs(p[1] - out[-1][1]) < 0.005:
            continue
        if len(out) >= 2:
            a = out[-2]; b = out[-1]
            cr = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
            if abs(cr) < 0.0015 and (p[0] - b[0]) * (b[0] - a[0]) + (p[1] - b[1]) * (b[1] - a[1]) > 0:
                out[-1] = p; continue
        out.append(p)
    return out


def _main(tag, origin, normal, uax, names, box):
    k = L['load'](); X = k.K(); k.budget(70)
    n = k.unit(normal); u = k.unit(uax); v = (n[1] * u[2] - n[2] * u[1], n[2] * u[0] - n[0] * u[2], n[0] * u[1] - n[1] * u[0])
    pl = adsk.core.Plane.create(k.Wp(*origin), k.dv(n))
    out = {'tag': tag, 'origin': origin, 'normal': n, 'u': u, 'v': v, 'box': box, 'bodies': {}}
    for nm in names:
        src = k.c.get(nm[2:]) if nm.startswith('c:') else X.body(nm)
        if src is None:
            continue
        t = X.tbm.copy(src); c = X.wbox(*box)
        if not t.boundingBox.intersects(c.boundingBox):
            continue
        X.sec(t, c)
        if not t.faces.count:
            continue
        try:
            w = X.tbm.planeIntersection(t, pl)
        except Exception as e:
            out['bodies'][nm] = 'failed: %s' % e; continue
        if w is None:
            continue
        lines = []
        for e in w.edges:
            ev = e.evaluator; ok, a, b = ev.getParameterExtents()
            ok, pts = ev.getStrokes(a, b, 0.003)
            row = []
            for p in pts:
                q = k.W(p); d = (q[0] - origin[0], q[1] - origin[1], q[2] - origin[2])
                row.append([round(sum(d[i] * u[i] for i in range(3)), 2), round(sum(d[i] * v[i] for i in range(3)), 2)])
            row = thin(row)
            if len(row) > 1:
                lines.append(row)
        if lines:
            out['bodies'][nm] = lines
    json.dump(out, open(D + 'd23_%s.json' % tag, 'w'))
    print('JSON ' + json.dumps(out, separators=(',', ':')))


def main(tag, origin, normal, uax, names, box):
    L['out']('d23_%s.txt' % tag, _main, tag, origin, normal, uax, names, box)
# END
