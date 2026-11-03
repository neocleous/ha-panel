# rev F block 2e (2026-11-03): DMA45-4 envelopes + baffle blocks (Daniel 22:35, decision 3: self-tapping, speaker forward).
# Envelope sheet: frame 46.0 x 46.0 x 3.0, 4 x D3.3 on +-17.75, basket D40 26.1 behind the flange (29.1 overall).
# Pose (handover/K6): axis along world y at (XC +-70.5, z 28); frame x_rel 47.5..93.5, z 5..51; frame front face y 0.0
# (K6 <= 2.0 and >= 3 behind the chin inner face; 0.0 keeps >= 0.5 to the R9.5 inner corner at z 51 after the D1 layer).
# SPK_L (+x) / SPK_R (-x): frame box y -3.0..0.0 + basket cylinder y -3.0..-29.1 (terminals not dimensioned -> open item).
# BAFFLE: box x 47.5..93.5, z 5..51, y 0.7..12 ∩ INNER_E, minus a D40 bore on the axis; 1 mm CR foam gasket (0.7
# compressed) between the flange (y 0.0) and the block (y 0.7). Pilots D2.5 at +-17.75 / +-17.75, y 0.7 -> 4.0
# (M3 x 6 DIN912 from the flange back face y -3.0: tip y 3.0, 2.3 mm in the block). NEW body -> interference -> JOIN.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
SX, SZ, YF, FT, BD, RB = 70.5, 28.0, 0.0, 3.0, 26.1, 20.0
YBF = YF + 0.7


def ycyl(x, z, r, y0, y1):
    return X_.tbm.createCylinderOrCone(Dw(x, y0, z), r / 10, Dw(x, y1, z), r / 10)


def run(_context):
    global X_
    X = Ctx(); X_ = X
    out = {}
    try:
        hb = X.body('HOUSING_E'); inner = X.body('INNER_E')
        spk = {}
        for s, nm in ((1, 'SPK_L'), (-1, 'SPK_R')):
            if X.body(nm) is None:
                cx = XC + s * SX
                tb = X.wbox(cx - 23.0, cx + 23.0, YF - FT, YF, SZ - 23.0, SZ + 23.0)
                X.union(tb, ycyl(cx, SZ, RB, YF - FT + 0.01, YF - FT - BD))
                spk[nm] = X.add(tb, nm)
            else:
                spk[nm] = X.body(nm)
        out['spk_cm3'] = {k: round(v.volume, 3) for k, v in spk.items()}
        bl = None
        for s in (1, -1):
            cx = XC + s * SX
            b = X.wbox(cx - 23.0, cx + 23.0, YBF, 12.0, SZ - 23.0, SZ + 23.0)
            bl = b if bl is None else X.union(bl, b)
        X.tbm.booleanOperation(bl, X.tbm.copy(inner), adsk.fusion.BooleanTypes.IntersectionBooleanType)
        for s in (1, -1):
            cx = XC + s * SX
            X.diff(bl, ycyl(cx, SZ, RB, YBF - 1.0, 12.0))
            for dx in (-17.75, 17.75):
                for dz in (-17.75, 17.75):
                    X.diff(bl, ycyl(cx + dx, SZ + dz, 1.25, YBF - 1.0, 4.0))
        blk = X.add(bl, 'BAFFLE_tmp')
        out['baffle_cm3'] = round(blk.volume, 3)
        names = [b.name for b in X.comp.bRepBodies]
        others = [X.body(n) for n in names if n.startswith('LCD_')] + [X.body(n) for n in ('SLAB_frame', 'DOOR_F', 'PI5_F', 'SPK_L', 'SPK_R')]
        r = X.interference(blk, others)
        out['baffle_interf_nonzero'] = {k: v for k, v in r.items() if v > 0} or 'all 0 (%d)' % len(r)
        if any(v > 0 for v in r.values()):
            blk.isLightBulbOn = False
            raise RuntimeError('baffle interference %s' % out['baffle_interf_nonzero'])
        v0 = hb.volume
        X.combine(hb, [blk])
        hb = X.body('HOUSING_E')
        out['housing_cm3'] = (round(v0, 3), round(hb.volume, 3))
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
        out['spk_interf'] = {nm: X.interference(spk[nm], [hb, X.body('DOOR_F'), X.body('PI5_F'), X.body('PI5_F_cooler')]) for nm in spk}
        pr = {}
        for s in (1, -1):
            cx = XC + s * SX; k = '+x' if s > 0 else '-x'
            pr[k] = {'bore_open_y3_r19': all(not X.inside(hb, cx + 19 * math.cos(a), 3.0, SZ + 19 * math.sin(a)) for a in (0, 1.57, 3.14, 4.71)),
                     'block_solid_y2_r21': X.inside(hb, cx + 21.0, 2.0, SZ) and X.inside(hb, cx, 2.0, SZ + 21.0),
                     'pilot_open_y2': all(not X.inside(hb, cx + dx, 2.0, SZ + dz) for dx in (-17.75, 17.75) for dz in (-17.75, 17.75)),
                     'pilot_end_solid_y4.4': all(X.inside(hb, cx + dx, 4.4, SZ + dz) for dx in (-17.75, 17.75) for dz in (-17.75, 17.75)),
                     'block_back_face_open_y0.5': not X.inside(hb, cx + 21.5, 0.5, SZ)}
        out['probes'] = pr
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b2e_speakers_baffles', 'speakers + baffles', out)
    print(json.dumps(out))
