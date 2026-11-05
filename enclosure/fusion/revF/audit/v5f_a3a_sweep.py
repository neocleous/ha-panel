# HA panel model audit (2026-11-05) block 3a: insertion sweeps (A.1), read-only (TemporaryBRep copies only).
#   Set by the loader: LABEL, MOVE (body names moving together), FIXED (body names already installed), PATH (world-mm
#   offsets of the moving group from its installed pose, as waypoints; consecutive waypoints are joined by straight steps of
#   at most STEP mm, default 0.5), optional CROP margin (mm, default 2), K0 (resume step index) and MOVE_CROP
#   ({name: world box}) to move one lump of a multi-lump body (e.g. one bracket half).
#   Fixed bodies are cropped once to the moving group's swept box (+ CROP) – lesson 24. Each step: moving copies moved by
#   the step delta, design-box prefilter, then intersection volume with each cropped fixed body (> 0.005 mm³ is a hit).
#   Time-boxed at 45 s (stopped_at = next step). Result -> ~/Documents/audit/data/sweep_<LABEL>_<K0>.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
exec(open(os.path.expanduser('~/Documents/audit/scripts/v5f_audit_common.py')).read())


def steps_of(path, st, deg_step=0.5):
    pts = [tuple(path[0])]; m = len(path[0])
    for a, b in zip(path[:-1], path[1:]):
        L = math.sqrt(sum((b[i] - a[i]) ** 2 for i in range(3))); n = max(1, int(math.ceil(L / st - 1e-9)))
        if m > 3:
            n = max(n, int(math.ceil(abs(b[3] - a[3]) / deg_step - 1e-9)))
        for k in range(1, n + 1):
            pts.append(tuple(a[i] + (b[i] - a[i]) * k / n for i in range(m)))
    return pts


def bb_overlap(a, b):
    return not (a.maxPoint.x < b.minPoint.x or b.maxPoint.x < a.minPoint.x or a.maxPoint.y < b.minPoint.y or
                b.maxPoint.y < a.minPoint.y or a.maxPoint.z < b.minPoint.z or b.maxPoint.z < a.minPoint.z)


def run(_context):
    X = Ctx(); guard(X); out = {}; t0 = time.time()
    lab = globals().get('LABEL', 'sweep'); st = globals().get('STEP', 0.5); crop = globals().get('CROP', 2.0)
    k0 = globals().get('K0', 0)
    try:
        pts = steps_of(globals()['PATH'], st); out['n_steps'] = len(pts)
        mv = [(n, tb_copy(X, n)) for n in globals()['MOVE']]
        for n, t in mv:                               # MOVE_CROP {name: [x_rel0, x_rel1, y0, y1, z0, z1]}: one lump of a body
            cb = globals().get('MOVE_CROP', {}).get(n)
            if cb:
                inter(X, t, wbox_rel(X, cb))
        # swept world box of the moving group (corners of each body's tight world box over all path waypoints)
        lo = [1e9] * 3; hi = [-1e9] * 3
        for n, t in mv:
            bb = wbb(X, t)
            for pw in globals()['PATH']:
                dx, dy, dz = pw[0], pw[1], pw[2]
                for i, (a, b) in enumerate(((bb[0], bb[1]), (bb[2], bb[3]), (bb[4], bb[5]))):
                    d = (dx, dy, dz)[i]; lo[i] = min(lo[i], a + d); hi[i] = max(hi[i], b + d)
        region = wbox_rel(X, [lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]], crop)
        fx = []
        for n in globals()['FIXED']:
            b = X.body(n)
            if b is None:
                out.setdefault('missing', []).append(n); continue
            q = X.tbm.copy(b); inter(X, q, X.tbm.copy(region))
            if q.volume > 0:
                fx.append((n, q))
        out['fixed_in_region'] = [n for n, q in fx]
        rot = globals().get('ROT_PIVOT'); orig = [(n, X.tbm.copy(t)) for n, t in mv]   # ROT_PIVOT: (x_rel, y, z); PATH points (dx, dy, dz, deg)
        cur = (0.0, 0.0, 0.0)
        hits = []; worst = {}; stop = len(pts)
        for k in range(k0, len(pts)):
            if time.time() - t0 > 45:
                stop = k; break
            p = pts[k]
            if rot is None:
                d = (p[0] - cur[0], p[1] - cur[1], p[2] - cur[2]); cur = p
                for n, t in mv:
                    mvw(X, t, *d)
            else:                                      # rebuild each copy: rotation about world x through ROT_PIVOT, then shift
                M = adsk.core.Matrix3D.create(); M.setToRotation(math.radians(p[3]), V3(1, 0, 0), Dw(XC + rot[0], rot[1], rot[2]))
                tr = M.translation; w = wv((p[0], p[1], p[2])); tr.add(V3(w.x / 10, w.y / 10, w.z / 10)); M.translation = tr
                mv = []
                for n, t0_ in orig:
                    t = X.tbm.copy(t0_); X.tbm.transform(t, M); mv.append((n, t))
            for n, t in mv:
                tb = t.boundingBox
                for fn, q in fx:
                    if not bb_overlap(tb, q.boundingBox):
                        continue
                    v = vol_x(X, t, q)
                    if v > 0.005:
                        key = '%s | %s' % (n, fn)
                        if v > worst.get(key, [0])[0]:
                            qq = X.tbm.copy(t); inter(X, qq, X.tbm.copy(q))
                            worst[key] = [v, [round(c, 2) for c in p], [round(c, 1) for c in wbb(X, qq)]]
                        hits.append([k, [round(c, 2) for c in p], key, v])
        out['range'] = [k0, stop]; out['n_hit_steps'] = len(set(h[0] for h in hits)); out['worst'] = worst
        out['hits_first'] = hits[:30]
        json.dump(out, open(os.path.join(AUD, 'data', 'sweep_%s_%d.json' % (lab, k0)), 'w'))
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_a3a_sweep', lab, {k: v for k, v in out.items() if k != 'hits_first'})
    print(json.dumps({k: v for k, v in out.items() if k != 'hits_first'}))
