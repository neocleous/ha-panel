# Block 2: the faces of a body (or of a body's region) with their kind, normal, area, centre and world bounds, for laying out
# a change. READ-ONLY. Run: runpy.run_path(D + 'p20_faces.py')['dump'](tag, name, box=None, minarea=0.05)
import runpy, json, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
ST = {0: 'plane', 1: 'cyl', 2: 'cone', 3: 'sphere', 4: 'torus', 5: 'ellcyl', 6: 'ellcone', 7: 'nurbs'}


def _fbox(k, f):
    xs = []; ys = []; zs = []
    for v in f.vertices:
        w = k.W(v.geometry); xs.append(w[0]); ys.append(w[1]); zs.append(w[2])
    bb = f.boundingBox
    for p in (bb.minPoint, bb.maxPoint):
        pass
    return [round(min(xs), 2), round(max(xs), 2), round(min(ys), 2), round(max(ys), 2), round(min(zs), 2), round(max(zs), 2)] if xs else None


def dump(tag, name, box=None, minarea=0.05):
    k = L['load']()
    X = k.K()
    b = X.body(name)
    rows = []
    for i, f in enumerate(b.faces):
        a = f.area * 100.0
        if a < minarea:
            continue
        g = f.geometry
        c = k.W(f.centroid)
        if box and not (box[0] <= c[0] <= box[1] and box[2] <= c[1] <= box[3] and box[4] <= c[2] <= box[5]):
            continue
        r = {'i': i, 'kind': ST.get(g.surfaceType, str(g.surfaceType)), 'area': round(a, 2), 'c': [round(v, 2) for v in c], 'vbox': _fbox(k, f)}
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
        r['n'] = [round(v, 3) for v in k.wv(nv)]
        if g.surfaceType == 1:
            r['r'] = round(g.radius * 10.0, 3); r['axis'] = [round(v, 3) for v in k.wv(g.axis)]; r['o'] = [round(v, 2) for v in k.W(g.origin)]
        rows.append(r)
    L['jdump']('p20_faces_%s.json' % tag, {'body': name, 'box': box, 'faces': rows})
    print('%s: %s, %d faces listed' % (tag, name, len(rows)))
    for r in rows:
        print('%3d %-6s %7.2f n%s c%s vbox%s%s' % (r['i'], r['kind'], r['area'], r['n'], r['c'], r['vbox'], (' r %.3f axis %s' % (r['r'], r['axis'])) if 'r' in r else ''))
