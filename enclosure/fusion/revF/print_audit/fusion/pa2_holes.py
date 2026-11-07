# HA panel print audit, block 1 (P6): hole / pin / boss schedule from the B-rep, read-only. Method of the model audit's a1c,
#   for the 14 prints: every cylindrical face with r <= 5 mm -> diameter, hole (concave) or boss/pin (convex), world axis,
#   centre of its axial extent (x_rel, y, z), axial length, area and its share of a full cylinder (2 pi r L), and the print
#   (bracket halves by the centre's x_rel sign). Cones too (countersinks, chamfers). Writes print_audit/data/pa2_holes.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py'), encoding='utf-8').read())
exec(open(os.path.expanduser('~/Documents/HA_panel_renders/print_audit/scripts/pa_common.py'), encoding='utf-8').read())
PA2_OUT = os.path.join(PA_DIR, 'data', 'pa2_holes.json')


def pa2_tag(bn, xr):
    for (tag, b, side) in PA_PRINTS:
        if b == bn and (side is None or xr * side > 0):
            return tag
    return bn


def run(_context):
    X = Ctx(); out = {'t': time.strftime('%Y-%m-%d %H:%M:%S')}; t0 = time.time()
    try:
        pa_guard(X)
        rows = []
        for bn in sorted(set(b for (_, b, _) in PA_PRINTS)):
            b = X.body(bn)
            for f in b.faces:
                g = f.geometry; ot = g.objectType
                if ot not in (adsk.core.Cylinder.classType(), adsk.core.Cone.classType()):
                    continue
                ax = g.axis.copy(); ax.normalize(); o = g.origin
                if ot == adsk.core.Cylinder.classType():
                    r = g.radius * 10
                    if r > 5.0:
                        continue
                ts = []
                for v in f.vertices:
                    p = v.geometry; ts.append(((p.x - o.x) * ax.x + (p.y - o.y) * ax.y + (p.z - o.z) * ax.z) * 10)
                p = f.pointOnFace
                if not ts:
                    ts = [((p.x - o.x) * ax.x + (p.y - o.y) * ax.y + (p.z - o.z) * ax.z) * 10]
                t_lo, t_hi = min(ts), max(ts); tm = (t_lo + t_hi) / 2
                cpt = P3(o.x + ax.x * tm / 10, o.y + ax.y * tm / 10, o.z + ax.z * tm / 10)
                ok, n = f.evaluator.getNormalAtPoint(p)
                k = ((p.x - o.x) * ax.x + (p.y - o.y) * ax.y + (p.z - o.z) * ax.z)
                q = P3(o.x + ax.x * k, o.y + ax.y * k, o.z + ax.z * k)
                radial = V3(p.x - q.x, p.y - q.y, p.z - q.z)
                hole = radial.dotProduct(n) < 0
                aw = nw_of(ax); c_w = pa_wpt(cpt); L = t_hi - t_lo
                if ot == adsk.core.Cylinder.classType():
                    full = (f.area * 100) / (2 * math.pi * r * L) if L > 1e-6 else None
                    rows.append([pa2_tag(bn, c_w[0]), 'cyl', round(2 * r, 3), 'hole' if hole else 'boss', [round(v, 3) for v in aw],
                                 [round(v, 2) for v in c_w], round(L, 2), round(f.area * 100, 2),
                                 None if full is None else round(full, 3)])
                else:
                    rows.append([pa2_tag(bn, c_w[0]), 'cone', round(math.degrees(g.halfAngle), 1), 'hole' if hole else 'boss',
                                 [round(v, 3) for v in aw], [round(v, 2) for v in c_w], round(L, 2), round(f.area * 100, 2), None])
        out['rows'] = rows; out['n'] = len(rows)
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    pa_out(PA2_OUT, out)
    log('pa2_holes', 'run', {'n': out.get('n'), 't_s': out.get('t_s'), 'FAIL': out.get('FAIL')})
    print(json.dumps({k: out.get(k) for k in ('n', 't_s', 'FAIL')}, separators=(',', ':')))
