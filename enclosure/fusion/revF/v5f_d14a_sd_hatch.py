# rev F d14a (2026-11-06): microSD floor hatch, option 1 (Daniel 19:22). The card (x_rel -44.85…-29.45, z 6.41–7.41) is pulled
#   15.4 toward -x into a pocket in SPKBOX_R's inboard-bottom corner and drops out through a slot in the floor.
#   SPKBOX_R: + walls W (1.5 round the pocket, inside the old chamber air; W minus a r 3.15 cylinder keeps the lower bore
#   open), - pocket P (open toward the Pi and downward; it opens the bore's bottom over 12.6 mm, a 4.3 slot at z 8.0).
#   HOUSING_F_front: - slot S 17.7 x 13.0 through the floor - underside rebate R 0.8 deep for the cover's flange.
#   HATCH_COVER (new, printed): flange flush with the underside, plug, two 10 mm side beams with 45° / 45° catches that
#   seat on the floor's top at the slot's long edges (in the 1.2 gap under the box), fingernail notch. SD_SLED (new,
#   printed service tool, hidden): shoulder on the underside, stem, platform at the card's height, back-stop; refits the
#   card by pushing it 14.4 toward +x. DRY (default True) builds and reports; DRY False applies (old bodies -> *_d14).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
EXP = {'SPKBOX_R': 25.6435, 'HOUSING_F_front': 235.3238}
BX, BZ, BR = -52.75, 10.25, 3.1                 # lower screw bore of SPKBOX_R (axis along y)
P_BB = [-61.0, -45.9, -36.2, -23.6, 3.0, 8.0]   # pocket (void)
W_BB = [-62.5, -46.2, -37.7, -22.1, 3.9, 9.5]   # pocket + 1.5 walls (faces kept off the box's outer faces)
S_BB = [-61.2, -43.5, -36.4, -23.4, -1.0, 2.6]  # floor slot
R_BB = [-62.2, -42.9, -37.4, -22.4, -1.0, 0.8]  # underside rebate for the cover's flange


def unit(v):
    n = math.sqrt(sum(c * c for c in v)); return tuple(c / n for c in v)


def bore_cyl(X, r, y0=-60.0, y1=0.0):
    return X.tbm.createCylinderOrCone(Dw(XC + BX, y0, BZ), r / 10, Dw(XC + BX, y1, BZ), r / 10)


def halfspace(X, p0, n, a2, L=40.0):            # keeps n·(p - p0) <= 0; a2 ⟂ n
    n = unit(n)
    c = tuple(p0[i] - n[i] * L / 2 for i in range(3))
    return lbox(X, c, n, a2, L, L, L)


def cover(X):
    c = wbox_rel(X, [-62.1, -43.0, -37.3, -22.5, 0.0, 0.8])                      # flange, flush with the underside
    X.union(c, wbox_rel(X, [-61.1, -43.6, -36.3, -23.5, 0.8, 2.5]))             # plug
    for s, ye in ((1, -36.4), (-1, -23.4)):                                       # s 1: the -y edge, -1: the +y edge
        yf = ye + s * 0.1                                                         # beam's outer face, 0.1 inside the edge
        yb = sorted((yf, yf + s * 0.7)); yg = sorted((yf + s * 0.7, yf + s * 1.5))
        X.diff(c, wbox_rel(X, [-57.0, -46.5, yb[0], yb[1], 0.8, 2.6]))
        X.diff(c, wbox_rel(X, [-57.0, -46.5, yg[0], yg[1], 0.8, 2.6]))            # flex gap
        X.union(c, wbox_rel(X, [-58.5, -47.0, yb[0], yb[1], 0.8, 3.1]))           # beam, rooted at x -58.5…-57.0
        ya = yf - s * 0.35                                                        # catch apex, 0.25 beyond the slot edge
        w = wbox_rel(X, [-49.5, -47.0, min(yf, ya), max(yf, ya), 2.4, 3.1])
        inter(X, w, halfspace(X, (-48.0, yf, 2.4), (0.0, -s, -1.0), (1.0, 0.0, 0.0)))   # retaining face 45°
        inter(X, w, halfspace(X, (-48.0, yf, 3.1), (0.0, -s, 1.0), (1.0, 0.0, 0.0)))    # lead-in face 45°
        X.union(c, w)
    X.diff(c, wbox_rel(X, [-43.6, -42.9, -32.0, -27.0, -1.0, 0.5]))              # fingernail notch at the flange edge
    return c


def sled(X):
    s = wbox_rel(X, [-68.0, -50.0, -40.0, -20.0, -3.0, 0.0])                      # shoulder / handle on the underside
    X.union(s, wbox_rel(X, [-60.25, -58.25, -32.5, -26.5, 0.0, 5.41]))           # stem through the slot
    X.union(s, wbox_rel(X, [-60.25, -56.25, -34.9, -24.9, 5.41, 6.41]))          # platform (card bottom at 6.41)
    X.union(s, wbox_rel(X, [-60.25, -59.35, -34.9, -24.9, 6.41, 7.6]))           # back-stop
    return s


def run(_context):
    X = Ctx(); out = {}; t0 = time.time(); dry = globals().get('DRY', True)
    try:
        for k, v in EXP.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard: %s %s' % (k, None if b is None else round(b.volume, 4)))
        for n in ('SPKBOX_R_d14', 'HOUSING_F_front_d14', 'HATCH_COVER', 'SD_SLED', 'TOOL_sd_pocket', 'TOOL_sd_walls', 'TOOL_sd_slot'):
            if X.body(n) is not None:
                raise RuntimeError('%s exists already' % n)
        P_ = wbox_rel(X, P_BB)
        W_ = wbox_rel(X, W_BB); X.diff(W_, X.tbm.copy(P_)); X.diff(W_, bore_cyl(X, BR + 0.05))
        S_ = wbox_rel(X, S_BB); X.union(S_, wbox_rel(X, R_BB))
        box = tb_copy(X, 'SPKBOX_R')
        nb = X.tbm.copy(box); X.union(nb, X.tbm.copy(W_)); X.diff(nb, X.tbm.copy(P_))
        a_ = X.tbm.copy(nb); X.diff(a_, X.tbm.copy(box)); r_ = X.tbm.copy(box); X.diff(r_, X.tbm.copy(nb))
        out['box'] = {'old': round(box.volume, 4), 'new_tb': round(nb.volume, 4), 'added_mm3': round(a_.volume * 1000, 1),
                      'removed_mm3': round(r_.volume * 1000, 1), 'lumps': nb.lumps.count}
        fr = tb_copy(X, 'HOUSING_F_front')
        nf = X.tbm.copy(fr); X.diff(nf, X.tbm.copy(S_))
        out['front'] = {'old': round(fr.volume, 4), 'new_tb': round(nf.volume, 4), 'removed_mm3': round((fr.volume - nf.volume) * 1000, 1),
                        'lumps': nf.lumps.count}
        cv = cover(X); sl = sled(X)
        out['cover'] = {'mm3': round(cv.volume * 1000, 1), 'lumps': cv.lumps.count, 'bb': [round(v, 2) for v in wbb(X, cv)],
                        'x_front_new': vol_x(X, X.tbm.copy(cv), X.tbm.copy(nf)), 'x_box_new': vol_x(X, X.tbm.copy(cv), X.tbm.copy(nb)),
                        'x_pi': vol_x(X, X.tbm.copy(cv), tb_copy(X, 'PI5_F'))}
        out['sled'] = {'mm3': round(sl.volume * 1000, 1), 'lumps': sl.lumps.count, 'x_front_new': vol_x(X, X.tbm.copy(sl), X.tbm.copy(nf)),
                       'x_box_new': vol_x(X, X.tbm.copy(sl), X.tbm.copy(nb))}
        out['bore_head_path_x_box'] = {'old': vol_x(X, bore_cyl(X, 2.75, -60.0, -9.0), X.tbm.copy(box)),
                                       'new': vol_x(X, bore_cyl(X, 2.75, -60.0, -9.0), X.tbm.copy(nb))}
        if not dry:
            old = X.body('SPKBOX_R'); app = old.appearance; mat = old.material
            old.name = 'SPKBOX_R_d14'; old.isLightBulbOn = False
            bb_ = X.add(tb_copy(X, 'SPKBOX_R_d14'), 'SPKBOX_R')
            for attr, val in (('material', mat), ('appearance', app)):
                try:
                    setattr(bb_, attr, val)
                except Exception:
                    pass
            tw = X.add(X.tbm.copy(W_), 'TOOL_sd_walls'); tp = X.add(X.tbm.copy(P_), 'TOOL_sd_pocket')
            X.combine(X.body('SPKBOX_R'), [tw], op=JOIN, keep=True)
            X.combine(X.body('SPKBOX_R'), [tp], op=CUT, keep=True)
            tw.isLightBulbOn = False; tp.isLightBulbOn = False
            oldf = X.body('HOUSING_F_front'); appf = oldf.appearance; matf = oldf.material
            oldf.name = 'HOUSING_F_front_d14'; oldf.isLightBulbOn = False
            fb = X.add(tb_copy(X, 'HOUSING_F_front_d14'), 'HOUSING_F_front')
            for attr, val in (('material', matf), ('appearance', appf)):
                try:
                    setattr(fb, attr, val)
                except Exception:
                    pass
            ts = X.add(X.tbm.copy(S_), 'TOOL_sd_slot')
            X.combine(X.body('HOUSING_F_front'), [ts], op=CUT, keep=True); ts.isLightBulbOn = False
            stray = []
            for b3 in list(X.comp.bRepBodies):
                for base in ('SPKBOX_R', 'HOUSING_F_front'):
                    if b3.name.startswith(base + ' ('):
                        stray.append([b3.name, round(b3.volume * 1000, 4)])
                        b3.name = base + '_d14_sliver%d' % len(stray); b3.isLightBulbOn = False
            out['stray_bodies'] = stray
            hc = X.add(cv, 'HATCH_COVER')
            try:
                hc.appearance = appf
            except Exception:
                pass
            sb = X.add(sl, 'SD_SLED'); sb.isLightBulbOn = False
            nbx = X.body('SPKBOX_R'); nfx = X.body('HOUSING_F_front')
            out['applied'] = {'box_cm3': round(nbx.volume, 4), 'box_lumps': nbx.lumps.count,
                              'front_cm3': round(nfx.volume, 4), 'front_lumps': nfx.lumps.count,
                              'cover_cm3': round(hc.volume, 4), 'sled_cm3': round(sb.volume, 4)}
            I = lambda b_, x, y, z: X.inside(b_, XC + x, y, z)
            out['probes'] = {'pocket_open': not I(nbx, -53.0, -30.0, 6.9), 'pocket_open_low': not I(nbx, -58.0, -30.0, 4.5),
                             'ceiling': I(nbx, -58.0, -30.0, 8.75), 'outboard_wall': I(nbx, -61.75, -30.0, 6.0),
                             'back_wall': I(nbx, -58.0, -36.95, 6.0), 'front_wall': I(nbx, -58.0, -22.85, 6.0),
                             'bore_open_mid': not I(nbx, BX, -30.0, BZ), 'bore_open_rear': not I(nbx, BX, -45.0, BZ),
                             'tube_wall_kept': I(nbx, BX, -45.0, BZ - 3.55), 'slot_open': not I(nfx, -52.0, -30.0, 1.25),
                             'web_kept': I(nfx, -43.2, -30.0, 1.6), 'rebate': not I(nfx, -62.0, -30.0, 0.4),
                             'floor_kept': I(nfx, -63.0, -30.0, 1.25), 'floor_under_catch': I(nfx, -48.0, -36.6, 2.3)}
        out['dry'] = dry
        out['left_over'] = [b4.name for b4 in X.comp.bRepBodies if b4.name.endswith('_tmp')]
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d14a_sd_hatch', 'dry' if globals().get('DRY', True) else 'run', out)
    print(json.dumps(out, separators=(',', ':')))
