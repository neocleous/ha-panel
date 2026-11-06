# rev F d19b (2026-11-06), read-only: room for the printability fixes found by d19a. (A) under the LD2410C cradle's floor in the
#   front shell (flat 329 mm² at z 114.3, a ~112 mm support tower when the shell prints floor down): the cradle's own extents per
#   height and what lies below it; (B) under the main bracket's lower board-boss arms (z 33.5) on both halves; (C) the cap printed
#   top down: its overhang regions. Candidate solids vs every part (the door included) and the right box's B5j-3 path envelope.
#   Writes ~/Documents/HA_panel_renders/d_data/data/d19b_probe.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py'), encoding='utf-8').read())
import traceback
OUTF = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d19b_probe.json')
AUDD = os.path.expanduser('~/Documents/audit/data')
NEWP = ['TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'BME_HOOD', 'FOAM_bme_env', 'FOAM_bme_top_env', 'HOUSING_F_door']
CAND = {
    'A_under_cradle': [-88.0, -63.0, -34.0, -8.0, 88.0, 114.3],
    'B_R_under_arm': [-46.5, -38.0, -63.4, -57.7, 24.0, 33.5],
    'B_L_under_arm': [38.0, 46.5, -63.4, -57.7, 24.0, 33.5],
}


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        names = json.load(open(os.path.join(AUDD, 'a2a_parts.json'), encoding='utf-8')) + NEWP
        parts = [(n, X.body(n), wbb(X, X.body(n))) for n in names if X.body(n) is not None]

        def hits(t, skip=()):
            tb = wbb(X, t); res = {}
            for (n, b, pb) in parts:
                if n in skip or pb[0] > tb[1] or pb[1] < tb[0] or pb[2] > tb[3] or pb[3] < tb[2] or pb[4] > tb[5] or pb[5] < tb[4]:
                    continue
                q = X.tbm.copy(b); inter(X, q, X.tbm.copy(t)); v = q.volume * 1000
                if v > 0.005:
                    res[n] = [round(v, 2)] + [round(c, 2) for c in wbb(X, q)]
            return res
        out['cand_hits'] = {k: hits(wbox_rel(X, bb)) for k, bb in CAND.items()}
        # the right box swept along B5j-3 (union of every 2nd mm of the path) -> its envelope under the cradle
        box = tb_copy(X, 'SPKBOX_R'); env = None
        path = [(42, -70, 6), (42, -1, 6), (1, -1, 6), (1, -1, 0), (0, -1, 0), (0, 0, 0)]
        pts = []
        for a, b in zip(path[:-1], path[1:]):
            L = math.sqrt(sum((b[i] - a[i]) ** 2 for i in range(3))); n = max(1, int(math.ceil(L / 2.0)))
            pts += [tuple(a[i] + (b[i] - a[i]) * k / n for i in range(3)) for k in range(n)]
        pts.append(path[-1])
        for p in pts:
            c = X.tbm.copy(box); mvw(X, c, *p); inter(X, c, wbox_rel(X, CAND['A_under_cradle']))
            if c.volume > 0:
                env = c if env is None else X.union(env, c)
        out['boxR_path_in_A'] = [round(env.volume * 1000, 1)] + [round(v, 2) for v in wbb(X, env)] if env is not None else None
        # cradle extents: the front shell sliced every 1 mm from z 112 to 130 inside x -90…-60, y -36…-4
        fr = tb_copy(X, 'HOUSING_F_front'); inter(X, fr, wbox_rel(X, [-92.0, -60.0, -36.0, -4.0, 86.0, 132.0]))
        sl = {}
        for z in [88.0, 92.0, 96.0, 100.0, 104.0, 108.0, 112.0, 114.0, 114.6, 115.5, 116.6, 118.0, 122.0, 126.0, 130.0]:
            q = X.tbm.copy(fr); inter(X, q, wbox_rel(X, [-92.0, -60.0, -36.0, -4.0, z - 0.05, z + 0.05]))
            sl['z%g' % z] = [[round(l.volume * 10000, 1)] + [round(c, 2) for c in wbb(X, X.tbm.copy(l))] for l in q.lumps] if q.volume > 0 else []
        out['front_slices_cradle'] = sl
        for n in ('LD2410C_env_F', 'LEAD_RADAR', 'BME680_env', 'BME_HOOD', 'KO_K13', 'LEAD_BME680'):
            b = X.body(n)
            out['bb_' + n] = [round(c, 2) for c in wbb(X, b)] if b is not None else None
        out['t_s'] = round(time.time() - t0, 1)
        os.makedirs(os.path.dirname(OUTF), exist_ok=True)
        json.dump(out, open(OUTF, 'w'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
        try:
            json.dump(out, open(OUTF, 'w'))
        except Exception:
            pass
    log('v5f_d19b_fix_probe', 'probe', {'t_s': out.get('t_s'), 'FAIL': out.get('FAIL')})
    print(json.dumps({'t_s': out.get('t_s'), 'FAIL': out.get('FAIL')}, separators=(',', ':')))
