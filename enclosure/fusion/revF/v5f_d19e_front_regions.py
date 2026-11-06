# rev F d19e (2026-11-06), read-only: every overhang region of the front shell printed floor down (d19a's method, all regions,
#   not the top 10), with area, world box, mean angle from flat and height above the bed; and the same for the cap printed
#   top face down, the door, the 5807 cradle and the speaker boxes in their d19a orientations. Writes d19e_regions.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/HA_panel_renders/scripts_d/v5f_d19a_print_assess.py'), encoding='utf-8').read().split('def run(')[0])
import traceback
OUTF2 = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d19e_regions.json')
JOBS = [('Front shell', 'HOUSING_F_front', '+z'), ('Top cap', 'HOUSING_F_cap', '-z'), ('Rear door', 'HOUSING_F_door', '+z'),
        ('5807 cradle', 'CRADLE_5807', '+y'), ('Speaker box L', 'SPKBOX_L', '+y'), ('Speaker box R', 'SPKBOX_R', '+y'),
        ('ReSpeaker carrier', 'RESP_CARRIER', 'slab_front_down'), ('BME680 hood', 'BME_HOOD', '-y')]


def regions_all(P, T, U):
    hp = lambda i: P[i][0] * U[0] + P[i][1] * U[1] + P[i][2] * U[2]
    nodes = set(i for t in T for i in t[:3]); hv = {i: hp(i) for i in nodes}; h0 = min(hv.values())
    ov = []
    for t in T:
        d = t[3][0] * U[0] + t[3][1] * U[1] + t[3][2] * U[2]
        if d < -0.7071 and not (hv[t[0]] - h0 < 0.3 and hv[t[1]] - h0 < 0.3 and hv[t[2]] - h0 < 0.3):
            ov.append((t, d))
    par = {}

    def f(x):
        while par.setdefault(x, x) != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    for t, d in ov:
        ra = f(t[0]); par[f(t[1])] = ra; par[f(t[2])] = ra
    reg = {}
    for t, d in ov:
        k = f(t[0]); e = reg.setdefault(k, [0.0, [1e9, -1e9, 1e9, -1e9, 1e9, -1e9], 0.0, 1e9])
        e[0] += t[4]; e[2] += -d * t[4]
        for p in (P[t[0]], P[t[1]], P[t[2]]):
            for j in range(3):
                e[1][2 * j] = min(e[1][2 * j], p[j]); e[1][2 * j + 1] = max(e[1][2 * j + 1], p[j])
        e[3] = min(e[3], min(hv[t[0]], hv[t[1]], hv[t[2]]) - h0)
    lst = sorted(reg.values(), key=lambda e: -e[0])
    return [[round(e[0], 1), [round(v, 1) for v in e[1]], round(math.degrees(math.acos(min(1.0, e[2] / e[0]))), 0), round(e[3], 1)]
            for e in lst if e[0] >= 2.0]


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        for (lab, n, dn) in JOBS:
            P, T = mesh(X.body(n))
            out[lab] = {'dir': dn, 'regions': regions_all(P, T, DIRS[dn])}
        out['t_s'] = round(time.time() - t0, 1)
        json.dump(out, open(OUTF2, 'w'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    print(json.dumps({'t_s': out.get('t_s'), 'FAIL': out.get('FAIL'), 'n': {k: len(v['regions']) for k, v in out.items() if isinstance(v, dict)}}))
