# rev F block 6 / V11-2 (2026-11-05): after B6V-1 – USB-C grommet at the raised inlet, the chosen Pi-power route, checks.
#   1. GROMMET_usbc_F rebuilt with the B5i geometry at ZC 20.6 (old → GROMMET_usbc_F_b5, hidden): flange 1.0 on the cloth
#      face x ±15.1, z 11.2–30.0 (R2), sleeve 0.8 round the raised bezel (bore x ±11.3, z 14.2–27.0), 2 × Ø1.8 heat-stake
#      pins at (x_rel ±13.6, z 20.6).
#   2. PIPWR_a_env (hidden): the B4j V11a_px envelope (CableCreation-type 90° adapter 12.5 × 7.5 × 12 on the Pi USB-C, the
#      straight plug 12.4 × 6.6 × 20 + relief Ø6 × 12 out of its +x port, both plug orientations) + the main-board end: plug
#      12.4 × 6.6 × 20 under the USB4105 (x_rel 18.8…31.2, y −69.9…−63.3, z 14.0–33.9; receptacle on the main board's back
#      face at its bottom edge z 34, axis y −66.6). LEAD_PI_POWER (hidden): Ø5 cable from the Pi-end relief (x +6.3, y −65.3,
#      z 11) down to the floor (z 5.5) and up into the main-board plug's relief with R8.5.
#   3. Checks: the new / moved bodies (grommet, cradle, PD_5807_env, KO_5807_pigtail, LEAD_PIGTAIL_20V, PIPWR_a_env,
#      LEAD_PI_POWER, front, door) against every current part; door + grommet pulled straight back (1…80 mm) against the
#      front, cradle and 5807 envelope; routed Pi-power length (plug tip to plug tip).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
ZC = 20.6
BX, BZ, SW = 11.3, 6.4, 0.8
FX, FZ, FR, PX = 15.1, 9.4, 2.0, 13.6
EXPECT = {'HOUSING_F_front': 237.926, 'HOUSING_F_door': 53.536, 'CRADLE_5807': 1.598, 'GROMMET_usbc_F': 0.488}
SKIP_PREFIX = ('HOUSING_F', 'HOUSING_E', 'REF_', 'INNER_', 'TOOL_', 'V11', 'RENDER_', 'sk_')
SKIP_SUFFIX = ('_b4n', '_b4d', '_b1', '_b2', '_b5', '_revE', '_revD', '_tmp', '_wip', '_r2')
STALE = ('HOUSING_shell', 'DOOR_tray', 'REF_outer_hidden', 'DOOR_plate', 'DOOR_F', 'GROMMET_usbc', 'TOUCH_pcb', 'LD2410C_env',
         'SENSOR_strip_L', 'SENSOR_strip_R', 'SPK_driver_D40', 'PD_trigger_env_20V')


def current_parts(X):
    parts = []
    for b in X.comp.bRepBodies:
        n = b.name
        if n.startswith(SKIP_PREFIX) or n.endswith(SKIP_SUFFIX) or n in STALE or n.startswith(('VOICEPE_', 'BUCK_', 'AMP_', 'SPK_driver', 'SENSOR_strip')) \
                or (n.startswith('PI5_') and n not in ('PI5_F', 'PI5_F_cooler')) or (n.startswith('TOUCH_') and n != 'TOUCH_PCB'):
            continue
        parts.append(b)
    return parts + [X.body(n) for n in ('HOUSING_F_front', 'HOUSING_F_door')]


def tube(X, pts, dia):
    r = dia / 20; t = None
    for i in range(len(pts) - 1):
        p, q = pts[i], pts[i + 1]
        c = X.tbm.createCylinderOrCone(Dw(XC + p[0], p[1], p[2]), r, Dw(XC + q[0], q[1], q[2]), r)
        t = c if t is None else X.union(t, c)
    for p in pts[1:-1]:
        X.union(t, X.tbm.createSphere(Dw(XC + p[0], p[1], p[2]), r))
    return t


def plen(pts):
    return sum(math.sqrt(sum((pts[i + 1][k] - pts[i][k]) ** 2 for k in range(3))) for i in range(len(pts) - 1))


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.002:
                raise RuntimeError('guard: %s volume %s, expected %s' % (k, None if b is None else round(b.volume, 3), v))
        if X.body('GROMMET_usbc_F_b5') is not None or X.body('PIPWR_a_env') is not None:
            raise RuntimeError('B6V-2 ran already')
        # 1. grommet (B5i geometry, bore through the flange as in B5i-2)
        go = X.body('GROMMET_usbc_F'); go.name = 'GROMMET_usbc_F_b5'; go.isLightBulbOn = False
        yw = {}
        for sx in (1, -1):
            o = (XC + sx * (PX + 2.0), -100.0, ZC)
            ref = [r for r in ray_hits(X, o, (0, 1, 0), ('REF_F_outer',))]
            runs = solid_runs(X, o, (0, 1, 0), 'HOUSING_F_door', 25.0)
            yw[sx] = (-100.0 + ref[0][0], -100.0 + runs[0][1])
        out['pin_wall_y_cloth_inner'] = {k: [round(a, 2), round(b, 2)] for k, (a, b) in yw.items()}
        sh = tb_copy(X, 'REF_F_outer'); mvw(X, sh, 0.0, -1.0, 0.0); X.diff(sh, tb_copy(X, 'REF_F_outer'))
        pr = X.wbox(XC - FX + FR, XC + FX - FR, -95.0, -78.0, ZC - FZ, ZC + FZ)
        X.union(pr, X.wbox(XC - FX, XC + FX, -95.0, -78.0, ZC - FZ + FR, ZC + FZ - FR))
        for sx in (1, -1):
            for sz in (1, -1):
                xx = XC + sx * (FX - FR); zz = ZC + sz * (FZ - FR)
                X.union(pr, X.tbm.createCylinderOrCone(Dw(xx, -95.0, zz), FR / 10, Dw(xx, -78.0, zz), FR / 10))
        inter(X, sh, pr)
        sl = X.wbox(XC - BX - SW, XC + BX + SW, -95.0, -75.0, ZC - BZ - SW, ZC + BZ + SW)
        ref3 = tb_copy(X, 'REF_F_outer'); mvw(X, ref3, 0.0, -0.3, 0.0)
        inter(X, sl, ref3)
        shr = tb_copy(X, 'INNER_E'); X.diff(shr, tb_copy(X, 'TOOL_inner_skin_0p7'))
        X.diff(sl, shr)
        X.union(sh, sl)
        for sx in (1, -1):
            yc, yi = yw[sx]
            X.union(sh, X.tbm.createCylinderOrCone(Dw(XC + sx * PX, yc - 0.5, ZC), 0.09, Dw(XC + sx * PX, yi + 1.5, ZC), 0.09))
        X.diff(sh, X.wbox(XC - BX, XC + BX, -96.0, -74.0, ZC - BZ, ZC + BZ))
        g = X.add(sh, 'GROMMET_usbc_F')
        out['grommet_cm3'] = [0.488, round(g.volume, 3)]; out['grommet_lumps'] = g.lumps.count
        # 2. Pi-power route
        pe = X.tbm.copy(X.body('V11a_px'))
        X.union(pe, X.wbox(XC + 18.8, XC + 31.2, -69.9, -63.3, 14.0, 33.9))
        pb = X.add(pe, 'PIPWR_a_env'); pb.isLightBulbOn = False
        R = 8.5
        pts = [(6.3, -65.3, 11.0), (10.0, -65.6, 8.0), (13.0, -66.0, 5.8), (16.5, -66.6, 5.5)]
        arc = [(16.5 + R * math.sin(math.radians(a)), -66.6, 14.0 - R * math.cos(math.radians(a))) for a in (22.5, 45.0, 67.5, 90.0)]
        route = pts + arc
        lb = X.add(tube(X, route, 5.0), 'LEAD_PI_POWER'); lb.isLightBulbOn = False
        L_route = plen(route)
        out['pipwr_mm'] = {'pi_plug_rigid': 20.0, 'pi_relief': 12.0, 'cable_route': round(L_route, 1), 'mb_plug_rigid': 20.0,
                           'tip_to_tip': round(20.0 + 12.0 + L_route + 20.0, 1), 'slack_0.2m': round(200.0 - (20.0 + 12.0 + L_route + 20.0), 1)}
        # 3. checks
        parts = current_parts(X)
        moved = ['GROMMET_usbc_F', 'CRADLE_5807', 'PD_5807_env', 'KO_5807_pigtail', 'LEAD_PIGTAIL_20V', 'PIPWR_a_env', 'LEAD_PI_POWER',
                 'HOUSING_F_front', 'HOUSING_F_door']
        res = {}
        for mn in moved:
            m = X.body(mn); mb = m.boundingBox; hits = {}
            for o in parts:
                if o.name == mn or (o.name in moved and moved.index(o.name) < moved.index(mn)):
                    continue                                   # each pair of moved bodies once
                ob = o.boundingBox
                if ob.maxPoint.x < mb.minPoint.x or ob.minPoint.x > mb.maxPoint.x or ob.maxPoint.y < mb.minPoint.y or \
                        ob.minPoint.y > mb.maxPoint.y or ob.maxPoint.z < mb.minPoint.z or ob.minPoint.z > mb.maxPoint.z:
                    continue
                lo = [max(mb.minPoint.x, ob.minPoint.x), max(mb.minPoint.y, ob.minPoint.y), max(mb.minPoint.z, ob.minPoint.z)]
                hi = [min(mb.maxPoint.x, ob.maxPoint.x), min(mb.maxPoint.y, ob.maxPoint.y), min(mb.maxPoint.z, ob.maxPoint.z)]
                box = X.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(P3((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2),
                                      V3(1, 0, 0), V3(0, 1, 0), hi[0] - lo[0] + 0.02, hi[1] - lo[1] + 0.02, hi[2] - lo[2] + 0.02))
                qa = X.tbm.copy(m); inter(X, qa, box)
                if qa.volume <= 0:
                    continue
                qb = X.tbm.copy(o); inter(X, qb, X.tbm.copy(box)); inter(X, qa, qb)
                v = qa.volume * 1000
                if v > 0.005:
                    hits[o.name] = round(v, 2)
            res[mn] = hits or 'all 0'
        out['interference_mm3'] = res
        db = X.body('HOUSING_F_door'); g = X.body('GROMMET_usbc_F')
        sweep = {}
        for dy in (1.0, 3.0, 10.0, 30.0, 80.0):
            q = X.tbm.copy(db); X.union(q, X.tbm.copy(g)); mvw(X, q, 0.0, -dy, 0.0)
            sweep[str(dy)] = {n: vol_x(X, q, X.body(n)) for n in ('HOUSING_F_front', 'CRADLE_5807', 'PD_5807_env')}
        out['door_sweep_mm3'] = sweep
        out['probes'] = {'bore_open': not X.inside(g, XC, -84.0, ZC), 'sleeve_wall_top': X.inside(g, XC, -84.0, ZC + BZ + 0.4),
                         'pin_in_cavity': X.inside(g, XC + PX, yw[1][1] + 1.0, ZC),
                         'receptacle_window_z': [round(15.4 + 6.5, 1), round(19.1 + 6.5, 1)]}
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b6v2_v11_grommet_route', 'build', out)
    print(json.dumps(out))
