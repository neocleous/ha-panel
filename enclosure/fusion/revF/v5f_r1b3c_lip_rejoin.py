# rev F rework R1b-3c (2026-11-04): rejoin the lip. R1b-3b's 0.2 cut disconnected the lip from the front shell (the lip
# only touched the wall along an edge) -> two bodies. Fix: root band = skin 1.4 ∩ (y -53.5...-55.0, z >= 6.5) on the
# front's inner surface (stays 0.4 behind the chamber back partitions' rear face y -53.1), union main front + lip + root,
# minus both upper-lane notches (UL and mirrored UR, r 4.0 along the lane axes, y -58.5...-53.4).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback


def segs(f, a, b, st):
    out = []; cur = None; v = a
    while v <= b + 1e-9:
        s = f(v)
        if s and cur is None: cur = v
        if not s and cur is not None: out.append([round(cur, 2), round(v - st, 2)]); cur = None
        v += st
    if cur is not None: out.append([round(cur, 2), round(b, 2)])
    return out


def run(_context):
    X = Ctx(); out = {}
    try:
        B = adsk.fusion.BooleanTypes
        main = X.body('HOUSING_F_front (1)'); lip = X.body('HOUSING_F_front')
        if main is None or lip is None or lip.volume > 10:
            raise RuntimeError('unexpected bodies')
        out['in_cm3'] = (round(main.volume, 3), round(lip.volume, 3))
        lip.name = 'R1_lip_piece_tmp'; main.name = 'HOUSING_F_front'
        root = X.tbm.copy(X.body('TOOL_inner_skin_1p4'))
        X.tbm.booleanOperation(root, X.wbox(-150, 150, -55.0, -53.5, 6.5, 250), B.IntersectionBooleanType)
        tb = X.tbm.copy(X.body('R1_lip_piece_tmp'))
        X.union(tb, root)
        for xs in (47.5, -47.5):
            n = X.tbm.createCylinderOrCone(Dw(xs, -17.80, 146.23), 0.40, Dw(xs, -65.72, 110.12), 0.40)
            X.tbm.booleanOperation(n, X.wbox(-150, 150, -58.5, -53.4, 0, 250), B.IntersectionBooleanType)
            X.diff(tb, n)
        out['lip_root_cm3'] = round(tb.volume, 3)
        X.body('R1_lip_piece_tmp').deleteMe()
        X.combine(X.body('HOUSING_F_front'), [X.add(tb, 'R1_lip_root_tmp')])
        fb = X.body('HOUSING_F_front'); db = X.body('HOUSING_F_door')
        out['front_cm3'] = round(fb.volume, 3); out['front_lumps'] = fb.lumps.count
        out['names_with_front'] = [b.name for b in X.comp.bRepBodies if 'HOUSING_F_front' in b.name]
        t = X.tbm.copy(fb); X.tbm.booleanOperation(t, X.tbm.copy(db), B.IntersectionBooleanType)
        out['front_x_door_mm3'] = round(t.volume * 1000, 3)
        out['front_vs_lanes'] = X.interference(fb, [X.body(n) for n in ('KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR')])
        sc = {}
        for y in (-54.5, -55.15, -56.5, -57.8, -58.15):
            sc[y] = {'front': segs(lambda x: X.inside(fb, XC + x, y, 60.0), 62.0, 80.0, 0.02),
                     'door': segs(lambda x: X.inside(db, XC + x, y, 60.0), 62.0, 80.0, 0.02)}
        out['scan_+x_z60'] = sc
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_r1b3c_lip_rejoin', 'lip rejoined', out)
    print(json.dumps(out))
