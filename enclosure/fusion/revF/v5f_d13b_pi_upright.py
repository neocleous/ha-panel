# rev F d13b (2026-11-06), read-only: Daniel 19:08 – the Pi stood on its short edge against a speaker box (board flat on the
#   box's inboard face, components inboard), using the height above today's Pi. Envelope from PI5_F: 1.94 under the PCB,
#   PCB 1.4, 16.45 above; 85 + 3.3 (USB / RJ45 overhang) + 1.7 (card) along z, 57.7 along y. Each candidate vs the part
#   list without the parts that move with the Pi; card paths (SD end up: out upward; down: out through the floor) and the
#   cooler exhaust (it blows out of the SD end). Writes ~/Documents/HA_panel_renders/d_data/data/d13b_probe.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
OUTF = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d13b_probe.json')
AUDD = os.path.expanduser('~/Documents/audit/data')
NEWP = ['TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'BME_HOOD', 'FOAM_bme_env', 'FOAM_bme_top_env']
MOVES = ('PI5_F', 'PI5_F_cooler', 'KO_K7_fan', 'GPIO_plugA_env', 'GPIO_plugB_env', 'PIPWR_a_env', 'LEAD_PI_POWER',
         'USBA_plug_env', 'USBA_cable_env', 'LEAD_USB_RESP')
GUARD = {'HOUSING_F_front': 235.3238, 'SPKBOX_R': 25.6435, 'SPKBOX_L': 25.6082, 'HOUSING_F_door': 47.2694}


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        for k, v in GUARD.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard %s %s' % (k, None if b is None else round(b.volume, 4)))
        names = json.load(open(os.path.join(AUDD, 'a2a_parts.json'))) + NEWP
        parts = []
        for n in names:
            b = X.body(n)
            if b is not None and n not in MOVES:
                try:
                    parts.append((n, b, wbb(X, b)))
                except Exception:
                    pass
        out['n_parts'] = len(parts)
        R = {}

        def region(key, bb):
            t = wbox_rel(X, bb); res = {}
            for (n, b, pb) in parts:
                if pb[0] > bb[1] or pb[1] < bb[0] or pb[2] > bb[3] or pb[3] < bb[2] or pb[4] > bb[5] or pb[5] < bb[4]:
                    continue
                qq = X.tbm.copy(b); inter(X, qq, X.tbm.copy(t)); v = qq.volume * 1000
                if v > 0.005:
                    res[n] = [round(v, 1)] + [round(c, 1) for c in wbb(X, qq)]
            R[key] = {'bb': bb, 'hits': res}
        for side, s in (('R', -1), ('L', 1)):
            x0, x1 = sorted((s * 45.5, s * 25.7))
            region(side + '_pi', [x0, x1, -59.7, -2.0, 3.0, 93.0])
            cx0, cx1 = sorted((s * 45.5, s * 42.5))
            region(side + '_card_up', [cx0, cx1, -36.0, -23.8, 93.0, 110.0])
            region(side + '_card_down', [cx0, cx1, -36.0, -23.8, -0.6, 3.0])
            ex0, ex1 = sorted((s * 41.0, s * 31.5))
            region(side + '_exhaust_up', [ex0, ex1, -50.1, -7.6, 93.0, 113.0])
            region(side + '_column', [x0, x1, -64.0, 0.0, 26.0, 130.0])
        out['regions'] = R
        out['t_s'] = round(time.time() - t0, 1)
        os.makedirs(os.path.dirname(OUTF), exist_ok=True)
        json.dump(out, open(OUTF, 'w'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
        try:
            json.dump(out, open(OUTF, 'w'))
        except Exception:
            pass
    log('v5f_d13b_pi_upright', 'probe', {'t_s': out.get('t_s'), 'FAIL': out.get('FAIL')})
    print(json.dumps({'t_s': out.get('t_s'), 'FAIL': out.get('FAIL')}, separators=(',', ':')))
