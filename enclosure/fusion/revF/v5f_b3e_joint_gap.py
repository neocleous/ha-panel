# rev F block 3e (2026-11-04): restore the 0.3 front/door joint gap above the opening.
#   B3d's fill region started at y −55.3, so at the back centre around z 165 (where the back face crosses the split plane)
#   it also filled the joint gap y −55.3…−55.0 (B3d deficit lump 1.4 mm³, x_rel ±9.9, z 164.9…165.9). Above z 163 the front
#   shell had nothing behind y −55.0 (the lip ends below z ≈ 161), so cut x_rel ±120, y −55.3…−55.0, z 163…190.
#   Checks: front ∩ that box = 0; top deficit (skin 2.5 ∩ y −55.0…30, z 165…190 − front) = 0; front vs door 0.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
EXPECT = {'HOUSING_F_front': 240.591, 'HOUSING_F_door': 55.484}


def run(_context):
    X = Ctx(); out = {}
    B = adsk.fusion.BooleanTypes; tbm = X.tbm
    try:
        for n, v in EXPECT.items():
            b = X.body(n)
            if b is None or abs(b.volume - v) > 0.002:
                raise RuntimeError('guard: %s volume %s, expected %s' % (n, None if b is None else round(b.volume, 3), v))
        fb = X.body('HOUSING_F_front'); v0 = fb.volume
        t = tbm.copy(fb); tbm.booleanOperation(t, X.wbox(XC - 120, XC + 120, -55.3, -55.0, 163, 190), B.IntersectionBooleanType)
        out['in_gap_before_mm3'] = round(t.volume * 1000, 3)
        if t.volume > 0:
            X.combine(fb, [X.add(X.wbox(XC - 120, XC + 120, -55.3, -55.0, 163, 190), 'B3E_gap_tmp')], op=CUT)
            fb = X.body('HOUSING_F_front')
        t = tbm.copy(fb); tbm.booleanOperation(t, X.wbox(XC - 120, XC + 120, -55.3, -55.0, 163, 190), B.IntersectionBooleanType)
        out['in_gap_after_mm3'] = round(t.volume * 1000, 3)
        out['front_cm3'] = [round(v0, 3), round(fb.volume, 3)]; out['front_lumps'] = fb.lumps.count
        sr = tbm.copy(X.body('TOOL_outer_skin_2p5_F')); tbm.booleanOperation(sr, X.wbox(XC - 120, XC + 120, -55.0, 30, 165, 190), B.IntersectionBooleanType)
        tbm.booleanOperation(sr, tbm.copy(fb), B.DifferenceBooleanType)
        out['top_deficit_mm3'] = round(sr.volume * 1000, 3)
        out['front_vs_door'] = X.interference(fb, [X.body('HOUSING_F_door')])
        out['names'] = [b.name for b in X.comp.bRepBodies if b.name.startswith(('HOUSING_F', 'B3'))]
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b3e_joint_gap', 'gap', out)
    print(json.dumps(out))
