# rev F block 6 / V11 (2026-11-05): V11 option 1 (Daniel 2026-11-05 09:16, "2. Ok"): Pi power by a 90° adapter (female
#   port toward +x) + the 0.2 m straight 5 A cable along the floor behind the Pi to a USB4105 on the main board's bottom
#   edge (back face, opening down, x_rel +25) – the checkpoint-4 recommendation. The straight plug out of the adapter
#   (V11a_px: x_rel −25.7…−5.7, y −71.5…−59.1, z 4.8…17.2 for either plug orientation) runs under the 5807, so:
#   1. Front shell: cradle floor bosses (±5.5, −72.5) → (±3.8, −76.0) (Ø8 z 2.0–8.0, Ruthex M3 Ø4.0 z 2.3–8.0; the two
#      bosses merge); RR door screw hole (x_rel −19, y −74.5) → (−19, −77.0) (Ø3.4 + Ø6.5 × 1.0 c-bore from below).
#      Leg x ±3.8: the M3 head's c-bore (Ø6.5) clears the 5807 posts (Ø6 at ±7.6, −81.16) by 0.16; at ±5.5 it notched them.
#   2. Door: RR boss (−19, −74.5) → (−19, −77.0) (Ø8 z 2.8–10.5, 2.0 rib to the nearest INNER_E wall found by 36 rays,
#      Ruthex Ø4.0 z 2.3–9.5); the old boss and rib removed inside the cavity above the floor cove.
#      Inlet cutout x ±12.2, z 6.8–21.4 → z 13.3–27.9 (old one filled with the door's wall profile = REF_F_outer − 0.7
#      recess − (INNER_E − 0.7 layer)); pin holes Ø2.1 (±13.6, z 14.1) → z 20.6.
#   3. CRADLE_5807 (old → CRADLE_5807_b5, hidden): copy + 6.5; plate cut back to y ≤ −72.0 (behind the plug; the front pads
#      go, the board's free end over 21 mm is unsupported); old fixing holes filled; legs Ø8 z 8.0–14.6 at (±3.8, −76.0);
#      2 × M3 × 12 DIN912 (Ø3.4, c-bore Ø6.5 × 1.5 → head top z 19.0, 1.5 under the board).
#   4. PD_5807_env, KO_5807_pigtail + 6.5 (old → *_b5, hidden); LEAD_PIGTAIL_20V from the raised X4 (old → *_b5).
#   Then v5f_b6v2: grommet at ZC 20.6, the V11 route envelopes, checks.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
DZ = 6.5
EXPECT = {'HOUSING_F_front': 237.918, 'HOUSING_F_door': 53.572, 'CRADLE_5807': 1.827, 'GROMMET_usbc_F': 0.488}
FB_OLD, FB_NEW = ((5.5, -72.5), (-5.5, -72.5)), ((3.8, -76.0), (-3.8, -76.0))
RR_OLD, RR_NEW = (-19.0, -74.5), (-19.0, -77.0)
RB, Z0, Z1, RH, ZH = 4.0, 2.8, 10.5, 2.0, 9.5           # door boss (R1c-2)


def wall_dir_ray(X, xr, y, z=7.0, n=36):                 # nearest INNER_E wall from a cavity point, by rays
    best = (1e9, 0.0)
    for i in range(n):
        a = 2 * math.pi * i / n
        hs = ray_hits(X, (XC + xr, y, z), (math.cos(a), math.sin(a), 0.0), ('INNER_E',))
        if hs and hs[0][0] < best[0]:
            best = (hs[0][0], a)
    return best


def boss_tool(X, xr, y, d, a, rr=RB, rw=RH, embed=0.5):
    x = XC + xr
    tb = X.wcyl_z(x, y, rr, Z0, Z1)
    L = d + embed
    c = (x + math.cos(a) * L / 2, y + math.sin(a) * L / 2, (Z0 + Z1) / 2)
    ldir = V3(math.cos(a), math.sin(a) * C, -math.sin(a) * S)
    wdir = V3(-math.sin(a), math.cos(a) * C, -math.cos(a) * S)
    X.union(tb, X.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(Dw(*c), ldir, wdir, L / 10, rw / 10, (Z1 - Z0) / 10)))
    return tb


def tube(X, pts, dia):                                    # x_rel, y, z points
    r = dia / 20; t = None
    for i in range(len(pts) - 1):
        p, q = pts[i], pts[i + 1]
        c = X.tbm.createCylinderOrCone(Dw(XC + p[0], p[1], p[2]), r, Dw(XC + q[0], q[1], q[2]), r)
        t = c if t is None else X.union(t, c)
    for p in pts[1:-1]:
        X.union(t, X.tbm.createSphere(Dw(XC + p[0], p[1], p[2]), r))
    return t


def plen(pts):
    return round(sum(math.sqrt(sum((pts[i + 1][k] - pts[i][k]) ** 2 for k in range(3))) for i in range(len(pts) - 1)), 1)


def run(_context):
    X = Ctx(); out = {'step': 'start'}
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.002:
                raise RuntimeError('guard: %s volume %s, expected %s' % (k, None if b is None else round(b.volume, 3), v))
        for n in ('CRADLE_5807_b5', 'PD_5807_env_b5', 'KO_5807_pigtail_b5', 'LEAD_PIGTAIL_20V_b5'):
            if X.body(n) is not None:
                raise RuntimeError('%s exists already' % n)
        fb = X.body('HOUSING_F_front'); db = X.body('HOUSING_F_door')
        v0 = {'front': round(fb.volume, 3), 'door': round(db.volume, 3)}
        # 1. front shell: cradle floor bosses and the RR screw hole
        rem = None
        for (xr, y) in FB_OLD:
            t = X.wcyl_z(XC + xr, y, 4.1, 2.5, 8.1)
            rem = t if rem is None else X.union(rem, t)
        X.combine(fb, [X.add(rem, 'B6V_fboss_rem_tmp')], op=CUT); fb = X.body('HOUSING_F_front')
        fill = None
        for (xr, y) in FB_OLD:
            t = X.wcyl_z(XC + xr, y, 2.05, 2.2, 2.5)
            fill = t if fill is None else X.union(fill, t)
        t = X.wcyl_z(XC + RR_OLD[0], RR_OLD[1], 3.3, 0.0, 2.5); inter(X, t, X.wbox(-250, 250, -250, 250, -1.0, 2.5))
        flo = tb_copy(X, 'REF_F_outer'); inter(X, flo, X.wbox(-250, 250, -250, 250, -1.0, 2.5)); inter(X, t, flo)
        X.union(fill, t)
        new = None
        for (xr, y) in FB_NEW:
            t = X.wcyl_z(XC + xr, y, 4.0, 2.0, 8.0)
            new = t if new is None else X.union(new, t)
        X.union(fill, new)
        X.combine(fb, [X.add(fill, 'B6V_ffill_tmp')]); fb = X.body('HOUSING_F_front')
        cut = None
        for (xr, y) in FB_NEW:
            t = X.wcyl_z(XC + xr, y, 2.0, 2.3, 8.1)
            cut = t if cut is None else X.union(cut, t)
        X.union(cut, X.wcyl_z(XC + RR_NEW[0], RR_NEW[1], 1.7, -1.0, 3.0))
        X.union(cut, X.wcyl_z(XC + RR_NEW[0], RR_NEW[1], 3.25, -1.0, 1.0))
        X.combine(fb, [X.add(cut, 'B6V_fcut_tmp')], op=CUT); fb = X.body('HOUSING_F_front')
        out['front_cm3'] = [v0['front'], round(fb.volume, 3)]; out['front_lumps'] = fb.lumps.count
        out['step'] = 'front'
        # 2. door: RR boss
        cav = tb_copy(X, 'INNER_E'); X.diff(cav, tb_copy(X, 'TOOL_inner_skin_0p7'))
        cove = tb_copy(X, 'TOOL_outer_skin_3p2'); inter(X, cove, X.wbox(-250, 250, -250, 250, -1.0, 6.3))
        d0, a0 = wall_dir_ray(X, *RR_OLD)
        r0 = boss_tool(X, RR_OLD[0], RR_OLD[1], d0, a0, rr=4.1, rw=2.6, embed=0.6)
        X.union(r0, X.wcyl_z(XC + RR_OLD[0], RR_OLD[1], 4.1, Z0 - 0.1, Z1 + 0.1))
        inter(X, r0, cav); X.diff(r0, cove)
        X.combine(db, [X.add(r0, 'B6V_dboss_rem_tmp')], op=CUT); db = X.body('HOUSING_F_door')
        d1, a1 = wall_dir_ray(X, *RR_NEW)
        nb = boss_tool(X, RR_NEW[0], RR_NEW[1], d1, a1)
        X.diff(nb, X.wcyl_z(XC + RR_NEW[0], RR_NEW[1], 2.0, Z0 - 0.5, ZH))
        out['rr_rib'] = {'old_d_deg': [round(d0, 2), round(math.degrees(a0), 1)], 'new_d_deg': [round(d1, 2), round(math.degrees(a1), 1)]}
        out['rr_new_vs_front_mm3'] = vol_x(X, nb, fb)
        X.combine(db, [X.add(nb, 'B6V_dboss_new_tmp')]); db = X.body('HOUSING_F_door')
        X.combine(db, [X.add(X.wcyl_z(XC + RR_NEW[0], RR_NEW[1], 2.0, 2.3, ZH), 'B6V_dboss_hole_tmp')], op=CUT)
        db = X.body('HOUSING_F_door')
        out['step'] = 'door_boss'
        # 2b. door: inlet cutout and pin holes up 6.5
        wallp = tb_copy(X, 'REF_F_outer'); X.diff(wallp, tb_copy(X, 'TOOL_outer_skin_0p7'))
        cav2 = tb_copy(X, 'INNER_E'); X.diff(cav2, tb_copy(X, 'TOOL_inner_skin_0p7')); X.diff(wallp, cav2)
        inter(X, wallp, X.wbox(-250, 250, -250, YJ_D, -1.0, 260))
        f = X.wbox(XC - 12.3, XC + 12.3, -95.0, -70.0, 6.7, 21.5)
        for sx in (1, -1):
            X.union(f, X.tbm.createCylinderOrCone(Dw(XC + sx * 13.6, -95.0, 14.1), 0.11, Dw(XC + sx * 13.6, -70.0, 14.1), 0.11))
        inter(X, f, wallp)
        X.combine(db, [X.add(f, 'B6V_inlet_fill_tmp')]); db = X.body('HOUSING_F_door')
        c2 = X.wbox(XC - 12.2, XC + 12.2, -95.0, -70.0, 6.8 + DZ, 21.4 + DZ)
        for sx in (1, -1):
            X.union(c2, X.tbm.createCylinderOrCone(Dw(XC + sx * 13.6, -95.0, 14.1 + DZ), 0.105, Dw(XC + sx * 13.6, -70.0, 14.1 + DZ), 0.105))
        X.combine(db, [X.add(c2, 'B6V_inlet_cut_tmp')], op=CUT); db = X.body('HOUSING_F_door')
        out['door_cm3'] = [v0['door'], round(db.volume, 3)]; out['door_lumps'] = db.lumps.count
        out['step'] = 'door_inlet'
        # 3. cradle
        co = X.body('CRADLE_5807'); co.name = 'CRADLE_5807_b5'; co.isLightBulbOn = False
        cr = X.tbm.copy(co); mvw(X, cr, 0.0, 0.0, DZ)
        X.diff(cr, X.wbox(XC - 12.0, XC + 12.0, -72.0, -50.0, 0.0, 40.0))
        for (xr, y) in FB_OLD:
            t = X.wcyl_z(XC + xr, y, 3.3, 8.0 + DZ, 11.0 + DZ); inter(X, t, X.wbox(XC - 10.5, XC + 10.5, -82.1, -72.0, 8.0 + DZ, 11.0 + DZ))
            X.union(cr, t)
        for (xr, y) in FB_NEW:
            X.union(cr, X.wcyl_z(XC + xr, y, 4.0, 8.0, 8.0 + DZ + 0.1))
        for (xr, y) in FB_NEW:
            X.diff(cr, X.wcyl_z(XC + xr, y, 1.7, 7.9, 11.1 + DZ))
            X.diff(cr, X.wcyl_z(XC + xr, y, 3.25, 9.5 + DZ, 11.1 + DZ))
        cb = X.add(cr, 'CRADLE_5807')
        out['cradle_cm3'] = [1.827, round(cb.volume, 3)]; out['cradle_lumps'] = cb.lumps.count
        out['step'] = 'cradle'
        # 4. envelopes and the pigtail lead
        for n, vis in (('PD_5807_env', True), ('KO_5807_pigtail', False)):
            o = X.body(n); o.name = n + '_b5'; o.isLightBulbOn = False
            t = X.tbm.copy(o); mvw(X, t, 0.0, 0.0, DZ); b = X.add(t, n); b.isLightBulbOn = vis
        o = X.body('LEAD_PIGTAIL_20V'); o.name = 'LEAD_PIGTAIL_20V_b5'; o.isLightBulbOn = False
        pts = [(0.0, -64.77, 16.0 + DZ), (0.0, -61.5, 28.5), (0.0, -58.0, 34.0), (0.0, -55.0, 37.5), (0.0, -53.6, 37.5)]
        lb = X.add(tube(X, pts, 3.2), 'LEAD_PIGTAIL_20V'); lb.isLightBulbOn = False
        out['pigtail_len_mm'] = [plen([(0.0, -64.77, 16.0), (0.0, -62.0, 22.0), (0.0, -58.5, 32.0), (0.0, -55.0, 37.5), (0.0, -53.6, 37.5)]), plen(pts)]
        out['step'] = 'envelopes'
        # probes
        P = lambda b, x, y, z: X.inside(b, XC + x, y, z)
        fb = X.body('HOUSING_F_front'); db = X.body('HOUSING_F_door')
        out['probes'] = {
            'fboss_old_gone': not P(fb, 5.5 + 3.0, -72.5, 5.0) and not P(fb, -5.5 - 3.0, -72.5, 5.0),
            'floor_at_old_boss': P(fb, 5.5, -72.5, 2.4) and P(fb, -5.5, -72.5, 2.4),
            'fboss_new_solid': P(fb, 3.8 + 3.0, -76.0, 5.0) and P(fb, -3.8 - 3.0, -76.0, 5.0) and P(fb, 0.0, -76.0, 5.0),
            'fboss_new_holes_open': not P(fb, 3.8, -76.0, 5.0) and not P(fb, -3.8, -76.0, 5.0),
            'rr_hole_old_filled': P(fb, -19.0, -73.0, 0.5) and P(fb, -19.0, -74.5, 2.0),   # (−19, −74.5, z < 1) is in the new c-bore
            'rr_hole_new_open': not P(fb, -19.0, -77.0, 0.5) and not P(fb, -19.0, -77.0, 2.0) and not P(fb, -19.0 + 2.5, -77.0, 0.5),
            'rr_floor_solid_beside': P(fb, -19.0 + 2.5, -77.0, 2.0),
            'dboss_old_gone': not P(db, -19.0, -71.5, 6.0) and not P(db, -19.0 + 3.0, -73.5, 6.0),
            'dboss_new_solid': P(db, -19.0 + 3.0, -77.0, 6.0) and P(db, -19.0 - 3.0, -77.0, 6.0),
            'dboss_new_hole_open': not P(db, -19.0, -77.0, 6.0),
            'cradle_front_gone': not P(cb, 0.0, -65.0, 9.5 + DZ),
            'cradle_legs_solid': P(cb, 3.8 + 3.0, -76.0, 11.0) and P(cb, -3.8 - 3.0, -76.0, 11.0),
            'cradle_holes_open': not P(cb, 3.8, -76.0, 11.0) and not P(cb, -3.8, -76.0, 16.5),
            'cradle_old_holes_filled': P(cb, 5.5, -73.0, 16.0) and P(cb, -5.5, -73.0, 16.0),
        }
        out['door_wall_runs'] = {'z10_old_cutout': solid_runs(X, (XC, -100.0, 10.0), (0, 1, 0), 'HOUSING_F_door', 30.0),
                                 'z20_new_cutout': solid_runs(X, (XC, -100.0, 20.0), (0, 1, 0), 'HOUSING_F_door', 30.0),
                                 'z14.1_old_pin': solid_runs(X, (XC + 13.6, -100.0, 14.1), (0, 1, 0), 'HOUSING_F_door', 30.0),
                                 'z20.6_new_pin': solid_runs(X, (XC + 13.6, -100.0, 20.6), (0, 1, 0), 'HOUSING_F_door', 30.0)}
        out['step'] = 'done'
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b6v1_v11_option1', 'build', out)
    print(json.dumps(out))
