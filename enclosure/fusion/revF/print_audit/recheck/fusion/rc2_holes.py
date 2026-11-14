# rc2_holes (block 1, point 10): hole / pin / boss schedule from the B-rep of the 13 printed bodies, method of pa2_holes.py:
#   every cylindrical face with r <= 6 mm -> diameter, hole (concave) or boss/pin (convex), world axis, centre of its axial extent
#   (x_rel, y, z), axial length, area and its share of a full cylinder (2 pi r L); cones too (countersinks, chamfers).
#   READ-ONLY on the design. Writes print_audit_recheck/data/rc2_holes.json.


def run(_context):
    X = RcCtx(); t0 = time.time(); out = {'t': time.strftime('%Y-%m-%d %H:%M:%S')}
    out['guard'] = rc_guard(X)[0]
    rows = []
    cyl = adsk.core.Cylinder.classType(); con = adsk.core.Cone.classType()
    for tag, bn in RC_PRINTS:
        b = X.body(bn)
        for f in b.faces:
            g = f.geometry; ot = g.objectType
            if ot not in (cyl, con):
                continue
            ax = g.axis.copy(); ax.normalize(); o = g.origin
            if ot == cyl:
                r = g.radius * 10
                if r > 6.0:
                    continue
            ts = [((v.geometry.x - o.x) * ax.x + (v.geometry.y - o.y) * ax.y + (v.geometry.z - o.z) * ax.z) * 10 for v in f.vertices]
            p = f.pointOnFace
            if not ts:
                ts = [((p.x - o.x) * ax.x + (p.y - o.y) * ax.y + (p.z - o.z) * ax.z) * 10]
            t_lo, t_hi = min(ts), max(ts); tm = (t_lo + t_hi) / 2
            cpt = adsk.core.Point3D.create(o.x + ax.x * tm / 10, o.y + ax.y * tm / 10, o.z + ax.z * tm / 10)
            ok, n = f.evaluator.getNormalAtPoint(p)
            k = ((p.x - o.x) * ax.x + (p.y - o.y) * ax.y + (p.z - o.z) * ax.z)
            q = adsk.core.Point3D.create(o.x + ax.x * k, o.y + ax.y * k, o.z + ax.z * k)
            radial = adsk.core.Vector3D.create(p.x - q.x, p.y - q.y, p.z - q.z)
            hole = radial.dotProduct(n) < 0
            aw = rc_wvec(ax); c_w = rc_wpt(cpt); L = t_hi - t_lo
            if ot == cyl:
                full = (f.area * 100) / (2 * math.pi * r * L) if L > 1e-6 else None
                rows.append([tag, 'cyl', round(2 * r, 3), 'hole' if hole else 'boss', [round(v, 4) for v in aw],
                             [round(v, 3) for v in c_w], round(L, 3), round(f.area * 100, 2), None if full is None else round(full, 3)])
            else:
                rows.append([tag, 'cone', round(math.degrees(g.halfAngle), 2), 'hole' if hole else 'boss', [round(v, 4) for v in aw],
                             [round(v, 3) for v in c_w], round(L, 3), round(f.area * 100, 2), None])
    out['rows'] = rows; out['n'] = len(rows); out['t_s'] = round(time.time() - t0, 1)
    rc_out(os.path.join(RC_DIR, 'data', 'rc2_holes.json'), out)
    rc_log('rc2_holes', 'run', {'n': out['n'], 't_s': out['t_s']})
    print(json.dumps({'n': out['n'], 't_s': out['t_s'], 'guard_ok': True}, separators=(',', ':')))
