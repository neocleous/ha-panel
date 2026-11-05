# rev F block 5j-2 (2026-11-05), read-only: speaker-box insertion path against the rebuilt lip (D1: lip and pads 0.7 deeper).
#   R2 path per box: lift 6 -> in along +y at 40 mm inboard -> sideways out to the final x 1.0 behind the final pose -> lower
#   6 -> push 1.0 forward. Checked here where the box passes the lip and pads: (a) the +y travel at 40 inboard, lifted 6,
#   for box offsets dy −66…−46 (the box's front passes the lip's rear end) at 1 mm; (b) the sideways move at dy −1.0,
#   lifted 6, x offset −40…0 at 1 mm; (c) lowering at dy −1.0, x 0, lift 6…0 at 1 mm. Front shell cropped to each box's
#   path region first (lesson 24).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        fb = X.body('HOUSING_F_front')
        for bn, s in (('SPKBOX_L', 1), ('SPKBOX_R', -1)):
            box = X.body(bn)
            bb = wbb(X, box)
            region = X.wbox(XC + min(bb[0], bb[0] - 40 * s) - 3, XC + max(bb[1], bb[1] - 40 * s) + 3, bb[2] - 70, bb[3] + 3, bb[4] - 3, bb[5] + 9)
            crop = X.tbm.copy(fb); inter(X, crop, region)
            res = {'a_in_y': {}, 'b_sideways': {}, 'c_lower': {}}

            def at(dx, dy, dz):
                q = X.tbm.copy(box); mvw(X, q, dx, dy, dz)
                return vol_x(X, q, crop)
            for dy in range(-66, -45):
                v = at(-40.0 * s, float(dy), 6.0)
                if v > 0: res['a_in_y'][str(dy)] = v
            for k in range(0, 41):
                v = at(-float(k) * s, -1.0, 6.0)
                if v > 0: res['b_sideways'][str(-k)] = v
            for k in range(0, 7):
                v = at(0.0, -1.0, float(k))
                if v > 0: res['c_lower'][str(k)] = v
            out[bn] = {kk: (vv or 'all 0') for kk, vv in res.items()}
            log('v5f_b5j2_box_paths', bn, out[bn])
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b5j2_box_paths', 'paths', out)
    print(json.dumps(out))
