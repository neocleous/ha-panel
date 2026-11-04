# rev F rework R2b-1 (2026-11-04): hidden tool bodies for the separate speaker boxes (kept short: one Fusion call each).
#   TOOL_inner_skin_2p7  = INNER_E copy hollowed by shellFeatures, insideThickness 2.7 (as R1b-1).
#   TOOL_cav_1p2_slide   = (INNER_E - skin 1.2) ∩ (same moved +1.0 in world y), restricted to the two chamber zones
#                          (x_rel ±40...±130, y -60...2, z 0...82): the box's outer surface stays 1.2 inside the wall
#                          (D1 0.7 + 0.5) at its final position and 1.0 behind it (sideways slide).
#   TOOL_cav_2p7_slide   = same with skin 2.7 (box walls 1.5).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback


def run(_context):
    X = Ctx(); out = {}
    B = adsk.fusion.BooleanTypes; tbm = X.tbm

    def mv(t, dx, dy, dz):
        m = adsk.core.Matrix3D.create(); m.translation = V3(dx / 10, (dy * C + dz * S) / 10, (-dy * S + dz * C) / 10)
        tbm.transform(t, m); return t
    try:
        t0 = time.time()
        if X.body('TOOL_inner_skin_2p7') is None:
            b = X.add(tbm.copy(X.body('INNER_E')), 'TOOL_inner_skin_2p7')
            coll = adsk.core.ObjectCollection.create(); coll.add(b)
            si = X.feats.shellFeatures.createInput(coll, False); si.insideThickness = VI(0.27)
            X.feats.shellFeatures.add(si)
            b = X.body('TOOL_inner_skin_2p7'); b.isLightBulbOn = False
            out['TOOL_inner_skin_2p7'] = {'cm3': round(b.volume, 3), 'lumps': b.lumps.count, 's': round(time.time() - t0, 1)}
        ie = X.body('INNER_E')
        for k, nm, cn in ((1.2, 'TOOL_inner_skin_1p2', 'TOOL_cav_1p2_slide'), (2.7, 'TOOL_inner_skin_2p7', 'TOOL_cav_2p7_slide')):
            if X.body(cn) is not None:
                out[cn] = 'exists'; continue
            t1 = time.time()
            reg = X.wbox(XC + 40, XC + 130, -60, 2, 0, 82); X.union(reg, X.wbox(XC - 130, XC - 40, -60, 2, 0, 82))
            c = tbm.copy(ie); tbm.booleanOperation(c, reg, B.IntersectionBooleanType)
            sk = tbm.copy(X.body(nm)); tbm.booleanOperation(sk, X.wbox(XC - 135, XC + 135, -65, 7, -5, 87), B.IntersectionBooleanType)
            tbm.booleanOperation(c, sk, B.DifferenceBooleanType)
            cs = mv(tbm.copy(c), 0, 1.0, 0)
            tbm.booleanOperation(c, cs, B.IntersectionBooleanType)
            b = X.add(c, cn); b.isLightBulbOn = False
            out[cn] = {'cm3': round(b.volume, 3), 'lumps': b.lumps.count, 's': round(time.time() - t1, 1)}
            log('v5f_r2b1_box_tools', cn, out[cn])
        cv = X.body('TOOL_cav_1p2_slide')
        out['probe'] = {'+x_in_x80_y-20_z30': X.inside(cv, XC + 80, -20, 30), '+x_wall_gap': not X.inside(cv, XC + 99.5, -20, 30)}
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_r2b1_box_tools', 'tools', out)
    print(json.dumps(out))
