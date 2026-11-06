# rev F audit-response d6b (2026-11-06): cap fixes (audit findings 1 (cap void), 38 (mic gasket squeeze)).
#   HOUSING_F_cap (old -> HOUSING_F_cap_d6, hidden):
#     1   the closed void at (53.48, −38.64, 177.35) (≈ 0.009 mm³, corner of the c1 VEML pocket filled in c2) filled with exactly
#         that air (design box round the void shell + 0.002, minus the cap).
#     38  the strip's squeeze is set by the geometry: 4 seat pads per strip pocket (1.2 × 1.2, hanging 0.7 from the plate's
#         underside, z 177.6–178.3) at the strip corners (inset 0.8; clear of the Ø1.8 pins at x ±11.5 / ±30 and the Ø1.5 ports
#         at ±35.5). Staking the two pins pulls the strip onto the pads: strip z 176.8–177.6, gasket 1.0 -> 0.7 (30 %, as the
#         speaker gaskets); cut the gasket with 1.6 × 1.6 corner notches. Pins then reach 2.0 below the strip (was 1.7).
#   MIC_strip_L / R_env (old -> *_d6, hidden): strip box z 176.8–177.6 + gasket box z 177.6–178.3 minus the corner notches.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
CAP = 'HOUSING_F_cap'
EXPECT = {CAP: 9.9147}
STRIPS = {'MIC_strip_L_env': (8.5, 37.5), 'MIC_strip_R_env': (-37.5, -8.5)}
Y0, Y1 = -29.5, -23.5
PAD, INSET = 1.2, 0.8


def pads_of(X, x0, x1):
    t = None
    for xc in (x0 + INSET, x1 - INSET):
        for yc in (Y1 - INSET, Y0 + INSET):
            p = X.wbox(XC + xc - PAD / 2, XC + xc + PAD / 2, yc - PAD / 2, yc + PAD / 2, 177.6, 178.35)
            t = p if t is None else X.union(t, p)
    return t


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        cb = X.body(CAP)
        if abs(cb.volume - EXPECT[CAP]) > 0.0005:
            raise RuntimeError('guard: cap %s' % round(cb.volume, 4))
        for n in ['HOUSING_F_cap_d6'] + [k + '_d6' for k in STRIPS]:
            if X.body(n) is not None:
                raise RuntimeError('%s exists already' % n)
        c = X.add(X.tbm.copy(cb), 'HOUSING_F_cap_d6'); c.isLightBulbOn = False
        v0 = cb.volume
        # void
        vf = None
        for li in range(cb.lumps.count):
            L = cb.lumps.item(li)
            for si in range(L.shells.count):
                s = L.shells.item(si)
                if s.isVoid:
                    bb = s.boundingBox; m = 0.0002
                    bx = dbox(X, (bb.minPoint.x - m) * 10, (bb.maxPoint.x + m) * 10, (bb.minPoint.y - m) * 10, (bb.maxPoint.y + m) * 10,
                              (bb.minPoint.z - m) * 10, (bb.maxPoint.z + m) * 10)
                    X.diff(bx, X.tbm.copy(cb)); vf = bx if vf is None else X.union(vf, bx)
        out['void_fill_mm3'] = None if vf is None else round(vf.volume * 1000, 4)
        if vf is not None:
            if vf.volume * 1000 > 0.5:
                raise RuntimeError('void fill too large')
            X.combine(cb, [X.add(vf, 'D6B_void_tmp')]); cb = X.body(CAP)
        # pads
        pads = None
        for n, (x0, x1) in STRIPS.items():
            p = pads_of(X, x0, x1); pads = p if pads is None else X.union(pads, p)
        pn = X.tbm.copy(pads); X.diff(pn, X.tbm.copy(cb))
        out['pads_mm3'] = [round(pads.volume * 1000, 3), round(pn.volume * 1000, 3)]
        ox = {}
        for n in ('HOUSING_F_front', 'LEAD_MIC_L', 'LEAD_MIC_R', 'KO_mic_L', 'KO_mic_R', 'LEAD_VEML', 'VEML_env'):
            if X.body(n) is not None:
                ox[n] = vol_x(X, X.tbm.copy(pads), tb_copy(X, n))
        out['pads_x'] = ox
        X.combine(cb, [X.add(pads, 'D6B_pads_tmp')]); cb = X.body(CAP)
        out['cap_cm3'] = [round(v0, 4), round(cb.volume, 4)]; out['cap_lumps'] = cb.lumps.count
        out['cap_voids_left'] = sum(1 for li in range(cb.lumps.count) for si in range(cb.lumps.item(li).shells.count)
                                    if cb.lumps.item(li).shells.item(si).isVoid)
        # strip envelopes
        envx = {}
        for n, (x0, x1) in STRIPS.items():
            o = X.body(n); o.name = n + '_d6'; o.isLightBulbOn = False
            e = X.wbox(XC + x0, XC + x1, Y0, Y1, 176.8, 177.6)
            gk = X.wbox(XC + x0, XC + x1, Y0, Y1, 177.6, 178.3)
            for xc in (x0 + INSET, x1 - INSET):
                for yc in (Y1 - INSET, Y0 + INSET):
                    X.diff(gk, X.wbox(XC + xc - 0.8, XC + xc + 0.8, yc - 0.8, yc + 0.8, 177.5, 178.4))
            X.union(e, gk)
            nb = X.add(e, n); nb.isLightBulbOn = False
            envx[n] = {'x_cap_mm3': vol_x(X, tb_copy(X, n), tb_copy(X, CAP)), 'x_front_mm3': vol_x(X, tb_copy(X, n), tb_copy(X, 'HOUSING_F_front')),
                       'cm3': round(nb.volume, 4)}
        out['envs'] = envx
        P = lambda b, x, y, z: X.inside(b, XC + x, y, z)
        out['probes'] = {'pad_L_in': P(cb, 9.3, -24.3, 177.9), 'pad_R_in': P(cb, -36.7, -28.7, 177.9), 'pad_bottom_free': not P(cb, 9.3, -24.3, 177.55),
                         'pin_kept': P(cb, 11.5, -26.5, 175.5), 'port_open': not P(cb, 35.5, -26.5, 179.0)}
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d6b_cap_fixes', 'run', out)
    print(json.dumps(out, separators=(',', ':')))
