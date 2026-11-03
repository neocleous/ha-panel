# rev F block 1c (2026-11-03): DOOR_F additions - six screw pads D11 z 2.5 -> 5.0 under the shell bosses, and four Pi 5
# bosses (K10; Ruthex RX-M2.5x5.7) D7.6 z 2.5 -> 7.5 + D6.0 land z 7.5 -> 8.0 (Pi PCB bottom at z 8.0) at the Pi holes
# (world (-41.5, -54.5), (16.5, -54.5), (-41.5, -5.5), (16.5, -5.5)). NEW body -> interference -> combine JOIN into DOOR_F.
# --- paste v5f_common.py above this line ---
SCREWS = [(XC + 88.5, -7.0), (XC - 88.5, -7.0), (XC + 75.5, -45.75), (XC - 75.5, -45.75), (XC + 44.0, -68.5), (XC - 44.0, -68.5)]
PI_HOLES = [(-41.5, -54.5), (16.5, -54.5), (-41.5, -5.5), (16.5, -5.5)]


def run(_context):
    X = Ctx()
    door = X.body('DOOR_F')
    tb = None
    for (x, y) in SCREWS:
        c = X.wcyl_z(x, y, 5.5, 2.0, 5.0)              # starts 0.5 inside the plate
        tb = c if tb is None else X.union(tb, c)
    for (x, y) in PI_HOLES:
        X.union(tb, X.wcyl_z(x, y, 3.8, 2.0, 7.5))
        X.union(tb, X.wcyl_z(x, y, 3.0, 7.4, 8.0))
    add = X.add(tb, 'DOOR_add_tmp')
    others = [X.body(n) for n in ('HOUSING_E', 'SLAB_frame', 'LCD_glass')]
    out = {'interf': X.interference(add, others)}
    if any(v > 0 for v in out['interf'].values()):
        log('v5f_b1c_door_pads_pi_bosses', 'ABORT', out)
        raise RuntimeError('interference %s' % out['interf'])
    v0 = door.volume
    X.combine(door, [add])
    door = X.body('DOOR_F')
    out['door_vol'] = (round(v0, 2), round(door.volume, 2))
    out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name == 'DOOR_add_tmp']
    out['probes'] = {
        'pads_z4.8': [X.inside(door, x + 5.0, y, 4.8) for (x, y) in SCREWS],
        'pi_boss_z7': [X.inside(door, x + 3.5, y, 7.0) for (x, y) in PI_HOLES],
        'pi_land_z7.9_r2.9': [X.inside(door, x + 2.9, y, 7.9) for (x, y) in PI_HOLES],
        'pi_land_z7.9_r3.2_open': [not X.inside(door, x + 3.2, y, 7.9) for (x, y) in PI_HOLES]}
    out['interf_after'] = X.interference(door, [X.body('HOUSING_E')])
    log('v5f_b1c_door_pads_pi_bosses', 'door additions', out)
    print(json.dumps(out))
