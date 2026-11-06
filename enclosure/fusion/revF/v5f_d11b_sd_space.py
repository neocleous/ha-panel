# rev F d11b (2026-11-06), read-only: the space behind the right speaker box for the microSD socket (x_rel -80…-30,
#   y -66…-50, z 0…90): every body there (incl. hidden envelopes, leads, keep-outs) and sections at z 30 / 45 / 60 / 75
#   and y -53.5 / -56. Writes ~/Documents/HA_panel_renders/d_data/data/d11b_probe.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
exec(open(os.path.expanduser('~/Documents/HA_panel_renders/scripts_d/v5f_d0_sections.py')).read())   # sections()
import traceback
OUTF = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data/d11b_probe.json')
WIN = [-80.0, -30.0, -66.0, -50.0, 0.0, 90.0]
SKIP = ('_d', '_c0', '_c1', '_c2', '_wip', '_fail', 'REF_', 'TOOL_', 'INNER_', 'HOUSING_E', 'HOUSING_shell', 'RENDER_', 'DOOR_tray')


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    try:
        near = {}
        for b in X.comp.bRepBodies:
            nm = b.name
            if any(s in nm for s in SKIP) and nm not in ('HOUSING_F_door',):
                continue
            try:
                bb = wbb(X, b)
            except Exception:
                continue
            if bb[0] < WIN[1] and bb[1] > WIN[0] and bb[2] < WIN[3] and bb[3] > WIN[2] and bb[4] < WIN[5] and bb[5] > WIN[4]:
                q = X.tbm.copy(b); inter(X, q, wbox_rel(X, WIN))
                near[nm] = {'bb': [round(v, 2) for v in bb], 'vis': b.isLightBulbOn,
                            'in_win_bb': [round(v, 2) for v in wbb(X, q)] if q.volume > 0 else None}
        out['near'] = near
        NB = [n for n in near.keys()]
        PL = {}
        for zs in (30.0, 45.0, 60.0, 75.0):
            PL['Q_z%g' % zs] = ('z', zs, (-80.0, -30.0, -70.0, -45.0), NB)
        for ys in (-53.5, -56.0):
            PL['Q_y%g' % ys] = ('y', ys, (-80.0, -30.0, 0.0, 90.0), NB)
        out['sec'] = sections(X, PL)
        out['t_s'] = round(time.time() - t0, 1)
        os.makedirs(os.path.dirname(OUTF), exist_ok=True)
        json.dump(out, open(OUTF, 'w'))
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d11b_sd_space', 'probe', {'n_near': len(out.get('near', {})), 't_s': out.get('t_s'), 'FAIL': out.get('FAIL')})
    print(json.dumps({'n_near': len(out.get('near', {})), 't_s': out.get('t_s'), 'FAIL': out.get('FAIL')}, separators=(',', ':')))
