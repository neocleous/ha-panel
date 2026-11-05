# rev F cap block c1e2 (2026-11-05): R0.3 on the groove's outer top edge of HOUSING_F_front.
#   c1e's edge filter ("other face non-planar, normal outward + up") also took the groove's INNER top edge (its wall leans
#   with the outer wall), so both the ledge's outer edge and the groove's inner top edge got R0.8 (the inner one is kept as a
#   lead-in for the spline roller: 0.54 setback on the 112° corner, ≈ 0.75 of the 1.29 land stays flat). Here the edge the
#   cloth is pulled over into the groove – the acute (≈ 68°) outer top edge – gets R0.3 (setback ≈ 0.44, ≈ 0.3 of the strip
#   stays flat). Selection: edges of the planar z-175.3 faces (y < −22.4) whose other face is non-planar with an inward /
#   downward normal and whose midpoint lies inside TOOL_cap_off4p1 (d < 4.1: the groove's outer wall at d 1.9, not the
#   flange's inner face at d 5.9).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
V_FRONT = 235.6426


def groove_outer_edges(X, b):
    coll = adsk.core.ObjectCollection.create(); info = []
    band = X.body('TOOL_cap_off4p1')
    for f in b.faces:
        if not f.geometry.objectType.endswith('Plane'):
            continue
        p = f.pointOnFace; ok, n = f.evaluator.getNormalAtPoint(p)
        if (n.y * S + n.z * C) < 0.999 or abs(wz(p) - 175.3) > 0.01 or wy(p) > -22.4:
            continue
        for e in f.edges:
            o = [g for g in e.faces if g != f]
            if not o or o[0].geometry.objectType.endswith('Plane'):
                continue
            ok, t0, t1 = e.evaluator.getParameterExtents(); ok, m = e.evaluator.getPointAtParameter((t0 + t1) / 2)
            ok, no = o[0].evaluator.getNormalAtPoint(m); nw = nw_of(no)
            ox, oy = m.x * 10 - XC, wy(m) + 35.0; L = math.hypot(ox, oy) or 1.0
            if (nw[0] * ox + nw[1] * oy) / L < -0.2 and nw[2] < -0.05 and band.pointContainment(m) in INS:
                coll.add(e); info.append([round(m.x * 10 - XC, 1), round(wy(m), 1)])
    return coll, info


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        F = X.body('HOUSING_F_front')
        out['guard'] = round(F.volume, 4)
        if abs(F.volume - V_FRONT) > 0.001:
            raise RuntimeError('volume guard: front %.4f' % F.volume)
        coll, info = groove_outer_edges(X, F)
        out['edges'] = {'n': coll.count, 'mid_pts': info}
        fi = X.feats.filletFeatures.createInput()
        fi.edgeSetInputs.addConstantRadiusEdgeSet(coll, VI(0.03), True)
        X.feats.filletFeatures.add(fi)
        F = X.body('HOUSING_F_front')
        out['after'] = {'front': round(F.volume, 4), 'lumps': F.lumps.count, 'faces': F.faces.count,
                        'dupes': [b.name for b in X.comp.bRepBodies if b.name.startswith(('HOUSING_F_front (', 'HOUSING_F_cap ('))]}
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_c1e2_groove_edge', 'run', out)
    print(json.dumps(out, separators=(',', ':')))
