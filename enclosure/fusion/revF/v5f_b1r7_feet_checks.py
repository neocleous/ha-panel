# rev F block 1r-7 (2026-11-03): four SJ5012 feet (D12.7 x 3.5 in the D13 x 0.5 recesses: z 0.5 -> -3.0) as FOOT_*
# envelopes at front (XC +-76, -6.9) and rear (XC +-25, -69.4); bbox-prefiltered interference of the floor-zone bodies vs
# housing, slab and every LCD_*; door vs feet; foot-to-counterbore clearances; body inventory.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
FEET = {'FL': (XC + 76.0, -6.9), 'FR': (XC - 76.0, -6.9), 'RL': (XC + 25.0, -69.4), 'RR': (XC - 25.0, -69.4)}
SCREWS = [(XC + 86.74, -7.66), (XC - 86.74, -7.66), (XC + 73.96, -45.63), (XC - 73.96, -45.63), (XC + 44.0, -66.74), (XC - 44.0, -66.74)]
PI_HOLES = [(-41.5, -54.5), (16.5, -54.5), (-41.5, -5.5), (16.5, -5.5)]


def run(_context):
    X = Ctx()
    out = {}
    try:
        for k, (x, y) in FEET.items():
            if X.body('FOOT_' + k) is None:
                X.add(X.wcyl_z(x, y, 6.35, -3.0, 0.5), 'FOOT_' + k)
        feet = [X.body('FOOT_' + k) for k in FEET]
        names = [b.name for b in X.comp.bRepBodies]
        lcd = [X.body(n) for n in names if n.startswith('LCD_')]
        hb = X.body('HOUSING_E'); slab = X.body('SLAB_frame')
        new = [X.body(n) for n in ('DOOR_F', 'PI5_F', 'PI5_F_cooler', 'GPIO_plugA_env', 'GPIO_plugB_env')] + feet

        def bbox_overlap(a, b):
            A = a.boundingBox; B = b.boundingBox
            return all(A.minPoint.asArray()[i] <= B.maxPoint.asArray()[i] and B.minPoint.asArray()[i] <= A.maxPoint.asArray()[i] for i in range(3))

        mat = {}; npairs = 0; nchecked = 0
        for b in new:
            cands = [o for o in [hb, slab] + lcd if o is not None]
            npairs += len(cands)
            cands = [o for o in cands if bbox_overlap(b, o)]
            nchecked += len(cands)
            r = X.interference(b, cands)
            mat[b.name] = {k: v for k, v in r.items() if v > 0} or 'all 0'
        out['interference_nonzero'] = mat
        out['pairs'] = {'total': npairs, 'bbox_overlapping_checked': nchecked}
        out['door_vs_feet'] = X.interference(X.body('DOOR_F'), feet)
        out['housing_vs_KO_fan'] = X.interference(hb, [X.body('KO_K7_fan')])
        clr = {}
        for k, (x, y) in FEET.items():
            ds = min(math.hypot(x - a, y - b) for a, b in SCREWS)
            dp = min(math.hypot(x - a, y - b) for a, b in PI_HOLES)
            clr[k] = {'to_cbore_edge': round(ds - 6.35 - 3.25, 2), 'to_pi_insert_axis': round(dp, 2)}
        out['foot_clearance_mm'] = clr
        door = X.body('DOOR_F')
        # v5f_b1r6 probed 'no recess at the screw' at x -+ 4.5; for FL/FR that point lies inside the front foot recess
        # (screw-foot 10.77, recess r 6.5). Re-probe at y +- 4.5 and confirm the web between recess and counterbore.
        out['screw_no_recess_y+-4.5_z0.25'] = [X.inside(door, x, y + 4.5, 0.25) and X.inside(door, x, y - 4.5, 0.25) for (x, y) in SCREWS]
        out['FL_FR_x-4.5_in_foot_recess'] = [math.hypot(SCREWS[i][0] + s * 4.5 - FEET[k][0], SCREWS[i][1] - FEET[k][1]) < 6.5
                                             for i, s, k in ((0, -1, 'FL'), (1, 1, 'FR'))]
        out['web_recess_to_cbore_mm'] = {k: round(min(math.hypot(x - a, y - b) for a, b in SCREWS) - 6.5 - 3.25, 2) for k, (x, y) in FEET.items()}
        inv = [(b.name, round(b.volume, 3), b.isLightBulbOn) for b in X.comp.bRepBodies]
        out['n_bodies'] = len(inv); out['n_visible'] = sum(1 for i in inv if i[2])
        out['tmp_left'] = [n for (n, _, _) in inv if n.endswith('_tmp') or n.startswith('Body') or n.startswith('DBOSS_')]
        out['key_cm3'] = {n: v for (n, v, _) in inv if n in ('HOUSING_E', 'DOOR_F', 'DOOR_F_b1', 'TOOL_ring_opening_6p5') or n.startswith('FOOT_')}
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b1r7_feet_checks', 'feet + checks', out)
    print(json.dumps(out))
