# rev F j6b (2026-11-12): close, block 6.2 - read-only probes for wall thickness, gaps and holes.
#   MODE 'needles': NEEDLES (from the loader) = [[label, [body names], frame, p0, p1], ...]; a needle is a 0.04 x 0.04 bar from p0 to p1
#     (frame 'W' world x_rel, y, z; 'S' slab x_rel, depth, Zd; 'B' board u, v, w). For each body: the stretches of the needle that lie
#     inside it, as distances from p0 in mm. A wall's thickness is a stretch's length; a gap is the space between two stretches.
#   MODE 'dist': PAIRS = [[a, b], ...]: smallest distance between two model bodies, with both points (world).
#   MODE 'inserts': every hole of radius RR (default 2.0) found by j6c in the printed parts: how much of a tube of wall WALL (default
#     1.6) round it is solid, whether the hole itself is empty, and whether it is closed behind its end (a plug 1.0 long).
#   MODE 'boxes': BOXES = [[label, body, frame, x0, x1, y0, y1, z0, z1], ...]: mm3 of the body inside each box, and its extent there.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_j_lib.py'), encoding='utf-8').read())
MODE = globals().get('MODE', 'needles')
TAG = globals().get('TAG', '')
NEEDLES = globals().get('NEEDLES', [])
PAIRS = globals().get('PAIRS', [])
BOXES = globals().get('BOXES', [])
RR = globals().get('RR', 2.0)
WALL = globals().get('WALL', 1.6)


BIGB = ('HOUSING_F_front', 'HOUSING_F_door', 'FLOOR_PLATE', 'SLAB_frame')
BUDGET = globals().get('BUDGET', 30.0)


PARTS = {}                                      # per call: a body's parts are looked up once (a big body's volume read costs up to a second, lesson 135)


def parts_of(X, name):                          # a big body is probed slab by slab (the eight slabs j6a2 left in the cache): a boolean
    if name in PARTS:                           #   with the whole shell as its tool costs 5-13 s, with a slab a fraction of that (lesson 133)
        return PARTS[name]
    c = cache()
    out = None
    if name in BIGB:
        v = round(X.body(name).volume, 6)
        tl = [c.get(('tile', name, v, i)) for i in range(8)]
        if all(t is not None for t in tl):
            out = [t for t in tl if t.faces.count > 0]
    if out is None:
        out = [tcopy(X, name)]
    PARTS[name] = out
    return out


def solid_in(X, shape, parts):                  # mm3 of a temporary shape inside a body given as its parts
    v = 0.0
    for p in parts:
        if shape.boundingBox.intersects(p.boundingBox):
            v += solid(X, shape, p)
    return v


def merged(iv):                                 # stretches from several slabs joined where they meet
    out = []
    for a, b in sorted(iv):
        if out and a <= out[-1][1] + 0.03:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def pt(fr, p):
    return Bp(*p) if fr == 'B' else (Dp(*p) if fr == 'S' else Wp(*p))


def bar(X, a, b, w=0.004):
    d = V3(b.x - a.x, b.y - a.y, b.z - a.z); L = d.length; d.normalize()
    ref = V3(0, 0, 1) if abs(d.z) < 0.9 else V3(1, 0, 0)
    wd = d.crossProduct(ref); wd.normalize()
    cen = P3((a.x + b.x) / 2.0, (a.y + b.y) / 2.0, (a.z + b.z) / 2.0)
    return X.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(cen, d, wd, L, w, w)), d


def stretches(X, a, b, body):
    nd, d = bar(X, a, b)
    if not nd.boundingBox.intersects(body.boundingBox):          # a slab the needle does not reach costs a boolean for nothing
        return []
    try:
        X.tbm.booleanOperation(nd, body, BT.IntersectionBooleanType)
    except Exception:
        return 'boolean failed'
    out = []
    for l in nd.lumps:
        ts = [((v.geometry.x - a.x) * d.x + (v.geometry.y - a.y) * d.y + (v.geometry.z - a.z) * d.z) * 10.0 for v in l.vertices]
        out.append([round(min(ts), 2), round(max(ts), 2)])
    return sorted(out)


def run(_context):
    st = {'mode': MODE}
    t0 = time.time()
    try:
        X = K()
        if MODE == 'needles':
            out = {}
            for lab, names, fr, p0, p1 in NEEDLES:
                a = pt(fr, p0); b = pt(fr, p1)
                row = {}
                for n in names:
                    if X.body(n) is None:
                        row[n] = 'missing'; continue
                    s = []
                    for prt in parts_of(X, n):
                        q = stretches(X, a, b, prt)
                        if isinstance(q, list):
                            s += q
                    s = merged(s)
                    if s:
                        row[n] = s
                out[lab] = row
            st['needles'] = out
        elif MODE == 'dist':
            mm = X.app.measureManager
            out = {}
            for a, b in PAIRS:
                m = mm.measureMinimumDistance(X.body(a), X.body(b))
                out[a + '~' + b] = [round(m.value * 10.0, 2), [round(v, 1) for v in W(m.positionOne)], [round(v, 1) for v in W(m.positionTwo)]]
            st['dist'] = out
        elif MODE == 'boxes':
            out = {}
            for lab, n, fr, x0, x1, y0, y1, z0, z1 in BOXES:
                bx = X.wbox(x0, x1, y0, y1, z0, z1) if fr == 'W' else (X.dbox(x0, x1, y0, y1, z0, z1) if fr == 'S' else bbox_b(X, x0, x1, y0, y1, z0, z1))
                full = X.vol(bx)
                t = X.cp(bx); X.sec(t, tcopy(X, n))
                v = X.vol(t)
                out[lab] = [round(v, 2), round(full, 2), t.lumps.count, wext(t) if (v > 0.001 and sum(l.vertices.count for l in t.lumps) < 4000) else None]
            st['boxes'] = out
        elif MODE == 'inserts':
            holes = json.load(open(os.path.join(S3, 'j6c_holes.json')))
            out = {}
            for bn, rows in holes.items():
                body = parts_of(X, bn)
                res = []
                for r, q, a, ta, tb, cov in rows:
                    if abs(r - RR) > 0.06:
                        continue
                    pa = Wp(q[0] + ta * a[0], q[1] + ta * a[1], q[2] + ta * a[2])
                    pb = Wp(q[0] + tb * a[0], q[1] + tb * a[1], q[2] + tb * a[2])
                    core = X.tbm.createCylinderOrCone(pa, (r - 0.1) / 10.0, pb, (r - 0.1) / 10.0)
                    tube = X.tbm.createCylinderOrCone(pa, (r + WALL) / 10.0, pb, (r + WALL) / 10.0)
                    X.dif(tube, X.tbm.createCylinderOrCone(pa, (r + 0.05) / 10.0, pb, (r + 0.05) / 10.0))
                    ends = []
                    for sgn, t in ((-1.0, ta), (1.0, tb)):
                        p1 = Wp(q[0] + (t + sgn * 0.1) * a[0], q[1] + (t + sgn * 0.1) * a[1], q[2] + (t + sgn * 0.1) * a[2])
                        p2 = Wp(q[0] + (t + sgn * 1.1) * a[0], q[1] + (t + sgn * 1.1) * a[1], q[2] + (t + sgn * 1.1) * a[2])
                        plug = X.tbm.createCylinderOrCone(p1, (r - 0.2) / 10.0, p2, (r - 0.2) / 10.0)
                        ends.append(round(solid_in(X, plug, body) / X.vol(plug), 2))
                    mid = [round(q[i] + (ta + tb) / 2.0 * a[i], 1) for i in range(3)]
                    res.append({'at': mid, 'axis': [round(v, 2) for v in a], 'depth': round(tb - ta, 2), 'core solid': round(solid_in(X, core, body) / X.vol(core), 3),
                                'wall solid': round(solid_in(X, tube, body) / X.vol(tube), 3), 'solid beyond the two ends': ends})
                if res:
                    out[bn] = res
            st['inserts'] = out
        elif MODE == 'iron':
            # MODE 'iron': can the soldering iron (envelope of the audit: tip dia 6 x 10, barrel dia 10 x 65, handle dia 16.8 x 98) stand on
            #   the axis of an insert hole? IRON = [[label, mouth (world), 'out' direction (world), [bodies in the way]], ...]; TILTS =
            #   [[toward the middle deg, up deg], ...]. Per tilt: mm3 of each of the three sections inside each body, and of a dia 2.0 rod
            #   of the same length (the key) for comparison.
            out = {}
            SEG = (('tip dia 6', 0.5, 10.0, 3.0), ('barrel dia 10', 10.0, 75.0, 5.0), ('handle dia 16.8', 75.0, 173.0, 8.4), ('rod dia 2', 0.5, 173.0, 1.0))
            for lab, m, d0, names in globals().get('IRON', []):
                rows = {}
                for ta, tb in globals().get('TILTS', [[0, 0]]):
                    ca, sa = math.cos(math.radians(ta)), math.sin(math.radians(ta))
                    cb, sb = math.cos(math.radians(tb)), math.sin(math.radians(tb))
                    sx = -1.0 if m[0] > 0 else 1.0
                    d = (d0[0] * ca * cb + sx * sa * cb, d0[1] * ca * cb, d0[2] * ca * cb + sb)
                    n = math.sqrt(sum(q * q for q in d)); d = tuple(q / n for q in d)
                    row = {}
                    for sl, s0, s1, r in SEG:
                        cyl = X.tbm.createCylinderOrCone(Wp(*[m[i] + d[i] * s0 for i in range(3)]), r / 10.0, Wp(*[m[i] + d[i] * s1 for i in range(3)]), r / 10.0)
                        for nm in names:
                            v = solid_in(X, cyl, parts_of(X, nm))
                            if v > 0.005:
                                row['%s in %s' % (sl, nm)] = round(v, 1)
                    rows['%g toward the middle, %g up' % (ta, tb)] = row if row else 'free'
                out[lab] = rows
            st['iron'] = out
        elif MODE == 'axis':
            # MODE 'axis': how thick a straight rod can stand on a hole's axis? AXIS = [[label, mouth (world), 'out' direction (world),
            #   [bodies]], ...]; per radius in RADII: mm3 of a rod from 0.5 to 173 behind the mouth inside the bodies, and the stretch
            #   along the axis (mm behind the mouth) where it is inside.
            out = {}
            for lab, m, d, names in globals().get('AXIS', []):
                row = {}
                a0 = Wp(*[m[i] + d[i] * 0.5 for i in range(3)]); a1 = Wp(*[m[i] + d[i] * 173.0 for i in range(3)])
                dv = V3(a1.x - a0.x, a1.y - a0.y, a1.z - a0.z); dv.normalize()
                for r in globals().get('RADII', (0.2, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0)):
                    v = 0.0; ts = []
                    for nm in names:
                        for prt in parts_of(X, nm):
                            cyl = X.tbm.createCylinderOrCone(a0, r / 10.0, a1, r / 10.0)
                            if not cyl.boundingBox.intersects(prt.boundingBox):
                                continue
                            X.tbm.booleanOperation(cyl, prt, BT.IntersectionBooleanType)
                            v += X.vol(cyl)
                            for vt in cyl.vertices:
                                g = vt.geometry
                                ts.append(((g.x - a0.x) * dv.x + (g.y - a0.y) * dv.y + (g.z - a0.z) * dv.z) * 10.0 + 0.5)
                    row['radius %g' % r] = [round(v, 2), [round(min(ts), 1), round(max(ts), 1)] if ts else None]
                out[lab] = row
            st['axis'] = out
        elif MODE == 'shift':
            # MODE 'shift': SHIFT = [[moving bodies], [standing bodies], [[dx, dy, dz] world, ...]]: mm3 of each moving body, moved, inside
            #   each standing body. For a part that leaves with the plate unit: does it clear what stays in the shell on the way?
            mv, stn, offs = globals()['SHIFT']
            out = {}
            for o in offs:
                row = {}
                for a in mv:
                    t = X.cp(tcopy(X, a)); X.move(t, o[0], o[1], o[2])
                    for bn in stn:
                        v = solid_in(X, t, parts_of(X, bn))
                        if v > 0.005:
                            row[a + ' in ' + bn] = round(v, 2)
                out['%g, %g, %g' % tuple(o)] = row if row else 'free'
            st['shift'] = out
        elif MODE == 'vdist':
            # MODE 'vdist': VD = [body A, body B]: the distance from every vertex of A to body B (model bodies). The gap of a joint that
            #   has seats shows as the cluster of small distances above 0. Cached per vertex; stops after BUDGET: call until 'left' is 0.
            A, Bn = globals()['VD']
            c = cache(); res = c.setdefault(('j6b_vdist', A, Bn), {})
            a = X.body(A); b = X.body(Bn); mm = X.app.measureManager
            nv = a.vertices.count; left = 0
            for i in range(nv):
                if i in res:
                    continue
                if time.time() - t0 > BUDGET:
                    left = nv - i; break
                v = a.vertices.item(i)
                res[i] = [round(mm.measureMinimumDistance(v, b).value * 10.0, 3), [round(q, 1) for q in W(v.geometry)]]
            rows = sorted(res.values())
            bins = ((0.0, 0.005), (0.005, 0.15), (0.15, 0.25), (0.25, 0.35), (0.35, 0.6), (0.6, 1.0), (1.0, 2.0), (2.0, 1e9))
            st['left'] = left; st['vertices'] = nv; st['done'] = len(rows)
            st['bins'] = {'%g..%g' % (lo, hi): sum(1 for r in rows if lo <= r[0] < hi) for lo, hi in bins}
            st['samples'] = {'%g..%g' % (lo, hi): [r for r in rows if lo <= r[0] < hi][::max(1, len([r for r in rows if lo <= r[0] < hi]) // 10)][:12] for lo, hi in bins[1:6]}
        elif MODE == 'walls':
            # MODE 'walls': for every flat face of the bodies in WALLS (from the loader: {body: [world boxes] or None}) that is at least
            #   AMIN mm2 (and whose sample point lies in one of the boxes, if boxes are given): how much material stands behind the face
            #   at its sample point, along the inward normal, up to DEPTH. One sample a face: a survey, not a proof. Cached per body
            #   and face; a call stops after BUDGET seconds: call until 'left' is 0.
            WALLS = globals().get('WALLS', {})
            AMIN = globals().get('AMIN', 3.0); DEPTH = globals().get('DEPTH', 8.0)
            c = cache(); res = c.setdefault('j6b_walls', {})
            PLANE = adsk.core.SurfaceTypes.PlaneSurfaceType
            left = 0; out = {}
            for bn, boxes in WALLS.items():
                b = X.body(bn); prts = None
                rb = res.setdefault(bn, {})
                nf = b.faces.count
                for i in range(nf):
                    if i in rb:
                        continue
                    if time.time() - t0 > BUDGET:
                        left += nf - i; break
                    f = b.faces.item(i)
                    if f.geometry.surfaceType != PLANE or f.area * 100.0 < AMIN:
                        rb[i] = None; continue
                    p = f.pointOnFace
                    pw = W(p)
                    if boxes and not any(q[0] <= pw[0] <= q[1] and q[2] <= pw[1] <= q[3] and q[4] <= pw[2] <= q[5] for q in boxes):
                        rb[i] = None; continue
                    ok, n = f.evaluator.getNormalAtPoint(p)
                    a = P3(p.x + n.x * 0.01, p.y + n.y * 0.01, p.z + n.z * 0.01)
                    e = P3(p.x - n.x * DEPTH / 10.0, p.y - n.y * DEPTH / 10.0, p.z - n.z * DEPTH / 10.0)
                    if prts is None:
                        prts = parts_of(X, bn)
                    s = []
                    for prt in prts:
                        q = stretches(X, a, e, prt)
                        if isinstance(q, list):
                            s += q
                    s = merged(s)
                    th = None
                    for u, v in s:
                        if u <= 0.15:
                            th = round(v - 0.1, 2); break
                    rb[i] = [th, [round(v, 1) for v in pw], [round(v, 2) for v in (n.x, n.y * C - n.z * S, n.y * S + n.z * C)], round(f.area * 100.0, 1)]
                rows = [r for r in rb.values() if r is not None and r[0] is not None]
                thin = sorted(rows, key=lambda r: r[0])
                out[bn] = {'faces': nf, 'sampled': len(rows), 'no stretch found': sum(1 for r in rb.values() if r is not None and r[0] is None),
                           'under 0.8': sum(1 for r in rows if r[0] < 0.8), '0.8 to 1.2': sum(1 for r in rows if 0.8 <= r[0] < 1.2),
                           '1.2 to 1.6': sum(1 for r in rows if 1.2 <= r[0] < 1.6), '1.6 and more': sum(1 for r in rows if r[0] >= 1.6),
                           'thinnest (mm, at, normal, face mm2)': thin[:globals().get('NTHIN', 14)]}
            st['left'] = left; st['walls'] = out
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-6:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('j6b_' + MODE + TAG, st)


run(None)
