# rev F d16d (2026-11-06): d16a's right box again with the raise kept out of the box's insertion path (B5j-3 sweep of the d16a
#   box: its raised top hit RESP_CARRIER at 42 inboard / lift 6 and the BME680 tray during the sideways move). Same notch.
#   No raise over x_rel <= -56.9 at y -60…-24 (the box passes under the tray), over the LCD lane strip, nor at y > -10
#   (under RESP_CARRIER at 42 inboard). Current SPKBOX_R (d16a) -> SPKBOX_R_d16a (hidden); rebuilt from SPKBOX_R_d14.
# (d16a header:) microSD by finger (Daniel 19:52 / 19:58: finger notch, no extender; the right box made taller to win
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
EXP = {'SPKBOX_R': globals().get('EXP_BOX', 26.7318), 'SPKBOX_R_d14': 25.6435, 'HOUSING_F_front': 235.2295}
OLD_NAME = globals().get('OLD_NAME', 'SPKBOX_R_d16a')                # name for the replaced box (hidden)
CY1 = globals().get('CY1', -30.0)                                     # channel's front end (y); its wall 1.5 further
RAISE = int(globals().get('RAISE', 6))
C_BB = [-64.0, -45.9, -53.0, CY1, 3.0, 16.0]
K_BB = [-61.3, -45.9, -36.2, -23.6, 3.0, 8.5]
W_BBS = [[-65.5, -46.2, -51.9, CY1 + 1.5, 3.9, 17.5], [-62.8, -46.2, -37.7, -22.1, 3.9, 10.0]]
EXCL_OUT = [[-100.0, -56.9, -60.0, -24.0, 60.0, 100.0], [-50.0, -40.0, -40.0, 5.0, 60.0, 100.0],
            [-100.0, -40.0, -10.0, 5.0, 60.0, 100.0]]          # under the BME680 tray's path, LCD lane strip, under RESP_CARRIER
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
        if X.body(OLD_NAME) is not None:
            raise RuntimeError('%s exists already' % OLD_NAME)
        base = tb_copy(X, 'SPKBOX_R_d14')
        A0, sealed0 = chamber_tb(X, base, -1)
        F = X.tbm.copy(base); X.union(F, X.tbm.copy(A0))
        new = X.tbm.copy(base)
        Fr = stack_up(X, F, 70.0, 76.0, RAISE, 75.9)
        Ar = stack_up(X, A0, 68.5, 74.5, RAISE, 74.4)
        for e in EXCL_OUT:
            X.diff(Fr, wbox_rel(X, e)); X.diff(Ar, wbox_rel(X, grow(e, 1.5)))
        inter(X, Fr, tb_copy(X, 'TOOL_cav_1p2_slide')); inter(X, Ar, tb_copy(X, 'TOOL_cav_2p7_slide'))
        X.union(new, Fr); X.diff(new, Ar)
        out['raise'] = {'mm': RAISE, 'outer_add_mm3': round(Fr.volume * 1000, 1), 'air_add_mm3': round(Ar.volume * 1000, 1),
                        'outer_bb': [round(c, 2) for c in wbb(X, Fr)] if Fr.volume > 0 else None, 'lumps': Fr.lumps.count}
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
        d_ = X.tbm.copy(new); X.diff(d_, tb_copy(X, 'SPKBOX_R'))
        out['vs_current_added_mm3'] = round(d_.volume * 1000, 2)
        out['spk_x_new_mm3'] = vol_x(X, X.tbm.copy(new), tb_copy(X, 'SPK_R'))
        if not dry:
            o = X.body('SPKBOX_R'); app = o.appearance; mat = o.material
            o.name = OLD_NAME; o.isLightBulbOn = False
            nb = X.add(new, 'SPKBOX_R')
            for attr, val in (('material', mat), ('appearance', app)):
                try:
                    setattr(nb, attr, val)
                except Exception:
                    pass
            out['applied'] = {'box_cm3': round(nb.volume, 4), 'box_lumps': nb.lumps.count}
        out['dry'] = dry
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d16d_box_reraise', 'dry' if globals().get('DRY', True) else 'run', out)
    print(json.dumps(out, separators=(',', ':')))
