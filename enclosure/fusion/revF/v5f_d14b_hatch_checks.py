# rev F d14b (2026-11-06), read-only: checks after d14a. Box air (both chambers, sealed); SPKBOX_R's added material lies in
#   its old chamber air (so its outer shape and insertion path are unchanged); the lower bore's Ø5.5 head path; the card's
#   way out (15.4 toward -x, then down through the slot) and the tweezers' zones vs every part except the Pi and the cover;
#   the card's way back on SD_SLED (up 8, then 14.75 toward +x) and the sled itself vs every part except the cover (the
#   card also without the Pi: it ends in the Pi's socket). Writes ~/Documents/HA_panel_renders/d_data/data/d14b_checks.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
OUTF = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d14b_checks.json')
AUDD = os.path.expanduser('~/Documents/audit/data')
NEWP = ['TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'BME_HOOD', 'FOAM_bme_env', 'FOAM_bme_top_env', 'HATCH_COVER']
GUARD = {'HOUSING_F_front': 234.701, 'SPKBOX_R': 25.5694, 'SPKBOX_R_d14': 25.6435, 'SPKBOX_L': 25.6082, 'HATCH_COVER': 0.586,
         'SD_SLED': 1.1956}
PCIN = adsk.fusion.PointContainment.PointInsidePointContainment
CARD0 = [-59.25, -43.85, -35.38, -24.42, 6.41, 7.41]       # card on the sled before the push


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
        air = {}
        for (box, spk, sx) in (('SPKBOX_R', 'SPK_R', -1), ('SPKBOX_L', 'SPK_L', 1), ('SPKBOX_R_d14', 'SPK_R', -1)):
            ch, Rb, cb = chamber(X, box, sx)
            if ch is None:
                air[box] = 'point not in any lump'; continue
            s = tb_copy(X, spk); inter(X, s, X.tbm.copy(ch))
            air[box] = {'upper': round(ch.volume, 3), 'lower': round(ch.volume - s.volume, 3),
                        'sealed': all(abs(cb[i] - Rb[i]) > 0.05 for i in range(6))}
            if box == 'SPKBOX_R_d14':
                ad = tb_copy(X, 'SPKBOX_R'); X.diff(ad, tb_copy(X, 'SPKBOX_R_d14'))
                out['added_mm3'] = round(ad.volume * 1000, 2)
                X.diff(ad, X.tbm.copy(ch)); out['added_outside_old_air_mm3'] = round(ad.volume * 1000, 3)
        out['air'] = air
        hp = X.tbm.createCylinderOrCone(Dw(XC - 52.75, -60.0, 10.25), 0.275, Dw(XC - 52.75, -9.0, 10.25), 0.275)
        out['bore_head_path_mm3'] = vol_x(X, hp, tb_copy(X, 'SPKBOX_R'))
        names = json.load(open(os.path.join(AUDD, 'a2a_parts.json'))) + NEWP
        parts = []
        for n in names:
            b = X.body(n)
            if b is not None:
                parts.append((n, b, wbb(X, b)))
        out['n_parts'] = len(parts)

        def hits_of(t, skip=()):
            tb = wbb(X, t); res = {}
            for (n, b, pb) in parts:
                if n in skip or pb[0] > tb[1] or pb[1] < tb[0] or pb[2] > tb[3] or pb[3] < tb[2] or pb[4] > tb[5] or pb[5] < tb[4]:
                    continue
                q = X.tbm.copy(b); inter(X, q, X.tbm.copy(t)); v = q.volume * 1000
                if v > 0.005:
                    res[n] = [round(v, 2)] + [round(c, 2) for c in wbb(X, q)]
            return res
        R = {}
        R['card_out_x'] = hits_of(wbox_rel(X, [-60.3, -43.0, -35.4, -24.4, 6.41, 7.41]), ('PI5_F',))
        R['card_out_down'] = hits_of(wbox_rel(X, [-60.3, -44.8, -35.4, -24.4, -1.0, 7.41]), ('PI5_F', 'HATCH_COVER'))
        R['card_out_down_cover'] = vol_x(X, wbox_rel(X, [-60.3, -44.8, -35.4, -24.4, -1.0, 7.41]), tb_copy(X, 'HATCH_COVER'))
        R['tweezers_below'] = hits_of(wbox_rel(X, [-46.0, -43.2, -36.2, -23.6, -0.6, 6.36]), ('PI5_F', 'HATCH_COVER'))
        R['tweezers_above'] = hits_of(wbox_rel(X, [-44.85, -43.2, -35.6, -24.2, 7.46, 8.7]))
        # sled + card path
        steps = [(0.0, 0.0, dz) for dz in [-8.0 + 0.5 * k for k in range(17)]] + [(0.5 * k, 0.0, 0.0) for k in range(1, 30)] + [(14.75, 0.0, 0.0)]
        sw = {'sled': {}, 'card': {}}
        for (dx, dy, dz) in steps:
            s_ = tb_copy(X, 'SD_SLED'); mvw(X, s_, dx, dy, dz)
            for n, h in hits_of(s_, ('HATCH_COVER',)).items():
                if n not in sw['sled'] or h[0] > sw['sled'][n][0]:
                    sw['sled'][n] = [h[0], [dx, dz]]
            c_ = wbox_rel(X, CARD0); mvw(X, c_, dx, dy, dz)
            for n, h in hits_of(c_, ('HATCH_COVER', 'PI5_F')).items():
                if n not in sw['card'] or h[0] > sw['card'][n][0]:
                    sw['card'][n] = [h[0], [dx, dz]]
        R['sled_path'] = sw; R['n_steps'] = len(steps)
        st = tb_copy(X, 'SD_SLED'); mvw(X, st, 14.75, 0, 0)
        R['sled_end_x_pi_mm3'] = vol_x(X, st, tb_copy(X, 'PI5_F'))
        out['paths'] = R
        out['cover_bb'] = [round(c, 2) for c in wbb(X, X.body('HATCH_COVER'))]
        out['t_s'] = round(time.time() - t0, 1)
        os.makedirs(os.path.dirname(OUTF), exist_ok=True)
        json.dump(out, open(OUTF, 'w'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
        try:
            json.dump(out, open(OUTF, 'w'))
        except Exception:
            pass
    log('v5f_d14b_hatch_checks', 'run', {k: v for k, v in out.items() if k != 'paths'})
    print(json.dumps({k: v for k, v in out.items() if k != 'paths'}, separators=(',', ':')))
