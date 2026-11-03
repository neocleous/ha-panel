# rev F block 2e-2 (2026-11-03): clearance cut for the front door bosses under the speaker baskets. SPK_L/R vs HOUSING_E
# was 0.40 mm3: the FL/FR boss cap's inboard top corner (x_rel 82.74..83.38, z 11.65..12.7) sits inside the D40 basket
# envelope. Cut HOUSING_E with a D40.6 cylinder (basket + 0.3) over the basket length (y -3.0 .. -29.1). The insert hole
# wall (z 5.0..11.7) is untouched; only the cap corner above z ~12.2 is trimmed.
# Result 2026-11-03: 3.05 mm3 removed, SPK_L/R vs HOUSING_E 0, hole wall and cap probes true.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback

def run(_context):
    X = Ctx(); out = {}
    try:
        hb = X.body('HOUSING_E')
        tb = None
        for s in (1, -1):
            cx = XC + s * 70.5
            c = X.tbm.createCylinderOrCone(Dw(cx, -3.0, 28.0), 2.03, Dw(cx, -29.1, 28.0), 2.03)
            tb = c if tb is None else X.union(tb, c)
        tool = X.add(tb, 'BASKET_clear_tmp')
        v0 = hb.volume
        X.combine(hb, [tool], op=CUT)
        hb = X.body('HOUSING_E')
        out['housing_cm3'] = (round(v0, 3), round(hb.volume, 4), round((v0 - hb.volume) * 1000, 2))
        out['spk_interf'] = {nm: X.interference(X.body(nm), [hb]) for nm in ('SPK_L', 'SPK_R')}
        out['boss_hole_wall_z11_inboard'] = [X.inside(hb, XC + s * 83.5, -7.66, 11.0) for s in (1, -1)]
        out['boss_cap_z12.4_axis'] = [X.inside(hb, XC + s * 86.74, -7.66, 12.4) for s in (1, -1)]
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b2e2_basket_clearance', 'boss cap trim', out)
    print(json.dumps(out))
