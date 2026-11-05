# rev F block 6w-1c (2026-11-05): tool for decision 1 (a), second form. B6w-2b/2c: a fill bounded by the exact 3.2 surface is
#   a sheet ≈ 0.0002 thick wherever the wall is vertical (the 3.2 surface and the D1 surface nearly coincide), and the
#   front's union fails there (ASM_INCONS_FACE). Target 3.22 below the cloth face instead (wall 2.52 normal): the fill is
#   then ≥ 0.02 thick everywhere it exists, 0.02 being 2 000 × the modelling tolerance and far below any print resolution.
#   TOOL_outer_skin_3p22_F (hidden) = REF_F_outer ∩ z ≤ 176.0 hollowed by shellFeatures insideThickness 3.22, z-176 cap
#   removed (as B6w-1). No part changed.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
NAME, T, Z1 = 'TOOL_outer_skin_3p22_F', 3.22, 176.0


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        if X.body(NAME) is not None:
            raise RuntimeError('%s exists' % NAME)
        ref = X.body('REF_F_outer')
        tb = X.tbm.copy(ref)
        X.tbm.booleanOperation(tb, X.wbox(-250, 250, -250, 250, -5.0, Z1), adsk.fusion.BooleanTypes.IntersectionBooleanType)
        b = X.add(tb, NAME)
        cap = None
        for f in b.faces:
            if f.geometry.objectType.endswith('Plane') and abs(wz(f.pointOnFace) - Z1) < 0.05:
                ok, n = f.evaluator.getNormalAtPoint(f.pointOnFace)
                if abs(n.y * S + n.z * C) > 0.99:
                    cap = f
        if cap is None:
            raise RuntimeError('cap at z %s not found' % Z1)
        coll = adsk.core.ObjectCollection.create(); coll.add(cap)
        si = X.feats.shellFeatures.createInput(coll, False)
        si.insideThickness = VI(T / 10)
        X.feats.shellFeatures.add(si)
        b = X.body(NAME); b.isLightBulbOn = False
        out['cm3'] = round(b.volume, 3); out['lumps'] = b.lumps.count; out['faces'] = b.faces.count
        # chin: cloth face y 7.5 → 3.22 skin inner surface at y 4.28 (z 25); door back x 0, z 60: inside to ≈ −78.58
        out['probe'] = {'chin_y4.35_in': X.inside(b, XC, 4.35, 25.0), 'chin_y4.20_out': not X.inside(b, XC, 4.20, 25.0),
                        'door_back_y-80.2_in': X.inside(b, XC, -80.2, 60.0), 'door_back_y-78.2_out': not X.inside(b, XC, -78.2, 60.0)}
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b6w1c_skin3p22', 'tool', out)
    print(json.dumps(out))
