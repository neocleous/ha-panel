# rev F block 5e-3 (2026-11-05): re-cut the front shell's openings that the D1 layer closed.
#   Grille lattices (b2f pattern: 199 × Ø1.9 on a 2.5 hex pitch inside Ø38 per speaker, axis XC ± 70.5, z 28), now along
#   world y from 3.5 (inside the Ø40 bore, whose front end moved from y 5.0 to 4.3) to 8.0; the lattice wall is 2.5 again
#   after the 0.7 recess (y 4.3…6.8). Speaker clamp pilots Ø2.5, y −0.5…5.0 at (x_rel ±52.75, z 10.25 / 45.75) (R2c).
#   Exhaust and BME680 slots with the kept B4l tools (TOOL_exhaust_slots, TOOL_bme680_slots).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
PTS = []
for j in range(-9, 10):
    for i in range(-9, 10):
        x = 2.5 * i + (1.25 if j % 2 else 0.0); z = 2.165 * j
        if math.hypot(x, z) + 0.95 <= 19.0:
            PTS.append((x, z))
PILOTS = [(52.75, 10.25), (52.75, 45.75), (-52.75, 10.25), (-52.75, 45.75)]


def run(_context):
    X = Ctx(); out = {'holes_per_side': len(PTS)}
    t0 = time.time()
    try:
        fb = X.body('HOUSING_F_front'); v0 = fb.volume
        lg = [e for e in json.load(open(LOG)) if e['script'] == 'v5f_b5e2_lip_d1']
        if not lg or 'FAIL' in lg[-1]['data'] or abs(lg[-1]['data']['cm3'][1] - v0) > 0.003:
            raise RuntimeError('guard: B5e-2 not the last change to HOUSING_F_front (%s cm3)' % round(v0, 3))
        cut = None
        for s in (1, -1):
            cx = XC + s * 70.5
            for (dx, dz) in PTS:
                c = X.tbm.createCylinderOrCone(Dw(cx + dx, 3.5, 28.0 + dz), 0.095, Dw(cx + dx, 8.0, 28.0 + dz), 0.095)
                cut = c if cut is None else X.union(cut, c)
        for (xr, z) in PILOTS:
            X.union(cut, X.tbm.createCylinderOrCone(Dw(XC + xr, -0.5, z), 0.125, Dw(XC + xr, 5.0, z), 0.125))
        X.union(cut, tb_copy(X, 'TOOL_exhaust_slots'))
        X.union(cut, tb_copy(X, 'TOOL_bme680_slots'))
        out['t_tool_s'] = round(time.time() - t0, 1)
        X.combine(fb, [X.add(cut, 'B5E3_recut_tmp')], op=CUT)
        fb = X.body('HOUSING_F_front')
        out['cm3'] = [round(v0, 3), round(fb.volume, 3)]
        out['lumps'] = fb.lumps.count
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
        pr = {}
        for s in (1, -1):
            cx = XC + s * 70.5; k = '+x' if s > 0 else '-x'
            pr[k] = {'holes_open_y4.6': sum(1 for (dx, dz) in PTS if not X.inside(fb, cx + dx, 4.6, 28.0 + dz)),
                     'bars_solid_y4.6': sum(1 for (dx, dz) in PTS if X.inside(fb, cx + dx + 1.25, 4.6, 28.0 + dz + 0.72) or
                                            X.inside(fb, cx + dx, 4.6, 28.0 + dz + 1.08))}
        pr['pilots_open_y4.6'] = [not X.inside(fb, XC + xr, 4.6, z) for (xr, z) in PILOTS]
        out['probes'] = pr
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b5e3_front_recut', 'recut', out)
    print(json.dumps(out))
