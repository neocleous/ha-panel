# HA panel model audit (2026-11-05) block 3b: tool lines (A.1 / A.2), read-only.
#   TOOLS (loader): [label, head point (x_rel, y, z), [world directions], Lmax mm, tool body Ø mm]. For each direction, the
#   tool body is a cylinder from 0.3 mm off the head along the direction; the free length is the longest L <= Lmax with zero
#   intersection against every FIXED body (bisection to 0.5 mm, design-box prefilter), with the first body hit.
#   Result -> ~/Documents/audit/data/tools_<LABEL>.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
exec(open(os.path.expanduser('~/Documents/audit/scripts/v5f_audit_common.py')).read())


def cyl(X, p, u, L0, L1, r):
    a = Dw(XC + p[0] + u[0] * L0, p[1] + u[1] * L0, p[2] + u[2] * L0)
    b = Dw(XC + p[0] + u[0] * L1, p[1] + u[1] * L1, p[2] + u[2] * L1)
    return X.tbm.createCylinderOrCone(a, r / 10, b, r / 10)


def ov(a, b):
    return not (a.maxPoint.x < b.minPoint.x or b.maxPoint.x < a.minPoint.x or a.maxPoint.y < b.minPoint.y or
                b.maxPoint.y < a.minPoint.y or a.maxPoint.z < b.minPoint.z or b.maxPoint.z < a.minPoint.z)


def first_hit(X, c, fx):
    bb = c.boundingBox
    for n, q in fx:
        if ov(bb, q.boundingBox) and vol_x(X, c, q) > 0.005:
            return n
    return None


def run(_context):
    X = Ctx(); guard(X); out = {}; t0 = time.time()
    try:
        fx = [(n, X.tbm.copy(X.body(n))) for n in globals()['FIXED'] if X.body(n) is not None]
        reg = globals().get('REGION')                 # optional world box [x_rel0, x_rel1, y0, y1, z0, z1]: crop fixed bodies once
        if reg:
            keep = []
            for n, q in fx:
                inter(X, q, wbox_rel(X, reg))
                if q.volume > 0:
                    keep.append((n, q))
            fx = keep
        res = []
        for (lab, p, dirs, Lmax, dia) in globals()['TOOLS']:
            for d in dirs:
                L_ = math.sqrt(sum(c * c for c in d)); u = [c / L_ for c in d]
                hit = first_hit(X, cyl(X, p, u, 0.3, Lmax, dia / 2), fx)
                if hit is None:
                    res.append([lab, [round(c, 3) for c in u], Lmax, None]); continue
                lo, hi = 0.3, Lmax; who = hit
                while hi - lo > 0.5:
                    mid = (lo + hi) / 2
                    h = first_hit(X, cyl(X, p, u, 0.3, mid, dia / 2), fx)
                    if h is None:
                        lo = mid
                    else:
                        hi = mid; who = h
                res.append([lab, [round(c, 3) for c in u], round(lo, 1), who])
            if time.time() - t0 > 50:
                out['stopped_after'] = lab; break
        out['res'] = res
        json.dump(out, open(os.path.join(AUD, 'data', 'tools_%s.json' % globals().get('LABEL', 'x')), 'w'))
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_a3b_tools', globals().get('LABEL', 'x'), {k: v for k, v in out.items()})
    for r in out.get('res', []):
        print(r)
    print({k: v for k, v in out.items() if k != 'res'})
