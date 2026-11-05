# rev F cap block c1e (2026-11-05): R0.8 on the ledge's outer edge (cloth turns over it) + step-1 checks.
#   Edge chain: edges of the planar z-175.3 ledge faces of HOUSING_F_front (y < −22.5) whose other face is the cloth
#   recess (non-planar, outward normal). Fallback R0.6, else skipped and reported.
#   Checks: volumes / lumps / duplicate names; front ∩ cap, front ∩ door, cap ∩ door; horizontal ray stations through the
#   ledge, groove, cap rim and lip (x 0 and x 30 toward −y, y −30 toward ±x) at z 171…177; post tops vs plate underside.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
DO_FILLET = True
R_LIST = (0.8, 0.6)
POSTS = {'FL': (60.0, -27.0), 'FR': (-60.0, -27.0), 'BL': (28.0, -38.1), 'BR': (-28.0, -38.1)}
NAMES = ('HOUSING_F_front', 'HOUSING_F_cap', 'REF_F_outer')


def ledge_edges(X, b):
    coll = adsk.core.ObjectCollection.create(); info = []
    for f in b.faces:
        if not f.geometry.objectType.endswith('Plane'):
            continue
        p = f.pointOnFace; ok, n = f.evaluator.getNormalAtPoint(p)
        nz = n.y * S + n.z * C
        if nz < 0.999 or abs(wz(p) - 175.3) > 0.01 or wy(p) > -22.4:
            continue
        for e in f.edges:
            o = [g for g in e.faces if g != f]
            if not o or o[0].geometry.objectType.endswith('Plane'):
                continue
            ok, t0, t1 = e.evaluator.getParameterExtents(); ok, m = e.evaluator.getPointAtParameter((t0 + t1) / 2)
            ok, no = o[0].evaluator.getNormalAtPoint(m); nw = nw_of(no)
            ox, oy = m.x * 10 - XC, wy(m) + 35.0; L = math.hypot(ox, oy) or 1.0
            if (nw[0] * ox + nw[1] * oy) / L > 0.2 and nw[2] > 0.05:      # outward + up: the recess (leaning wall)
                coll.add(e); info.append([round(m.x * 10 - XC, 1), round(wy(m), 1)])
    return coll, info


def stations(X):
    S_ = {}
    for (lab, o, d) in (('x0_back', (0.0, -35.0), (0, -1, 0)), ('x30_back', (30.0, -35.0), (0, -1, 0)),
                        ('y-30_side+x', (0.0, -30.0), (1, 0, 0)), ('y-30_side-x', (0.0, -30.0), (-1, 0, 0))):
        rows = []
        for z in (171.0, 172.0, 173.0, 174.0, 175.0, 175.55, 176.0, 177.0):
            hs = [h for h in ray_hits(X, (XC + o[0], o[1], z), d, NAMES)]
            rows.append([z] + [[h[1][9:12], round(h[2] if d[0] else h[3], 2)] for h in hs[:8]])
        S_[lab] = rows
    return S_


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        F, Cp, D = X.body('HOUSING_F_front'), X.body('HOUSING_F_cap'), X.body('HOUSING_F_door')
        out['before'] = {'front': round(F.volume, 4), 'cap': round(Cp.volume, 4), 'door': round(D.volume, 4),
                         'faces_front': F.faces.count}
        if DO_FILLET:
            coll, info = ledge_edges(X, F)
            out['ledge_edges'] = {'n': coll.count, 'mid_pts': info[:40]}
            done = None
            for r in R_LIST:
                try:
                    fi = X.feats.filletFeatures.createInput()
                    fi.edgeSetInputs.addConstantRadiusEdgeSet(coll, VI(r / 10), True)
                    X.feats.filletFeatures.add(fi); done = r; break
                except Exception as e:
                    out['fillet_R%.1f' % r] = 'FAILED ' + str(e)[:80]
                    F = X.body('HOUSING_F_front'); coll, info = ledge_edges(X, F)
            out['fillet'] = done
        F = X.body('HOUSING_F_front')
        out['after'] = {'front': round(F.volume, 4), 'lumps': [F.lumps.count, Cp.lumps.count],
                        'dupes': [b.name for b in X.comp.bRepBodies if b.name.startswith(('HOUSING_F_front (', 'HOUSING_F_cap ('))]}
        out['x'] = {'front_cap': vol_x(X, tb_copy(X, 'HOUSING_F_front'), tb_copy(X, 'HOUSING_F_cap')),
                    'front_door': vol_x(X, tb_copy(X, 'HOUSING_F_front'), tb_copy(X, 'HOUSING_F_door')),
                    'cap_door': vol_x(X, tb_copy(X, 'HOUSING_F_cap'), tb_copy(X, 'HOUSING_F_door'))}
        pt = {}
        for k, (xr, y) in POSTS.items():
            hf = ray_hits(X, (XC + xr + 3.0, y, 172.0), (0, 0, 1), ('HOUSING_F_front',))
            hc = ray_hits(X, (XC + xr + 3.0, y, 172.0), (0, 0, 1), ('HOUSING_F_cap',))
            pt[k] = {'post_top_z': [round(h[4], 3) for h in hf[:2]], 'cap_first_z': round(hc[0][4], 3) if hc else None}
        out['post_tops'] = pt
        out['stations'] = stations(X)
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_c1e_fillet_checks', 'run', out)
    print(json.dumps({k: out.get(k) for k in ('before', 'ledge_edges', 'fillet', 'after', 'x', 'post_tops', 't_s', 'FAIL')},
                     separators=(',', ':'))[:5000])
