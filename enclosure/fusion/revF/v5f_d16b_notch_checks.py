# rev F d16b (2026-11-06), read-only: checks after d16a / d16d (finger notch, taller right box). Box air (R, sealed); the finger's way
#   in from behind (door off: between the bracket post and the lip, into the channel, to the card's end), the card's way
#   out (15.4 toward -x) and the space round its grip end vs every part (the door left out: it is off); the cooler exhaust
#   window vs the box; the clear width of the way in (rays along ±x from x_rel -61 at stations behind the box, every part
#   but the door). Writes ~/Documents/HA_panel_renders/d_data/data/d16b_checks.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
OUTF = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d16b_checks.json')
AUDD = os.path.expanduser('~/Documents/audit/data')
NEWP = ['TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'BME_HOOD', 'FOAM_bme_env', 'FOAM_bme_top_env']
GUARD = {'HOUSING_F_front': 235.2273, 'SPKBOX_R': 26.3874, 'SPKBOX_L': 25.6082}
CY1 = -31.0                                                   # channel's front wall (d16d)
Y_ST = [-68.0, -65.0, -62.3, -59.0, -56.5, -54.5, -53.0]           # width stations (y) behind the box's rear face
Z_ST = [3.5, 6.0, 8.5, 11.0, 13.5, 16.0, 20.0, 25.0]
PCIN = adsk.fusion.PointContainment.PointInsidePointContainment


def chamber(X, box, sx):
    bb = wbb(X, X.body(box)); g = 1.0
    Rb = [bb[0] - g, bb[1] + g, bb[2] - g, bb[3] + g, bb[4] - g, bb[5] + g]
    A = wbox_rel(X, Rb)
    X.diff(A, tb_copy(X, box)); X.diff(A, wbox_rel(X, [Rb[0], Rb[1], -3.7, -3.0, Rb[4], Rb[5]]))
    a = Dw(XC + sx * 62.0, -53.0, 30.0); b = Dw(XC + sx * 62.0, -49.5, 30.0)
    X.diff(A, X.tbm.createCylinderOrCone(a, 0.16, b, 0.16))
    pc = Dw(XC + sx * 70.5, -30.0, 62.0)
    for L in A.lumps:
        t = X.tbm.copy(L)
        if t.pointContainment(pc) == PCIN:
            cb = wbb(X, t)
            return t, Rb, cb
    return None, Rb, None


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        for k, v in GUARD.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard %s %s (expected %s)' % (k, None if b is None else round(b.volume, 4), v))
        ch, Rb, cb = chamber(X, 'SPKBOX_R', -1)
        s_ = tb_copy(X, 'SPK_R'); inter(X, s_, X.tbm.copy(ch))
        out['air_R'] = {'upper': round(ch.volume, 3), 'lower': round(ch.volume - s_.volume, 3),
                        'sealed': all(abs(cb[i] - Rb[i]) > 0.05 for i in range(6))}
        names = json.load(open(os.path.join(AUDD, 'a2a_parts.json'))) + NEWP
        parts = [(n, X.body(n), wbb(X, X.body(n))) for n in names if X.body(n) is not None]
        out['n_parts'] = len(parts)

        def hits_of(bb, skip=()):
            t = wbox_rel(X, bb); res = {}
            for (n, b, pb) in parts:
                if n in skip or pb[0] > bb[1] or pb[1] < bb[0] or pb[2] > bb[3] or pb[3] < bb[2] or pb[4] > bb[5] or pb[5] < bb[4]:
                    continue
                q = X.tbm.copy(b); inter(X, q, X.tbm.copy(t)); v = q.volume * 1000
                if v > 0.005:
                    res[n] = [round(v, 2)] + [round(c, 2) for c in wbb(X, q)]
            return res
        R = {}
        R['finger_entry'] = hits_of([-69.5, -53.0, -75.0, -52.05, 2.6, 15.5], ('HOUSING_F_door',))
        R['finger_channel'] = hits_of([-64.0, -45.9, -52.0, CY1, 2.6, 15.5])
        R['fingertip_below_card'] = hits_of([-45.9, -43.2, -36.0, -30.0, 2.6, 6.36])
        R['fingertip_above_card'] = hits_of([-45.9, -43.2, -36.0, -30.0, 7.46, 13.5])
        R['card_out_x'] = hits_of([-60.3, -43.0, -35.4, -24.4, 6.41, 7.41], ('PI5_F',))
        ex = wbox_rel(X, [-46.0, -42.45, -50.1, -7.6, 13.6, 23.1])
        R['exhaust_window_x_box_mm3'] = vol_x(X, ex, tb_copy(X, 'SPKBOX_R'))
        out['paths'] = R
        wn = tuple(n for (n, b, pb) in parts if n != 'HOUSING_F_door'); W = {}
        for y in Y_ST:
            row = []
            for z in Z_ST:
                o = (XC - 61.0, y, z)
                ins = [n for (n, b, pb) in parts if n != 'HOUSING_F_door' and pb[0] <= -61.0 <= pb[1] and pb[2] <= y <= pb[3]
                       and pb[4] <= z <= pb[5] and b.pointContainment(Dw(*o)) in INS]
                if ins:
                    row.append([z, 'inside'] + ins); continue
                hi = ray_hits(X, o, (1, 0, 0), wn); lo = ray_hits(X, o, (-1, 0, 0), wn)
                xi = round(-61.0 + hi[0][0], 2) if hi else None; xo = round(-61.0 - lo[0][0], 2) if lo else None
                row.append([z, xo, xi, round(xi - xo, 2) if (xi is not None and xo is not None) else None,
                            lo[0][1] if lo else None, hi[0][1] if hi else None])
            W['y%g' % y] = row
        out['entry_width'] = W
        out['t_s'] = round(time.time() - t0, 1)
        os.makedirs(os.path.dirname(OUTF), exist_ok=True)
        json.dump(out, open(OUTF, 'w'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
        try:
            json.dump(out, open(OUTF, 'w'))
        except Exception:
            pass
    log('v5f_d16b_notch_checks', 'run', out)
    print(json.dumps(out, separators=(',', ':')))
