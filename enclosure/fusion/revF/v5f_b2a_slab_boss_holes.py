# rev F block 2a (2026-11-03): LCD screw holes in the slab boss (Daniel 2026-11-03 21:01, option 4a; pocket depth 1.0
# instead of 2.0 because the thread test can't be done on his panel). The four D2.7 holes at design (x +-47.5, Z ZS +- 34)
# -> D3.4 through the boss (solid d 9.0 -> 14.8), + D6.5 head pockets 1.0 deep from the boss back face (d 14.8 -> 13.8).
# DIN912 M3 x 6 from the seat at d 13.8 ends at d 7.8: inside the 1.5 threaded standoff (d 7.4-8.9 in Daniel's STEP).
# Design-frame cylinders along -Y (d), one TemporaryBRep tool, combine CUT; probes; interference vs slab / LCD_*.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
ZS = -27.43
AX = [(47.5, ZS - 34.0), (-47.5, ZS - 34.0), (47.5, ZS + 34.0), (-47.5, ZS + 34.0)]   # design x, Z (mm)


def run(_context):
    X = Ctx()
    out = {}
    try:
        hb = X.body('HOUSING_E')
        dcyl = lambda x, Z, r, d0, d1: X.tbm.createCylinderOrCone(P3(x / 10, -d0 / 10, Z / 10), r / 10, P3(x / 10, -d1 / 10, Z / 10), r / 10)
        ins = lambda b, x, d, Z: b.pointContainment(P3(x / 10, -d / 10, Z / 10)) in INS
        pre = {('%g,%g' % a): {'solid_d9.2..14.6': [ins(hb, a[0] + 1.6, d, a[1]) for d in (9.2, 11.0, 14.6)], 'open_d15.2': not ins(hb, a[0] + 1.6, 15.2, a[1])} for a in AX}
        out['pre_r1.6'] = pre
        tb = None
        for (x, Z) in AX:
            t = dcyl(x, Z, 1.7, 8.0, 16.0)
            X.union(t, dcyl(x, Z, 3.25, 13.8, 16.0))
            tb = t if tb is None else X.union(tb, t)
        cut = X.add(tb, 'SLABBOSS_cut_tmp')
        v0 = hb.volume
        X.combine(hb, [cut], op=CUT)
        hb = X.body('HOUSING_E')
        out['housing_cm3'] = (round(v0, 3), round(hb.volume, 3), round(v0 - hb.volume, 4))
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name == 'SLABBOSS_cut_tmp']
        pr = {}
        for (x, Z) in AX:
            pr['%g,%g' % (x, Z)] = {
                'hole_open_d11_r1.5': not ins(hb, x + 1.5, 11.0, Z) and not ins(hb, x, 11.0, Z + 1.5),
                'boss_solid_d11_r1.9': ins(hb, x + 1.9, 11.0, Z) and ins(hb, x - 1.9, 11.0, Z),
                'pocket_open_d14.3_r3.0': not ins(hb, x + 3.0, 14.3, Z) and not ins(hb, x - 3.0, 14.3, Z),
                'seat_solid_d13.6_r2.5': ins(hb, x + 2.5, 13.6, Z) and ins(hb, x - 2.5, 13.6, Z),
                'lip_toward_opening_d14.3': ins(hb, x, 14.3, Z + (3.6 if Z < ZS else -3.6))}
        out['probes'] = pr
        names = [b.name for b in X.comp.bRepBodies]
        others = [X.body(n) for n in names if n.startswith('LCD_')] + [X.body('SLAB_frame')]
        r = X.interference(hb, others)
        out['interf_nonzero'] = {k: v for k, v in r.items() if v > 0} or 'all 0 (%d bodies)' % len(r)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b2a_slab_boss_holes', 'slab boss D3.4 + D6.5x1.0', out)
    print(json.dumps(out))
