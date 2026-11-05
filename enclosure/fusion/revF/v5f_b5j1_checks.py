# rev F block 5j-1 (2026-11-05), read-only: block-5 checks.
#   1. Interference of HOUSING_F_front / HOUSING_F_door / GROMMET_usbc_F with every current part (bbox pre-filter, PI5_F
#      cropped), and with each other; non-zero results with the overlap's world box.
#   2. Walls under the cloth along rays (REF entry = cloth face; part runs): chin, both sides, rear corners, door back, back
#      above the door, bottom-fillet bend, hard top band; joint gap; magnets (door pocket / skin / lap gap / lip pocket / pad
#      skin); LD2410C air in front of the antenna; touch PCB lifted 0.9 vs the front shell.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
SKIP_PREFIX = ('HOUSING_F', 'HOUSING_E', 'REF_', 'INNER_', 'TOOL_', 'V11', 'RENDER_', 'sk_')
SKIP_SUFFIX = ('_b4n', '_b4d', '_b1', '_b2', '_revE', '_revD', '_tmp', '_wip', '_r2')
STALE = ('HOUSING_shell', 'DOOR_tray', 'REF_outer_hidden', 'DOOR_plate', 'DOOR_F', 'GROMMET_usbc', 'TOUCH_pcb', 'LD2410C_env',
         'SENSOR_strip_L', 'SENSOR_strip_R', 'SPK_driver_D40', 'PD_trigger_env_20V')


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        fb = X.body('HOUSING_F_front'); db = X.body('HOUSING_F_door'); g = X.body('GROMMET_usbc_F')
        out['cm3'] = {'front': round(fb.volume, 3), 'door': round(db.volume, 3), 'grommet': round(g.volume, 3) if g else None}
        out['lumps'] = {'front': fb.lumps.count, 'door': db.lumps.count}
        # current parts: every body not a housing, reference, tool, stale rev D/E leftover or superseded copy
        parts = []
        for b in X.comp.bRepBodies:
            n = b.name
            if n.startswith(SKIP_PREFIX) or n.endswith(SKIP_SUFFIX) or n in STALE or n.startswith(('VOICEPE_', 'BUCK_', 'AMP_', 'SPK_driver', 'SENSOR_strip')) \
                    or n == 'GROMMET_usbc_F' or (n.startswith('PI5_') and n not in ('PI5_F', 'PI5_F_cooler')) \
                    or (n.startswith('TOUCH_') and n != 'TOUCH_PCB'):
                continue
            parts.append(b)
        out['n_parts'] = len(parts)
        res = {}
        for hn, hb in (('front', fb), ('door', db), ('grommet', g)):
            if hb is None:
                continue
            lb = hb.boundingBox; hits = {}
            for o in parts:
                ob = o.boundingBox
                if ob.maxPoint.x < lb.minPoint.x or ob.minPoint.x > lb.maxPoint.x or ob.maxPoint.y < lb.minPoint.y or \
                        ob.minPoint.y > lb.maxPoint.y or ob.maxPoint.z < lb.minPoint.z or ob.minPoint.z > lb.maxPoint.z:
                    continue
                q = X.tbm.copy(o)
                if o.name == 'PI5_F':
                    inter(X, q, X.wbox(-150, 150, -70, 5, 0, 40))
                inter(X, q, X.tbm.copy(hb))
                v = q.volume * 1000
                if v > 0.005:
                    hits[o.name] = [round(v, 2), [round(c, 1) for c in wbb(X, q)]]
            res[hn] = hits or 'all 0'
        res['front_x_door'] = vol_x(X, fb, db)
        if g:
            res['grommet_x_front'] = vol_x(X, g, fb); res['grommet_x_door'] = vol_x(X, g, db)
        out['interference_mm3'] = res
        out['t_interf_s'] = round(time.time() - t0, 1)

        def wall(o, d, part, tmax=40.0):
            ref = [r[0] for r in ray_hits(X, o, d, ('REF_F_outer',))]
            return {'ref_t': round(ref[0], 2) if ref else None, 'front': solid_runs(X, o, d, 'HOUSING_F_front', tmax),
                    'door': solid_runs(X, o, d, 'HOUSING_F_door', tmax)}
        r2 = math.sqrt(0.5)
        out['walls'] = {
            'chin_x30_z40_-y': wall((XC + 30.0, 20.0, 40.0), (0, -1, 0), 'HOUSING_F_front', 25.0),
            'side_+x_y-10_z120_-x': wall((XC + 120.0, -10.0, 120.0), (-1, 0, 0), 'HOUSING_F_front'),
            'side_-x_y-45_z30_+x': wall((XC - 120.0, -45.0, 30.0), (1, 0, 0), 'HOUSING_F_front'),
            'rear_corner_+x_z40_n': wall((XC + 120.0, -100.0, 40.0), (-0.70, 0.71, 0.0), 'HOUSING_F_door', 120.0),
            'rear_corner_-x_z120_front': wall((XC - 80.0, -80.0, 120.0), (0.60, 0.80, 0.0), 'HOUSING_F_front', 80.0),
            'door_back_x-30_z100_+y': wall((XC - 30.0, -120.0, 100.0), (0, 1, 0), 'HOUSING_F_door', 50.0),
            'bend_+x_y-30_45deg': wall((XC + 110.0, -30.0, -10.0), (-r2, 0, r2), 'HOUSING_F_front', 40.0),
            'bend_chin_x0_45deg': wall((XC, 20.0, -10.0), (0, -r2, r2), 'HOUSING_F_front', 40.0),
            'hard_top_back_x0_z179_+y': wall((XC, -100.0, 179.0), (0, 1, 0), 'HOUSING_F_front', 60.0),
        }
        out['slot_face_hard_d12.5_Z36_x0'] = fb.pointContainment(P3(XC / 10, -1.25, 3.6)) in INS
        out['slot_face_hard_d12.5_Z-91_x60'] = fb.pointContainment(P3((XC + 60.0) / 10, -1.25, -9.1)) in INS
        out['joint_gap'] = {str(z): [not X.inside(fb, XC + sx * 76.0, -55.15, z) and not X.inside(db, XC + sx * 76.0, -55.15, z)
                                     for sx in (1, -1)] for z in (25.0, 60.0)}
        mp = {}
        for s in (1, -1):
            for (zm, ym) in MAG_D1:
                p, n, xr, nw = magnet_point(X, s, zm, ym)
                fi = lambda k: fb.pointContainment(qpt(p, n, k)) in INS
                di = lambda k: db.pointContainment(qpt(p, n, k)) in INS
                mp['%+d,%g' % (s, zm)] = {'door_pocket_open': not di(1.0), 'door_skin': di(-0.3), 'lap_gap': not fi(-0.8) and not di(-0.8),
                                          'pad_skin': fi(-1.05), 'lip_pocket_open': not fi(-2.0)}
        out['magnets'] = mp
        a = math.radians(LD_A); nld = (-math.sin(a), math.cos(a), 0.0)
        hs = [r for r in ray_hits(X, (XC + LD_F[0], LD_F[1], LD_F[2]), nld, ('HOUSING_F_front',))]
        out['ld2410c_air_mm'] = round(hs[0][0], 2) if hs else None
        q = X.tbm.copy(X.body('TOUCH_PCB')); mvw(X, q, 0, 0, 0.9)
        out['touch_pcb_lift0.9_x_front_mm3'] = vol_x(X, q, fb)
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b5j1_checks', 'checks', out)
    print(json.dumps(out))
