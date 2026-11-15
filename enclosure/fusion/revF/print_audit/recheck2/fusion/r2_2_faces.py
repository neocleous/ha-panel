# r2_2_faces (block 1): every face of the scope-A bodies, READ-ONLY. For each face: kind, area (mm2), a point on it (world),
#   the outward normal there (world), for cylinders and cones the axis (world), radius / half angle and whether it is a hole
#   (normal toward the axis); the world box of its vertices. Writes data/r2_2_faces_<tag>.json. Parts: R2_ARGS['parts'].
R2_KIND = {0: 'plane', 1: 'cylinder', 2: 'cone', 3: 'sphere', 4: 'torus', 5: 'ellipcyl', 6: 'ellipcone', 7: 'nurbs'}


def run(_context):
    X = R2Ctx(); t0 = time.time(); r2_guard(X)
    want = R2_ARGS['parts'].split(',')
    res = {}
    for tag, bn in R2_PRINTS:
        if tag not in want:
            continue
        if time.time() - t0 > 65:
            res[tag] = 'not done (time)'; continue
        b = X.body(bn); rows = []
        for i, f in enumerate(b.faces):
            st = f.geometry.surfaceType
            p = f.pointOnFace
            ok, n = f.evaluator.getNormalAtPoint(p)
            row = {'i': i, 'k': R2_KIND.get(st, str(st)), 'a': round(f.area * 100.0, 3), 'p': [round(v, 3) for v in r2_wpt(p)],
                   'n': [round(v, 4) for v in r2_wvec(n)] if ok else None}
            g = f.geometry
            if st == 1:
                ax = g.axis; o = g.origin
                row['r'] = round(g.radius * 10.0, 4); row['ax'] = [round(v, 5) for v in r2_wvec(ax)]; row['o'] = [round(v, 3) for v in r2_wpt(o)]
                # hole if the outward normal points toward the axis
                w = adsk.core.Vector3D.create(p.x - o.x, p.y - o.y, p.z - o.z); axn = ax.copy(); axn.normalize()
                t = w.dotProduct(axn); radial = adsk.core.Vector3D.create(w.x - axn.x * t, w.y - axn.y * t, w.z - axn.z * t)
                row['hole'] = bool(ok and radial.dotProduct(n) < 0)
            elif st == 2:
                ax = g.axis; o = g.origin
                row['ha'] = round(math.degrees(g.halfAngle), 3); row['ax'] = [round(v, 5) for v in r2_wvec(ax)]
                row['o'] = [round(v, 3) for v in r2_wpt(o)]; row['r'] = round(g.radius * 10.0, 4)
            vs = [r2_wpt(v.geometry) for v in f.vertices]
            if vs:
                row['bb'] = [round(min(q[j] for q in vs), 3) if k == 0 else round(max(q[j] for q in vs), 3) for j in range(3) for k in (0, 1)]
            rows.append(row)
        res[tag] = len(rows)
        r2_out(os.path.join(R2_DIR, 'data', 'r2_2_faces_%s.json' % tag), rows)
    r2_log('r2_2_faces', 'run', res)
    print(json.dumps({'res': res, 't_s': round(time.time() - t0, 1)}))
