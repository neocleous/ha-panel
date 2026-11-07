# rev F d22e (2026-11-07), read-only: checks after d22d. The added material (new front minus HOUSING_F_front_d22) against every
#   part, keep-out, lead and envelope; cap / front at rest and with the cap lifted 0.1-5.0 mm (its way on from above); the M3
#   heads' seats and holes open; the four added lumps' boxes.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py'), encoding='utf-8').read())
import traceback
GUARD = {'HOUSING_F_front': 235.9107, 'HOUSING_F_cap': 9.9441, 'HOUSING_F_door': 47.2633, 'HOUSING_F_front_d22': 235.2569}
AUDD = os.path.expanduser('~/Documents/audit/data')
NEWP = ['TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'BME_HOOD', 'FOAM_bme_env', 'FOAM_bme_top_env', 'HOUSING_F_door']
AX, AY = 43.36, -32.85


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        for k, v in GUARD.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard: %s %s' % (k, None if b is None else round(b.volume, 4)))
        add = tb_copy(X, 'HOUSING_F_front'); X.diff(add, tb_copy(X, 'HOUSING_F_front_d22'))
        rem = tb_copy(X, 'HOUSING_F_front_d22'); X.diff(rem, tb_copy(X, 'HOUSING_F_front'))
        out['front_added'] = [round(add.volume * 1000, 2), add.lumps.count] + [round(c, 2) for c in wbb(X, add)]
        out['front_removed_mm3'] = round(rem.volume * 1000, 3)
        out['added_lumps'] = []
        for L in add.lumps:
            q = X.tbm.copy(L)
            out['added_lumps'].append([round(q.volume * 1000, 1)] + [round(c, 2) for c in wbb(X, q)])
        names = json.load(open(os.path.join(AUDD, 'a2a_parts.json'), encoding='utf-8')) + NEWP
        others = [b.name for b in X.comp.bRepBodies if b.name.startswith(('KO_', 'LEAD_')) or b.name.endswith('_env')]
        ab = wbb(X, add); hits = {}; n_tested = 0
        for n in list(dict.fromkeys(names + others)):
            b = X.body(n)
            if b is None or n in ('HOUSING_F_front', 'HOUSING_F_front_d22'):
                continue
            pb = wbb(X, b)
            if pb[0] > ab[1] + 0.6 or pb[1] < ab[0] - 0.6 or pb[2] > ab[3] + 0.6 or pb[3] < ab[2] - 0.6 or pb[4] > ab[5] + 0.6 or pb[5] < ab[4] - 0.6:
                continue
            n_tested += 1
            v = vol_x(X, add, b)
            if v > 0.0:
                hits[n] = v
        out['added_x_bodies'] = hits; out['bodies_near'] = n_tested
        out['cap_front_mm3'] = vol_x(X, tb_copy(X, 'HOUSING_F_cap'), tb_copy(X, 'HOUSING_F_front'))
        lift = {}
        for dz in (0.1, 0.3, 0.7, 1.0, 2.0, 3.0, 4.0, 5.0):
            cp = mvw(X, tb_copy(X, 'HOUSING_F_cap'), 0.0, 0.0, dz)
            lift['%.1f' % dz] = vol_x(X, cp, add)
        out['cap_lifted_x_added_mm3'] = lift
        I = lambda n, x, y, z: X.inside(X.body(n), XC + x, y, z)
        pr = {}
        for s, tag in ((1, 'SL'), (-1, 'SR')):
            pr[tag] = {'seat_open': not I('HOUSING_F_front', s * 41.0, AY, 169.3), 'head_space_open': not I('HOUSING_F_front', s * AX, AY, 168.0),
                       'hole_open': not I('HOUSING_F_front', s * AX, AY, 171.0), 'pad_top_172.59': I('HOUSING_F_front', s * 38.61, AY, 172.59),
                       'boss_end_172.61': I('HOUSING_F_cap', s * 40.36, AY, 172.61), 'web_in': I('HOUSING_F_front', s * 34.0, -38.0, 170.0),
                       'frib_in': I('HOUSING_F_front', s * 39.0, -25.0, 165.0)}
        out['probes'] = pr; out['probes_ok'] = all(all(v.values()) for v in pr.values())
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d22e_checks', 'run', out)
    print(json.dumps(out, separators=(',', ':')))
