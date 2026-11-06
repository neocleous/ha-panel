# rev F d16a (2026-11-06): microSD by finger (Daniel 19:52 / 19:58: finger notch, no extender; the right box made taller to win
#   the air back). Replaces d14's hatch. SPKBOX_R rebuilt from SPKBOX_R_d14 (before the hatch):
#   - finger channel C (x_rel -64.0…-45.9, y from the rear face to -30.0, z up to 16.0, open at the bottom and toward the
#     Pi) + card slot K (x_rel -61.3…-45.9, y -36.2…-23.6, z up to 8.5) so the card slides 15.4 toward -x; walls 1.5 = W ∩ old
#     chamber air (the lower bore stays a sealed tube from y -30.0 forward; its rear part goes with the channel);
#   - top raised RAISE mm: the top 6 mm of the box (outer) and of its air (inner) copied up in 1 mm steps, outside the BME680
#     tray's footprint (the box passes under it at lift 6) and the LCD lane corner, clipped to TOOL_cav_1p2_slide / _2p7_slide.
#   HOUSING_F_front restored from HOUSING_F_front_d14 (solid floor) without the right floor tie bridge, which stood in the
#   finger's way behind the box. HATCH_COVER, SD_SLED -> *_d16 (hidden). DRY (default True) builds and reports only.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
EXP = {'SPKBOX_R': 25.5694, 'SPKBOX_R_d14': 25.6435, 'HOUSING_F_front': 234.701, 'HOUSING_F_front_d14': 235.3238,
       'HATCH_COVER': 0.586, 'SD_SLED': 1.1956}
RAISE = int(globals().get('RAISE', 6))
C_BB = [-64.0, -45.9, -53.0, -30.0, 3.0, 16.0]
K_BB = [-61.3, -45.9, -36.2, -23.6, 3.0, 8.5]
W_BBS = [[-65.5, -46.2, -51.9, -28.5, 3.9, 17.5], [-62.8, -46.2, -37.7, -22.1, 3.9, 10.0]]
EXCL_OUT = [[-83.5, -56.9, -60.0, -25.0, 60.0, 100.0], [-50.0, -40.0, -40.0, 5.0, 60.0, 100.0]]   # BME680 tray, LCD lane strip
BRIDGE_BB = [-61.7, -55.1, -58.7, -54.3, 2.55, 8.2]                                                # right floor tie bridge
PCIN = adsk.fusion.PointContainment.PointInsidePointContainment


def grow(bb, m):
    return [bb[0] - m, bb[1] + m, bb[2] - m, bb[3] + m, bb[4], bb[5]]


def chamber_tb(X, box_tb, sx):
    bb = wbb(X, box_tb); g = 1.0
    Rb = [bb[0] - g, bb[1] + g, bb[2] - g, bb[3] + g, bb[4] - g, bb[5] + g]
    A = wbox_rel(X, Rb)
    X.diff(A, X.tbm.copy(box_tb)); X.diff(A, wbox_rel(X, [Rb[0], Rb[1], -3.7, -3.0, Rb[4], Rb[5]]))
    a = Dw(XC + sx * 62.0, -53.0, 30.0); b = Dw(XC + sx * 62.0, -49.5, 30.0)
    X.diff(A, X.tbm.createCylinderOrCone(a, 0.16, b, 0.16))
    pc = Dw(XC + sx * 70.5, -30.0, 62.0)
    for L in A.lumps:
        t = X.tbm.copy(L)
        if t.pointContainment(pc) == PCIN:
            cb = wbb(X, t)
            return t, all(abs(cb[i] - Rb[i]) > 0.05 for i in range(6))
    return None, False


def stack_up(X, t, z0, z1, n, zcut):            # copies of t ∩ [z0, z1] moved +1…+n, kept above zcut
    s = X.tbm.copy(t); inter(X, s, wbox_rel(X, [-200, 200, -200, 200, z0, z1]))
    acc = None
    for k in range(1, n + 1):
        c = X.tbm.copy(s); mvw(X, c, 0.0, 0.0, float(k))
        acc = c if acc is None else X.union(acc, c)
    inter(X, acc, wbox_rel(X, [-200, 200, -200, 200, zcut, z1 + n + 1]))
    return acc


def run(_context):
    X = Ctx(); out = {}; t0 = time.time(); dry = globals().get('DRY', True)
    try:
        for k, v in EXP.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard: %s %s' % (k, None if b is None else round(b.volume, 4)))
        for n in ('SPKBOX_R_d16', 'HOUSING_F_front_d16', 'HATCH_COVER_d16', 'SD_SLED_d16'):
            if X.body(n) is not None:
                raise RuntimeError('%s exists already' % n)
        base = tb_copy(X, 'SPKBOX_R_d14')
        A0, sealed0 = chamber_tb(X, base, -1)
        out['old_air'] = {'upper': round(A0.volume, 3), 'sealed': sealed0}
        F = X.tbm.copy(base); X.union(F, X.tbm.copy(A0))
        new = X.tbm.copy(base)
        if RAISE > 0:
            Fr = stack_up(X, F, 70.0, 76.0, RAISE, 75.9)
            Ar = stack_up(X, A0, 68.5, 74.5, RAISE, 74.4)
            for e in EXCL_OUT:
                X.diff(Fr, wbox_rel(X, e)); X.diff(Ar, wbox_rel(X, grow(e, 1.5)))
            inter(X, Fr, tb_copy(X, 'TOOL_cav_1p2_slide')); inter(X, Ar, tb_copy(X, 'TOOL_cav_2p7_slide'))
            X.union(new, Fr); X.diff(new, Ar)
            out['raise'] = {'mm': RAISE, 'outer_add_mm3': round(Fr.volume * 1000, 1), 'air_add_mm3': round(Ar.volume * 1000, 1),
                            'outer_bb': [round(c, 2) for c in wbb(X, Fr)] if Fr.volume > 0 else None}
        W = None
        for bb in W_BBS:
            w = wbox_rel(X, bb); W = w if W is None else X.union(W, w)
        inter(X, W, X.tbm.copy(A0))
        X.union(new, W)
        N = wbox_rel(X, C_BB); X.union(N, wbox_rel(X, K_BB))
        X.diff(new, N)
        A1, sealed1 = chamber_tb(X, new, -1)
        s = tb_copy(X, 'SPK_R'); inter(X, s, X.tbm.copy(A1))
        out['box_tb'] = {'cm3': round(new.volume, 4), 'lumps': new.lumps.count, 'bb': [round(c, 2) for c in wbb(X, new)]}
        out['new_air'] = {'upper': round(A1.volume, 3), 'lower': round(A1.volume - s.volume, 3), 'sealed': sealed1}
        hp = X.tbm.createCylinderOrCone(Dw(XC - 52.75, -60.0, 10.25), 0.275, Dw(XC - 52.75, -9.0, 10.25), 0.275)
        out['bore_head_path_mm3'] = vol_x(X, hp, X.tbm.copy(new))
        ox = {}
        for n in ('SPK_R', 'PI5_F', 'PI5_F_cooler', 'HOUSING_F_front_d14', 'MAIN_BRACKET', 'BME_HOOD', 'KO_K5_LR', 'LEAD_BME680',
                  'LEAD_SPK_R', 'TOUCH_CLIP_R', 'MAIN_front_env', 'LEAD_RADAR'):
            if X.body(n) is not None:
                ox[n] = [vol_x(X, X.tbm.copy(new), tb_copy(X, n)), vol_x(X, X.tbm.copy(base), tb_copy(X, n))]
        out['new_vs_old_x'] = ox                                                    # [new, old] overlaps (mm³)
        fr = tb_copy(X, 'HOUSING_F_front_d14'); br = X.tbm.copy(fr); inter(X, br, wbox_rel(X, BRIDGE_BB))
        out['bridge_mm3'] = round(br.volume * 1000, 2); out['bridge_bb'] = [round(c, 2) for c in wbb(X, br)] if br.volume > 0 else None
        nf = X.tbm.copy(fr); X.diff(nf, wbox_rel(X, BRIDGE_BB))
        out['front_tb'] = {'cm3': round(nf.volume, 4), 'lumps': nf.lumps.count}
        if not dry:
            o = X.body('SPKBOX_R'); app = o.appearance; mat = o.material
            o.name = 'SPKBOX_R_d16'; o.isLightBulbOn = False
            nb = X.add(new, 'SPKBOX_R')
            for attr, val in (('material', mat), ('appearance', app)):
                try:
                    setattr(nb, attr, val)
                except Exception:
                    pass
            of = X.body('HOUSING_F_front'); appf = of.appearance; matf = of.material
            of.name = 'HOUSING_F_front_d16'; of.isLightBulbOn = False
            fb = X.add(nf, 'HOUSING_F_front')
            for attr, val in (('material', matf), ('appearance', appf)):
                try:
                    setattr(fb, attr, val)
                except Exception:
                    pass
            for n in ('HATCH_COVER', 'SD_SLED'):
                b = X.body(n); b.name = n + '_d16'; b.isLightBulbOn = False
            I = lambda b_, x, y, z: X.inside(b_, XC + x, y, z)
            out['applied'] = {'box_cm3': round(nb.volume, 4), 'box_lumps': nb.lumps.count, 'front_cm3': round(fb.volume, 4),
                              'front_lumps': fb.lumps.count}
            out['probes'] = {'channel_open': not I(nb, -55.0, -45.0, 9.0), 'card_slot_open': not I(nb, -58.0, -27.0, 6.9),
                             'channel_ceiling': I(nb, -55.0, -45.0, 16.75), 'channel_front_wall': I(nb, -58.0, -29.25, 12.0),
                             'outboard_wall': I(nb, -64.75, -45.0, 9.0), 'bore_open_front': not I(nb, -52.75, -15.0, 10.25),
                             'tube_wall_front': I(nb, -52.75, -15.0, 6.7), 'floor_restored': I(fb, -52.0, -30.0, 1.25),
                             'bridge_gone': not I(fb, -58.5, -56.5, 6.0), 'floor_under_bridge': I(fb, -58.5, -56.5, 1.25)}
        out['dry'] = dry
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d16a_finger_notch', 'dry' if globals().get('DRY', True) else 'run', out)
    print(json.dumps(out, separators=(',', ':')))
