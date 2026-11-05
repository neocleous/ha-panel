# rev F block 5j-3 (2026-11-05), read-only: speaker-box insertion path re-ordered for the D1 layer.
#   B5j-2 found (both boxes): (1) the +y travel at 40 inboard (lifted 6) brushes the rebuilt lip's rear end, ≤ 0.23 mm³
#   (dy −59…−54); (2) at the final x, lifted ≥ 4, the box's top-outboard edge meets the D1 layer on the leaning side wall
#   (lift 4 / 5 / 6: 2.6–3.0 / 36 / 112 mm³; 1 mm inboard: 0). New path per box: lift 6 -> +y at 42 inboard -> sideways
#   outboard to 1 mm inboard of the final x (dy −1.0, lift 6) -> lower 6 -> last 1 mm outboard on the floor -> push 1.0 forward.
#   Checked here: (a) +y travel at 42 inboard, dy −70…−40 at 1 mm; (b) sideways 42 -> 1 inboard at 1 mm; (c) lowering at
#   1 inboard, lift 6 -> 0 at 0.5 mm; (d) last 1 mm outboard at lift 0 in 0.25 mm; (e) push dy −1.0 -> 0 in 0.25 mm.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
IN = 42.0


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        fb = X.body('HOUSING_F_front')
        for bn, s in (('SPKBOX_L', 1), ('SPKBOX_R', -1)):
            box = X.body(bn)
            bb = wbb(X, box)
            region = X.wbox(XC + min(bb[0], bb[0] - IN * s) - 3, XC + max(bb[1], bb[1] - IN * s) + 3, bb[2] - 75, bb[3] + 3, bb[4] - 3, bb[5] + 9)
            crop = X.tbm.copy(fb); inter(X, crop, region)
            res = {'a_in_y_42': {}, 'b_sideways_to_1': {}, 'c_lower_at_1': {}, 'd_last_1mm_floor': {}, 'e_push': {}}

            def at(dx, dy, dz):
                q = X.tbm.copy(box); mvw(X, q, dx, dy, dz)
                return vol_x(X, q, crop)
            for dy in range(-70, -39):
                v = at(-IN * s, float(dy), 6.0)
                if v > 0: res['a_in_y_42'][str(dy)] = v
            for k in range(1, 43):
                v = at(-float(k) * s, -1.0, 6.0)
                if v > 0: res['b_sideways_to_1'][str(k)] = v
            for i in range(0, 13):
                v = at(-1.0 * s, -1.0, 6.0 - 0.5 * i)
                if v > 0: res['c_lower_at_1'][str(6.0 - 0.5 * i)] = v
            for i in range(0, 5):
                v = at(-(1.0 - 0.25 * i) * s, -1.0, 0.0)
                if v > 0: res['d_last_1mm_floor'][str(1.0 - 0.25 * i)] = v
            for i in range(0, 5):
                v = at(0.0, -1.0 + 0.25 * i, 0.0)
                if v > 0: res['e_push'][str(-1.0 + 0.25 * i)] = v
            out[bn] = {kk: (vv or 'all 0') for kk, vv in res.items()}
            log('v5f_b5j3_box_paths2', bn, out[bn])
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b5j3_box_paths2', 'paths', out)
    print(json.dumps(out))
