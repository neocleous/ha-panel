# rev F block 6i (2026-11-05), read-only: body inventory for block 6 (masses, STEP list, docs): every body with
#   visibility, volume (cm³), lumps, world bbox [x_rel0, x_rel1, y0, y1, z0, z1] and world centroid (x_rel, y, z).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        rows = []
        for b in X.comp.bRepBodies:
            try:
                c = b.physicalProperties.centerOfMass
                cw = [round(c.x * 10 - XC, 2), round(wy(c), 2), round(wz(c), 2)]
            except Exception:
                cw = None
            rows.append([b.name, b.isLightBulbOn, round(b.volume, 4), b.lumps.count, [round(v, 1) for v in wbb(X, b)], cw])
        out['n'] = len(rows)
        out['visible'] = [r for r in rows if r[1]]
        out['hidden'] = [[r[0], r[2]] for r in rows if not r[1]]
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b6i_inventory', 'inventory', out)
    print(json.dumps({'n': out.get('n'), 'n_visible': len(out.get('visible', [])), 't_s': out.get('t_s'), 'FAIL': out.get('FAIL')}))
