# rev F audit-response d5h (2026-11-06): root fillets at the load-bearing roots only (audit finding 13, plan "13 load-bearing
#   roots only"). Concave edges found by geometry (height / distance from the axis) and checked concave by containment of a
#   points 0.03 either side along (n1 − n2) (both in the body = concave); one fillet feature per group, a failed group leaves its body as it is.
#   A  front: cradle floor bosses + web, root at the floor top z 2.5                       R0.8
#   B  front: the four Pi bosses, root at z 2.5 (R0.5: the nearest intake hole edge is 4.5 from the axis)   R0.5
#   C  CRADLE_5807: legs + web under the plate (z 14.5)                                    R0.8
#   D  CRADLE_5807: the two M2 posts on the plate (z 17.0 / 17.5)                          R0.5
#   E  MAIN_BRACKET: foot bosses under the tabs (z 8.6)                                    R0.8
#   F  door: boss / rib / wall junctions of the four M3 bosses (vertical edges, z 2.9–10.4) R0.5
#   Hidden copies: <name>_d5h0.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
F, D, CR, B_ = 'HOUSING_F_front', 'HOUSING_F_door', 'CRADLE_5807', 'MAIN_BRACKET'   # (not C: that is cos 12° in v5f_common)
EXPECT = {F: 233.5399, D: 47.2694, CR: 2.1709, B_: 5.3418}
PI = ((18.35, -5.5), (-39.65, -5.5), (18.35, -54.5), (-39.65, -54.5))
DB = ((19.0, -74.5), (-19.0, -77.0), (50.0, -67.0), (-50.0, -67.0))


def W(p):
    return (p.x * 10 - XC, wy(p), wz(p))


def edge_pts(e):
    ev = e.evaluator; ok, t0, t1 = ev.getParameterExtents()
    pts = []
    for t in (t0, (t0 + t1) / 2, t1):
        ok, p = ev.getPointAtParameter(t); pts.append(p)
    return pts


def concave(b, e):
    """concave iff both points p ± 0.03 mm along (n1 − n2) lie in the body (for a convex edge both lie outside; a mixed
    result means a normal came back flipped - skipped)."""
    if e.faces.count != 2:
        return False
    ev = e.evaluator; ok, t0, t1 = ev.getParameterExtents(); ok, p = ev.getPointAtParameter((t0 + t1) / 2)
    ns = []
    for f in e.faces:
        ok, n = f.evaluator.getNormalAtPoint(p)
        if not ok:
            return False
        ns.append(n)
    dx, dy, dz = ns[0].x - ns[1].x, ns[0].y - ns[1].y, ns[0].z - ns[1].z
    L = math.sqrt(dx * dx + dy * dy + dz * dz)
    if L < 0.2:
        return False
    k = 0.003 / L
    a_ = b.pointContainment(P3(p.x + dx * k, p.y + dy * k, p.z + dz * k)) in INS
    c_ = b.pointContainment(P3(p.x - dx * k, p.y - dy * k, p.z - dz * k)) in INS
    return a_ and c_


def pick(b, test):
    res = []
    for e in b.edges:
        try:
            ws = [W(p) for p in edge_pts(e)]
        except Exception:
            continue
        if test(ws) and concave(b, e):
            res.append(e)
    return res


def fillet(X, edges, R):
    coll = adsk.core.ObjectCollection.create()
    for e in edges:
        coll.add(e)
    fi = X.feats.filletFeatures.createInput()
    fi.edgeSetInputs.addConstantRadiusEdgeSet(coll, VI(R / 10.0), True)
    X.feats.filletFeatures.add(fi)


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard: %s %s (expected %s)' % (k, None if b is None else round(b.volume, 4), v))
            c0 = X.body(k + '_d5h0')
            if c0 is not None and abs(c0.volume - v) > 0.0005:
                raise RuntimeError('%s_d5h0 exists with another volume' % k)
        for k in EXPECT:
            if X.body(k + '_d5h0') is None:                     # (a first run that changed nothing left these copies)
                c = X.add(X.tbm.copy(X.body(k)), k + '_d5h0'); c.isLightBulbOn = False
        z_ = lambda ws, z, tol=0.02: all(abs(w[2] - z) < tol for w in ws)
        near = lambda ws, cx, cy, r: all(math.hypot(w[0] - cx, w[1] - cy) <= r for w in ws)
        groups = [
            ('A', F, 0.8, lambda ws: z_(ws, 2.5) and all(-6.0 <= w[0] <= 11.0 and -77.0 <= w[1] <= -68.0 for w in ws)),
            ('B', F, 0.5, lambda ws: z_(ws, 2.5) and any(near(ws, cx, cy, 4.0) for cx, cy in PI)),
            ('C', CR, 0.8, lambda ws: z_(ws, 14.5) and all(-6.0 <= w[0] <= 11.0 and -77.0 <= w[1] <= -68.0 for w in ws)),
            ('D', CR, 0.5, lambda ws: (z_(ws, 17.0) or z_(ws, 17.5)) and any(near(ws, cx, -81.16, 3.3) for cx in (-7.493, 7.747))),
            ('E', B_, 0.8, lambda ws: z_(ws, 8.6) and any(near(ws, s * 49.5, -58.0, 4.3) for s in (1, -1))),
            ('F', D, 0.5, lambda ws: all(2.85 < w[2] < 10.45 for w in ws) and max(w[2] for w in ws) - min(w[2] for w in ws) > 1.0 and
             any(all(math.hypot(w[0] - cx, w[1] - cy) < 9.0 for w in ws) and all(math.hypot(w[0] - cx, w[1] - cy) > 2.2 for w in ws)
                 for cx, cy in DB)),
        ]
        res = {}
        for g, name, R, test in groups:
            b = X.body(name); v0 = b.volume
            try:
                es = pick(b, test)
                info = {'n': len(es)}
                if not es:
                    info['note'] = 'no edges'; res[g] = info; continue
                info['mid'] = [[round(v, 2) for v in W(edge_pts(e)[1])] for e in es[:12]]
                try:
                    fillet(X, es, R); info['ok'] = True
                except Exception as ex:
                    info['ok'] = False; info['err'] = str(ex)[:120]; info['note'] = 'group failed, body unchanged'
                b = X.body(name)
                info['dv_mm3'] = round((b.volume - v0) * 1000, 3); info['lumps'] = b.lumps.count
            except Exception as ex:
                info = {'FAIL': str(ex)[:160]}
            res[g] = info
            log('v5f_d5h_root_fillets', 'group', {g: info, 't_s': round(time.time() - t0, 1)})
        out['groups'] = res
        out['cm3'] = {k: round(X.body(k).volume, 4) for k in EXPECT}
        out['lumps'] = {k: X.body(k).lumps.count for k in EXPECT}
        # checks: Pi seats vs PI5_F, bracket vs boxes, cradle vs front, door band vs front
        reg = None
        for (x, y) in PI:
            r_ = X.wcyl_z(XC + x, y, 4.6, 2.0, 8.2); reg = r_ if reg is None else X.union(reg, r_)
        s_ = tb_copy(X, F); inter(X, s_, reg)
        out['x'] = {'pi_boss_region_x_PI5_F': vol_x(X, s_, tb_copy(X, 'PI5_F')),
                    'bracket_x_SPKBOX_L': vol_x(X, tb_copy(X, B_), tb_copy(X, 'SPKBOX_L')),
                    'bracket_x_SPKBOX_R': vol_x(X, tb_copy(X, B_), tb_copy(X, 'SPKBOX_R')),
                    'cradle_x_front': vol_x(X, tb_copy(X, CR), tb_copy(X, F)),
                    'cradle_x_PD_5807_env': vol_x(X, tb_copy(X, CR), tb_copy(X, 'PD_5807_env'))}
        band = tb_copy(X, D); inter(X, band, X.wbox(XC - 100, XC + 100, -100, -40, 2.0, 11.0))
        out['x']['door_band_x_front'] = vol_x(X, band, tb_copy(X, F))
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d5h_root_fillets', 'run', out)
    print(json.dumps(out, separators=(',', ':')))
