# rev F d1b (2026-11-06): d1's combines split MAIN_BRACKET by lump (lesson 43 / "JOIN of disjoint tools leaves separate
#   bodies"): MAIN_BRACKET = −x half (boss, plug, insert hole), MAIN_BRACKET (1) = +x half (boss, NO insert hole),
#   MAIN_BRACKET (2) = the +x half's plug. Rebuilt as ONE body (two lumps) from TemporaryBRep copies: union of the three,
#   +x insert hole cut; the three split bodies renamed *_d1split_* and hidden.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
FB = 49.5, -58.0


def run(_context):
    X = Ctx(); out = {}
    try:
        R = X.body('MAIN_BRACKET'); L = X.body('MAIN_BRACKET (1)'); Pl = X.body('MAIN_BRACKET (2)')
        if R is None or L is None or Pl is None:
            raise RuntimeError('split bodies not as expected')
        exp = {R.name: 2.6709, L.name: 2.7342, Pl.name: 0.0188}
        for b in (R, L, Pl):
            if abs(b.volume - exp[b.name]) > 0.0005:
                raise RuntimeError('guard %s %.4f' % (b.name, b.volume))
        t = X.tbm.copy(R); X.union(t, X.tbm.copy(L)); X.union(t, X.tbm.copy(Pl))
        X.diff(t, X.wcyl_z(XC + FB[0], FB[1], 2.0, 2.4, 9.5))
        R.name = 'MAIN_BRACKET_d1split_R'; L.name = 'MAIN_BRACKET_d1split_L'; Pl.name = 'MAIN_BRACKET_d1split_plug'
        for b in (R, L, Pl):
            b.isLightBulbOn = False
        nb = X.add(t, 'MAIN_BRACKET')
        out['bracket'] = {'cm3': round(nb.volume, 4), 'lumps': nb.lumps.count, 'lump_cm3': [round(l.volume, 4) for l in nb.lumps]}
        P = lambda x, y, z: X.inside(nb, XC + x, y, z)
        out['probes'] = {k: {'boss_wall_z5_r3': P(s * FB[0] + 3.0, FB[1], 5.0), 'insert_open_z5': not P(s * FB[0], FB[1], 5.0),
                             'insert_open_z9.3': not P(s * FB[0], FB[1], 9.3), 'old_hole_filled_z10.5': P(s * FB[0], FB[1], 10.5),
                             'post_z40': P(s * 49.5, -60.5, 40.0), 'insert_boss_M2.5_open': not P(s * 41.5, -60.0, 37.5)}
                         for s, k in ((1, 'L'), (-1, 'R'))}
        oth = ['HOUSING_F_front', 'HOUSING_F_door', 'SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'PI5_F', 'PI5_F_cooler', 'MAIN_pcb',
               'MAIN_back_env', 'PIPWR_a_env', 'LEAD_PI_POWER', 'LEAD_SPK_L', 'LEAD_SPK_R', 'USBA_plug_env', 'USBA_cable_env',
               'CRADLE_5807', 'PD_5807_env', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR', 'MAIN_front_env']
        xx = {n: vol_x(X, X.tbm.copy(nb), X.tbm.copy(X.body(n))) for n in oth if X.body(n) is not None}
        out['bracket_x'] = {k: v for k, v in xx.items() if v > 0} or 'all 0'
        old = X.body('MAIN_BRACKET_d0')
        out['vs_d0_front_env'] = vol_x(X, X.tbm.copy(old), X.tbm.copy(X.body('MAIN_front_env')))
        out['names'] = sorted(b.name for b in X.comp.bRepBodies if b.name.startswith('MAIN_BRACKET'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d1b_bracket_merge', 'run', out)
    print(json.dumps(out, separators=(',', ':')))
