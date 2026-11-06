# rev F d9g (2026-11-06): BME680 tray, assembly fixes from the d9f sweeps.
#   - The floor lip (w 6.7…7.5, up to u -7.0) stopped the board sliding in along -w: it goes; the floor stays flush to w 7.5
#     and gets a groove (w 5.5…6.9, 0.6 deep) that the hood's back plate drops into.
#   - The hood's slots met the pins edge-on (the hood slides toward the wall): the hood now comes in above the pins and drops
#     3.5 along them, through Ø2.4 holes; its top plate stays 0.7 off the wall (the wall leans in above the tray), the 1 mm
#     top foam closes that gap.
#   HOUSING_F_front: changed in place (old -> HOUSING_F_front_d9f, hidden). BME_HOOD rebuilt (old -> BME_HOOD_d9f, hidden).
import os
exec(open(os.path.expanduser('~/Documents/HA_panel_renders/scripts_d/v5f_d9c_bme_cup.py')).read())   # frame, fbox, air, P
import traceback
EXP = {'HOUSING_F_front': 235.8961, 'BME_HOOD': 0.772}


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        for k, v in EXP.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard: %s %s' % (k, None if b is None else round(b.volume, 4)))
        for n in ('HOUSING_F_front_d9f', 'BME_HOOD_d9f'):
            if X.body(n) is not None:
                raise RuntimeError('%s exists already' % n)
        fb = X.body('HOUSING_F_front')
        c = X.add(X.tbm.copy(fb), 'HOUSING_F_front_d9f'); c.isLightBulbOn = False
        v0 = fb.volume
        AIR = air(X)
        region = fbox(X, -18, 18, -26, 16, -12, 12)
        inter(X, AIR, region)
        cut = fbox(X, -13.0, 13.0, -8.0, -6.9, 6.6, 7.6); inter(X, cut, X.tbm.copy(AIR))
        X.union(cut, fbox(X, -12.9, 12.9, -8.6, -7.9, 5.5, 6.9))
        q = X.tbm.copy(cut); inter(X, q, tb_copy(X, 'HOUSING_F_front'))
        out['cut_mm3'] = round(q.volume * 1000, 2)
        X.combine(fb, [X.add(cut, 'D9G_cut_tmp')], op=CUT); fb = X.body('HOUSING_F_front')
        out['front_cm3'] = [round(v0, 4), round(fb.volume, 4)]; out['front_lumps'] = fb.lumps.count
        # hood
        oh = X.body('BME_HOOD'); app = oh.appearance; oh.name = 'BME_HOOD_d9f'; oh.isLightBulbOn = False
        lair = air(X, 'TOOL_inner_skin_1p4'); inter(X, lair, X.tbm.copy(region))
        hood = fbox(X, -12.9, 12.9, -8.5, 9.2, 5.5, 6.7)
        tp = fbox(X, -13.9, 13.9, 8.0, 9.2, -12.0, 6.7); inter(X, tp, lair)
        X.union(hood, tp)
        for s in (1, -1):
            X.diff(hood, fcyl_u(X, s * 11.7, 3.0, 7.5, 9.7, 1.2))
        hb = X.add(hood, 'BME_HOOD')
        try:
            hb.appearance = app
        except Exception:
            pass
        out['hood_cm3'] = round(hb.volume, 4); out['hood_lumps'] = hb.lumps.count
        out['hood_x_front_mm3'] = vol_x(X, tb_copy(X, 'BME_HOOD'), tb_copy(X, 'HOUSING_F_front'))
        out['hood_x_env_mm3'] = vol_x(X, tb_copy(X, 'BME_HOOD'), tb_copy(X, 'BME680_env'))
        out['hood_x_foams_mm3'] = [vol_x(X, tb_copy(X, 'BME_HOOD'), tb_copy(X, 'FOAM_bme_env')),
                                   vol_x(X, tb_copy(X, 'BME_HOOD'), tb_copy(X, 'FOAM_bme_top_env'))]
        PR = lambda b_, t, u, w: X.inside(b_, XC + P(t, u, w)[0], P(t, u, w)[1], P(t, u, w)[2])
        out['probes'] = {'lip_gone': not PR(fb, 5, -7.5, 7.1), 'floor_flush': PR(fb, 5, -8.1, 7.1), 'groove': not PR(fb, 5, -8.3, 6.2),
                         'under_groove': PR(fb, 5, -8.9, 6.2), 'side_wall': PR(fb, 11.7, 0, 2.0), 'pin': PR(fb, -11.7, 10.0, 3.0),
                         'hood_in_groove': PR(hb, 5, -8.3, 6.1), 'hood_hole': not PR(hb, 11.7, 8.6, 3.0), 'hood_top': PR(hb, 0, 8.6, 2.0),
                         'hood_wall_gap': not PR(hb, 0, 8.6, -3.4)}
        out['left_over'] = [b_.name for b_ in X.comp.bRepBodies if b_.name.endswith('_tmp')]
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d9g_bme_groove_hood', 'run', out)
    print(json.dumps(out, separators=(',', ':')))
