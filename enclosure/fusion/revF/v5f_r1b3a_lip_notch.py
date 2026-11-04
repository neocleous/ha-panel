# rev F rework R1b-3a (2026-11-04): notch the front shell's lip where the upper +x LCD-screw lane (KO_K5_UL) crosses it
# (32.86 mm3 in R1b-2): cut r 4.0 along the UL lane axis within y -58.5...-54.9. Then x-scans of the joint at z 60.
# Result: front 260.120 -> 260.051 cm3, front vs all four lanes 0. The scans showed the R1b-2 lip sitting on the door's
# inner surface with no clearance (INNER_E's inside skins lie in the cavity) -> corrected in R1b-3b/3c.
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
        fb = X.body('HOUSING_F_front')
        v0 = fb.volume
        if X.interference(fb, [X.body('KO_K5_UL')])['KO_K5_UL'] > 0:
            t = X.tbm.createCylinderOrCone(Dw(47.5, -17.80, 146.23), 0.40, Dw(47.5, -65.72, 110.12), 0.40)
            X.tbm.booleanOperation(t, X.wbox(-150, 150, -58.5, -54.9, 0, 250), B.IntersectionBooleanType)
            out['notch_tool_cm3'] = round(t.volume, 3)
            X.combine(fb, [X.add(t, 'R1_lipnotch_tmp')], op=CUT)
            fb = X.body('HOUSING_F_front')
        out['front_cm3'] = (round(v0, 3), round(fb.volume, 3))
        out['front_vs_lanes'] = X.interference(fb, [X.body(n) for n in ('KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR')])
        db = X.body('HOUSING_F_door')
        sc = {}
        for y in (-55.15, -56.5, -57.8, -58.15, -59.0):
            sc[y] = {'front': segs(lambda x: X.inside(fb, XC + x, y, 60.0), 62.0, 80.0, 0.05),
                     'door': segs(lambda x: X.inside(db, XC + x, y, 60.0), 62.0, 80.0, 0.05)}
        out['scan_+x_z60'] = sc
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_r1b3_lip_notch', 'notch + scans', out)
    print(json.dumps(out))
