# rev F block 5i (2026-11-05): USB-C grommet body on the door (brief block 5; rev D GROMMET_usbc pattern: flange on the cloth
# face + sleeve through the panel), around the 5807 cradle's bezel (B4g: x ±11.0, z 8.0–20.2, face y −84.6).
#   GROMMET_usbc_F (separate print, fixed to the door, comes off with it):
#   bore    x ±11.3, z 7.7–20.5 (0.3 round the bezel: the door + grommet slide off backwards over it)
#   sleeve  0.8 wall -> x ±12.1, z 6.9–21.3, from the cloth face (REF_F_outer) through cloth + wall to the door's inner
#           surface (s −0.7); door cutout x ±12.2, z 6.8–21.4 (B5f)
#   flange  x ±15.1, z 4.7–23.5, R2.0 corners, 1.0 on the cloth face (REF_F_outer moved 1.0 in −y minus REF_F_outer, so it
#           follows the back face); covers the cloth's cut edge by ≥ 2.2
#   pins    2 × Ø1.8 heat-stake pins (rev D strip-pin pattern) at (x_rel ±13.6, z 14.1) through Ø2.1 door holes, 1.5 proud of
#           the door's inner surface for the stake head – no adhesive-only fixing (Daniel's rule).
#   ZC (inlet centre) follows the 5807: + 6.5 if V11 option 1 raises it.
#   As run on 2026-11-05 the bore was cut from the sleeve only; B5i-2 then opened the flange (this file now does both).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
ZC = 14.1
BX, BZ = 11.3, 6.4          # bore half sizes
SW = 0.8                    # sleeve wall
FX, FZ, FR = 15.1, 9.4, 2.0  # flange half sizes, corner radius
PX = 13.6                   # pin x_rel


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        if X.body('GROMMET_usbc_F') is not None:
            raise RuntimeError('GROMMET_usbc_F exists already')
        db = X.body('HOUSING_F_door')
        lg = [e for e in json.load(open(LOG)) if e['script'] == 'v5f_b5g_recess_feet']
        if not lg or 'FAIL' in lg[-1]['data'] or abs(lg[-1]['data']['door_cm3'][1] - db.volume) > 0.003:
            raise RuntimeError('guard: HOUSING_F_door %s cm3 is not the B5g result' % round(db.volume, 3))
        # wall at the pin axes, measured 2 mm outboard of the pin holes (REF entry = cloth face, door exit = inner surface)
        yw = {}
        for sx in (1, -1):
            o = (XC + sx * (PX + 2.0), -100.0, ZC)
            ref = [r for r in ray_hits(X, o, (0, 1, 0), ('REF_F_outer',))]
            runs = solid_runs(X, o, (0, 1, 0), 'HOUSING_F_door', 25.0)
            yw[sx] = (-100.0 + ref[0][0], -100.0 + runs[0][1])
        out['pin_wall_y_cloth_inner'] = {k: [round(a, 2), round(b, 2)] for k, (a, b) in yw.items()}
        # flange
        sh = tb_copy(X, 'REF_F_outer'); mvw(X, sh, 0.0, -1.0, 0.0); X.diff(sh, tb_copy(X, 'REF_F_outer'))
        pr = X.wbox(XC - FX + FR, XC + FX - FR, -95.0, -78.0, ZC - FZ, ZC + FZ)
        X.union(pr, X.wbox(XC - FX, XC + FX, -95.0, -78.0, ZC - FZ + FR, ZC + FZ - FR))
        for sx in (1, -1):
            for sz in (1, -1):
                xx = XC + sx * (FX - FR); zz = ZC + sz * (FZ - FR)
                X.union(pr, X.tbm.createCylinderOrCone(Dw(xx, -95.0, zz), FR / 10, Dw(xx, -78.0, zz), FR / 10))
        inter(X, sh, pr)
        out['flange_cm3'] = round(sh.volume, 3)
        # sleeve
        sl = X.wbox(XC - BX - SW, XC + BX + SW, -95.0, -75.0, ZC - BZ - SW, ZC + BZ + SW)
        ref3 = tb_copy(X, 'REF_F_outer'); mvw(X, ref3, 0.0, -0.3, 0.0)        # sleeve starts 0.3 inside the flange
        inter(X, sl, ref3)
        shr = tb_copy(X, 'INNER_E'); X.diff(shr, tb_copy(X, 'TOOL_inner_skin_0p7'))
        X.diff(sl, shr)
        X.diff(sl, X.wbox(XC - BX, XC + BX, -96.0, -74.0, ZC - BZ, ZC + BZ))
        out['sleeve_cm3'] = round(sl.volume, 3)
        X.union(sh, sl)
        for sx in (1, -1):
            yc, yi = yw[sx]
            X.union(sh, X.tbm.createCylinderOrCone(Dw(XC + sx * PX, yc - 0.5, ZC), 0.09, Dw(XC + sx * PX, yi + 1.5, ZC), 0.09))
        X.diff(sh, X.wbox(XC - BX, XC + BX, -96.0, -74.0, ZC - BZ, ZC + BZ))   # bore through the flange too (as run: B5i-2)
        g = X.add(sh, 'GROMMET_usbc_F')
        out['grommet_cm3'] = round(g.volume, 3); out['lumps'] = g.lumps.count
        oth = [X.body(n) for n in ('HOUSING_F_door', 'HOUSING_F_front', 'CRADLE_5807', 'PD_5807_env', 'KO_5807_pigtail', 'LEAD_PIGTAIL_20V',
                                   'FOOT_RL', 'FOOT_RR')]
        out['interf'] = X.interference(g, oth)
        # door + grommet pulled straight back: vs the front shell, the cradle (bezel) and the 5807
        sweep = {}
        for dy in (1.0, 3.0, 10.0, 30.0, 80.0):
            q = X.tbm.copy(db); X.union(q, X.tbm.copy(g)); mvw(X, q, 0.0, -dy, 0.0)
            sweep[str(dy)] = {n: vol_x(X, q, X.body(n)) for n in ('HOUSING_F_front', 'CRADLE_5807', 'PD_5807_env')}
        out['door_sweep_mm3'] = sweep
        out['probes'] = {'bore_open': not X.inside(g, XC, -84.0, ZC), 'sleeve_wall_top': X.inside(g, XC, -84.0, ZC + BZ + 0.4),
                         'flange_x14.5': X.inside(g, XC + 14.5, yw[1][0] - 0.5, ZC),
                         'pin_in_cavity': X.inside(g, XC + PX, yw[1][1] + 1.0, ZC)}
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b5i_grommet', 'grommet', out)
    print(json.dumps(out))
