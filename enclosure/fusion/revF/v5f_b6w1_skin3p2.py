# rev F block 6w-1 (2026-11-05): tool for Daniel's decision 1 (a) (11:18): thicken the wall to 2.5 normal where it leans.
#   TOOL_outer_skin_3p2_F (hidden) = REF_F_outer ∩ z ≤ 176.0 hollowed by shellFeatures insideThickness 3.2 with the z-176
#   cap removed (the R3 top edges start above z 177; a 3.2 inward offset of R3 would degenerate, lesson 35). In the cloth
#   zone the plastic must reach 3.2 below the cloth face (0.7 recess + 2.5 wall). No part changed.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
NAME, T, Z1 = 'TOOL_outer_skin_3p2_F', 3.2, 176.0


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
        out['bbox'] = [round(v, 1) for v in (b.boundingBox.minPoint.z * 10, b.boundingBox.maxPoint.z * 10)]
        # probes: 3.2 skin at the door back (x 0, z 60: cloth face y −81.78, B5f → inside to ≈ −78.6) and the chin (y 7.5 → 4.3)
        out['probe'] = {'door_back_y-80.2_in': X.inside(b, XC, -80.2, 60.0), 'door_back_y-78.2_out': not X.inside(b, XC, -78.2, 60.0),
                        'door_back_y-82.2_out': not X.inside(b, XC, -82.2, 60.0),
                        'chin_y4.6_in': X.inside(b, XC, 4.6, 25.0), 'chin_y4.0_out': not X.inside(b, XC, 4.0, 25.0)}
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b6w1_skin3p2', 'tool', out)
    print(json.dumps(out))
