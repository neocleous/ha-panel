# HA panel model audit (2026-11-05) block 1d: ASCII section maps by point containment, read-only.
#   SECS (set by the loader): list of [label, body, origin (x_rel, y, z), u (world dir), v (world dir), nu, nv, step mm].
#   Each map row is one v step (top row = largest v), '#' inside, '.' outside, 'o' on the surface. Printed and logged.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
exec(open(os.path.expanduser('~/Documents/audit/scripts/v5f_audit_common.py')).read())
PC = adsk.fusion.PointContainment


def run(_context):
    X = Ctx(); guard(X); out = {}; t0 = time.time()
    try:
        for (lab, name, o, u, v, nu, nv, st) in globals().get('SECS', []):
            b = X.body(name); rows = []
            for j in range(nv - 1, -1, -1):
                s = ''
                for i in range(nu):
                    p = [o[k] + u[k] * i * st + v[k] * j * st for k in range(3)]
                    c = b.pointContainment(Dw(XC + p[0], p[1], p[2]))
                    s += '#' if c == PC.PointInsidePointContainment else ('o' if c == PC.PointOnPointContainment else '.')
                rows.append(s)
            out[lab] = rows
            print('%s  %s  origin %s u %s v %s step %s (top row v = %.2f)' % (lab, name, o, u, v, st, (nv - 1) * st))
            for s in rows:
                print('  ' + s)
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
        print(out['FAIL'])
    log('v5f_a1d_sections', 'sections', out)
