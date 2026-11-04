# rev F rework R1b-3b (2026-11-04): correct the lap joint. INNER_E's inside skins lie in the cavity, so the R1b-2 lip
# (skin 1.2) sat directly on the door's inner surface with zero clearance, and the "rebate" (skin 1.4) removed nothing
# from the door's wall. New joint = inner flange: the front shell's lip lies 0.2 inside the door's inner surface,
# 1.2 thick (cavity layer 0.2…1.4 from INNER_E's surface), y −58.0…−55.0, z >= 6.5; the door's wall keeps 2.5 to the joint.
#   front − (skin 0.2 ∩ band) ∪ ((skin 1.4 − skin 1.2) ∩ band) − UL lane notch (r 4.0 along the KO_K5_UL axis).
# TOOL_inner_skin_0p2 kept hidden. The UL notch (R1b-3a, 2026-11-04) is re-applied because the new lip layer
# 1.2…1.4 is added after it.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
YS, ZL = -55.0, 6.5


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
        if X.body('TOOL_inner_skin_0p2') is None:
            b = X.add(X.tbm.copy(X.body('INNER_E')), 'TOOL_inner_skin_0p2')
            coll = adsk.core.ObjectCollection.create(); coll.add(b)
            si = X.feats.shellFeatures.createInput(coll, False); si.insideThickness = VI(0.02)
            X.feats.shellFeatures.add(si)
            X.body('TOOL_inner_skin_0p2').isLightBulbOn = False
        band = lambda: X.wbox(-150, 150, YS - 3.0, YS, ZL, 250)
        rm = X.tbm.copy(X.body('TOOL_inner_skin_0p2'))
        X.tbm.booleanOperation(rm, band(), B.IntersectionBooleanType)
        add = X.tbm.copy(X.body('TOOL_inner_skin_1p4'))
        X.tbm.booleanOperation(add, X.tbm.copy(X.body('TOOL_inner_skin_1p2')), B.DifferenceBooleanType)
        X.tbm.booleanOperation(add, band(), B.IntersectionBooleanType)
        notch = X.tbm.createCylinderOrCone(Dw(47.5, -17.80, 146.23), 0.40, Dw(47.5, -65.72, 110.12), 0.40)
        X.tbm.booleanOperation(notch, X.wbox(-150, 150, -58.5, -54.9, 0, 250), B.IntersectionBooleanType)
        X.diff(add, notch)
        out['tools_cm3'] = {'remove_0p2': round(rm.volume, 3), 'add_1p2_1p4': round(add.volume, 3)}
        fb = X.body('HOUSING_F_front'); v0 = fb.volume
        X.combine(fb, [X.add(rm, 'R1_lipfix_rm_tmp')], op=CUT)
        fb = X.body('HOUSING_F_front')
        X.combine(fb, [X.add(add, 'R1_lipfix_add_tmp')])
        fb = X.body('HOUSING_F_front')
        out['front_cm3'] = (round(v0, 3), round(fb.volume, 3)); out['front_lumps'] = fb.lumps.count
        db = X.body('HOUSING_F_door')
        sc = {}
        for y in (-55.15, -56.5, -57.8, -58.15):
            sc[y] = {'front': segs(lambda x: X.inside(fb, XC + x, y, 60.0), 62.0, 80.0, 0.02),
                     'door': segs(lambda x: X.inside(db, XC + x, y, 60.0), 62.0, 80.0, 0.02)}
        out['scan_+x_z60'] = sc
        out['front_vs'] = {k: v for k, v in X.interference(fb, [db] + [X.body(n) for n in ('KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR')]).items()}
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_r1b3b_lip_fix', 'inner flange', out)
    print(json.dumps(out))
# Result 2026-11-04: the 0.2 cut disconnected the lip (it only touched the wall along an edge): HOUSING_F_front became the
# 2.452 cm3 lip piece and the shell "HOUSING_F_front (1)" 257.629 cm3. Rejoined with a root band in R1b-3c.
