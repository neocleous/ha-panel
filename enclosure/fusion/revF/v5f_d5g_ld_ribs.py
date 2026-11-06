# rev F audit-response d5g (2026-11-06): LD2410C positive retention (audit finding 40). The B3i cradle's lips stop the module
#   going outward; nothing stops it falling back inward. Two heat-stake ribs, one on each cradle arm, behind the module's
#   short edges: 1.2 thick (along the module's width), 6.0 tall (z 124.5–130.5), from 1.0 inside the module's back-face plane
#   to 2.5 behind it, 0.1 clear of the module's edges (t ±8.1…9.3) so the module still pushes in past them. After fitting, each
#   rib tip is pressed over the module's back edge with the iron (as the strip pins). Vertical ribs: no overhang floor-down.
#   Frame from LD2410C_env_F (v5f_d5d): back-face centre (−69.962, −23.6, 127.5), back normal n (0.857, −0.515, 0),
#   width axis t (0.515, 0.857, 0), 16 × 22 × 3.
#   HOUSING_F_front (old -> HOUSING_F_front_d5e, hidden).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
F = 'HOUSING_F_front'
EXPECT = {F: 233.5171}
CB = (-69.962, -23.6, 127.5)
NB = (0.857, -0.515, 0.0)
TW = (0.515, 0.857, 0.0)


def at(tt, nn, z=127.5):
    return (CB[0] + tt * TW[0] + nn * NB[0], CB[1] + tt * TW[1] + nn * NB[1], z)


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        fb = X.body(F)
        if abs(fb.volume - EXPECT[F]) > 0.0005:
            raise RuntimeError('guard: front %s' % round(fb.volume, 4))
        if X.body('HOUSING_F_front_d5e') is not None:
            raise RuntimeError('HOUSING_F_front_d5e exists already')
        ribs = None; per = []
        for s in (1, -1):
            c = at(s * 8.7, 0.75)
            r = lbox(X, c, TW, NB, 1.2, 3.5, 6.0)
            emb = vol_x(X, X.tbm.copy(r), X.tbm.copy(fb))
            per.append({'side': s, 'centre': [round(v, 3) for v in c], 'embedded_mm3': emb, 'total_mm3': round(r.volume * 1000, 2)})
            ribs = r if ribs is None else X.union(ribs, r)
        out['ribs'] = per
        if any(p['embedded_mm3'] < 0.5 for p in per):
            raise RuntimeError('a rib does not reach the cradle arm: %s' % per)
        ox = {}
        for n in ('LD2410C_env_F', 'LEAD_RADAR', 'SLAB_frame', 'LCD_panel_body', 'HOUSING_F_door', 'BME680_env', 'LEAD_BME680'):
            if X.body(n) is not None:
                ox[n] = vol_x(X, X.tbm.copy(ribs), tb_copy(X, n))
        out['ribs_x'] = ox
        if any(v > 0 for v in ox.values()):
            raise RuntimeError('rib overlap: %s' % ox)
        c0 = X.add(X.tbm.copy(fb), 'HOUSING_F_front_d5e'); c0.isLightBulbOn = False
        v0 = fb.volume
        X.combine(fb, [X.add(ribs, 'D5G_ribs_tmp')]); fb = X.body(F)
        out['front_cm3'] = [round(v0, 4), round(fb.volume, 4)]; out['front_lumps'] = fb.lumps.count
        # module insertion path: env moved 4 mm inward (along +n) and back, 0.25 steps, against the front
        sw = {}
        for k in range(0, 17):
            d = 0.25 * k
            e = tb_copy(X, 'LD2410C_env_F'); mvw(X, e, NB[0] * d, NB[1] * d, 0.0)
            v = vol_x(X, e, tb_copy(X, F))
            if v > 0:
                sw[str(d)] = v
        out['insert_path_x_front'] = sw or 'all 0'
        P = lambda p: X.inside(fb, XC + p[0], p[1], p[2])
        out['probes'] = {'rib+_tip': P(at(8.7, 2.3)), 'rib-_tip': P(at(-8.7, 2.3)), 'gap+_open': not P(at(8.05, 1.5)),
                         'gap-_open': not P(at(-8.05, 1.5)), 'rib_top_z130.4': P(at(8.7, 2.0, 130.4)), 'rib_above_free': not P(at(8.7, 2.3, 131.0))}
        out['left_over'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp')]
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d5g_ld_ribs', 'run', out)
    print(json.dumps(out, separators=(',', ':')))
