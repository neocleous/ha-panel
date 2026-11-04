# rev F rework R1c-2 (2026-11-04): lower-lane notches in the lip (R1c-1 left 13.38 mm3 of lip/pad in KO_K5_LL), the door's
# four M3 bosses, the USB-C slot and the 5807 envelope.
#   notch: r 4.0 along the LL / LR lane axes (world x +-47.5), y -63.5...-53.4.
#   door bosses at x_rel +-19 (y -74.5) and +-50 (y -67.0): D8, z 2.8-10.5 (0.3 above the floor), Ruthex M3 hole D4.0
#     z 2.8-9.5, 2.0 rib to the nearest INNER_E wall (wall_dir at z 7, +0.5 embed). DIN912 M3 x 6 from below through the
#     floor's D3.4 hole and D6.5 x 1.0 counterbore (R1a): 4.2 mm in the insert.
#   USB-C: 5807 flat, PCB z 14.0-15.6, receptacle on top (z 15.6-18.86, socket centre z 17.2), centred on the door
#     (x = XC), receptacle face 0.1 inside the outer surface (y -84.6); slot through the door wall x +-10.5, z 12.7-19.2 (covers the 1.0 underside keep-out).
#     PD_5807_env = PCB 20.32 x 23.5 (y -83.7...-60.2) + receptacle 8.94 x 7.35 + 1.0 underside keep-out;
#     KO_5807_pigtail = x +-5, y -60.2...-50.2, z 14-24 (>= 10 for the pigtail bend, E0).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
DB = {'DL': (50.0, -67.0), 'DR': (-50.0, -67.0), 'DCL': (19.0, -74.5), 'DCR': (-19.0, -74.5)}
RB, Z0, Z1, RH, ZH = 4.0, 2.8, 10.5, 2.0, 9.5


def run(_context):
    X = Ctx(); out = {}
    try:
        B = adsk.fusion.BooleanTypes
        fb = X.body('HOUSING_F_front'); db = X.body('HOUSING_F_door'); ie = X.body('INNER_E')
        v0 = (fb.volume, db.volume)
        notch = None
        for xs in (47.5, -47.5):
            t = X.tbm.createCylinderOrCone(Dw(xs, -3.66, 79.72), 0.40, Dw(xs, -101.1, 102.21), 0.40)
            X.tbm.booleanOperation(t, X.wbox(-150, 150, -63.5, -53.4, 0, 250), B.IntersectionBooleanType)
            notch = t if notch is None else X.union(notch, t)
        X.combine(fb, [X.add(notch, 'R1C2_notch_tmp')], op=CUT)
        fb = X.body('HOUSING_F_front')

        def wall_dir(x, y, z=7.0, n=36):
            best = (1e9, None)
            for i in range(n):
                a = 2 * math.pi * i / n; lo, hi = 0.0, 40.0
                for _ in range(18):
                    m = (lo + hi) / 2
                    if X.inside(ie, x + m * math.cos(a), y + m * math.sin(a), z): lo = m
                    else: hi = m
                if lo < best[0]: best = (lo, a)
            return best
        bosses = None; ribs = {}
        for k, (xr, y) in DB.items():
            x = XC + xr
            d, a = wall_dir(x, y)
            ribs[k] = (round(d, 2), round(math.degrees(a), 1))
            tb = X.wcyl_z(x, y, RB, Z0, Z1)
            L = d + 0.5
            c = (x + math.cos(a) * L / 2, y + math.sin(a) * L / 2, (Z0 + Z1) / 2)
            ldir = V3(math.cos(a), math.sin(a) * C, -math.sin(a) * S)
            wdir = V3(-math.sin(a), math.cos(a) * C, -math.cos(a) * S)
            X.union(tb, X.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(Dw(*c), ldir, wdir, L / 10, RH / 10, (Z1 - Z0) / 10)))
            X.diff(tb, X.wcyl_z(x, y, 2.0, Z0 - 0.5, ZH))
            bosses = tb if bosses is None else X.union(bosses, tb)
        out['ribs_d_deg'] = ribs
        slot = X.wbox(XC - 10.5, XC + 10.5, -92.0, -79.0, 12.7, 19.2)
        bt = X.add(bosses, 'R1C2_bosses_tmp')
        out['boss_vs_front_mm3'] = X.interference(bt, [fb])
        X.combine(db, [bt])
        db = X.body('HOUSING_F_door')
        X.combine(db, [X.add(slot, 'R1C2_slot_tmp')], op=CUT)
        db = X.body('HOUSING_F_door')
        env = X.wbox(XC - 10.16, XC + 10.16, -83.7, -60.2, 14.0, 15.6)
        X.union(env, X.wbox(XC - 4.47, XC + 4.47, -84.6, -77.25, 15.6, 18.86))
        X.union(env, X.wbox(XC - 10.16, XC + 10.16, -83.7, -60.2, 13.0, 14.0))
        if X.body('PD_5807_env') is None:
            X.add(env, 'PD_5807_env')
        if X.body('KO_5807_pigtail') is None:
            k = X.add(X.wbox(XC - 5.0, XC + 5.0, -60.2, -50.2, 14.0, 24.0), 'KO_5807_pigtail'); k.isLightBulbOn = False
        out['cm3'] = {'front': (round(v0[0], 3), round(fb.volume, 3)), 'door': (round(v0[1], 3), round(db.volume, 3))}
        out['lumps'] = {'front': fb.lumps.count, 'door': db.lumps.count}
        pe = X.body('PD_5807_env'); kp = X.body('KO_5807_pigtail')
        oth = [fb, db, X.body('PI5_F'), X.body('PI5_F_cooler')]
        out['env_interf'] = X.interference(pe, oth)
        out['pigtail_interf'] = X.interference(kp, oth)
        out['front_vs_lanes'] = X.interference(fb, [X.body(n) for n in ('KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR')])
        pr = {}
        for k, (xr, y) in DB.items():
            x = XC + xr
            pr[k] = {'hole_open_z6': not X.inside(db, x, y, 6.0), 'boss_wall_z6': X.inside(db, x + 3.0, y, 6.0) and X.inside(db, x - 3.0, y, 6.0),
                     'gap_z2.65': not X.inside(db, x + 3.0, y, 2.65) and not X.inside(fb, x + 3.0, y, 2.65),
                     'floor_hole_open_z1.5': not X.inside(fb, x, y, 1.5), 'cap_z10.0': X.inside(db, x, y, 10.0)}
        out['probes'] = pr
        out['slot_open'] = not X.inside(db, XC, -83.5, 16.5) and not X.inside(db, XC + 9.5, -83.5, 14.5)
        out['wall_beside_slot'] = X.inside(db, XC + 11.5, -83.5, 16.5) and X.inside(db, XC, -83.5, 20.5)
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_r1c2_bosses_usb', 'bosses + usb', out)
    print(json.dumps(out))
