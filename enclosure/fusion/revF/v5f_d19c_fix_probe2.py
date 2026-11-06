# rev F d19c (2026-11-06), read-only: second probe for the printability fixes. (A) two ribs under the LD2410C cradle floor at
#   y -24.5…-22.5 and -11…-9 (clear of the BME680 hood at y <= -25.4): the front shell's own material in each rib slab per height
#   (the wall's inner face) and every other part / keep-out in the rib slabs; (B) the main bracket's lower-arm gussets
#   (x ±(38.5…46.5), y -62.5…-58.5, z 24…35.7) vs every part; (C) the cap printed top down (d19a's stats for -z with regions).
#   Writes ~/Documents/HA_panel_renders/d_data/data/d19c_probe.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py'), encoding='utf-8').read())
import traceback
OUTF = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d19c_probe.json')
AUDD = os.path.expanduser('~/Documents/audit/data')
NEWP = ['TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'BME_HOOD', 'FOAM_bme_env', 'FOAM_bme_top_env', 'HOUSING_F_door']
RIBS = {'rib_back': (-24.5, -22.5), 'rib_front': (-11.0, -9.0)}


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        names = json.load(open(os.path.join(AUDD, 'a2a_parts.json'), encoding='utf-8')) + NEWP
        ko = [b.name for b in X.comp.bRepBodies if b.name.startswith('KO_') and b.isLightBulbOn is not None]
        allb = [(n, X.body(n), wbb(X, X.body(n))) for n in list(dict.fromkeys(names + ko)) if X.body(n) is not None]

        def hits(t, skip=()):
            tb = wbb(X, t); res = {}
            for (n, b, pb) in allb:
                if n in skip or pb[0] > tb[1] or pb[1] < tb[0] or pb[2] > tb[3] or pb[3] < tb[2] or pb[4] > tb[5] or pb[5] < tb[4]:
                    continue
                try:
                    q = X.tbm.copy(b); inter(X, q, X.tbm.copy(t)); v = q.volume * 1000
                except Exception as e:
                    res[n] = 'fail ' + str(e)[:40]; continue
                if v > 0.005:
                    res[n] = [round(v, 2)] + [round(c, 2) for c in wbb(X, q)]
            return res
        frc = tb_copy(X, 'HOUSING_F_front'); inter(X, frc, wbox_rel(X, [-100.0, -60.0, -26.0, -7.0, 84.0, 118.0]))
        A = {}
        for k, (y0, y1) in RIBS.items():
            slab = wbox_rel(X, [-100.0, -63.0, y0, y1, 84.0, 114.3])
            A[k + '_others'] = hits(slab, ('HOUSING_F_front',))
            prof = []
            for z in (86.0, 90.0, 94.0, 98.0, 102.0, 106.0, 110.0, 113.0, 114.1):
                try:
                    q = X.tbm.copy(frc); inter(X, q, wbox_rel(X, [-100.0, -63.0, y0, y1, z - 0.05, z + 0.05]))
                    prof.append([z] + ([[round(c, 2) for c in wbb(X, X.tbm.copy(l))[0:2]] for l in q.lumps] if q.volume > 0 else []))
                except Exception as e:
                    prof.append([z, 'fail ' + str(e)[:40]])
            A[k + '_front_x_ranges'] = prof
        out['A'] = A
        out['B'] = {s: hits(wbox_rel(X, bb)) for s, bb in (('R', [-46.5, -38.5, -62.5, -58.5, 24.0, 35.7]), ('L', [38.5, 46.5, -62.5, -58.5, 24.0, 35.7]))}
        G2 = {'__name__': 'x'}
        exec(open(os.path.expanduser('~/Documents/HA_panel_renders/scripts_d/v5f_d19a_print_assess.py'), encoding='utf-8').read(), G2)
        P, T = G2['mesh'](X.body('HOUSING_F_cap'))
        out['C_cap_-z'] = G2['stats'](P, T, (0.0, 0.0, -1.0), True)
        out['ko_names'] = ko
        out['t_s'] = round(time.time() - t0, 1)
        os.makedirs(os.path.dirname(OUTF), exist_ok=True)
        json.dump(out, open(OUTF, 'w'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
        try:
            json.dump(out, open(OUTF, 'w'))
        except Exception:
            pass
    log('v5f_d19c_fix_probe2', 'probe', {'t_s': out.get('t_s'), 'FAIL': out.get('FAIL')})
    print(json.dumps({'t_s': out.get('t_s'), 'FAIL': out.get('FAIL')}, separators=(',', ':')))
