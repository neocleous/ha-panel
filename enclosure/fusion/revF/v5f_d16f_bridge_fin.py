# rev F d16f (2026-11-06): the right floor tie bridge's last 0.1 mm. d16a cut the bridge to x_rel -61.7 but it ran to -61.8, so a
#   0.1 x 4.0 x 5.4 fin stood on the floor in the finger's way in (d16b's entry zone). HOUSING_F_front minus FIN_BB; old state ->
#   HOUSING_F_front_d16f (hidden). Reports the front's lumps round the bridge in d14, now and after. DRY (default True) reports only.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
EXP = {'HOUSING_F_front': 235.2295, 'HOUSING_F_front_d14': 235.3238}
FIN_BB = [-62.0, -61.5, -58.7, -54.3, 2.55, 8.2]
NEAR_BB = [-63.0, -54.5, -59.5, -53.5, 2.6, 9.0]          # round the bridge, above the floor's top


def lumps_in(X, t, bb):
    q = X.tbm.copy(t); inter(X, q, wbox_rel(X, bb)); L = []
    for lp in q.lumps:
        u = X.tbm.copy(lp); L.append([round(u.volume * 1000, 3)] + [round(c, 2) for c in wbb(X, u)])
    return sorted(L, key=lambda r: -r[0])


def run(_context):
    X = Ctx(); out = {}; t0 = time.time(); dry = globals().get('DRY', True)
    try:
        for k, v in EXP.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.0005:
                raise RuntimeError('guard: %s %s' % (k, None if b is None else round(b.volume, 4)))
        if X.body('HOUSING_F_front_d16f') is not None:
            raise RuntimeError('HOUSING_F_front_d16f exists already')
        fr = tb_copy(X, 'HOUSING_F_front')
        out['near_d14'] = lumps_in(X, tb_copy(X, 'HOUSING_F_front_d14'), NEAR_BB)
        out['near_now'] = lumps_in(X, fr, NEAR_BB)
        nf = X.tbm.copy(fr); X.diff(nf, wbox_rel(X, FIN_BB))
        out['near_new'] = lumps_in(X, nf, NEAR_BB)
        out['front_tb'] = {'cm3': round(nf.volume, 4), 'removed_mm3': round((fr.volume - nf.volume) * 1000, 3),
                           'lumps': nf.lumps.count, 'lumps_now': fr.lumps.count}
        if not dry:
            of = X.body('HOUSING_F_front'); app = of.appearance; mat = of.material
            of.name = 'HOUSING_F_front_d16f'; of.isLightBulbOn = False
            fb = X.add(nf, 'HOUSING_F_front')
            for attr, val in (('material', mat), ('appearance', app)):
                try:
                    setattr(fb, attr, val)
                except Exception:
                    pass
            I = lambda b_, x, y, z: X.inside(b_, XC + x, y, z)
            out['applied'] = {'front_cm3': round(fb.volume, 4), 'front_lumps': fb.lumps.count}
            out['probes'] = {'fin_gone': not I(fb, -61.75, -56.5, 5.0), 'floor_kept': I(fb, -61.75, -56.5, 1.25),
                             'floor_kept_out': I(fb, -62.5, -56.5, 1.25), 'bridge_still_gone': not I(fb, -58.5, -56.5, 6.0)}
        out['dry'] = dry
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d16f_bridge_fin', 'dry' if globals().get('DRY', True) else 'run', out)
    print(json.dumps(out, separators=(',', ':')))
