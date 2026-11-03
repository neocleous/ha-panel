# rev F block 1r-4 (2026-11-03): six M3 door bosses at the inset-6.8 positions (screw axis 6.0 from the door edge, so the
# r 5.5 pad stays 0.5 inside it; /home/claude/work/place_b1r.py). Same boss as v5f_b1b: D8, z 5.0-12.7, Ruthex RX-M3x5.7
# hole D4.0 z 5.0-11.7, 2.0 rib to the nearest INNER_E wall (+0.5 embed). NEW bodies -> interference -> combine JOIN.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
AXES = {'FL': (XC + 86.74, -7.66), 'FR': (XC - 86.74, -7.66), 'ML': (XC + 73.96, -45.63), 'MR': (XC - 73.96, -45.63),
        'RL': (XC + 44.0, -66.74), 'RR': (XC - 44.0, -66.74)}
RB, Z0, Z1, RH, ZH = 4.0, 5.0, 12.7, 2.0, 11.7


def run(_context):
    X = Ctx()
    out = {'axes': {k: (round(v[0] - XC, 2), v[1]) for k, v in AXES.items()}, 'ribs': {}}
    try:
        inner = X.body('INNER_E'); hb = X.body('HOUSING_E')

        def wall_dir(x, y, z=9.0, n=36):
            best = (1e9, None)
            for i in range(n):
                a = 2 * math.pi * i / n; lo, hi = 0.0, 40.0
                for _ in range(18):
                    m = (lo + hi) / 2
                    if X.inside(inner, x + m * math.cos(a), y + m * math.sin(a), z): lo = m
                    else: hi = m
                if lo < best[0]: best = (lo, a)
            return best

        tools = []
        for k, (x, y) in AXES.items():
            d, a = wall_dir(x, y)
            out['ribs'][k] = (round(d, 2), round(math.degrees(a), 1))
            tb = X.wcyl_z(x, y, RB, Z0, Z1)
            L = d + 0.5
            c = (x + math.cos(a) * L / 2, y + math.sin(a) * L / 2, (Z0 + Z1) / 2)
            ldir = V3(math.cos(a), math.sin(a) * C, -math.sin(a) * S)
            wdir = V3(-math.sin(a), math.cos(a) * C, -math.cos(a) * S)
            X.union(tb, X.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(Dw(*c), ldir, wdir, L / 10, RH / 10, (Z1 - Z0) / 10)))
            X.diff(tb, X.wcyl_z(x, y, 2.0, Z0 - 0.5, ZH))
            tools.append(X.add(tb, 'DBOSS_' + k))
        others = [X.body(n) for n in ('SLAB_frame', 'LCD_glass', 'DOOR_F', 'LCD_panel_body', 'LCD_pcb_76x110', 'PI5_F',
                                      'PI5_F_cooler', 'GPIO_plugA_env', 'GPIO_plugB_env', 'KO_K7_fan')]
        out['interf'] = {t.name: X.interference(t, others) for t in tools}
        bad = {k: v for k, v in out['interf'].items() if any(val > 0 for val in v.values())}
        if bad:
            for t in tools:
                t.isLightBulbOn = False
            raise RuntimeError('interference: %s' % json.dumps(bad))
        v0 = hb.volume
        X.combine(hb, tools)
        hb = X.body('HOUSING_E')
        out['housing_cm3'] = (round(v0, 3), round(hb.volume, 3))
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('DBOSS_')]
        pr = {}
        for k, (x, y) in AXES.items():
            pr[k] = {'hole_z8_open': not X.inside(hb, x, y, 8.0), 'wall_r3_z8': X.inside(hb, x + 3.0, y, 8.0) and X.inside(hb, x - 3.0, y, 8.0),
                     'cap_z12.2': X.inside(hb, x, y, 12.2), 'below_z4.5_open': not X.inside(hb, x, y, 4.5),
                     'outside_r4.2_z8_open': not X.inside(hb, x, y + 4.2, 8.0) or not X.inside(hb, x, y - 4.2, 8.0)}
        out['probes'] = pr
        out['all_ok'] = all(all(v.values()) for v in pr.values())
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b1r4_bosses', 'bosses inset 6.8', out)
    print(json.dumps(out))
