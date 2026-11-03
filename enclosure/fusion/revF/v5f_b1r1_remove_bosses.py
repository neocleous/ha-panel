# rev F block 1r-1 (2026-11-03): start of the block-1 revision (Daniel 21:01: shell ring with an inside radius, door inset
# 6.8, feet away from the screws).
# 1. DOOR_F -> DOOR_F_b1 and FOOT_* -> FOOT_*_b1, hidden (kept).
# 2. Remove the six b1 door bosses (v5f_b1b) from HOUSING_E: tool = INNER_E ∩ (per b1 axis: cylinder r 4.3, z 4.6-13.1,
#    + rib box 2.4 wide, z 4.6-13.1, from the axis to 3.0 past the wall along the b1 rib direction), combine CUT.
#    The rib direction is recomputed exactly as v5f_b1b did (36 directions x 18 bisections at z 9 on INNER_E, which is
#    unchanged since). The ∩ INNER_E keeps the shell wall itself untouched. Expect HOUSING_E 248.68 -> 246.44 cm3.
# b1r scripts load the common header from ~/Documents/v5f_common.py (a copy of the repo file) instead of pasting it.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
OLD = {'FL': (XC + 88.5, -7.0), 'FR': (XC - 88.5, -7.0), 'ML': (XC + 75.5, -45.75), 'MR': (XC - 75.5, -45.75),
       'RL': (XC + 44.0, -68.5), 'RR': (XC - 44.0, -68.5)}
Z0, Z1 = 4.6, 13.1


def run(_context):
    X = Ctx()
    out = {}
    try:
        ren = {}
        for nm in ['DOOR_F'] + ['FOOT_' + k for k in OLD]:
            b = X.body(nm)
            if b is not None and X.body(nm + '_b1') is None:
                b.name = nm + '_b1'; b.isLightBulbOn = False; ren[nm] = round(b.volume, 3)
        out['renamed_hidden_cm3'] = ren
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

        tool = None; ribs = {}
        for k, (x, y) in OLD.items():
            d, a = wall_dir(x, y)
            ribs[k] = (round(d, 2), round(math.degrees(a), 1), a)
            t = X.wcyl_z(x, y, 4.3, Z0, Z1)
            L = d + 3.0
            c = (x + math.cos(a) * L / 2, y + math.sin(a) * L / 2, (Z0 + Z1) / 2)
            ldir = V3(math.cos(a), math.sin(a) * C, -math.sin(a) * S)
            wdir = V3(-math.sin(a), math.cos(a) * C, -math.cos(a) * S)
            X.union(t, X.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(Dw(*c), ldir, wdir, L / 10, 0.24, (Z1 - Z0) / 10)))
            tool = t if tool is None else X.union(tool, t)
        out['ribs_d_deg'] = {k: v[:2] for k, v in ribs.items()}
        X.tbm.booleanOperation(tool, X.tbm.copy(inner), adsk.fusion.BooleanTypes.IntersectionBooleanType)
        cut = X.add(tool, 'B1R_bosscut_tmp')
        out['tool_cm3'] = round(cut.volume, 3)
        v0 = hb.volume
        X.combine(hb, [cut], op=CUT)
        hb = X.body('HOUSING_E')
        out['housing_cm3'] = (round(v0, 3), round(hb.volume, 3), round(v0 - hb.volume, 3))
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name == 'B1R_bosscut_tmp']
        pr = {}
        for k, (x, y) in OLD.items():
            d, _, a = ribs[k]
            pr[k] = {'axis_z8_open': not X.inside(hb, x, y, 8.0),
                     'boss_wall_z8_open': not X.inside(hb, x + 3.0, y, 8.0) and not X.inside(hb, x - 3.0, y, 8.0),
                     'rib_mid_z9_open': not X.inside(hb, x + math.cos(a) * d / 2, y + math.sin(a) * d / 2, 9.0),
                     'wall_kept_z9': X.inside(hb, x + math.cos(a) * (d + 1.0), y + math.sin(a) * (d + 1.0), 9.0)}
        out['probes'] = pr
        out['all_probes_ok'] = all(all(v.values()) for v in pr.values())
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b1r1_remove_bosses', 'remove b1 bosses', out)
    print(json.dumps(out))
