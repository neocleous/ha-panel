# change3/c3_shell.py - the FDM fix pass (2026-11-18): the shell (HOUSING_F_front), built on a temporary copy k.c['shell_wip'].
# Exec'd into sys.modules['c3'] after c3_lib.py and c3_fix.py. k = c3k (v5f_k_lib.py). World mm.
# skin_tool() is the only function that touches the document: it makes and deletes one AUD_ body (INNER_E hollowed, as the TOOL_inner_skin_* tools were made).
import adsk.core, adsk.fusion, sys, math
k = sys.modules['c3k']
G = k.c.setdefault('g22', {})
CYL = adsk.core.SurfaceTypes.CylinderSurfaceType
LIPD = k.unit((0.0, 0.957, -0.289))                     # the direction TOOL_lip_end was swept along (v5f_d10d_lip_end_loft.py)


def skin_tool(X, t):                                    # INNER_E hollowed with inside thickness t (mm): a temporary copy, cached
    key = ('skin', t)
    if key in k.c:
        return k.c[key]
    nm = 'AUD_inner_skin'
    old = X.body(nm)
    if old is not None:
        old.deleteMe()
    b = X.root.bRepBodies.add(X.tbm.copy(X.body('INNER_E'))); b.name = nm; b.isLightBulbOn = False
    coll = adsk.core.ObjectCollection.create(); coll.add(b)
    si = X.root.features.shellFeatures.createInput(coll, False)
    si.insideThickness = adsk.core.ValueInput.createByReal(t / 10.0)
    X.root.features.shellFeatures.add(si)
    b = X.body(nm)
    k.c[key] = X.tbm.copy(b)
    b.deleteMe()
    return k.c[key]


def lip_axes(X, sh):                                    # the ten magnet pads (cylinders r 6.0) and the key lanes (r 4.0) that cross the lip: axis lines
    pads = {}; lanes = {}
    zone = X.wbox(-85.0, 85.0, -66.0, -52.0, 0.0, 165.0).boundingBox
    for f in sh.faces:
        g = f.geometry
        if g.surfaceType != CYL or not zone.intersects(f.boundingBox):
            continue
        r = g.radius * 10.0
        if abs(r - 6.0) > 0.005 and abs(r - 4.0) > 0.005:
            continue
        p = k.W(f.pointOnFace)
        if not (-66.0 <= p[1] <= -52.0):
            continue
        o = k.W(g.origin); a = k.unit(k.wv(g.axis))
        if a[1] < 0:
            a = tuple(-v for v in a)
        s = -o[1] / a[1] - 55.0 / a[1]                  # the axis point at y = -55
        q = (round(o[0] + a[0] * s, 2), -55.0, round(o[2] + a[2] * s, 2))
        d = pads if abs(r - 6.0) < 0.005 else lanes
        d[(q, tuple(round(v, 3) for v in a))] = (tuple(o[i] + a[i] * s for i in range(3)), a)
    return list(pads.values()), list(lanes.values())


def lip_layer(X, t0=2.1, t1=2.9):                       # the layer t0 .. t1 inside INNER_E over the lip's band (the lip is 0.9 .. 2.1)
    sh = X.body('HOUSING_F_front')
    A = X.tbm.copy(skin_tool(X, t1)); X.dif(A, X.tbm.copy(X.body('TOOL_inner_skin_2p1')) if abs(t0 - 2.1) < 1e-9 else X.tbm.copy(skin_tool(X, t0)))
    X.sec(A, X.wbox(-150.0, 150.0, -63.5, -53.5, 6.5, 250.0))              # behind the door frame's front faces (y -53.5), above the lip's lower ends
    out = {'layer in the box': round(X.vol(A), 3)}
    le = X.body('TOOL_lip_end')
    X.dif(A, X.tbm.copy(le))                                                # the opening: the lip's end face is this tool's side, swept along LIPD
    t = X.tbm.copy(le); X.move(t, LIPD[0], LIPD[1], LIPD[2]); X.dif(A, t)
    out['outside the opening'] = round(X.vol(A), 3)
    pads, lanes = lip_axes(X, sh)
    for (q, a) in pads:                                                     # the pads keep their tops and pockets: the layer stops at their sides
        X.dif(A, X.cyl(k.along(q, a, -8.0), k.along(q, a, 8.0), 6.0))
    for (q, a) in lanes:                                                    # the display screws' key lanes stay open
        c = X.cyl(k.along(q, a, -30.0), k.along(q, a, 30.0), 4.0)
        X.dif(A, c)
    out['pads'] = len(pads); out['lanes'] = len(lanes); out['layer'] = round(X.vol(A), 3); out['lumps'] = A.lumps.count
    k.c['lip_layer'] = A
    return out


def shell_start(X):
    k.c['shell_wip'] = X.cp(X.body('HOUSING_F_front'))
    return round(X.vol(k.c['shell_wip']), 3)


def shell_add(X, tb):
    b = k.c['shell_wip']; v0 = X.vol(b); X.uni(b, X.tbm.copy(tb))
    return round(X.vol(b) - v0, 3), b.lumps.count, b.faces.count


def shell_cut(X, tb):
    b = k.c['shell_wip']; v0 = X.vol(b); X.dif(b, X.tbm.copy(tb))
    return round(X.vol(b) - v0, 3), b.lumps.count, b.faces.count
