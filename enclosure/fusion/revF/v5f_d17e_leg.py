# rev F d17e (2026-11-06): the cranked column's leg 5.5 × 4.5 → 5.5 × 6.5 (y −60.5…−54.0) from the boss to the knee (z 10.5–21),
#   so its bending section about x is twice the old column's (the knee adds a 15.25 offset). Behind the box's rear face (gap
#   reported), 2.5 off the shell, 1.25 off the finger's line. Old state → MAIN_BRACKET_d17e (hidden). DRY (default True) reports only.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py'), encoding='utf-8').read())
import traceback
EXP = {'MAIN_BRACKET': 6.1301}
LEG2_BB = [-67.5, -62.0, -60.5, -54.0, 10.5, 21.0]
AUDD = os.path.expanduser('~/Documents/audit/data')
NEWP = ['TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'BME_HOOD', 'FOAM_bme_env', 'FOAM_bme_top_env']


def run(_context):
    X = Ctx(); out = {}; t0 = time.time(); dry = globals().get('DRY', True)
    try:
        for k, v in EXP.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard: %s %s' % (k, None if b is None else round(b.volume, 4)))
        if X.body('MAIN_BRACKET_d17e') is not None:
            raise RuntimeError('MAIN_BRACKET_d17e exists already')
        br0 = tb_copy(X, 'MAIN_BRACKET')
        br = X.tbm.copy(br0); X.union(br, wbox_rel(X, LEG2_BB))
        out['bracket_tb'] = {'cm3': round(br.volume, 4), 'lumps': br.lumps.count, 'added_mm3': round((br.volume - br0.volume) * 1000, 2)}
        names = json.load(open(os.path.join(AUDD, 'a2a_parts.json'), encoding='utf-8')) + NEWP + ['HOUSING_F_door']
        xs = {}
        for n in names:
            if n == 'MAIN_BRACKET' or X.body(n) is None:
                continue
            a = vol_x(X, X.tbm.copy(br), tb_copy(X, n))
            if a > 0:
                xs[n] = [a, vol_x(X, X.tbm.copy(br0), tb_copy(X, n))]
        out['bracket_x_parts_new_old'] = xs
        q = tb_copy(X, 'SPKBOX_R'); inter(X, q, wbox_rel(X, [-67.5, -62.0, -54.0, -40.0, 10.5, 21.0]))
        out['box_rear_face_y_min'] = round(wbb(X, q)[2], 2) if q.volume > 0 else None
        if not dry:
            ob = X.body('MAIN_BRACKET'); app = ob.appearance; mat = ob.material
            ob.name = 'MAIN_BRACKET_d17e'; ob.isLightBulbOn = False
            nb = X.add(br, 'MAIN_BRACKET')
            for attr, val in (('material', mat), ('appearance', app)):
                try:
                    setattr(nb, attr, val)
                except Exception:
                    pass
            I = lambda b_, x, y, z: X.inside(b_, XC + x, y, z)
            out['applied'] = {'bracket_cm3': round(nb.volume, 4), 'bracket_lumps': nb.lumps.count}
            out['probes'] = {'leg_back': I(nb, -64.75, -60.0, 15.0), 'leg_front': I(nb, -64.75, -54.5, 15.0),
                             'above_leg_front_open': not I(nb, -64.75, -54.5, 23.0), 'insert_hole_open': not I(nb, -65.0, -57.0, 5.0)}
        out['dry'] = dry
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d17e_leg', 'dry' if globals().get('DRY', True) else 'run', out)
    print(json.dumps(out, separators=(',', ':')))
