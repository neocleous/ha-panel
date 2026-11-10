# rev F g2b (2026-11-10): step 1, block 2 - read-only: every cylindrical hole r 0.7...3.4 in the printed parts (world frame, mm), grouped per
# axis: radius, a point on the axis, direction, extent along it, angular coverage (face area / full cylinder area). Fillets drop out by
# coverage. Result in g2b_holes.json (full) and g2b_status.json (counts).
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_fp_lib.py'), encoding='utf-8').read())
BODIES = ['FLOOR_PLATE', 'HOUSING_F_cap', 'HOUSING_F_door', 'HOUSING_F_front', 'SPKBOX_L', 'SPKBOX_R', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R', 'CRADLE_5807',
          'RESP_CARRIER', 'SLAB_frame', 'BME_HOOD', 'GROMMET_usbc_F']
CYL = adsk.core.SurfaceTypes.CylinderSurfaceType


def wv(v):                               # design vector -> world direction
    return (v.x, v.y * C - v.z * S, v.y * S + v.z * C)


def run(_context):
    st = {}; out = {}
    t0 = time.time()
    try:
        X = K()
        for bn in BODIES:
            b = X.body(bn)
            if b is None:
                st[bn] = 'missing'; continue
            groups = {}
            nf = 0
            for f in b.faces:
                g = f.geometry
                if g.surfaceType != CYL:
                    continue
                r = g.radius * 10.0
                if r < 0.7 or r > 3.4:
                    continue
                if bn == 'FLOOR_PLATE' and abs(r - 1.0) < 0.05:
                    continue                                   # the 475 intake holes
                o = W(g.origin); a = wv(g.axis)
                n = math.sqrt(sum(c * c for c in a)); a = tuple(c / n for c in a)
                k = max(range(3), key=lambda i: abs(a[i]))
                if a[k] < 0:
                    a = tuple(-c for c in a)
                # hole or pin: outward normal toward the axis = hole
                p = f.pointOnFace
                ok, nv = f.evaluator.getNormalAtPoint(p)
                pw = W(p); nw = wv(nv)
                t = sum((pw[i] - o[i]) * a[i] for i in range(3))
                rad = tuple(pw[i] - (o[i] + t * a[i]) for i in range(3))
                if sum(rad[i] * nw[i] for i in range(3)) > 0:
                    continue                                   # convex: a pin, boss or outer fillet
                # canonical point on the axis: where the dominant coordinate is 0
                s = -o[k] / a[k]
                q = tuple(o[i] + s * a[i] for i in range(3))
                key = (round(r, 2), tuple(round(c, 1) for c in q), tuple(round(c, 3) for c in a))
                ts = []
                for v in f.vertices:
                    w = W(v.geometry)
                    ts.append(sum((w[i] - q[i]) * a[i] for i in range(3)))
                gq = groups.setdefault(key, {'t': [], 'area': 0.0})
                gq['t'] += ts; gq['area'] += f.area * 100.0
                nf += 1
            rows = []
            for (r, q, a), gq in groups.items():
                if not gq['t']:
                    continue
                t0_, t1_ = min(gq['t']), max(gq['t'])
                L = t1_ - t0_
                cov = gq['area'] / (2 * math.pi * r * L) if L > 0.05 else 0.0
                if cov < 0.55:
                    continue
                rows.append([r, list(q), list(a), round(t0_, 2), round(t1_, 2), round(cov, 2)])
            rows.sort(key=lambda t: (t[2], t[0], t[1]))
            out[bn] = rows
            st[bn] = [nf, len(rows)]
            status('g2b', st)
        json.dump(out, open(os.path.join(FP, 'g2b_holes.json'), 'w'), separators=(',', ':'))
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status('g2b', st)


run(None)
