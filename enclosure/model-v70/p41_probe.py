# Block 4, before the block (architect log 2026-11-24-d, section 6, point 3): the base plate's cradle bosses beside the door's
# seats and the grommet's ears, read with needles. READ-ONLY (temporary bodies only, none added to the model).
#   every face of FLOOR_PLATE in x -13..13, y -80..-66, z 2.4..14 with its surface type (0 plane, 1 cylinder, 2 cone, 3 sphere,
#   4 torus, 5 ellipse cylinder, ...); then needles along +y at a grid of (x, z): where the plate begins, coming from the door
# Run: runpy.run_path(D + 'p41_probe.py')['main']()  -> p41_probe.txt
import runpy
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def _main():
    k = L['load'](); X = k.K(); k.budget(70)
    print(L['stamp'](), 'before', X.state())
    P = X.body('FLOOR_PLATE')
    box = (-13.0, 13.0, -80.0, -66.0, 2.4, 14.0)
    rows = []
    for f in P.faces:
        ws = [k.W(v.geometry) for v in f.vertices]
        p = k.W(f.pointOnFace)
        if not (box[0] <= p[0] <= box[1] and box[2] <= p[1] <= box[3] and box[4] <= p[2] <= box[5]):
            continue
        ext = [round(fn(w[i] for w in ws), 2) for i in range(3) for fn in (min, max)] if ws else None
        g = f.geometry
        extra = ''
        if g.surfaceType == 1:
            extra = 'r %.3f origin %s axis %s' % (g.radius * 10, k.r2(k.W(g.origin)), k.r2(k.wv(g.axis), 3))
        elif g.surfaceType == 2:
            extra = 'cone r %.3f half-angle %.1f origin %s axis %s' % (g.radius * 10, g.halfAngle * 57.2958, k.r2(k.W(g.origin)), k.r2(k.wv(g.axis), 3))
        elif g.surfaceType == 0:
            ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
            extra = 'normal %s' % k.r2(k.wv(nv), 3)
        rows.append((g.surfaceType, round(f.area * 100, 2), k.r2(p), ext, extra))
    for r in sorted(rows, key=lambda q: (q[2][1], q[2][0])):
        print('  type %d area %7.2f at %s ext %s %s' % r)
    parts = [X.tbm.copy(P)]
    print('needles along +y from y -80 to -68: the plate starts at')
    for z in (4.0, 5.0, 5.6, 6.0, 6.83, 8.0, 9.0, 10.0, 10.5, 11.0, 11.27, 12.0, 12.4):
        line = []
        for x in (-6.5, -5.5, -4.5, -4.16, -3.5, -2.5, -1.5, 0.0, 2.5, 4.0, 4.5, 4.81, 5.5, 6.5, 7.5, 8.12, 9.0, 10.0, 10.5):
            s = k.needle_t(X, parts, (x, -80.0, z), (x, -68.0, z), 0.02)
            line.append('%+.2f:%s' % (x, ('%.2f' % (-80.0 + s[0][0])) if s else '-'))
        print('  z %5.2f  %s' % (z, '  '.join(line)))
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p41_probe.txt', _main)
