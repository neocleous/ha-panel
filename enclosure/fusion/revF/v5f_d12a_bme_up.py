# rev F d12a (2026-11-06): BME680 tray 6 mm higher. The right speaker box goes in by the B5j-3 path (sideways at lift 6, its
#   top at z 82); d9's tray, whose 45° underside reached z 77 at the wall, sat in that path (72.5 mm³ at 6 mm from the seat).
#   Everything of d9c / d9f / d9g moves +6.0 up the wall (u), so +10.0 from the original sensor position; the underside is
#   clipped at z 83 (1.0 over the box's top in the path) - a 1.2 flat at the wall's foot, prints without support.
#   HOUSING_F_front: rebuilt from HOUSING_F_front_d9 (before any BME work) - original slots filled, slots +10.0 up, tray
#   (floor flush to w 7.5 with the hood groove, side walls 2.4, pads, lead slot, pins), then d10d's lip-end cut again
#   (TOOL_lip_end). Old front -> HOUSING_F_front_d12a; BME_HOOD, BME680_env, FOAM_bme_env, FOAM_bme_top_env, LEAD_BME680,
#   TOOL_bme680_slots -> *_d12 (hidden) and rebuilt at the new height. The board sits 0.6 further from the wall (the wall
#   leans in more up here; pads 0.6 taller); the foam zone behind it is 1.9 (2 mm A13 – the real board's stack sets the
#   squeeze).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
FR = 'HOUSING_F_front'
EXP = {FR: 235.31, 'HOUSING_F_front_d9': 233.5514, 'BME_HOOD': 0.808}
CE0 = (-73.44, -42.106, 91.325)
DU = 10.0
Z_BOX = 83.0
EW = 0.6                                   # board 0.6 further into the room: the wall leans in more up here (env ∩ wall 4.47 → 0)


def _unit(v):
    n = math.sqrt(sum(c * c for c in v)); return tuple(c / n for c in v)


TT = _unit((0.6504, -0.7596, 0.0))
_u = (0.1139, 0.0976, 0.9887); _k = sum(_u[i] * TT[i] for i in range(3))
UU = _unit(tuple(_u[i] - _k * TT[i] for i in range(3)))
NI = (-(TT[1] * UU[2] - TT[2] * UU[1]), -(TT[2] * UU[0] - TT[0] * UU[2]), -(TT[0] * UU[1] - TT[1] * UU[0]))
CE = tuple(CE0[i] + DU * UU[i] for i in range(3))


def P(t, u, w):
    return tuple(CE[i] + t * TT[i] + u * UU[i] + w * NI[i] for i in range(3))


def fbox(X, t0, t1, u0, u1, w0, w1):
    c = P((t0 + t1) / 2, (u0 + u1) / 2, (w0 + w1) / 2)
    return lbox(X, c, TT, UU, t1 - t0, u1 - u0, w1 - w0)


def fcyl_u(X, t, w, u0, u1, r0, r1=None):
    a = P(t, u0, w); b = P(t, u1, w)
    return X.tbm.createCylinderOrCone(Dw(XC + a[0], a[1], a[2]), r0 / 10, Dw(XC + b[0], b[1], b[2]), (r0 if r1 is None else r1) / 10)


def air(X, skin='TOOL_inner_skin_0p7'):
    a = tb_copy(X, 'INNER_E'); X.diff(a, tb_copy(X, skin)); return a


def run(_context):
    X = Ctx(); out = {}; t0 = time.time(); dry = globals().get('DRY', True)
    try:
        for k, v in EXP.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard: %s %s' % (k, None if b is None else round(b.volume, 4)))
        REN = ['BME_HOOD', 'BME680_env', 'FOAM_bme_env', 'FOAM_bme_top_env', 'LEAD_BME680', 'TOOL_bme680_slots']
        for n in ['HOUSING_F_front_d12a'] + [r + '_d12' for r in REN]:
            if X.body(n) is not None:
                raise RuntimeError('%s exists already' % n)
        for n in ('TOOL_lip_end', 'TOOL_bme680_slots_d9', 'BME680_env_d9', 'INNER_E', 'TOOL_inner_skin_0p7', 'TOOL_inner_skin_1p4'):
            if X.body(n) is None:
                raise RuntimeError('%s missing' % n)
        mv = (DU * UU[0], DU * UU[1], DU * UU[2])
        AIR = air(X)
        region = fbox(X, -18, 18, -26, 16, -12, 12)
        inter(X, AIR, region)
        outer = tb_copy(X, 'REF_F_outer'); X.diff(outer, tb_copy(X, 'TOOL_outer_skin_0p7')); inter(X, outer, X.tbm.copy(region))
        wallp = X.tbm.copy(outer); X.diff(wallp, X.tbm.copy(AIR))
        so = tb_copy(X, 'TOOL_bme680_slots_d9')
        sf = X.tbm.copy(wallp); inter(X, sf, X.tbm.copy(so))
        sn = X.tbm.copy(so); mvw(X, sn, *mv)
        # tray
        tray = None
        for s in (1, -1):
            sw = fbox(X, min(s * 10.5, s * 12.9), max(s * 10.5, s * 12.9), -9.2, 8.0, -12.0, 5.5)
            tray = sw if tray is None else X.union(tray, sw)
        X.union(tray, fbox(X, -12.9, 12.9, -9.2, -8.0, -12.0, 7.5))
        d = tuple((UU[i] - NI[i]) / math.sqrt(2) for i in range(3))
        s0 = (-9.2 - 7.5) / math.sqrt(2); L = 120.0
        half = lbox(X, tuple(CE[i] + d[i] * (s0 + L / 2) for i in range(3)), TT, d, L, L, L)
        wg = fbox(X, -12.9, 12.9, -30.0, -9.2, -12.0, 7.5); inter(X, wg, half)
        X.union(tray, wg)
        inter(X, tray, X.tbm.copy(outer)); inter(X, tray, X.wbox(-250, 250, -250, 250, Z_BOX, 260))
        cav = fbox(X, -10.5, 10.5, -8.0, 8.6, -12.0, 5.5); inter(X, cav, X.tbm.copy(AIR))
        slot = fbox(X, -2.0, 2.0, -30.0, -7.9, 0.0, 7.6); inter(X, slot, X.tbm.copy(AIR))
        groove = fbox(X, -12.9, 12.9, -8.6, -7.9, 5.5, 6.9)
        X.diff(tray, cav); X.diff(tray, slot); X.diff(tray, groove)
        for tc in (9.25, -9.25):
            for uc in (6.75, -6.75):
                p_ = fbox(X, tc - 0.75, tc + 0.75, uc - 0.75, uc + 0.75, -12.0, -3.0 + EW); inter(X, p_, X.tbm.copy(AIR))
                X.union(tray, p_)
        for s in (1, -1):
            X.union(tray, fcyl_u(X, s * 11.7, 3.0, 7.9, 11.0, 0.9))
        out['tray_mm3'] = round(tray.volume * 1000, 1)
        out['tray_bb'] = [round(v, 2) for v in wbb(X, tray)]
        nf = tb_copy(X, 'HOUSING_F_front_d9'); X.union(nf, X.tbm.copy(sf)); X.union(nf, X.tbm.copy(tray))
        X.diff(nf, X.tbm.copy(sn)); X.diff(nf, X.tbm.copy(groove)); X.diff(nf, tb_copy(X, 'TOOL_lip_end'))
        out['newfront_cm3_tb'] = round(nf.volume, 4)
        cur = tb_copy(X, FR)
        a_ = X.tbm.copy(nf); X.diff(a_, X.tbm.copy(cur)); b_ = X.tbm.copy(cur); X.diff(b_, X.tbm.copy(nf))
        out['vs_current_mm3'] = {'added': round(a_.volume * 1000, 1), 'removed': round(b_.volume * 1000, 1),
                                 'added_bb': [round(v, 1) for v in wbb(X, a_)] if a_.volume > 0 else None,
                                 'removed_bb': [round(v, 1) for v in wbb(X, b_)] if b_.volume > 0 else None}
        ox = {}
        for n in ('LEAD_RADAR', 'HOUSING_F_door', 'MAIN_BRACKET', 'KO_K5_LR', 'KO_K5_UR', 'KO_capkey_SR', 'LD2410C_env_F', 'SPK_R'):
            if X.body(n) is not None:
                v = vol_x(X, X.tbm.copy(tray), tb_copy(X, n))
                if v > 0.0:
                    ox[n] = v
        b = tb_copy(X, 'SPKBOX_R'); mvw(X, b, 0, 0, 7.0); ox['SPKBOX_R_up7'] = vol_x(X, X.tbm.copy(tray), b)
        out['tray_x'] = ox
        # hood, envelopes, lead
        lair = air(X, 'TOOL_inner_skin_1p4'); inter(X, lair, X.tbm.copy(region))
        hood = fbox(X, -12.9, 12.9, -8.5, 9.2, 5.5, 6.7)
        tp = fbox(X, -13.9, 13.9, 8.0, 9.2, -12.0, 6.7); inter(X, tp, lair)
        X.union(hood, tp)
        for s in (1, -1):
            X.diff(hood, fcyl_u(X, s * 11.7, 3.0, 7.5, 9.7, 1.2))
        env = tb_copy(X, 'BME680_env_d9'); mvw(X, env, mv[0] + EW * NI[0], mv[1] + EW * NI[1], mv[2] + EW * NI[2])
        foam = fbox(X, -10.5, 10.5, -8.0, 8.0, 3.0 + EW, 5.5)
        ftop = fbox(X, -10.5, 10.5, 7.5, 8.0, -12.0, 5.5); inter(X, ftop, X.tbm.copy(AIR))
        hd = P(0.0, -7.5, 1.75); bl = P(0.0, -15.5, 1.75); bo = P(0.0, -15.5, 10.0)
        pts = [(-36.0, 2.0, 46.0), (-36.0, 0.5, 52.0), (-38.0, -8.0, 60.0), (-38.0, -22.0, 92.0), (-50.0, -26.0, 96.0), (-60.0, -32.0, 98.0),
               bo, bl, hd]
        lead = None
        for a, b2 in zip(pts[:-1], pts[1:]):
            c_ = X.tbm.createCylinderOrCone(Dw(XC + a[0], a[1], a[2]), 0.15, Dw(XC + b2[0], b2[1], b2[2]), 0.15)
            lead = c_ if lead is None else X.union(lead, c_)
        for q in pts[1:-1]:
            X.union(lead, X.tbm.createSphere(Dw(XC + q[0], q[1], q[2]), 0.15))
        out['lead_len_mm'] = round(sum(math.dist(a, b2) for a, b2 in zip(pts[:-1], pts[1:])), 1)
        chk = {'hood_x_front': vol_x(X, X.tbm.copy(hood), X.tbm.copy(nf)), 'hood_x_env': vol_x(X, X.tbm.copy(hood), X.tbm.copy(env)),
               'env_x_front': vol_x(X, X.tbm.copy(env), X.tbm.copy(nf)), 'foam_x_front': vol_x(X, X.tbm.copy(foam), X.tbm.copy(nf)),
               'ftop_x_front': vol_x(X, X.tbm.copy(ftop), X.tbm.copy(nf)), 'lead_x_front': vol_x(X, X.tbm.copy(lead), X.tbm.copy(nf)),
               'lead_x_hood': vol_x(X, X.tbm.copy(lead), X.tbm.copy(hood))}
        for n in ('KO_K5_LR', 'LEAD_RADAR', 'SPKBOX_R', 'MAIN_front_env', 'LD2410C_env_F'):
            if X.body(n) is not None:
                chk['lead_x_' + n] = vol_x(X, X.tbm.copy(lead), tb_copy(X, n))
                chk['hood_x_' + n] = vol_x(X, X.tbm.copy(hood), tb_copy(X, n))
        out['checks'] = chk
        if not dry:
            old = X.body(FR); app = old.appearance; mat = old.material
            old.name = 'HOUSING_F_front_d12a'; old.isLightBulbOn = False
            for r in REN:
                o = X.body(r); o.name = r + '_d12'; o.isLightBulbOn = False
            fb = X.add(tb_copy(X, 'HOUSING_F_front_d9'), FR)
            try:
                fb.material = mat
            except Exception:
                pass
            try:
                fb.appearance = app
            except Exception:
                pass
            X.combine(fb, [X.add(sf, 'D12A_fill_tmp')]); fb = X.body(FR)
            X.combine(fb, [X.add(tray, 'D12A_tray_tmp')]); fb = X.body(FR)
            X.combine(fb, [X.add(X.tbm.copy(sn), 'D12A_slots_tmp')], op=CUT); fb = X.body(FR)
            X.combine(fb, [X.add(groove, 'D12A_groove_tmp')], op=CUT); fb = X.body(FR)
            X.combine(fb, [X.body('TOOL_lip_end')], op=CUT, keep=True); fb = X.body(FR)
            X.body('TOOL_lip_end').isLightBulbOn = False
            stray = []
            for b3 in list(X.comp.bRepBodies):
                if b3.name.startswith(FR + ' ('):
                    stray.append([b3.name, round(b3.volume * 1000, 4)])
                    b3.name = 'HOUSING_F_front_d12a_sliver%d' % len(stray); b3.isLightBulbOn = False
            out['stray_bodies'] = stray
            out['front_cm3'] = round(fb.volume, 4); out['front_lumps'] = fb.lumps.count
            out['front_voids'] = sum(1 for li in range(fb.lumps.count) for si in range(fb.lumps.item(li).shells.count)
                                     if fb.lumps.item(li).shells.item(si).isVoid)
            X.add(sn, 'TOOL_bme680_slots').isLightBulbOn = False
            hb = X.add(hood, 'BME_HOOD')
            try:
                hb.appearance = app
            except Exception:
                pass
            X.add(env, 'BME680_env').isLightBulbOn = False
            X.add(foam, 'FOAM_bme_env').isLightBulbOn = False
            X.add(ftop, 'FOAM_bme_top_env').isLightBulbOn = False
            X.add(lead, 'LEAD_BME680').isLightBulbOn = False
            out['hood_cm3'] = round(hb.volume, 4)
            PR = lambda b_, t, u, w: X.inside(b_, XC + P(t, u, w)[0], P(t, u, w)[1], P(t, u, w)[2])
            out['probes'] = {'cavity_free': not PR(fb, 0, 0, 0), 'side_wall': PR(fb, 11.7, 0, 2.0), 'floor': PR(fb, 5, -8.9, 4.5),
                             'groove': not PR(fb, 5, -8.3, 6.2), 'wedge': PR(fb, 5, -12.0, 2.0), 'slot_free': not PR(fb, 0, -8.6, 5.0),
                             'pin': PR(fb, 11.7, 10.0, 3.0), 'pad': PR(fb, 9.25, 6.75, -3.2),
                             'old_slot_filled': PR(fb, 0, -13.0, -4.75), 'new_slot1_open': not PR(fb, 0, -3.0, -4.75),
                             'new_slot2_open': not PR(fb, 0, 3.0, -4.75), 'hood_in_groove': PR(hb, 5, -8.3, 6.1),
                             'hood_hole': not PR(hb, 11.7, 8.6, 3.0), 'hood_top': PR(hb, 0, 8.6, 2.0)}
            out['lip_end_square'] = not X.inside(fb, XC + 0.0, -63.45, 127.6)
        out['dry'] = dry
        out['left_over'] = [b4.name for b4 in X.comp.bRepBodies if b4.name.endswith('_tmp')]
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d12a_bme_up', 'dry' if globals().get('DRY', True) else 'run', out)
    print(json.dumps(out, separators=(',', ':')))
