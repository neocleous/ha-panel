# rev F rework R2b-1b (2026-11-04): hidden tool bodies for the separate speaker boxes, second run (one Fusion call).
# Run 2 (SKINS = 4.7 / 6.2): offsets for the 3.5 x 3.5 step along the boxes' bottom-outboard edge (clears the R3.5 floor
# cove, also after the D1 0.7 layer).
#   TOOL_inner_skin_2p7  = INNER_E copy hollowed by shellFeatures, insideThickness 2.7 (as R1b-1).
#   TOOL_cav_1p2_slide   = (INNER_E - skin 1.2) ∩ (same moved +1.0 in world y), restricted to the two chamber zones
#                          (x_rel ±40...±130, y -60...2, z 0...82): the box's outer surface stays 1.2 inside the wall
#                          (D1 0.7 + 0.5) at its final position and 1.0 behind it (sideways slide).
#   TOOL_cav_2p7_slide   = same with skin 2.7 (box walls 1.5).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
SKINS = (4.7, 6.2)          # run 1 was (1.2 [existing skin], 2.7)


def run(_context):
    X = Ctx(); out = {}
    B = adsk.fusion.BooleanTypes; tbm = X.tbm

    def mv(t, dx, dy, dz):
        m = adsk.core.Matrix3D.create(); m.translation = V3(dx / 10, (dy * C + dz * S) / 10, (-dy * S + dz * C) / 10)
        tbm.transform(t, m); return t
    try:
        t0 = time.time()
        for th in SKINS:
            nm = 'TOOL_inner_skin_%dp%d' % (int(th), round((th - int(th)) * 10))
            if X.body(nm) is not None: continue
            b = X.add(tbm.copy(X.body('INNER_E')), nm)
            coll = adsk.core.ObjectCollection.create(); coll.add(b)
            si = X.feats.shellFeatures.createInput(coll, False); si.insideThickness = VI(th / 10)
            X.feats.shellFeatures.add(si)
            b = X.body(nm); b.isLightBulbOn = False
            out[nm] = {'cm3': round(b.volume, 3), 'lumps': b.lumps.count, 's': round(time.time() - t0, 1)}
        ie = X.body('INNER_E')
        for th in SKINS:
            tag = '%dp%d' % (int(th), round((th - int(th)) * 10))
            nm, cn = 'TOOL_inner_skin_' + tag, 'TOOL_cav_' + tag + '_slide'
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
            log('v5f_r2b1b_step_tools', cn, out[cn])
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_r2b1b_step_tools', 'tools', out)
    print(json.dumps(out))
