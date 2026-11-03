# rev F block 1d (2026-11-03): DOOR_F cuts - per screw axis: SJ5012 foot recess D13 x 0.5 (z 0-0.5), counterbore D6.5
# z 0.5-3.5 (DIN912 M3 head D5.5 x 3.0 ends flush with the recess floor), through hole D3.4 to the pad top (z 5.0);
# Pi insert holes D4.0 z 0.8-8.0 (Ruthex M2.5, insert top 0.5 below the land); intake field 10 x 10 x D2 on 3.0 pitch under
# the Pi fan (x -16.1..10.9, y -36.7..-9.7; rev D open area 314 mm2). One TemporaryBRep tool, combine CUT.
# --- paste v5f_common.py above this line ---
SCREWS = [(XC + 88.5, -7.0), (XC - 88.5, -7.0), (XC + 75.5, -45.75), (XC - 75.5, -45.75), (XC + 44.0, -68.5), (XC - 44.0, -68.5)]
PI_HOLES = [(-41.5, -54.5), (16.5, -54.5), (-41.5, -5.5), (16.5, -5.5)]
INTAKE = [(-16.1 + 3.0 * i, -36.7 + 3.0 * j) for i in range(10) for j in range(10)]


def run(_context):
    X = Ctx()
    door = X.body('DOOR_F')
    tb = None
    def u(t):
        nonlocal tb
        tb = t if tb is None else X.union(tb, t)
    for (x, y) in SCREWS:
        u(X.wcyl_z(x, y, 6.5, -0.5, 0.5))
        u(X.wcyl_z(x, y, 3.25, -0.5, 3.5))
        u(X.wcyl_z(x, y, 1.7, -0.5, 5.5))
    for (x, y) in PI_HOLES:
        u(X.wcyl_z(x, y, 2.0, 0.8, 8.5))
    for (x, y) in INTAKE:
        u(X.wcyl_z(x, y, 1.0, -0.5, 3.0))
    cut = X.add(tb, 'DOOR_cut_tmp')
    v0 = door.volume
    X.combine(door, [cut], op=adsk.fusion.FeatureOperations.CutFeatureOperation)
    door = X.body('DOOR_F')
    out = {'door_vol': (round(v0, 2), round(door.volume, 2)),
           'left_over': [b.name for b in X.comp.bRepBodies if b.name == 'DOOR_cut_tmp']}
    out['probes'] = {
        'recess_open_z0.25_r6': [not X.inside(door, x + 6.0, y, 0.25) for (x, y) in SCREWS],
        'cbore_open_z2_r3': [not X.inside(door, x + 3.0, y, 2.0) for (x, y) in SCREWS],
        'through_open_z4.5': [not X.inside(door, x, y, 4.5) for (x, y) in SCREWS],
        'under_head_z4.2_r2.5': [X.inside(door, x + 2.5, y, 4.2) for (x, y) in SCREWS],
        'pi_hole_open_z5': [not X.inside(door, x, y, 5.0) for (x, y) in PI_HOLES],
        'pi_floor_z0.4': [X.inside(door, x, y, 0.4) for (x, y) in PI_HOLES],
        'intake_open': sum(1 for (x, y) in INTAKE if not X.inside(door, x, y, 1.25)),
        'intake_bar_solid': sum(1 for (x, y) in INTAKE if X.inside(door, x + 1.5, y + 1.5, 1.25))}
    out['interf'] = X.interference(door, [X.body('HOUSING_E'), X.body('SLAB_frame')])
    log('v5f_b1d_door_cuts', 'door cuts', out)
    print(json.dumps(out))
