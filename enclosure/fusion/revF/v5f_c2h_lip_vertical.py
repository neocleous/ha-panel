# rev F cap block c2h (2026-11-05): make the cap's locating lip vertical so the cap can be put on straight down.
#   Found while writing up c2: the lip (c1, kept in c2) is the band 6.1…7.3 inside REF_F_outer at z 173.3–175.85, so it
#   leans with the walls (back wall 0.38 mm per mm forward going up, sides ≈ 0.4 inward). The flange's inner face (d 5.9)
#   leans the same way, 0.2 outside the lip. Lowered vertically, the lip's bottom edge (z 173.3) is outside the flange's top
#   inner edge (z 175.3) by 0.38 × 2.0 − 0.2 ≈ 0.55: the cap could not be fitted (c1 had the same lip).
#   Fix: new lip = the band's top slice (z 175.3–175.85, d 6.1…7.3) copied straight down in 0.5 steps and cut at z 173.3, i.e.
#   a vertical skirt with the footprint the band has at the flange's top: 0.2 off the flange at z 175.3, the gap opening to
#   ≈ 1.0 at z 173.3. The old lip's outer sliver (old − new − bosses) is removed. Front shell unchanged.
#   Gates: insertion sweep – cap moved up h = 0.1 … 4.0 ∩ front shell top = 0 for every h (before: reported); cap ∩ front 0;
#   1 lump; VEML_env ∩ cap 0; KO_capkey_* ∩ cap 0. Commit: HOUSING_F_cap → HOUSING_F_cap_c2a (hidden), new HOUSING_F_cap.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
MODE = 'commit'
Y_TC = -22.6
V_FRONT, V_CAP = 237.2748, 9.931
SCREWS = {'BL': (25.91, -37.80), 'BR': (-25.91, -37.80), 'SL': (43.36, -32.85), 'SR': (-43.36, -32.85)}
HS = (0.1, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 3.0, 4.0)


def tool(t):
    return 'TOOL_cap_off%s' % (('%.2f' % t).rstrip('0').rstrip('.')).replace('.', 'p')


def band(X, t_out, t_in, z0, z1, y1):
    b = tb_copy(X, tool(t_in)); inter(X, b, X.wbox(-250, 250, -250, y1, z0, z1))
    if t_out > 0:
        X.diff(b, tb_copy(X, tool(t_out)))
    return b


def sweep(X, cap, FT):
    r = {}
    for h in HS:
        c = X.tbm.copy(cap); mvw(X, c, 0.0, 0.0, h)
        r['%.2f' % h] = vol_x(X, c, FT)
    return r


def run(_context):
    X = Ctx(); out = {'MODE': MODE}
    t0 = time.time()
    try:
        F, Cp = X.body('HOUSING_F_front'), X.body('HOUSING_F_cap')
        out['guard'] = [round(F.volume, 4), round(Cp.volume, 4)]
        if abs(F.volume - V_FRONT) > 0.001 or abs(Cp.volume - V_CAP) > 0.001:
            raise RuntimeError('volume guard %s' % out['guard'])
        if X.body('HOUSING_F_cap_c2a') is not None:
            raise RuntimeError('HOUSING_F_cap_c2a exists')
        FT = tb_copy(X, 'HOUSING_F_front'); inter(X, FT, X.wbox(-250, 250, -250, 250, 165.0, 260.0))
        CAP = tb_copy(X, 'HOUSING_F_cap')
        out['sweep_before_mm3'] = sweep(X, CAP, FT)
        top = band(X, 6.1, 7.3, 175.3, 175.85, Y_TC)
        NL = X.tbm.copy(top)
        for k in range(1, 6):
            s = X.tbm.copy(top); mvw(X, s, 0.0, 0.0, -0.5 * k); X.union(NL, s)
        inter(X, NL, X.wbox(-250, 250, -250, Y_TC, 173.3, 175.85))
        OL = band(X, 6.1, 7.3, 173.3, 175.85, Y_TC)
        BO = None
        for k, (cx, cy) in SCREWS.items():
            b = X.wcyl_z(XC + cx, cy, 4.0, 172.4, 177.7)
            BO = b if BO is None else X.union(BO, b)
        RM = X.tbm.copy(OL); X.diff(RM, X.tbm.copy(NL)); X.diff(RM, BO)
        out['lip_mm3'] = {'old': round(OL.volume * 1000, 1), 'new': round(NL.volume * 1000, 1), 'removed': round(RM.volume * 1000, 1)}
        C2 = X.tbm.copy(CAP); X.diff(C2, RM); X.union(C2, NL)
        out['cap'] = {'cm3': round(C2.volume, 4), 'lumps': C2.lumps.count, 'faces': C2.faces.count}
        g = {'cap_x_front': vol_x(X, C2, FT), 'sweep_after_mm3': sweep(X, C2, FT),
             'veml': vol_x(X, C2, tb_copy(X, 'VEML_env')),
             'lanes': {k: vol_x(X, C2, tb_copy(X, 'KO_capkey_' + k)) for k in SCREWS}}
        RT = tb_copy(X, 'REF_F_outer'); g['cap_outside_REF_mm3'] = round(C2.volume * 1000 - vol_x(X, C2, RT), 3)
        out['gates'] = g
        ok = (C2.lumps.count == 1 and g['cap_x_front'] < 0.01 and all(v < 0.01 for v in g['sweep_after_mm3'].values())
              and g['veml'] < 0.01 and all(v < 0.01 for v in g['lanes'].values()))
        out['gates_ok'] = ok
        if MODE == 'commit' and ok:
            app_, mat_ = Cp.appearance, Cp.material
            Cp.name = 'HOUSING_F_cap_c2a'; Cp.isLightBulbOn = False
            try:
                nb = X.add(C2, 'HOUSING_F_cap'); nb.material = mat_; nb.appearance = app_
            except Exception:
                Cp.name = 'HOUSING_F_cap'; Cp.isLightBulbOn = True
                raise
            out['committed'] = round(nb.volume, 4)
            out['dupes'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('HOUSING_F_cap (')]
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_c2h_lip_vertical', MODE, out)
    print(json.dumps(out, separators=(',', ':'))[:5000])
