# rev F rework block R1b-2 (2026-11-04): split HOUSING_F_wip into the front shell and the rear door.
#   HOUSING_F_front = wip − (y < −55.0 and z > 2.5)  [the whole floor stays with the front]
#                     + lip: TOOL_inner_skin_1p2 ∩ (y −58.0…−55.0, z >= 6.5)  [1.2 thick, 3.0 into the door's zone]
#                     + the four Pi bosses (DOOR_F_b2 ∩ r 3.9, z 2.5–8.1, with their D4.0 insert holes)
#   HOUSING_F_door  = wip ∩ (y <= −55.3, z >= 2.8) − rebate: TOOL_inner_skin_1p4 ∩ (y −58.3…−55.3, z >= 6.5)
#                     [joint gap 0.3 at the plane and above the floor; lip clearance 0.2 radial, 0.3 at its end]
# Above the floor cove (z < 6.5) the joint is the plain 0.3 gap. HOUSING_E and HOUSING_F_wip hidden (kept).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
PI_AX = [(-42.2, -54.5), (15.8, -54.5), (-42.2, -5.5), (15.8, -5.5)]
YS, G, ZG, ZL = -55.0, 0.3, 2.5, 6.5


def run(_context):
    X = Ctx(); out = {}
    try:
        if X.body('HOUSING_F_front') is not None:
            raise RuntimeError('HOUSING_F_front exists already')
        B = adsk.fusion.BooleanTypes
        wip = X.body('HOUSING_F_wip')
        front = X.tbm.copy(wip)
        X.diff(front, X.wbox(-150, 150, -150, YS, ZG, 250))
        lip = X.tbm.copy(X.body('TOOL_inner_skin_1p2'))
        X.tbm.booleanOperation(lip, X.wbox(-150, 150, YS - 3.0, YS, ZL, 250), B.IntersectionBooleanType)
        out['lip_cm3'] = round(lip.volume, 3)
        X.union(front, lip)
        pib = X.tbm.copy(X.body('DOOR_F_b2'))
        cyl = None
        for (x, y) in PI_AX:
            c = X.wcyl_z(x, y, 3.9, ZG, 8.1)
            cyl = c if cyl is None else X.union(cyl, c)
        X.tbm.booleanOperation(pib, cyl, B.IntersectionBooleanType)
        out['pi_bosses_cm3'] = round(pib.volume, 3)
        X.union(front, pib)
        door = X.tbm.copy(wip)
        X.tbm.booleanOperation(door, X.wbox(-150, 150, -150, YS - G, ZG + G, 250), B.IntersectionBooleanType)
        reb = X.tbm.copy(X.body('TOOL_inner_skin_1p4'))
        X.tbm.booleanOperation(reb, X.wbox(-150, 150, YS - 3.0 - G, YS - G, ZL, 250), B.IntersectionBooleanType)
        out['rebate_cm3'] = round(reb.volume, 3)
        X.diff(door, reb)
        fb = X.add(front, 'HOUSING_F_front')
        db = X.add(door, 'HOUSING_F_door')
        out['cm3'] = {'wip': round(wip.volume, 3), 'front': round(fb.volume, 3), 'door': round(db.volume, 3)}
        out['lumps'] = {'front': fb.lumps.count, 'door': db.lumps.count}
        for nm in ('HOUSING_E', 'HOUSING_F_wip'):
            X.body(nm).isLightBulbOn = False
        # probes at z 60 across the side joint (outer joint half-width 77.1, inner 73.6 at y -55)
        pr = {}
        for s in (1, -1):
            k = '+x' if s > 0 else '-x'
            pr[k] = {'front_wall_y-54.8': X.inside(fb, XC + s * 75.5, -54.8, 60.0),
                     'gap_y-55.15': not X.inside(fb, XC + s * 76.5, -55.15, 60.0) and not X.inside(db, XC + s * 76.5, -55.15, 60.0),
                     'lip_front_y-56.5': X.inside(fb, XC + s * 74.3, -56.5, 60.0),
                     'rebate_door_void_y-56.5': not X.inside(db, XC + s * 74.3, -56.5, 60.0),
                     'door_skin_y-56.5': X.inside(db, XC + s * 76.6, -56.5, 60.0),
                     'front_void_outside_lip': not X.inside(fb, XC + s * 76.6, -56.5, 60.0),
                     'door_full_wall_y-59.5': X.inside(db, XC + s * 69.8, -59.5, 60.0)}
        pr['floor'] = {'front_floor_under_door': X.inside(fb, XC, -80.0, 1.25), 'gap_z2.65': not X.inside(db, XC, -83.0, 2.65) and not X.inside(fb, XC, -83.0, 2.65),
                       'door_wall_z3.5': X.inside(db, XC, -83.6, 3.5)}
        pr['pi_bosses'] = [X.inside(fb, x + 3.0, y, 5.0) and not X.inside(fb, x, y, 5.0) for (x, y) in PI_AX]
        out['probes'] = pr
        oth = [X.body(n) for n in ('PI5_F', 'PI5_F_cooler', 'SPK_L', 'SPK_R', 'TOUCH_PCB', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR')]
        out['front_interf_nonzero'] = {k: v for k, v in X.interference(fb, oth + [db]).items() if v > 0} or 'all 0'
        out['door_interf_nonzero'] = {k: v for k, v in X.interference(db, oth).items() if v > 0} or 'all 0'
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_r1b2_split', 'front + door', out)
    print(json.dumps(out))
