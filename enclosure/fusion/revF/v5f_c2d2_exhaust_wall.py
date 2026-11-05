# rev F cap block c2d2 (2026-11-05), read-only: exhaust open length measured AT the back wall (c2d's rays along −y count
#   every rib in front of a slot, including the oblique SL/SR ribs that only touch the wall over ≈ 2.6). Per row (mid z),
#   x_rel −45…45 at 0.25: REF_F_outer hit along −y from y −30, point 2.4 inside REF along its normal (mid-wall, d 0.72–3.24)
#   → open if that point is not inside HOUSING_F_front (rib roots are cut at d ≥ 1.9, so they show there).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        F = X.body('HOUSING_F_front')
        for (lab, z) in (('row_162.5-165.5', 164.0), ('row_167.0-170.0', 168.5)):
            n_open = 0; blocked = []
            for i in range(0, 361):
                xr = -45.0 + i * 0.25
                hs = [h for h in ray_hits(X, (XC + xr, -30.0, z), (0, -1, 0), ('REF_F_outer',)) if h[0] > 1.0]
                if not hs:
                    continue
                h = hs[0]; n = h[5]
                p = (XC + h[2] - n[0] * 2.4, h[3] - n[1] * 2.4, h[4] - n[2] * 2.4)
                if F.pointContainment(Dw(*p)) in INS:
                    blocked.append(xr)
                else:
                    n_open += 1
            runs = []
            for xr in blocked:
                if runs and abs(xr - runs[-1][1] - 0.25) < 1e-6:
                    runs[-1][1] = xr
                else:
                    runs.append([xr, xr])
            out[lab] = {'open_mm': n_open * 0.25, 'open_mm2': round(n_open * 0.25 * 3.0, 1), 'blocked_runs': runs}
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_c2d2_exhaust_wall', 'run', out)
    print(json.dumps(out, separators=(',', ':')))
