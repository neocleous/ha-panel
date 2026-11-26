# Block 3: the grommet's new flange (Daniel's 1a: x +-15.6, z 9.9 to 33.9, R2), grown from version 69's flange so that its two
# curved faces stay the same surfaces. CHANGES THE DOCUMENT ONLY THROUGH A TEMPORARY BODY 'TMP_flange', deleted at the end:
#   1. a copy of GROMMET_usbc_F as a hidden body;
#   2. Delete Face (healing) of every face but the flange's ten: the opening, sleeve, lugs, pegs, recess go;
#   3. Delete Face of the four corner rounds (sharp corners);
#   4. Offset Face: bottom 1.3 down, top 0.8 up, each side 0.5 out;
#   5. a temporary copy cut to the new outline with R2 corners -> k.c['b3_flange'];
#   6. the body deleted.
# Run: runpy.run_path(D + 'p32_flange.py')['main']()  -> p32_flange.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
XH, Z0, Z1, R = 15.6, 9.9, 33.9, 2.0


def classify(k, b):
    keep = {}; other = []
    for f in b.faces:
        g = f.geometry; c = k.W(f.centroid); a = f.area * 100.0
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); n = k.wv(nv)
        t = g.surfaceType
        if t == 7 and a > 250 and n[1] < -0.9:
            keep['front'] = f
        elif t == 7 and a > 150 and n[1] > 0.9 and c[1] < -84.0:
            keep['back'] = f
        elif t == 0 and abs(n[2]) > 0.99 and abs(c[2] - 11.2) < 0.05 and c[1] < -84.4:
            keep['bottom'] = f
        elif t == 0 and abs(n[2]) > 0.99 and abs(c[2] - 33.1) < 0.05:
            keep['top'] = f
        elif t == 0 and abs(n[0]) > 0.99 and abs(abs(c[0]) - 15.1) < 0.05:
            keep['side_%s' % ('p' if c[0] > 0 else 'm')] = f
        elif t == 1 and abs(g.radius * 10.0 - 2.0) < 0.01 and abs(abs(c[0]) - 14.37) < 0.2:
            keep['corner_%s%s' % ('p' if c[0] > 0 else 'm', 't' if c[2] > 22 else 'b')] = f
        else:
            other.append(f)
    return keep, other


def oc(items):
    col = adsk.core.ObjectCollection.create()
    for f in items:
        col.add(f)
    return col


def _main():
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    for b in [b for b in X.root.bRepBodies if b.name.startswith('TMP_')]:
        b.deleteMe()
    src = X.body('GROMMET_usbc_F')
    body = X.add(X.tbm.copy(src), 'TMP_flange', like=src, show=False)
    feats = X.root.features
    keep, other = classify(k, body)
    print('kept', sorted(keep), 'others', len(other))
    if len(keep) != 10:
        raise RuntimeError('flange faces found: %s' % sorted(keep))
    v0 = body.volume * 1000.0
    df = feats.deleteFaceFeatures.add(oc(other))
    body = X.body('TMP_flange')
    print('after delete of %d faces: faces %d, solid %s, volume %.3f -> %.3f' % (len(other), body.faces.count, body.isSolid, v0, body.volume * 1000.0))
    keep, other = classify(k, body)
    corners = [keep[n] for n in sorted(keep) if n.startswith('corner')]
    feats.deleteFaceFeatures.add(oc(corners))
    body = X.body('TMP_flange')
    keep, other = classify(k, body)
    print('after corners: faces %d, kept %s, others %d, volume %.3f' % (body.faces.count, sorted(keep), len(other), body.volume * 1000.0))
    for name, dist in (('bottom', 1.3), ('top', 0.8), ('side_p', 0.5), ('side_m', 0.5)):
        keep, other = classify(k, body)
        f = keep[name] if name in keep else None
        if f is None:   # after a move the classifier's z test no longer matches: find the plane by its normal and extreme
            cand = [g for g in body.faces if g.geometry.surfaceType == 0]
            sel = {'bottom': lambda g: -k.W(g.centroid)[2], 'top': lambda g: k.W(g.centroid)[2],
                   'side_p': lambda g: k.W(g.centroid)[0], 'side_m': lambda g: -k.W(g.centroid)[0]}[name]
            f = max(cand, key=sel)
        inp = feats.offsetFacesFeatures.createInput([f], adsk.core.ValueInput.createByReal(dist / 10.0))
        feats.offsetFacesFeatures.add(inp)
        body = X.body('TMP_flange')
        bb = k.wbb(X, body)
        print('offset %-7s %.1f: box %s volume %.3f' % (name, dist, bb, body.volume * 1000.0))
    t = X.tbm.copy(body)
    # the outline with R2 corners, as a prism along y
    o = X.wbox(-XH + R, XH - R, -90, -80, Z0, Z1)
    X.uni(o, X.wbox(-XH, XH, -90, -80, Z0 + R, Z1 - R))
    for sx in (-1, 1):
        for zz in (Z0 + R, Z1 - R):
            X.uni(o, X.cyl((sx * (XH - R), -90.0, zz), (sx * (XH - R), -80.0, zz), R))
    X.sec(t, o)
    k.c['b3_flange'] = t
    print('flange: volume %.3f, faces %d, lumps %d, box %s' % (X.vol(t), t.faces.count, t.lumps.count,
                                                                [round(v, 3) for v in k.wbb(X, X.add(X.tbm.copy(t), 'TMP_flange_view', show=False))]))
    for b in [b for b in X.root.bRepBodies if b.name.startswith('TMP_')]:
        b.deleteMe()
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p32_flange.txt', _main)
