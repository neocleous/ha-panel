# rev F rework block R1a (2026-11-04): base body for the rear-door architecture (Daniel 2026-11-03 23:41 – 2026-11-04
# 08:40: removable back, solid floor, no floor door, magnets at the door edges, USB-C at the bottom of the door).
# HOUSING_F_wip = copy of HOUSING_E
#   - the six b1r4 door bosses + ribs: tool = INNER_E ∩ (cylinder r 4.3 + 2.4-wide rib box to 3.0 past the wall along
#     the b1r4 rib direction), z 4.95–13.1 (starts 0.05 below the boss bottom, so the R3.5 floor cove stays);
#   + solid floor = REF_E_outer ∩ z <= 2.5 (fills the old door opening and the 5.6 ring band);
#   - floor holes: Pi insert holes D4.0 z 0.8–2.6 (the Pi bosses themselves are added after the split, R1b), the 10 x 10
#     D2 intake field under the cooler, four SJ5012 recesses D13 x 0.5, four door-screw holes D3.4 + D6.5 x 1.0
#     counterbores (DIN912 M3 x 6 from below, head 2.0 proud of the underside, feet 3.5).
# DOOR_F -> DOOR_F_b2 and FOOT_* -> FOOT_*_b2 (hidden, kept); new FOOT_* envelopes D12.7, z -3.0–0.5.
# Layout (from the 2026-11-04 floor probe): flat underside = 6 mm inside the outer edge (R6 edge fillet); feet centres
# >= 7.5 inside it. Door-screw axes 3.3–3.5 in front of the door's inner wall at z 8, counterbores inside the flat zone.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
B1R4 = {'FL': (86.74, -7.66, 0.0, 10.19), 'FR': (-86.74, -7.66, 180.0, 10.19), 'ML': (73.96, -45.63, 320.0, 9.91),
        'MR': (-73.96, -45.63, 220.0, 9.91), 'RL': (44.0, -66.74, 290.0, 10.02), 'RR': (-44.0, -66.74, 250.0, 10.03)}
PI_AX = [(-42.2, -54.5), (15.8, -54.5), (-42.2, -5.5), (15.8, -5.5)]          # world x, y (b2c, after the -0.7 shift)
GRID = [(-16.8 + 3.0 * i, -36.7 + 3.0 * j) for i in range(10) for j in range(10)]  # world (b2c)
FEET = {'FL': (84.0, -6.5), 'FR': (-84.0, -6.5), 'RL': (30.0, -69.0), 'RR': (-30.0, -69.0)}     # x_rel, y
DSCREW = {'DL': (50.0, -67.0), 'DR': (-50.0, -67.0), 'DCL': (19.0, -74.5), 'DCR': (-19.0, -74.5)}  # x_rel, y
Z0, Z1 = 4.95, 13.1


def run(_context):
    X = Ctx(); out = {}
    try:
        if X.body('HOUSING_F_wip') is not None:
            raise RuntimeError('HOUSING_F_wip exists already')
        ren = {}
        for nm in ['DOOR_F', 'FOOT_FL', 'FOOT_FR', 'FOOT_RL', 'FOOT_RR']:
            b = X.body(nm)
            if b is not None and X.body(nm + '_b2') is None:
                b.name = nm + '_b2'; b.isLightBulbOn = False; ren[nm] = round(b.volume, 3)
        out['renamed_hidden_cm3'] = ren
        B = adsk.fusion.BooleanTypes
        tool = None
        for k, (xr, y, deg, d) in B1R4.items():
            x = XC + xr; a = math.radians(deg)
            t = X.wcyl_z(x, y, 4.3, Z0, Z1)
            L = d + 3.0
            c = (x + math.cos(a) * L / 2, y + math.sin(a) * L / 2, (Z0 + Z1) / 2)
            ldir = V3(math.cos(a), math.sin(a) * C, -math.sin(a) * S)
            wdir = V3(-math.sin(a), math.cos(a) * C, -math.cos(a) * S)
            X.union(t, X.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(Dw(*c), ldir, wdir, L / 10, 0.24, (Z1 - Z0) / 10)))
            tool = t if tool is None else X.union(tool, t)
        X.tbm.booleanOperation(tool, X.tbm.copy(X.body('INNER_E')), B.IntersectionBooleanType)
        out['boss_tool_cm3'] = round(tool.volume, 3)
        wip = X.tbm.copy(X.body('HOUSING_E'))
        v0 = wip.volume
        X.diff(wip, tool)
        v1 = wip.volume
        fl = X.tbm.copy(X.body('REF_E_outer'))
        X.tbm.booleanOperation(fl, X.wbox(-150, 150, -150, 150, -1.0, 2.5), B.IntersectionBooleanType)
        out['floor_plate_cm3'] = round(fl.volume, 3)
        X.union(wip, fl)
        v2 = wip.volume
        cut = None
        def addc(t):
            nonlocal cut
            cut = t if cut is None else X.union(cut, t)
        for (x, y) in PI_AX:
            addc(X.wcyl_z(x, y, 2.0, 0.8, 2.6))
        for (x, y) in GRID:
            addc(X.wcyl_z(x, y, 1.0, -0.5, 3.0))
        for k, (xr, y) in FEET.items():
            addc(X.wcyl_z(XC + xr, y, 6.5, -0.5, 0.5))
        for k, (xr, y) in DSCREW.items():
            addc(X.wcyl_z(XC + xr, y, 1.7, -0.5, 3.0)); addc(X.wcyl_z(XC + xr, y, 3.25, -0.5, 1.0))
        X.diff(wip, cut)
        v3 = wip.volume
        w = X.add(wip, 'HOUSING_F_wip')
        out['cm3'] = {'HOUSING_E': round(v0, 3), 'minus_bosses': round(v1, 3), 'plus_floor': round(v2, 3), 'minus_holes': round(v3, 3)}
        for k, (xr, y) in FEET.items():
            f = X.add(X.wcyl_z(XC + xr, y, 6.35, -3.0, 0.5), 'FOOT_' + k); f.isLightBulbOn = True
        hb = X.body('HOUSING_F_wip')
        pr = {}
        pr['floor_solid_z1.25'] = all(X.inside(hb, XC + xr, y, 1.25) for (xr, y) in ((0, -40), (60, -20), (70, -20), (-70, -20), (0, -70), (40, -5)))
        pr['old_bosses_gone_z8'] = {k: not X.inside(hb, XC + xr, y, 8.0) and not X.inside(hb, XC + xr + 3.0, y, 8.0) for k, (xr, y, _, _) in B1R4.items()}
        pr['intake_open'] = sum(1 for (x, y) in GRID if not X.inside(hb, x, y, 1.25))
        pr['intake_bars_solid'] = sum(1 for (x, y) in GRID if X.inside(hb, x + 1.5, y + 1.5, 1.25))
        pr['pi_holes'] = [(not X.inside(hb, x, y, 1.5)) and X.inside(hb, x, y, 0.4) for (x, y) in PI_AX]
        pr['feet_recess'] = {k: (not X.inside(hb, XC + xr, y, 0.25)) and X.inside(hb, XC + xr, y, 0.75) and X.inside(hb, XC + xr + 7.0, y, 0.25) for k, (xr, y) in FEET.items()}
        pr['screw_holes'] = {k: (not X.inside(hb, XC + xr, y, 2.0)) and (not X.inside(hb, XC + xr + 2.5, y, 0.5)) and X.inside(hb, XC + xr + 2.5, y, 1.75) for k, (xr, y) in DSCREW.items()}
        # cove kept: solid 1 mm in front of the wall's inner face at z 3.0 (cove spans u 2.5–4.2 there)
        pr['cove_z3'] = {'%g,%g' % p: X.inside(hb, XC + p[0], p[1], 3.0) for p in ((0.0, -81.3), (95.9, -10.0), (-95.9, -10.0))}
        out['probes'] = pr
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_r1a_floor', 'solid floor + bosses out', out)
    print(json.dumps(out))
