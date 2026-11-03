# rev F block 1r-6 (2026-11-03): DOOR_F cuts (Daniel 21:01, feet option 3: adhesive feet stay on, away from the screws).
# Per screw: counterbore D6.5 z -0.5 -> 3.5 (DIN912 M3 head D5.5 x 3.0, top 0.5 below the door underside), hole D3.4
# through the pad (z 5.0); no foot recess at the screws. Per foot: SJ5012 recess D13 x 0.5 (z 0 -> 0.5) at front
# (XC +-76, -6.9) and rear (XC +-25, -69.4) - edge >= 7.5, >= 10.75 from a screw axis (1.15 to the counterbore),
# >= 9.5 from a Pi insert, clear of the intake field. Pi insert holes D4.0 z 0.8 -> 8.5; intake 10 x 10 x D2.0 on 3.0
# pitch from (-16.1, -36.7). One TemporaryBRep tool, combine CUT.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
SCREWS = [(XC + 86.74, -7.66), (XC - 86.74, -7.66), (XC + 73.96, -45.63), (XC - 73.96, -45.63), (XC + 44.0, -66.74), (XC - 44.0, -66.74)]
FEET = {'FL': (XC + 76.0, -6.9), 'FR': (XC - 76.0, -6.9), 'RL': (XC + 25.0, -69.4), 'RR': (XC - 25.0, -69.4)}
PI_HOLES = [(-41.5, -54.5), (16.5, -54.5), (-41.5, -5.5), (16.5, -5.5)]
INTAKE = [(-16.1 + 3.0 * i, -36.7 + 3.0 * j) for i in range(10) for j in range(10)]


def run(_context):
    X = Ctx()
    out = {}
    try:
        door = X.body('DOOR_F')
        tb = None
        def u(t):
            nonlocal tb
            tb = t if tb is None else X.union(tb, t)
        for (x, y) in SCREWS:
            u(X.wcyl_z(x, y, 3.25, -0.5, 3.5))
            u(X.wcyl_z(x, y, 1.7, -0.5, 5.5))
        for (x, y) in FEET.values():
            u(X.wcyl_z(x, y, 6.5, -0.5, 0.5))
        for (x, y) in PI_HOLES:
            u(X.wcyl_z(x, y, 2.0, 0.8, 8.5))
        for (x, y) in INTAKE:
            u(X.wcyl_z(x, y, 1.0, -0.5, 3.0))
        cut = X.add(tb, 'DOOR_cut_tmp')
        v0 = door.volume
        X.combine(door, [cut], op=CUT)
        door = X.body('DOOR_F')
        out['door_cm3'] = (round(v0, 3), round(door.volume, 3))
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name == 'DOOR_cut_tmp']
        out['probes'] = {
            'cbore_open_z2_r3': [not X.inside(door, x + 3.0, y, 2.0) for (x, y) in SCREWS],
            'head_top_recess_z0.25_r3': [not X.inside(door, x - 3.0, y, 0.25) for (x, y) in SCREWS],
            'no_recess_at_screw_z0.25_r4.5': [X.inside(door, x + 4.5, y, 0.25) and X.inside(door, x - 4.5, y, 0.25) for (x, y) in SCREWS],
            'through_open_z4.5': [not X.inside(door, x, y, 4.5) for (x, y) in SCREWS],
            'under_head_z4.2_r2.5': [X.inside(door, x + 2.5, y, 4.2) for (x, y) in SCREWS],
            'foot_recess_open_z0.25_r6.2': [not X.inside(door, x + 6.2, y, 0.25) and not X.inside(door, x - 6.2, y, 0.25) for (x, y) in FEET.values()],
            'foot_floor_z0.75': [X.inside(door, x, y, 0.75) for (x, y) in FEET.values()],
            'pi_hole_open_z5': [not X.inside(door, x, y, 5.0) for (x, y) in PI_HOLES],
            'pi_floor_z0.4': [X.inside(door, x, y, 0.4) for (x, y) in PI_HOLES]}
        out['intake'] = {'open': sum(1 for (x, y) in INTAKE if not X.inside(door, x, y, 1.25)),
                         'bars_solid': sum(1 for (x, y) in INTAKE if X.inside(door, x + 1.5, y + 1.5, 1.25))}
        out['all_ok'] = all(all(v) for v in out['probes'].values()) and out['intake']['open'] == 100 and out['intake']['bars_solid'] == 100
        out['interf'] = X.interference(door, [X.body('HOUSING_E'), X.body('SLAB_frame')])
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b1r6_door_cuts', 'door cuts', out)
    print(json.dumps(out))
