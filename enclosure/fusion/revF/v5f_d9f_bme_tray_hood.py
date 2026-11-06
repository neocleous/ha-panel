# rev F d9f (2026-11-06): BME680 pocket, second form. d9c's open-top cup could not take the board: the wall leans in above
#   the cup, so the board could not drop in along the wall, and tilting it ran its inner face into the cup's back wall
#   (d9 sweeps, d9e). Now the board goes in from the room side, along -w, and a separate hood closes the back and the top:
#   HOUSING_F_front (d9c version -> HOUSING_F_front_d9c, hidden; rebuilt from HOUSING_F_front_d9, the pre-d9c front):
#     old slots filled, slots 4.0 higher (as d9c, TOOL_bme680_slots);
#     a tray moulded to the wall: floor 1.2 (u -9.2…-8.0) out to w 6.7 with a 1.0 lip at w 6.7…7.5, side walls 2.4
#     (t ±10.5…±12.9) from the wall to w 5.5 and up to u 8.0, a solid 45° underside down to z 77, four 0.5 seat pads at the
#     board's corners, a 4 wide lead slot through the floor open to the room side (the lead slides in with the board and is
#     sealed with a foam plug), heat-stake pins Ø1.8 on the side walls' tops (t ±11.7, w 3.0) to u 11.0.
#   BME_HOOD (new printed part, d9c's BME_LID -> BME_LID_d9c, hidden): back plate w 5.5…6.7 standing on the floor behind the
#     lip, top plate u 8.0…9.2 to 0.2 off the wall, two slots that slide over the pins (staked from above).
#   FOAM_bme_env: 2 mm closed-cell (A13) on the back plate, presses the board onto its pads; FOAM_bme_top_env: 1 mm (A12)
#     under the top plate, 0.5 compressed, seals the top and the gap along the wall.
import os
exec(open(os.path.expanduser('~/Documents/HA_panel_renders/scripts_d/v5f_d9c_bme_cup.py')).read())   # frame, fbox, air, P
import traceback
EXP = {'HOUSING_F_front': 235.8231, 'HOUSING_F_front_d9': 233.5514}


def fcyl_w(X, t, u, w0, w1, r):               # cylinder along w
    a = P(t, u, w0); b = P(t, u, w1)
    return X.tbm.createCylinderOrCone(Dw(XC + a[0], a[1], a[2]), r / 10, Dw(XC + b[0], b[1], b[2]), r / 10)


def run(_context):
    X = Ctx(); out = {}; t0 = time.time(); dry = globals().get('DRY', True)
    try:
        for k, v in EXP.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard: %s %s' % (k, None if b is None else round(b.volume, 4)))
        for n in ('HOUSING_F_front_d9c', 'BME_LID_d9c', 'FOAM_bme_env_d9c', 'BME_HOOD', 'FOAM_bme_top_env'):
            if X.body(n) is not None:
                raise RuntimeError('%s exists already' % n)
        AIR = air(X)
        region = fbox(X, -18, 18, -26, 16, -12, 12)
        inter(X, AIR, region)
        outer = tb_copy(X, 'REF_F_outer'); X.diff(outer, tb_copy(X, 'TOOL_outer_skin_0p7')); inter(X, outer, X.tbm.copy(region))
        wallp = X.tbm.copy(outer); X.diff(wallp, X.tbm.copy(AIR))
        so = tb_copy(X, 'TOOL_bme680_slots_d9')                     # the original slots
        sf = X.tbm.copy(wallp); inter(X, sf, X.tbm.copy(so))
        sn = tb_copy(X, 'TOOL_bme680_slots')                        # d9c's slots, 4.0 higher
        # tray
        tray = None
        for s in (1, -1):
            sw = fbox(X, min(s * 10.5, s * 12.9), max(s * 10.5, s * 12.9), -9.2, 8.0, -12.0, 5.5)
            tray = sw if tray is None else X.union(tray, sw)
        X.union(tray, fbox(X, -12.9, 12.9, -9.2, -8.0, -12.0, 6.7))
        X.union(tray, fbox(X, -12.9, 12.9, -9.2, -7.0, 6.7, 7.5))
        d = tuple((UU[i] - NI[i]) / math.sqrt(2) for i in range(3))
        s0 = (-9.2 - 7.5) / math.sqrt(2); L = 120.0
        half = lbox(X, tuple(CE[i] + d[i] * (s0 + L / 2) for i in range(3)), TT, d, L, L, L)
        wg = fbox(X, -12.9, 12.9, -30.0, -9.2, -12.0, 7.5); inter(X, wg, half)
        X.union(tray, wg)
        inter(X, tray, X.tbm.copy(outer)); inter(X, tray, X.wbox(-250, 250, -250, 250, Z_BOX, 260))
        cav = fbox(X, -10.5, 10.5, -8.0, 8.6, -12.0, 5.5); inter(X, cav, X.tbm.copy(AIR))
        slot = fbox(X, -2.0, 2.0, -30.0, -7.9, 0.0, 7.6); inter(X, slot, X.tbm.copy(AIR))
        X.diff(tray, cav); X.diff(tray, slot)
        for tc in (9.25, -9.25):
            for uc in (6.75, -6.75):
                p_ = fbox(X, tc - 0.75, tc + 0.75, uc - 0.75, uc + 0.75, -12.0, -3.0); inter(X, p_, X.tbm.copy(AIR))
                X.union(tray, p_)
        for s in (1, -1):
            X.union(tray, fcyl_u(X, s * 11.7, 3.0, 7.9, 11.0, 0.9))
        f9 = tb_copy(X, 'HOUSING_F_front_d9')
        newm = X.tbm.copy(tray); X.diff(newm, X.tbm.copy(f9))
        out['tray_mm3'] = [round(tray.volume * 1000, 1), round(newm.volume * 1000, 1)]
        out['newm_in_wall_mm3'] = vol_x(X, X.tbm.copy(newm), X.tbm.copy(wallp))
        ox = {}
        for n in ('LEAD_RADAR', 'LEAD_BME680', 'HOUSING_F_door', 'MAIN_BRACKET', 'KO_K5_LR', 'KO_K5_UR', 'KO_capkey_SR',
                  'LD2410C_env_F', 'SPK_R', 'BME680_env'):
            if X.body(n) is not None:
                v = vol_x(X, X.tbm.copy(newm), tb_copy(X, n))
                if v > 0.0:
                    ox[n] = v
        b = tb_copy(X, 'SPKBOX_R'); mvw(X, b, 0, 0, 1.0); ox['SPKBOX_R_up1.0'] = vol_x(X, X.tbm.copy(newm), b)
        out['tray_x'] = ox
        # hood
        lair = air(X, 'TOOL_inner_skin_0p9'); inter(X, lair, X.tbm.copy(region))
        hood = fbox(X, -12.9, 12.9, -8.0, 9.2, 5.5, 6.7)
        tp = fbox(X, -12.9, 12.9, 8.0, 9.2, -12.0, 6.7); inter(X, tp, lair)
        X.union(hood, tp)
        for s in (1, -1):
            X.diff(hood, fcyl_u(X, s * 11.7, 3.0, 7.5, 9.7, 1.1))
            X.diff(hood, fbox(X, s * 11.7 - 1.1, s * 11.7 + 1.1, 7.5, 9.7, 3.0, 7.5))
        out['hood_mm3'] = round(hood.volume * 1000, 1); out['hood_lumps'] = hood.lumps.count
        nf = X.tbm.copy(f9); X.union(nf, X.tbm.copy(sf)); X.union(nf, X.tbm.copy(tray)); X.diff(nf, X.tbm.copy(sn))
        out['hood_x_front_mm3'] = vol_x(X, X.tbm.copy(hood), X.tbm.copy(nf))
        out['hood_x_env_mm3'] = vol_x(X, X.tbm.copy(hood), tb_copy(X, 'BME680_env'))
        foam = fbox(X, -10.5, 10.5, -8.0, 8.0, 3.5, 5.5)
        ftop = fbox(X, -10.5, 10.5, 7.5, 8.0, -12.0, 5.5); inter(X, ftop, X.tbm.copy(AIR))
        out['foam_x'] = {'front': vol_x(X, X.tbm.copy(foam), X.tbm.copy(nf)), 'hood': vol_x(X, X.tbm.copy(foam), X.tbm.copy(hood)),
                         'env': vol_x(X, X.tbm.copy(foam), tb_copy(X, 'BME680_env')),
                         'top_front': vol_x(X, X.tbm.copy(ftop), X.tbm.copy(nf)), 'top_hood': vol_x(X, X.tbm.copy(ftop), X.tbm.copy(hood)),
                         'top_env': vol_x(X, X.tbm.copy(ftop), tb_copy(X, 'BME680_env'))}
        out['env_x_newfront_mm3'] = vol_x(X, tb_copy(X, 'BME680_env'), X.tbm.copy(nf))
        out['lead_x_newfront_mm3'] = vol_x(X, tb_copy(X, 'LEAD_BME680'), X.tbm.copy(nf))
        if not dry:
            old = X.body('HOUSING_F_front'); old.name = 'HOUSING_F_front_d9c'
            fb = X.add(X.tbm.copy(f9), 'HOUSING_F_front')
            try:
                fb.material = old.material
            except Exception:
                pass
            try:
                fb.appearance = old.appearance
            except Exception:
                pass
            old.isLightBulbOn = False
            X.combine(fb, [X.add(sf, 'D9F_fill_tmp')]); fb = X.body('HOUSING_F_front')
            X.combine(fb, [X.add(tray, 'D9F_tray_tmp')]); fb = X.body('HOUSING_F_front')
            X.combine(fb, [X.add(X.tbm.copy(sn), 'D9F_slots_tmp')], op=CUT); fb = X.body('HOUSING_F_front')
            out['front_cm3'] = round(fb.volume, 4); out['front_lumps'] = fb.lumps.count
            out['front_voids'] = sum(1 for li in range(fb.lumps.count) for si in range(fb.lumps.item(li).shells.count)
                                     if fb.lumps.item(li).shells.item(si).isVoid)
            o = X.body('BME_LID'); o.name = 'BME_LID_d9c'; o.isLightBulbOn = False
            o = X.body('FOAM_bme_env'); o.name = 'FOAM_bme_env_d9c'; o.isLightBulbOn = False
            hb = X.add(hood, 'BME_HOOD')
            try:
                hb.appearance = fb.appearance
            except Exception:
                pass
            X.add(foam, 'FOAM_bme_env').isLightBulbOn = False
            X.add(ftop, 'FOAM_bme_top_env').isLightBulbOn = False
            out['hood_cm3'] = round(hb.volume, 4)
            PR = lambda b_, t, u, w: X.inside(b_, XC + P(t, u, w)[0], P(t, u, w)[1], P(t, u, w)[2])
            out['probes'] = {'cavity_free': not PR(fb, 0, 0, 0), 'no_back_wall': not PR(fb, 0, 0, 6.1),
                             'side_wall': PR(fb, 11.7, 0, 2.0), 'side_wall_neg': PR(fb, -11.7, 0, 2.0), 'floor': PR(fb, 5, -8.6, 4.5),
                             'lip': PR(fb, 5, -7.5, 7.1), 'wedge': PR(fb, 5, -12.0, 0.0), 'slot_free': not PR(fb, 0, -8.6, 5.0),
                             'pin': PR(fb, 11.7, 10.0, 3.0), 'pad': PR(fb, 9.25, 6.75, -3.2), 'top_open': not PR(fb, 0, 8.3, 2.0),
                             'old_slot_filled': PR(fb, 0, -7.0, -4.75), 'new_slot1_open': not PR(fb, 0, -3.0, -4.75),
                             'new_slot2_open': not PR(fb, 0, 3.0, -4.75), 'hood_back': PR(hb, 0, 0, 6.1), 'hood_top': PR(hb, 0, 8.6, 2.0),
                             'hood_slot_free': not PR(hb, 11.7, 8.6, 5.0)}
        out['dry'] = dry
        out['left_over'] = [b_.name for b_ in X.comp.bRepBodies if b_.name.endswith('_tmp')]
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d9f_bme_tray_hood', 'dry' if globals().get('DRY', True) else 'run', out)
    print(json.dumps(out, separators=(',', ':')))
