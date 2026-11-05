# rev F cap block c1e4 (2026-11-05): fillets on the rebuilt front shell (c1d2) with explicit edge classes, + checks.
#   Edges of the planar z-175.3 faces whose midpoint lies behind the joint (y < −22.55; c1e2 had also caught a concave edge
#   in front of it), other face non-planar:
#     A  ledge outer edge (cloth turns over it): other face's normal outward + up, midpoint inside TOOL_cap_off1p9 → R0.8
#     B  groove outer top edge (cloth pulled into the groove, ≈ 68° corner): normal inward + down, inside TOOL_cap_off4p1 → R0.3
#     C  groove inner top edge (spline lead-in, cut cloth end): normal outward + up, outside TOOL_cap_off1p9, inside
#        TOOL_cap_off5 → R0.3
#   (c1e had given C R0.8 by accident – that version is HOUSING_F_front_c1v1, hidden.) One fillet feature with three edge
#   sets, fallback one feature per set. Checks: volumes, lumps, duplicates, intersections, post tops (the profile itself is
#   read from c1f's sections; stations() kept for a separate run).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
V_FRONT = 235.6726
POSTS = {'FL': (58.4, -27.0), 'FR': (-58.4, -27.0), 'BL': (28.0, -38.1), 'BR': (-28.0, -38.1)}
NAMES = ('HOUSING_F_front', 'HOUSING_F_cap', 'REF_F_outer')


def classify(X, b):
    sets = {'A': adsk.core.ObjectCollection.create(), 'B': adsk.core.ObjectCollection.create(),
            'C': adsk.core.ObjectCollection.create()}
    info = {'A': [], 'B': [], 'C': []}
    t19, t41, t50 = X.body('TOOL_cap_off1p9'), X.body('TOOL_cap_off4p1'), X.body('TOOL_cap_off5')
    for f in b.faces:
        if not f.geometry.objectType.endswith('Plane'):
            continue
        p = f.pointOnFace; ok, n = f.evaluator.getNormalAtPoint(p)
        if (n.y * S + n.z * C) < 0.999 or abs(wz(p) - 175.3) > 0.01:
            continue
        for e in f.edges:
            o = [g for g in e.faces if g != f]
            if not o or o[0].geometry.objectType.endswith('Plane'):
                continue
            ok, t0, t1 = e.evaluator.getParameterExtents(); ok, m = e.evaluator.getPointAtParameter((t0 + t1) / 2)
            if wy(m) > -22.55:
                continue
            ok, no = o[0].evaluator.getNormalAtPoint(m); nw = nw_of(no)
            ox, oy = m.x * 10 - XC, wy(m) + 35.0; L = math.hypot(ox, oy) or 1.0
            radial = (nw[0] * ox + nw[1] * oy) / L
            in19 = t19.pointContainment(m) in INS
            k = None
            if radial > 0.2 and nw[2] > 0.05:
                if in19:
                    k = 'A'
                elif t50.pointContainment(m) in INS:
                    k = 'C'
            elif radial < -0.2 and nw[2] < -0.05 and t41.pointContainment(m) in INS:
                k = 'B'
            if k:
                sets[k].add(e); info[k].append([round(m.x * 10 - XC, 1), round(wy(m), 1)])
    return sets, info


def stations(X):
    S_ = {}
    for (lab, o, d) in (('x0_back', (0.0, -35.0), (0, -1, 0)), ('x28_back', (28.0, -35.0), (0, -1, 0)),
                        ('y-30_side+x', (0.0, -30.0), (1, 0, 0)), ('y-30_side-x', (0.0, -30.0), (-1, 0, 0))):
        rows = []
        for z in (171.0, 172.0, 173.0, 174.0, 174.4, 175.0, 175.55, 176.0, 177.0):
            hs = [h for h in ray_hits(X, (XC + o[0], o[1], z), d, NAMES)]
            rows.append([z] + [[h[1][9:12], round(h[2] if d[0] else h[3], 2)] for h in hs[:8]])
        S_[lab] = rows
    return S_


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        F, Cp, D = X.body('HOUSING_F_front'), X.body('HOUSING_F_cap'), X.body('HOUSING_F_door')
        out['guard'] = round(F.volume, 4)
        if abs(F.volume - V_FRONT) > 0.001:
            raise RuntimeError('volume guard: front %.4f' % F.volume)
        sets, info = classify(X, F)
        out['edges'] = {k: {'n': sets[k].count, 'mid': info[k]} for k in sets}
        R = {'A': 0.08, 'B': 0.03, 'C': 0.03}
        try:
            fi = X.feats.filletFeatures.createInput()
            for k in ('A', 'B', 'C'):
                if sets[k].count:
                    fi.edgeSetInputs.addConstantRadiusEdgeSet(sets[k], VI(R[k]), True)
            X.feats.filletFeatures.add(fi); out['fillet'] = 'one feature'
        except Exception as e:
            out['fillet_one'] = 'FAILED ' + str(e)[:80]; done = []
            for k in ('A', 'B', 'C'):
                F = X.body('HOUSING_F_front'); sets, info = classify(X, F)
                if not sets[k].count:
                    continue
                try:
                    fi = X.feats.filletFeatures.createInput()
                    fi.edgeSetInputs.addConstantRadiusEdgeSet(sets[k], VI(R[k]), True)
                    X.feats.filletFeatures.add(fi); done.append(k)
                except Exception as e2:
                    out['fillet_' + k] = 'FAILED ' + str(e2)[:80]
            out['fillet'] = done
        F = X.body('HOUSING_F_front')
        out['after'] = {'front': round(F.volume, 4), 'cap': round(Cp.volume, 4), 'door': round(D.volume, 4),
                        'lumps': [F.lumps.count, Cp.lumps.count], 'faces_front': F.faces.count,
                        'dupes': [b.name for b in X.comp.bRepBodies if b.name.startswith(('HOUSING_F_front (', 'HOUSING_F_cap ('))]}
        top = lambda: X.wbox(-250, 250, -250, 250, 150.0, 260.0)
        FT = tb_copy(X, 'HOUSING_F_front'); inter(X, FT, top())
        DT = tb_copy(X, 'HOUSING_F_door'); inter(X, DT, top())
        out['x'] = {'front_cap': vol_x(X, FT, tb_copy(X, 'HOUSING_F_cap')), 'front_door': vol_x(X, FT, DT),
                    'cap_door': vol_x(X, tb_copy(X, 'HOUSING_F_cap'), DT)}
        pt = {}
        for k, (xr, y) in POSTS.items():
            hf = ray_hits(X, (XC + xr + 3.0, y, 172.0), (0, 0, 1), ('HOUSING_F_front',))
            hc = ray_hits(X, (XC + xr + 3.0, y, 172.0), (0, 0, 1), ('HOUSING_F_cap',))
            pt[k] = {'post_top_z': [round(h[4], 3) for h in hf[:2]], 'cap_first_z': round(hc[0][4], 3) if hc else None}
        out['post_tops'] = pt
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_c1e4_fillets_checks', 'run', out)
    print(json.dumps(out, separators=(',', ':'))[:9000])
