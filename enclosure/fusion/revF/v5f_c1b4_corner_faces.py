# rev F cap block c1b4 (2026-11-05), read-only: extent of REF_F_outer's two front-corner blend faces in z 160…177.2
#   (c1b3: NURBS 124 mm² at x ±80, y −19.9, z 169.3 between the front plane and the main side/back face) – sampled on a
#   20 × 20 parameter grid, world coordinates; and the main face's front boundary (its edges shared with the blends).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        tb = tb_copy(X, 'REF_F_outer')
        inter(X, tb, X.wbox(-250, 250, -250, 250, 160.0, 177.2))
        res = {}
        for f in tb.faces:
            if not f.geometry.objectType.endswith('NurbsSurface') or f.area * 100 > 1000:
                continue
            ev = f.evaluator; ok, pmin, pmax = ev.parametricRange().minPoint, None, None
            rng = ev.parametricRange(); u0, v0 = rng.minPoint.x, rng.minPoint.y; u1, v1 = rng.maxPoint.x, rng.maxPoint.y
            pts = []
            for i in range(21):
                for j in range(21):
                    pp = adsk.core.Point2D.create(u0 + (u1 - u0) * i / 20, v0 + (v1 - v0) * j / 20)
                    if not ev.isParameterOnFace(pp):
                        continue
                    ok, p3 = ev.getPointAtParameter(pp)
                    if ok:
                        pts.append((p3.x * 10 - XC, wy(p3), wz(p3)))
            key = 'x%+.0f' % (sum(p[0] for p in pts) / len(pts))
            # y extent per z band
            bands = {}
            for p in pts:
                zb = int(p[2] // 2 * 2)
                bands.setdefault(zb, [999, -999, 999, -999])
                b = bands[zb]; b[0] = min(b[0], p[1]); b[1] = max(b[1], p[1]); b[2] = min(b[2], p[0]); b[3] = max(b[3], p[0])
            res[key] = {'n_pts': len(pts), 'y_min': round(min(p[1] for p in pts), 2), 'y_max': round(max(p[1] for p in pts), 2),
                        'z_min': round(min(p[2] for p in pts), 2), 'z_max': round(max(p[2] for p in pts), 2),
                        'per_z2_[ymin,ymax,xmin,xmax]': {k: [round(q, 2) for q in v] for k, v in sorted(bands.items())}}
        out['corner_faces'] = res
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    print(json.dumps(out, separators=(',', ':'))[:8000])
