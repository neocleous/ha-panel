# HA panel model audit (2026-11-05) block 1c: hole and pin schedule from the B-rep, read-only (G.5 sideways holes, S.1).
#   For every printed part: each cylindrical face with r <= 4.5 mm -> Ø, hole (concave) or boss/pin (convex), world axis
#   (unit, x/y/z), centre of the face's extent along the axis (world mm, x_rel), axial length, and the part. Written to
#   ~/Documents/audit/data/holes.json (and the log). Also copies this audit's a1a log rows to data/a1a.json for offline use.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
exec(open(os.path.expanduser('~/Documents/audit/scripts/v5f_audit_common.py')).read())


def run(_context):
    X = Ctx(); guard(X); out = {}; t0 = time.time()
    try:
        os.makedirs(os.path.join(AUD, 'data'), exist_ok=True)
        rows = []
        for name in PRINTED:
            b = X.body(name)
            for f in b.faces:
                g = f.geometry
                if g.objectType != adsk.core.Cylinder.classType():
                    continue
                r = g.radius * 10
                if r > 4.5:
                    continue
                ax = g.axis; ax.normalize(); o = g.origin
                aw = nw_of(ax)
                # axial extent from the face's vertices projected on the axis
                ts = []
                for v in f.vertices:
                    p = v.geometry; ts.append(((p.x - o.x) * ax.x + (p.y - o.y) * ax.y + (p.z - o.z) * ax.z) * 10)
                if not ts:
                    ok, p0 = f.evaluator.getPointAtParameter(adsk.core.Point2D.create(0, 0)); ts = [0.0]
                t_lo, t_hi = min(ts), max(ts); tm = (t_lo + t_hi) / 2
                c = P3(o.x + ax.x * tm / 10, o.y + ax.y * tm / 10, o.z + ax.z * tm / 10)
                # concave (hole) if the outward face normal at a face point points toward the axis
                p = f.pointOnFace; ok, n = f.evaluator.getNormalAtPoint(p)
                k = ((p.x - o.x) * ax.x + (p.y - o.y) * ax.y + (p.z - o.z) * ax.z)
                q = P3(o.x + ax.x * k, o.y + ax.y * k, o.z + ax.z * k)
                radial = V3(p.x - q.x, p.y - q.y, p.z - q.z)
                hole = radial.dotProduct(n) < 0
                rows.append([name, round(2 * r, 3), 'hole' if hole else 'boss', [round(v, 3) for v in aw],
                             [round(v, 2) for v in wpt(c)], round(t_hi - t_lo, 2), round(f.area * 100, 2)])
        json.dump(rows, open(os.path.join(AUD, 'data', 'holes.json'), 'w'))
        out['n'] = len(rows)
        # copy this audit's a1a rows for the offline G.4 classification
        logrows = [r for r in json.load(open(LOG)) if r.get('script') == 'v5f_a1a_validity']
        json.dump(logrows, open(os.path.join(AUD, 'data', 'a1a.json'), 'w'))
        out['a1a_rows'] = len(logrows)
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_a1c_holes', 'holes', out)
    print(json.dumps(out))
