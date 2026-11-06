# rev F audit-response d4c (2026-11-06): door, USB-C grommet, 5807 cradle and the cradle's floor bosses (audit findings 2, 7,
#   8, 9, 32, 33; Daniel 10:27 go for the plan). Probe data: v5f_d4b1_probe / v5f_d4b2_probe (trial booleans, same numbers).
#   HOUSING_F_door (old -> HOUSING_F_door_d0, hidden):
#     8   old RR boss stub (Ø8 × 0.4 ring with a Ø4.0 hole at (x_rel −19.0, y −74.5), z 2.8–3.2, 7.4 mm³) cut; nothing above it.
#     7   bottom flange 0.4 -> 0.85: copies of the door's z 2.8–3.2 slice lifted 0.25 and 0.45 and joined (fills the cove foot
#         over the flange, 61.9 mm³, no other part within it); the bottom edge stays at z 2.8 (0.3 reveal over the floor).
#     32  the four M3 bosses (19, −74.5), (−19, −77.0), (±50, −67.0) lengthened 0.3 to z 2.5 (they now stand on the floor top
#         z 2.5, like the bracket feet); Ruthex holes Ø4.0 re-cut z 2.4–9.5 (insert set flush z 2.5–8.2; ISO 7380 M3 × 8 from
#         below: head in the Ø6.5 × 1.0 c-bore, 5.7 of thread, tip z 9.0).
#     9   pin holes: old Ø2.1 at x ±13.6 filled with the door's wall profile (REF_F_outer − 0.7 recess − (INNER_E − 0.7
#         layer), the B6V-1 inlet-fill method; the fill equals the hole, 8.62 mm³ each); new Ø1.7 at x ±13.85, z 20.6 ->
#         web to the cutout (x ±12.2) 0.80.
#   GROMMET_usbc_F (old -> GROMMET_usbc_F_d0, hidden), rebuilt with the B5i / B6V-2 construction:
#     9   pins Ø1.5 at x ±13.85, z 20.6, from 0.5 inside the flange to 1.5 past the door's inner face (wall measured 2 mm
#         outboard, x ±15.85, as before).
#     33  bore x ±11.3 opened upward to z 30.1 (was 27.0) through the flange and the cloth layer, i.e. everywhere outside the
#         door's outer face: the receptacle (axis z 23.7, face y −84.6) sits inside the flange's thickness, so a plug overmold
#         centred on it may now be 12.8 thick (was 6.6). The cloth's cut edge stays covered: a collar 0.8 round that opening
#         in the cloth layer (x ±12.1, top z 30.9, ending 0.1 short of the door's outer face) and the flange raised to z 33.1
#         (2.2 over the collar, 3.0 over the bore, as at the sides). The door's cutout (z 13.3–27.9) and the sleeve inside
#         the wall are unchanged; the bore's back wall above z 27.0 is the door's outer face.
#   CRADLE_5807 (old -> CRADLE_5807_d0, hidden):
#     2   web 4 wide between the tangent legs (x_rel 0.7…4.3, y −74.5…−70.5, z 8.0–14.6; 0.5 clear of the Ø3.4 holes).
#     8   leftover Ø3.4 / Ø6.5 hole at (−5.5, −72.5) filled where the plate is (x ≥ −5.2), keeping the leg's c-bore.
#   HOUSING_F_front (old -> HOUSING_F_front_d4, hidden):
#     2   web 4 wide between the tangent floor bosses (x_rel 0.7…4.3, y −74.5…−70.5, z 2.4–8.0; 0.2 clear of the Ruthex holes).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
EXPECT = {'HOUSING_F_door': 51.101, 'GROMMET_usbc_F': 0.4889, 'CRADLE_5807': 2.1564, 'HOUSING_F_front': 236.1678}
COPIES = {'HOUSING_F_door': 'HOUSING_F_door_d0', 'GROMMET_usbc_F': 'GROMMET_usbc_F_d0', 'CRADLE_5807': 'CRADLE_5807_d0',
          'HOUSING_F_front': 'HOUSING_F_front_d4'}
BOSSES = ((19.0, -74.5), (-19.0, -77.0), (50.0, -67.0), (-50.0, -67.0))
STUB, RR = (-19.0, -74.5), (-19.0, -77.0)
ZC = 20.6
BX, BZ, SW = 11.3, 6.4, 0.8
FX, FR, FZ0, FZ1 = 15.1, 2.0, 11.2, 33.1
BT, CT = 30.1, 30.9
PX0, PX, PR, HR = 13.6, 13.85, 0.75, 0.85
WEB = (0.7, 4.3, -74.5, -70.5)


def ycyl(X, x, z, r, y0=-95.0, y1=-70.0):
    return X.tbm.createCylinderOrCone(Dw(XC + x, y0, z), r / 10, Dw(XC + x, y1, z), r / 10)


def named(X, prefix):
    return [b.name for b in X.comp.bRepBodies if b.name.startswith(prefix)]


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard: %s %s (expected %s)' % (k, None if b is None else round(b.volume, 4), v))
        for n in COPIES.values():
            if X.body(n) is not None:
                raise RuntimeError('%s exists already' % n)
        v0 = {k: round(X.body(k).volume, 4) for k in EXPECT}
        for k, n in COPIES.items():
            if k == 'GROMMET_usbc_F':
                continue
            c = X.add(X.tbm.copy(X.body(k)), n); c.isLightBulbOn = False
        # ---------------- door
        db = X.body('HOUSING_F_door')
        ring = X.wcyl_z(XC + STUB[0], STUB[1], 4.05, 2.7, 3.3); X.diff(ring, X.wcyl_z(XC + RR[0], RR[1], 4.0, 0.0, 12.0))
        X.combine(db, [X.add(ring, 'D4C_stub_tmp')], op=CUT); db = X.body('HOUSING_F_door')
        out['door_after_stub'] = round(db.volume, 4)
        T = X.tbm.copy(db); inter(X, T, X.wbox(XC - 100, XC + 100, -100, -40, 2.7, 3.2))
        Tu = X.tbm.copy(T); mvw(X, Tu, 0, 0, 0.25); T2 = X.tbm.copy(T); mvw(X, T2, 0, 0, 0.45); X.union(Tu, T2)
        X.combine(db, [X.add(Tu, 'D4C_flange_tmp')]); db = X.body('HOUSING_F_door')
        out['door_after_flange'] = round(db.volume, 4)
        bo = None; bh = None
        for (x, y) in BOSSES:
            c = X.wcyl_z(XC + x, y, 4.0, 2.5, 2.85); bo = c if bo is None else X.union(bo, c)
            h = X.wcyl_z(XC + x, y, 2.0, 2.4, 9.5); bh = h if bh is None else X.union(bh, h)
        X.combine(db, [X.add(bo, 'D4C_boss_tmp')]); db = X.body('HOUSING_F_door')
        X.combine(db, [X.add(bh, 'D4C_bhole_tmp')], op=CUT); db = X.body('HOUSING_F_door')
        out['door_after_bosses'] = round(db.volume, 4)
        wallp = tb_copy(X, 'REF_F_outer'); X.diff(wallp, tb_copy(X, 'TOOL_outer_skin_0p7'))
        cav = tb_copy(X, 'INNER_E'); X.diff(cav, tb_copy(X, 'TOOL_inner_skin_0p7')); X.diff(wallp, cav)
        inter(X, wallp, X.wbox(XC - 60, XC + 60, -95.0, YJ_D, -1.0, 60.0))
        fill = None; ph = None
        for s in (1, -1):
            f = ycyl(X, s * PX0, ZC, 1.1); inter(X, f, X.tbm.copy(wallp)); fill = f if fill is None else X.union(fill, f)
            h = ycyl(X, s * PX, ZC, HR); ph = h if ph is None else X.union(ph, h)
        X.combine(db, [X.add(fill, 'D4C_pinfill_tmp')]); db = X.body('HOUSING_F_door')
        X.combine(db, [X.add(ph, 'D4C_pinhole_tmp')], op=CUT); db = X.body('HOUSING_F_door')
        out['door_cm3'] = [v0['HOUSING_F_door'], round(db.volume, 4)]; out['door_lumps'] = db.lumps.count
        out['t_door'] = round(time.time() - t0, 1)
        # ---------------- grommet (rebuilt)
        go = X.body('GROMMET_usbc_F'); go.name = 'GROMMET_usbc_F_d0'; go.isLightBulbOn = False
        yw = {}
        for s in (1, -1):
            o = (XC + s * (PX + 2.0), -100.0, ZC)
            ref = ray_hits(X, o, (0, 1, 0), ('REF_F_outer',))
            runs = solid_runs(X, o, (0, 1, 0), 'HOUSING_F_door', 25.0)
            yw[s] = (-100.0 + ref[0][0], -100.0 + runs[0][1])
        out['pin_wall_y_cloth_inner'] = {str(k): [round(a, 3), round(b, 3)] for k, (a, b) in yw.items()}
        sh = tb_copy(X, 'REF_F_outer'); mvw(X, sh, 0.0, -1.0, 0.0); X.diff(sh, tb_copy(X, 'REF_F_outer'))
        pr = X.wbox(XC - FX + FR, XC + FX - FR, -95.0, -78.0, FZ0, FZ1)
        X.union(pr, X.wbox(XC - FX, XC + FX, -95.0, -78.0, FZ0 + FR, FZ1 - FR))
        for sx in (1, -1):
            for zz in (FZ0 + FR, FZ1 - FR):
                xx = XC + sx * (FX - FR)
                X.union(pr, X.tbm.createCylinderOrCone(Dw(xx, -95.0, zz), FR / 10, Dw(xx, -78.0, zz), FR / 10))
        inter(X, sh, pr)
        out['flange_mm3'] = round(sh.volume * 1000, 2)
        ref3 = tb_copy(X, 'REF_F_outer'); mvw(X, ref3, 0.0, -0.3, 0.0)
        sl = X.wbox(XC - BX - SW, XC + BX + SW, -95.0, -75.0, ZC - BZ - SW, ZC + BZ + SW); inter(X, sl, X.tbm.copy(ref3))
        shr = tb_copy(X, 'INNER_E'); X.diff(shr, tb_copy(X, 'TOOL_inner_skin_0p7')); X.diff(sl, shr)
        X.diff(sl, X.wbox(XC - BX, XC + BX, -96.0, -74.0, ZC - BZ, ZC + BZ))
        out['sleeve_mm3'] = round(sl.volume * 1000, 2)
        dout = tb_copy(X, 'REF_F_outer'); X.diff(dout, tb_copy(X, 'TOOL_outer_skin_0p7'))
        d01 = X.tbm.copy(dout); mvw(X, d01, 0.0, -0.1, 0.0)
        co = X.wbox(XC - BX - SW, XC + BX + SW, -95.0, -75.0, ZC + BZ - 0.1, CT); inter(X, co, X.tbm.copy(ref3)); X.diff(co, d01)
        out['collar_mm3'] = round(co.volume * 1000, 2)
        X.union(sh, sl); X.union(sh, co)
        for s in (1, -1):
            yc, yi = yw[s]
            X.union(sh, X.tbm.createCylinderOrCone(Dw(XC + s * PX, yc - 0.5, ZC), PR / 10, Dw(XC + s * PX, yi + 1.5, ZC), PR / 10))
        X.diff(sh, X.wbox(XC - BX, XC + BX, -96.0, -74.0, ZC - BZ, ZC + BZ))
        ext = X.wbox(XC - BX, XC + BX, -96.0, -75.0, ZC + BZ - 0.05, BT); X.diff(ext, X.tbm.copy(dout))
        X.diff(sh, ext)
        g = X.add(sh, 'GROMMET_usbc_F')
        out['grommet_cm3'] = [v0['GROMMET_usbc_F'], round(g.volume, 4)]; out['grommet_lumps'] = g.lumps.count
        out['grommet_box'] = [round(v, 3) for v in wbb(X, g)]
        out['t_grommet'] = round(time.time() - t0, 1)
        # ---------------- cradle
        cb = X.body('CRADLE_5807')
        web = X.wbox(XC + WEB[0], XC + WEB[1], WEB[2], WEB[3], 8.0, 14.6)
        lf = X.wcyl_z(XC - 5.5, -72.5, 3.3, 14.5, 17.5); inter(X, lf, X.wbox(XC - 5.2, XC - 1.5, -72.05, -69.0, 14.5, 17.5))
        X.diff(lf, X.wcyl_z(XC - 1.5, -72.5, 3.25, 16.0, 17.6)); X.diff(lf, X.wcyl_z(XC - 1.5, -72.5, 1.7, 7.9, 17.6))
        out['cradle_fill_mm3'] = round(lf.volume * 1000, 2)
        X.union(web, lf)
        X.combine(cb, [X.add(web, 'D4C_cweb_tmp')]); cb = X.body('CRADLE_5807')
        out['cradle_cm3'] = [v0['CRADLE_5807'], round(cb.volume, 4)]; out['cradle_lumps'] = cb.lumps.count
        # ---------------- front floor web
        fb = X.body('HOUSING_F_front')
        X.combine(fb, [X.add(X.wbox(XC + WEB[0], XC + WEB[1], WEB[2], WEB[3], 2.4, 8.0), 'D4C_fweb_tmp')]); fb = X.body('HOUSING_F_front')
        out['front_cm3'] = [v0['HOUSING_F_front'], round(fb.volume, 4)]; out['front_lumps'] = fb.lumps.count
        # ---------------- probes
        P = lambda b, x, y, z: X.inside(b, XC + x, y, z)
        db = X.body('HOUSING_F_door'); g = X.body('GROMMET_usbc_F')
        pr_ = {
            'stub_gone_z3.0': not P(db, -19.0, -71.5, 3.0) and not P(db, -16.0, -73.0, 3.0),
            'flange_0.85_x0': P(db, 0.0, -79.3, 3.0) and P(db, 0.0, -79.3, 3.6) and not P(db, 0.0, -79.3, 3.7),
            'edge_z2.8_kept': not P(db, 0.0, -82.0, 2.75) and P(db, 0.0, -82.0, 2.85),
            'pin_old_filled': P(db, 12.75, -82.5, ZC) and P(db, -12.75, -82.5, ZC),
            'pin_new_open': not P(db, PX, -82.5, ZC) and not P(db, -PX, -82.5, ZC),
            'web_x12.6': P(db, 12.6, -82.5, ZC) and P(db, -12.6, -82.5, ZC),
            'cutout_open_x12.1': not P(db, 12.1, -82.5, ZC),
            'g_bore_open_flange_z29.5': not P(g, 0.0, -85.0, 29.5) and not P(g, 0.0, -84.45, 29.5),
            'g_bore_open_cloth_z29.5': not P(g, 0.0, -83.9, 29.5),
            'g_collar_top_z30.5': P(g, 0.0, -84.0, 30.5) and not P(g, 0.0, -83.61, 30.5),
            'g_collar_side_x11.7_z29': P(g, 11.7, -84.0, 29.0),
            'g_sleeve_top_wall_in_door': P(g, 0.0, -83.0, 27.4),
            'g_flange_top_z32.8': P(g, 0.0, -84.8, 32.8) and not P(g, 0.0, -84.8, 33.3),
            'g_pin_new': P(g, PX, -82.0, ZC) and P(g, -PX, -82.0, ZC) and not P(g, PX0 - 0.8, -82.0, ZC),
            'cradle_web': P(X.body('CRADLE_5807'), 2.5, -72.5, 11.0) and P(X.body('CRADLE_5807'), 2.5, -74.3, 11.0),
            'cradle_leftover_filled': P(X.body('CRADLE_5807'), -4.6, -71.6, 15.2) and P(X.body('CRADLE_5807'), -4.95, -70.0, 16.8),
            'cradle_leg_cbore_open': not P(X.body('CRADLE_5807'), -1.5 - 3.0, -72.5, 16.8) and not P(X.body('CRADLE_5807'), -1.5, -72.5, 12.0),
            'front_web': P(X.body('HOUSING_F_front'), 2.5, -72.5, 5.0) and not P(X.body('HOUSING_F_front'), -1.5, -72.5, 5.0)
                         and not P(X.body('HOUSING_F_front'), 6.5, -72.5, 5.0)}
        for (x, y) in BOSSES:
            pr_['boss_%g_%g' % (x, y)] = P(db, x + 3.0, y, 2.6) and not P(db, x, y, 2.6) and not P(db, x + 3.0, y, 2.45)
        out['probes'] = pr_
        out['all_probes_ok'] = all(pr_.values())
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
        out['split'] = [b.name for b in X.comp.bRepBodies if ' (' in b.name]
        out['names'] = {p: named(X, p) for p in ('HOUSING_F_door', 'GROMMET_usbc_F', 'CRADLE_5807', 'HOUSING_F_front')}
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d4c_door_grommet_cradle', 'run', out)
    print(json.dumps(out, separators=(',', ':')))
