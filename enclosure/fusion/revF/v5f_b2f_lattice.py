# rev F block 2f (2026-11-03): speaker grille lattices through the chin wall (handover / rev D pattern): D1.9 holes on a
# 2.5 hex pitch (rows 2.165 apart, odd rows offset 1.25) inside a D38 field (hole fully inside) centred on each speaker
# axis (XC +-70.5, z 28): 199 holes per side, 564 mm2 open (49.8 %). Holes along world y from y 4.5 (inside the D40 bore)
# to y 8.0 (outside the chin face at 7.5). One TemporaryBRep tool per side, combine CUT.
# Block 5 note: the D1 inner layer must not close the bore / lattice (exclude the two D40 bores or re-run this script).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
PTS = []
for j in range(-9, 10):
    for i in range(-9, 10):
        x = 2.5 * i + (1.25 if j % 2 else 0.0); z = 2.165 * j
        if math.hypot(x, z) + 0.95 <= 19.0:
            PTS.append((x, z))


def run(_context):
    X = Ctx(); out = {'holes_per_side': len(PTS)}
    try:
        hb = X.body('HOUSING_E'); v0 = hb.volume
        for s in (1, -1):
            cx = XC + s * 70.5
            tb = None
            for (dx, dz) in PTS:
                c = X.tbm.createCylinderOrCone(Dw(cx + dx, 4.5, 28.0 + dz), 0.095, Dw(cx + dx, 8.0, 28.0 + dz), 0.095)
                tb = c if tb is None else X.union(tb, c)
            X.combine(X.body('HOUSING_E'), [X.add(tb, 'LATTICE_tmp')], op=CUT)
        hb = X.body('HOUSING_E')
        out['housing_cm3'] = (round(v0, 3), round(hb.volume, 3))
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
        res = {}
        for s in (1, -1):
            cx = XC + s * 70.5; k = '+x' if s > 0 else '-x'
            res[k] = {'open': sum(1 for (dx, dz) in PTS if not X.inside(hb, cx + dx, 6.25, 28.0 + dz)),
                      'bars_solid': sum(1 for (dx, dz) in PTS if X.inside(hb, cx + dx + 1.25, 6.25, 28.0 + dz + 0.72) or X.inside(hb, cx + dx, 6.25, 28.0 + dz + 1.08)),
                      'outside_field_solid_r20': X.inside(hb, cx + 20.0, 6.25, 28.0) and X.inside(hb, cx, 6.25, 48.0 - 0.5)}
        out['probes'] = res
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b2f_lattice', 'lattice', out)
    print(json.dumps(out))
