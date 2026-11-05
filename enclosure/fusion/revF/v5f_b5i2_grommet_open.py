# rev F block 5i-2 (2026-11-05): open the grommet's flange over the bore (B5i subtracted the bore from the sleeve only, so the
# 1.0 flange plate covered the USB-C opening and touched the bezel face: 0.14 mm3). Cut x +-11.3, z 7.7-20.5 through the grommet.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
ZC = 14.1
BX, BZ = 11.3, 6.4


def run(_context):
    X = Ctx(); out = {}
    try:
        g = X.body('GROMMET_usbc_F'); db = X.body('HOUSING_F_door')
        lg = [e for e in json.load(open(LOG)) if e['script'] == 'v5f_b5i_grommet']
        if not lg or 'FAIL' in lg[-1]['data'] or abs(lg[-1]['data']['grommet_cm3'] - g.volume) > 0.002:
            raise RuntimeError('guard: GROMMET_usbc_F %s cm3 is not the B5i result' % round(g.volume, 3))
        v0 = g.volume
        X.combine(g, [X.add(X.wbox(XC - BX, XC + BX, -96.0, -74.0, ZC - BZ, ZC + BZ), 'B5I2_bore_tmp')], op=CUT)
        g = X.body('GROMMET_usbc_F')
        out['cm3'] = [round(v0, 3), round(g.volume, 3)]; out['lumps'] = g.lumps.count
        out['names'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('GROMMET')]
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
        out['interf'] = X.interference(g, [X.body(n) for n in ('HOUSING_F_door', 'HOUSING_F_front', 'CRADLE_5807', 'PD_5807_env',
                                                               'KO_5807_pigtail', 'LEAD_PIGTAIL_20V', 'FOOT_RL', 'FOOT_RR')])
        sweep = {}
        for dy in (1.0, 3.0, 10.0, 30.0, 80.0):
            q = X.tbm.copy(db); X.union(q, X.tbm.copy(g)); mvw(X, q, 0.0, -dy, 0.0)
            sweep[str(dy)] = {n: vol_x(X, q, X.body(n)) for n in ('HOUSING_F_front', 'CRADLE_5807', 'PD_5807_env')}
        out['door_sweep_mm3'] = sweep
        out['probes'] = {'opening_y-85.0': not X.inside(g, XC, -85.0, ZC), 'opening_y-84.0': not X.inside(g, XC, -84.0, ZC),
                         'flange_x13_y-85.0': X.inside(g, XC + 13.0, -85.0, ZC), 'flange_z22_y-85.0': X.inside(g, XC, -85.0, 22.0),
                         'sleeve_wall_top_y-83': X.inside(g, XC, -83.0, ZC + BZ + 0.4)}
        out['box'] = [round(v, 2) for v in wbb(X, g)]
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b5i2_grommet_open', 'grommet', out)
    print(json.dumps(out))
