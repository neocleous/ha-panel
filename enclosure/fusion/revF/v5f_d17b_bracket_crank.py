# rev F d17b (2026-11-06): Daniel 21:00 – crank the main-board bracket's right column so a finger goes straight along the floor
#   to the microSD (d16's channel). MAIN_BRACKET's right half loses its foot, tab and column below z 21 (x_rel −54.5…−44.5); it
#   gains a foot boss Ø8 z 2.5–11 with the Ruthex M3 hole Ø4.0 z 2.4–9.5 at (−65.0, −57.0), a leg 5.5 × 4.5 to z 27, a knee
#   z 21–27 back to the column and a 45° gusset under the knee at the leg (the finger stays below z 17). HOUSING_F_front: the old
#   Ø3.4 + Ø6.5 × 1.0 c-bore at (−49.5, −58.0) filled, the same cut at the new axis, and the 0.05 layer d16a / d16f left of the
#   tie bridge's base (their cuts started at z 2.55; the floor's top is 2.5 there) cut away. Old states → *_d17 (hidden). DRY default.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
EXP = {'MAIN_BRACKET': 5.3431, 'HOUSING_F_front': 235.2273}
AX_OLD = (-49.5, -58.0)
AX_NEW = (-65.0, -57.0)                                     # c-bore clear of the joint's cloth relief under the floor
CUT_BB = [-54.5, -44.5, -63.5, -53.0, 2.0, 21.0]             # right foot, tab and column below the knee
LEG_BB = [-67.5, -62.0, -59.5, -55.0, 10.5, 27.0]
KNEE_BB = [-66.0, -46.5, -62.5, -55.0, 21.0, 27.0]
GUS_BB = [-62.0, -58.0, -59.5, -55.0, 17.0, 21.0]             # 45° gusset under the knee, from (x −62, z 17) to (x −58, z 21)
PAD_BB = [-62.0, -55.0, -59.0, -54.0, 2.5, 2.6]               # the tie bridge's 0.05 base layer (floor top 2.5)
AUDD = os.path.expanduser('~/Documents/audit/data')
NEWP = ['TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'BME_HOOD', 'FOAM_bme_env', 'FOAM_bme_top_env']


def zcyl(X, ax, r, z0, z1):
    return X.tbm.createCylinderOrCone(Dw(XC + ax[0], ax[1], z0), r / 10, Dw(XC + ax[0], ax[1], z1), r / 10)


def unit(v):
    n = math.sqrt(sum(c * c for c in v)); return tuple(c / n for c in v)


def halfspace(X, p0, n, a2, L=60.0):                         # keeps n·(p − p0) <= 0; a2 ⟂ n
    n = unit(n); c = tuple(p0[i] - n[i] * L / 2 for i in range(3))
    return lbox(X, c, n, a2, L, L, L)


def run(_context):
    X = Ctx(); out = {}; t0 = time.time(); dry = globals().get('DRY', True)
    try:
        for k, v in EXP.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard: %s %s' % (k, None if b is None else round(b.volume, 4)))
        for n in ('MAIN_BRACKET_d17', 'HOUSING_F_front_d17'):
            if X.body(n) is not None:
                raise RuntimeError('%s exists already' % n)
        br0 = tb_copy(X, 'MAIN_BRACKET')
        br = X.tbm.copy(br0); X.diff(br, wbox_rel(X, CUT_BB))
        boss = zcyl(X, AX_NEW, 4.0, 2.5, 11.0)
        leg = wbox_rel(X, LEG_BB)
        knee = wbox_rel(X, KNEE_BB)
        gus = wbox_rel(X, GUS_BB); inter(X, gus, halfspace(X, (GUS_BB[0], -57.0, GUS_BB[4]), (1.0, 0.0, -1.0), (0.0, 1.0, 0.0)))
        for t in (boss, leg, knee, gus):
            X.union(br, t)
        X.diff(br, zcyl(X, AX_NEW, 2.0, 2.4, 9.5))
        rl = X.tbm.copy(br); inter(X, rl, wbox_rel(X, [-80.0, 0.0, -80.0, -40.0, 0.0, 100.0]))
        out['bracket_tb'] = {'cm3': round(br.volume, 4), 'lumps': br.lumps.count, 'right_mm3': round(rl.volume * 1000, 2),
                             'right_bb': [round(c, 2) for c in wbb(X, rl)], 'gusset_mm3': round(gus.volume * 1000, 2)}
        fr0 = tb_copy(X, 'HOUSING_F_front')
        fr = X.tbm.copy(fr0); X.union(fr, zcyl(X, AX_OLD, 3.3, 0.0, 2.5))
        filled = round((fr.volume - fr0.volume) * 1000, 2)
        X.diff(fr, zcyl(X, AX_NEW, 1.7, -1.0, 3.0)); X.diff(fr, zcyl(X, AX_NEW, 3.25, -1.0, 1.0))
        v_ = fr.volume; X.diff(fr, wbox_rel(X, PAD_BB)); pad = round((v_ - fr.volume) * 1000, 3)
        out['front_tb'] = {'cm3': round(fr.volume, 4), 'lumps': fr.lumps.count, 'filled_mm3': filled, 'pad_mm3': pad,
                           'net_mm3': round((fr.volume - fr0.volume) * 1000, 2)}
        rec = wbox_rel(X, [-78.0, -58.0, -64.0, -50.0, 0.02, 1.2]); X.diff(rec, X.tbm.copy(fr0))   # existing underside recesses
        cb = zcyl(X, AX_NEW, 3.25, -1.0, 1.0)
        out['underside_recess'] = {'lumps': [[round(l.volume * 1000, 2)] + [round(c, 2) for c in wbb(X, X.tbm.copy(l))] for l in rec.lumps],
                                   'x_new_cbore_mm3': vol_x(X, rec, cb)}
        names = json.load(open(os.path.join(AUDD, 'a2a_parts.json'))) + NEWP
        xs = {}
        for n in names:
            if n in ('MAIN_BRACKET', 'HOUSING_F_front') or X.body(n) is None:
                continue
            a = vol_x(X, X.tbm.copy(br), tb_copy(X, n)); b_ = vol_x(X, X.tbm.copy(br0), tb_copy(X, n))
            if a > 0 or b_ > 0:
                xs[n] = [a, b_]
        xs['HOUSING_F_front'] = [vol_x(X, X.tbm.copy(br), X.tbm.copy(fr)), vol_x(X, X.tbm.copy(br0), X.tbm.copy(fr0))]
        xs['HOUSING_F_door'] = [vol_x(X, X.tbm.copy(br), tb_copy(X, 'HOUSING_F_door')), vol_x(X, X.tbm.copy(br0), tb_copy(X, 'HOUSING_F_door'))]
        out['bracket_x_parts_new_old'] = xs
        if not dry:
            ob = X.body('MAIN_BRACKET'); app = ob.appearance; mat = ob.material
            ob.name = 'MAIN_BRACKET_d17'; ob.isLightBulbOn = False
            nb = X.add(br, 'MAIN_BRACKET')
            of = X.body('HOUSING_F_front'); appf = of.appearance; matf = of.material
            of.name = 'HOUSING_F_front_d17'; of.isLightBulbOn = False
            nf = X.add(fr, 'HOUSING_F_front')
            for (b_, m_, a_) in ((nb, mat, app), (nf, matf, appf)):
                for attr, val in (('material', m_), ('appearance', a_)):
                    try:
                        setattr(b_, attr, val)
                    except Exception:
                        pass
            I = lambda b_, x, y, z: X.inside(b_, XC + x, y, z)
            out['applied'] = {'bracket_cm3': round(nb.volume, 4), 'bracket_lumps': nb.lumps.count, 'front_cm3': round(nf.volume, 4),
                              'front_lumps': nf.lumps.count}
            out['probes'] = {'old_foot_gone': not I(nb, -49.5 + 3.0, -58.0, 5.0), 'old_column_low_gone': not I(nb, -49.5, -60.5, 15.0),
                             'column_kept': I(nb, -49.5, -60.5, 30.0), 'knee': I(nb, -56.0, -58.0, 24.0), 'leg': I(nb, -64.75, -57.25, 15.0),
                             'gusset': I(nb, -61.5, -57.0, 19.0), 'under_gusset_open': not I(nb, -59.0, -57.0, 18.0),
                             'boss_wall': I(nb, AX_NEW[0] + 3.0, -57.0, 5.0), 'insert_hole_open': not I(nb, AX_NEW[0], -57.0, 5.0),
                             'hole_top_closed': I(nb, AX_NEW[0], -57.0, 10.25), 'old_hole_filled': I(nf, -49.5, -58.0, 1.25),
                             'old_cbore_filled': I(nf, -49.5 + 2.5, -58.0, 0.5), 'new_hole_open': not I(nf, AX_NEW[0], -57.0, 1.75),
                             'new_cbore_open': not I(nf, AX_NEW[0] + 2.5, -57.0, 0.5), 'floor_round_new': I(nf, AX_NEW[0] + 2.5, -57.0, 1.75), 'pad_gone': not I(nf, -58.5, -56.5, 2.53),
                             'floor_under_pad': I(nf, -58.5, -56.5, 2.45)}
        out['dry'] = dry
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d17b_bracket_crank', 'dry' if globals().get('DRY', True) else 'run', out)
    print(json.dumps(out, separators=(',', ':')))
