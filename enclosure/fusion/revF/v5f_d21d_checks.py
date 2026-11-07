# rev F d21d (2026-11-07), read-only: checks after d21c. The added material (new front minus HOUSING_F_front_d21: the four
#   pad layers) against every part and keep-out; the removed material can only open gaps. Cap / front, door / grommet, door /
#   cradle, front / LD2410C at rest; the LD2410C slot's clearance over the board's top edge; the cap's and pads' contact faces.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py'), encoding='utf-8').read())
import traceback
GUARD = {'HOUSING_F_front': 235.2569, 'HOUSING_F_cap': 9.9441, 'HOUSING_F_door': 47.2633}
AUDD = os.path.expanduser('~/Documents/audit/data')
NEWP = ['TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'BME_HOOD', 'FOAM_bme_env', 'FOAM_bme_top_env', 'HOUSING_F_door']


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        for k, v in GUARD.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard: %s %s' % (k, None if b is None else round(b.volume, 4)))
        add = tb_copy(X, 'HOUSING_F_front'); X.diff(add, tb_copy(X, 'HOUSING_F_front_d21'))
        rem = tb_copy(X, 'HOUSING_F_front_d21'); X.diff(rem, tb_copy(X, 'HOUSING_F_front'))
        out['front_added'] = [round(add.volume * 1000, 3), add.lumps.count] + [round(c, 2) for c in wbb(X, add)]
        out['front_removed'] = [round(rem.volume * 1000, 3), rem.lumps.count] + [round(c, 2) for c in wbb(X, rem)]
        names = json.load(open(os.path.join(AUDD, 'a2a_parts.json'), encoding='utf-8')) + NEWP
        ko = [b.name for b in X.comp.bRepBodies if b.name.startswith('KO_')]
        ab = wbb(X, add); hits = {}
        for n in list(dict.fromkeys(names + ko)):
            b = X.body(n)
            if b is None or n == 'HOUSING_F_front':
                continue
            pb = wbb(X, b)
            if pb[0] > ab[1] + 0.1 or pb[1] < ab[0] - 0.1 or pb[2] > ab[3] + 0.1 or pb[3] < ab[2] - 0.1 or pb[4] > ab[5] + 0.1 or pb[5] < ab[4] - 0.1:
                continue
            v = vol_x(X, add, b)
            if v > 0.005:
                hits[n] = v
        out['added_x_parts'] = hits
        pairs = [('HOUSING_F_cap', 'HOUSING_F_front'), ('HOUSING_F_door', 'GROMMET_usbc_F'), ('HOUSING_F_door', 'CRADLE_5807'),
                 ('HOUSING_F_front', 'LD2410C_env_F'), ('HOUSING_F_door', 'HOUSING_F_front')]
        out['pairs_mm3'] = {a + ' | ' + b: vol_x(X, tb_copy(X, a), tb_copy(X, b)) for a, b in pairs}
        I = lambda n, x, y, z: X.inside(X.body(n), XC + x, y, z)
        out['contact'] = {'pad_top_172.59': I('HOUSING_F_front', -38.61, -32.85, 172.59), 'boss_end_172.61': I('HOUSING_F_cap', -40.36, -32.85, 172.61),
                          'gap_none_pad': not I('HOUSING_F_cap', -40.36, -32.85, 172.59), 'gap_none_boss': not I('HOUSING_F_front', -40.36, -32.85, 172.61)}
        ld = tb_copy(X, 'LD2410C_env_F'); out['ld_env_bb'] = [round(c, 3) for c in wbb(X, ld)]
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d21d_checks', 'run', out)
    print(json.dumps(out, separators=(',', ':')))
