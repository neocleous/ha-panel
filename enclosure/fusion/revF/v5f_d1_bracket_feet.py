# rev F audit-response d1 (2026-11-06; audit finding 22, Daniel 10:27 go): the main-board bracket is screwed from BELOW.
#   The b4b tab screws (M3 x 6 from above at (x_rel ±49.5, y −58.0)) sat 0.5 in front of the bracket's own posts
#   (y −62.5…−58.5 above z 12) and could not be inserted. The audit's fix (move to y −55.0) puts the Ø8 bosses 1 mm into the
#   speaker boxes (rear face y −52.0). Instead, as the door: ISO 7380 M3 x 8 from below through the floor into a Ruthex M3 in
#   a new Ø8 foot boss of the bracket, at the same axis.
#   HOUSING_F_front: floor bosses (Ø8 z 2.0…8.0, Ruthex hole Ø4.0 z 2.3…8.5) removed, the hole's 0.2 dimple filled; Ø3.4
#     through the floor + Ø6.5 × 1.0 c-bore from below (the door-screw pattern).
#   MAIN_BRACKET: foot boss Ø8 z 2.5…8.6 under each tab (bears on the floor top z 2.5 – designed contact), Ruthex M3 hole
#     Ø4.0 z 2.4…9.5 from the bottom face (insert z 2.5…8.2, screw tip z 9.0); the old Ø3.4 tab hole filled above z 9.4.
#   Stack: c-bore floor z 1.0, head z −0.65…1.0 (2.35 above the table at the feet's z −3.0), 5.7 of thread, tip 0.5 short.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
EXPECT = {'HOUSING_F_front': 236.6852, 'MAIN_BRACKET': 4.9002}
FB = 49.5, -58.0


def run(_context):
    X = Ctx(); out = {}
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard: %s %s (expected %s)' % (k, None if b is None else round(b.volume, 4), v))
        for n in ('HOUSING_F_front_d0', 'MAIN_BRACKET_d0'):
            if X.body(n) is not None:
                raise RuntimeError('%s exists already' % n)
        fb = X.body('HOUSING_F_front'); br = X.body('MAIN_BRACKET')
        k1 = X.add(X.tbm.copy(fb), 'HOUSING_F_front_d0'); k1.isLightBulbOn = False
        k2 = X.add(X.tbm.copy(br), 'MAIN_BRACKET_d0'); k2.isLightBulbOn = False
        v0f, v0b = fb.volume, br.volume
        # --- front shell: fill dimple, remove bosses, hole + c-bore from below
        fill = None; cut = None; hole = None
        for s in (1, -1):
            x = XC + s * FB[0]
            f = X.wcyl_z(x, FB[1], 2.1, 2.2, 2.6); fill = f if fill is None else X.union(fill, f)
            c = X.wcyl_z(x, FB[1], 4.15, 2.5, 8.4); cut = c if cut is None else X.union(cut, c)
            h = X.union(X.wcyl_z(x, FB[1], 1.7, -0.5, 2.7), X.wcyl_z(x, FB[1], 3.25, -0.5, 1.0))
            hole = h if hole is None else X.union(hole, h)
        X.combine(fb, [X.add(fill, 'D1_fill_tmp')]); fb = X.body('HOUSING_F_front')
        X.combine(fb, [X.add(cut, 'D1_cut_tmp')], op=CUT); fb = X.body('HOUSING_F_front')
        X.combine(fb, [X.add(hole, 'D1_hole_tmp')], op=CUT); fb = X.body('HOUSING_F_front')
        out['front_cm3'] = [round(v0f, 4), round(fb.volume, 4)]; out['front_lumps'] = fb.lumps.count
        # --- bracket: foot bosses, insert holes, fill the old tab hole above z 9.4
        boss = None; ih = None; plug = None
        for s in (1, -1):
            x = XC + s * FB[0]
            b_ = X.wcyl_z(x, FB[1], 4.0, 2.5, 8.6); boss = b_ if boss is None else X.union(boss, b_)
            i_ = X.wcyl_z(x, FB[1], 2.0, 2.4, 9.5); ih = i_ if ih is None else X.union(ih, i_)
            xs = sorted((XC + s * 46.5, XC + s * 53.5)); xp = sorted((XC + s * 46.5, XC + s * 52.5))
            region = X.union(X.wbox(xs[0], xs[1], -62.5, -54.0, 8.0, 11.0), X.wbox(xp[0], xp[1], -62.5, -58.5, 8.0, 84.0))
            p_ = X.wcyl_z(x, FB[1], 1.75, 9.4, 12.1); inter(X, p_, region)
            plug = p_ if plug is None else X.union(plug, p_)
        X.combine(br, [X.add(boss, 'D1_boss_tmp')]); br = X.body('MAIN_BRACKET')
        X.combine(br, [X.add(plug, 'D1_plug_tmp')]); br = X.body('MAIN_BRACKET')
        X.combine(br, [X.add(ih, 'D1_ih_tmp')], op=CUT); br = X.body('MAIN_BRACKET')
        out['bracket_cm3'] = [round(v0b, 4), round(br.volume, 4)]; out['bracket_lumps'] = br.lumps.count
        out['names'] = [b.name for b in X.comp.bRepBodies if b.name.startswith(('HOUSING_F_front', 'MAIN_BRACKET', 'D1_')) or ' (' in b.name and b.name.startswith(('HOUSING', 'MAIN'))]
        P = lambda b, x, y, z: X.inside(b, XC + x, y, z)
        pr = {}
        for s, k in ((1, 'L'), (-1, 'R')):
            x = s * FB[0]
            pr[k] = {'floor_boss_gone_z5': not P(fb, x + 3.0, FB[1], 5.0), 'floor_top_flat_z2.4': P(fb, x + 2.0, FB[1], 2.4),
                     'hole_open_z1.8': not P(fb, x, FB[1], 1.8), 'cbore_open_z0.5_r3': not P(fb, x + 3.0, FB[1], 0.5),
                     'floor_under_cbore_wall_z1.5_r2.5': P(fb, x + 2.5, FB[1], 1.5),
                     'boss_wall_z5_r3': P(br, x + 3.0, FB[1], 5.0), 'insert_open_z5': not P(br, x, FB[1], 5.0),
                     'insert_open_z9.3': not P(br, x, FB[1], 9.3), 'old_hole_filled_z10.5': P(br, x, FB[1], 10.5),
                     'boss_bottom_free_z2.45': not P(br, x + 3.0, FB[1], 2.45)}
        out['probes'] = pr
        oth = ['HOUSING_F_front', 'HOUSING_F_door', 'SPKBOX_L', 'SPKBOX_R', 'SPK_L', 'SPK_R', 'PI5_F', 'PI5_F_cooler', 'MAIN_pcb',
               'MAIN_front_env', 'MAIN_back_env', 'PIPWR_a_env', 'LEAD_PI_POWER', 'LEAD_SPK_L', 'LEAD_SPK_R', 'USBA_plug_env',
               'USBA_cable_env', 'CRADLE_5807', 'PD_5807_env', 'KO_K5_LL', 'KO_K5_LR', 'KO_K5_UL', 'KO_K5_UR', 'FOOT_RL', 'FOOT_RR']
        out['bracket_x'] = {n: vol_x(X, X.tbm.copy(br), X.tbm.copy(X.body(n))) for n in oth if X.body(n) is not None}
        out['bracket_x'] = {k: v for k, v in out['bracket_x'].items() if v > 0} or 'all 0'
        ld = {}
        for s, k in ((1, 'L'), (-1, 'R')):             # below the floor: head + key, nothing in the way down to the table
            c = X.wcyl_z(XC + s * FB[0], FB[1], 3.0, -3.0, 1.0)
            ld[k] = {n: vol_x(X, X.tbm.copy(c), X.tbm.copy(X.body(n))) for n in ('HOUSING_F_front', 'FOOT_RL', 'FOOT_RR', 'FOOT_FL', 'FOOT_FR')}
        out['below_floor_x'] = ld
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d1_bracket_feet', 'run', out)
    print(json.dumps(out, separators=(',', ':')))
