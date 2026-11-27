# Blocks 2 and 3: the holes this pass deepens, read before they are built and after. READ-ONLY (temporary bodies only).
# A hole is given as (label, part, mouth M, floor F, radius r, deeper by d): world points on its axis; inward = from M to F.
#   read   for each hole:
#          - the part's solid along the axis and along eight lines parallel to it just inside the hole's wall (r - 0.05), from 2
#            before the mouth to 14 beyond the floor: so the floor's place at the rim and the plastic behind it all round;
#          - the wall round the hole: eight lines parallel to the axis at r + 0.05, the least solid stretch;
#          - what else of the unit lies on the axis beyond the floor;
#          - the piece to be taken out, T (radius r, from the floor to d beyond it), and T grown by g all round the new end
#            (radius r + g, to d + g beyond the floor): what of the grown piece is not the part's plastic (air or another body:
#            where the wall round the new end is under g), and what of THAT lies outside the cloth reference REF_F_outer
#            (so: where the OUTER skin round the new end is under g);
#          - the least distance from T to the faces of the cloth reference (the last passes' reading of the outer skin, d62);
#          - the floor's height in the part's print, the way its face looks, and where its middle lands (m10's rule).
# Run: L.checked('s30_holes.py', sha)['main'](what, tag, **kw)  -> s30_<what>_<tag>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/screw_margins_v88/'
L = runpy.run_path(D + 's00_lib.py')
PIN = (adsk.fusion.PointContainment.PointInsidePointContainment, adsk.fusion.PointContainment.PointOnPointContainment)

# the holes of this pass, from ../model-v85/m11_holes.py and m10_m2.txt / m10_holes_b.txt (version 85; the shell and the door are
# unchanged since): (part, mouth, floor, radius, deeper by)
HOLES = {
    'sp_L1': ('HOUSING_F_front', (85.0, 5.7, 60.68), (85.0, -0.51, 59.36), 2.0, 0.6),
    'sp_R1': ('HOUSING_F_front', (-85.0, 5.7, 60.68), (-85.0, -0.51, 59.36), 2.0, 0.6),
    'hood': ('HOUSING_F_front', (-57.87, -50.61, 100.0), (-61.72, -49.05, 100.0), 0.8, 1.1),
    'grom_L': ('HOUSING_F_door', (9.0, -79.39, 9.71), (9.0, -80.72, 5.63), 0.8, 0.9),
    'grom_R': ('HOUSING_F_door', (-9.0, -79.39, 9.71), (-9.0, -80.72, 5.63), 0.8, 0.9),
    'door_1': ('HOUSING_F_door', (50.0, -67.0, 2.8), (50.0, -67.0, 10.0), 2.0, 0.5),
    'door_2': ('HOUSING_F_door', (19.0, -74.5, 2.8), (19.0, -74.5, 10.0), 2.0, 0.5),
    'door_3': ('HOUSING_F_door', (-19.0, -77.0, 2.8), (-19.0, -77.0, 10.0), 2.0, 0.5),
    'door_4': ('HOUSING_F_door', (-50.0, -67.0, 2.8), (-50.0, -67.0, 10.0), 2.0, 0.5),
}


def perp(a):
    r = (0.0, 0.0, 1.0) if abs(a[2]) < 0.9 else (1.0, 0.0, 0.0)
    u = (a[1] * r[2] - a[2] * r[1], a[2] * r[0] - a[0] * r[2], a[0] * r[1] - a[1] * r[0])
    n = math.sqrt(sum(q * q for q in u)); u = tuple(w / n for w in u)
    v = (a[1] * u[2] - a[2] * u[1], a[2] * u[0] - a[0] * u[2], a[0] * u[1] - a[1] * u[0])
    return u, v


def ring(u, v, n=8):
    return [tuple(u[i] * math.cos(2 * math.pi * j / n) + v[i] * math.sin(2 * math.pi * j / n) for i in range(3)) for j in range(n)]


def exact(k, b, M, F, r):
    """The hole's own faces: the cylinder of radius r nearest the given axis, its axis and its two ends, from the part's faces."""
    o = k.unit(tuple(F[i] - M[i] for i in range(3))); best = None
    for h in k.holes_of(b, r - 0.06, r + 0.06):
        if h['k'] != 'h':
            continue
        a = h['a']
        if abs(abs(sum(a[i] * o[i] for i in range(3))) - 1.0) > 1e-3:
            continue
        d = [h['A'][i] - M[i] for i in range(3)]; t = sum(d[i] * o[i] for i in range(3))
        off = math.sqrt(max(sum(q * q for q in d) - t * t, 0.0))
        if off < 0.3 and (best is None or off < best[0]):
            best = (off, h)
    return best


def st_read(k, X, names, gs=(1.0, 1.5, 1.6, 2.0, 2.5, 3.0), ref='REF_F_outer', sec=72):
    k.budget(sec)
    M10 = L['old']('m10')
    R = X.body(ref); Rt = X.tbm.copy(R)
    print('cloth reference %s: %.3f mm3, lumps %d, faces %d, world box %s' % (ref, R.volume * 1000.0, R.lumps.count, R.faces.count, k.wbb(X, R)))
    for nm in names:
        part, M, F, r, d = HOLES[nm]
        b = X.body(part); pl = k.parts(X, part)
        o = k.unit(tuple(F[i] - M[i] for i in range(3))); u, v = perp(o)
        depth = math.sqrt(sum((F[i] - M[i]) ** 2 for i in range(3)))
        print('\n%s: %s, mouth %s, floor %s, r %.2f, %.3f deep, inward %s; to go %.2f deeper' % (nm, part, k.r2(M, 3), k.r2(F, 3), r, depth, k.r2(o, 4), d))
        ex = exact(k, b, M, F, r)
        if ex:
            h = ex[1]
            print('   the part\'s cylinder: r %.3f, ends %s and %s, L %.3f, covered %.2f, %.3f off the given axis' % (h['r'], h['A'], h['B'], h['L'], h['cov'], ex[0]))
        p0 = tuple(M[i] - o[i] * 2.0 for i in range(3)); p1 = tuple(F[i] + o[i] * 14.0 for i in range(3))
        ax = [(round(a - 2.0, 2), round(c - 2.0, 2)) for a, c in k.needle_t(X, pl, p0, p1, 0.02)]
        print('   on the axis, solid (mm from the mouth inward): %s -> behind the floor %s' % (ax, [(round(a - depth, 2), round(c - depth, 2)) for a, c in ax if c > depth - 0.01]))
        rows = []; behind = []
        for w in ring(u, v):
            q0 = tuple(p0[i] + w[i] * (r - 0.05) for i in range(3)); q1 = tuple(p1[i] + w[i] * (r - 0.05) for i in range(3))
            st = [(round(a - 2.0 - depth, 2), round(c - 2.0 - depth, 2)) for a, c in k.needle_t(X, pl, q0, q1, 0.02)]
            st = [s for s in st if s[1] > -0.3]
            rows.append(st)
            if st:
                behind.append(st[0][1] - max(st[0][0], 0.0))
        print('   just inside the wall (r - 0.05), eight lines, solid (mm from the floor inward): %s' % rows)
        print('   behind the floor at the rim: least %.2f, most %.2f; after the deepening least %.2f' % (min(behind), max(behind), min(behind) - d) if behind else '   no solid behind the rim')
        wl = []
        for w in ring(u, v):
            q0 = tuple(M[i] + o[i] * 0.3 + w[i] * (r + 0.05) for i in range(3))
            for s in (0.3, depth * 0.5, depth - 0.2, depth + d - 0.05):
                a0 = tuple(M[i] + o[i] * s + w[i] * (r + 0.05) for i in range(3)); a1 = tuple(a0[i] + w[i] * 9.0 for i in range(3))
                st = k.needle_t(X, pl, a0, a1, 0.02)
                wl.append((round(st[0][1] - st[0][0], 2) if st and st[0][0] < 0.06 else 0.0, round(s, 2)))
        print('   the wall round it (from r + 0.05 outward), eight sides at four depths: least %s; all %s' % (min(wl), sorted(set(q[0] for q in wl))[:8]))
        others = []
        for q in k.current(X, leads=True, kos=False):
            if q.name == part or q.name in ('SCREWS_M2x6_env', 'DRV_screw_heads_env'):
                continue
            bb = k.wbb(X, q); lo = [min(F[i], p1[i]) - 0.5 for i in range(3)]; hi = [max(F[i], p1[i]) + 0.5 for i in range(3)]
            if bb[0] > hi[0] or bb[1] < lo[0] or bb[2] > hi[1] or bb[3] < lo[1] or bb[4] > hi[2] or bb[5] < lo[2]:
                continue
            st = k.needle_t(X, k.parts(X, q.name), F, p1, 0.02)
            if st:
                others.append((q.name, st))
        print('   other bodies on the axis within 14 beyond the floor (mm from the floor): %s' % others)
        thick = [c - depth for a, c in ax if c > depth - 0.01 and a <= depth + 0.05]
        if thick:
            for e in (0.2, 0.5, 1.0):
                px = tuple(F[i] + o[i] * (thick[0] + e) for i in range(3))
                print('   %.1f beyond the far face on the axis %s: in the reference %s; in the part %s' % (
                    e, k.r2(px, 2), R.pointContainment(k.Wp(*px)) in PIN, b.pointContainment(k.Wp(*px)) in PIN))
        T = X.cyl(F, tuple(F[i] + o[i] * d for i in range(3)), r)
        print('   T (the piece to go): %.4f mm3; of it in the part now %.4f' % (X.vol(T), k.xparts(X, T, pl)))
        for g in gs:
            Tg = X.cyl(F, tuple(F[i] + o[i] * (d + g) for i in range(3)), r + g)
            for p in pl:
                if Tg.faces.count and Tg.boundingBox.intersects(p.boundingBox):
                    X.dif(Tg, X.tbm.copy(p))
            if not Tg.faces.count or X.vol(Tg) < 1e-6:
                print('   grown %.1f round the new end: all of it is the part\'s plastic' % g); continue
            v_all = X.vol(Tg); lumps = X.lumps(Tg)[:6]
            To = X.tbm.copy(Tg); X.dif(To, X.tbm.copy(Rt))
            v_out = X.vol(To) if To.faces.count else 0.0
            print('   grown %.1f round the new end: %.4f mm3 is not the part\'s plastic, in %d lumps %s; of that OUTSIDE the cloth reference %.4f mm3 %s' % (
                g, v_all, Tg.lumps.count, lumps, v_out, X.lumps(To)[:4] if v_out > 0 else ''))
        best = None; tb = T.boundingBox
        for f in R.faces:
            fb = f.boundingBox
            if (fb.minPoint.x - 0.6 > tb.maxPoint.x or fb.maxPoint.x + 0.6 < tb.minPoint.x or fb.minPoint.y - 0.6 > tb.maxPoint.y or
                    fb.maxPoint.y + 0.6 < tb.minPoint.y or fb.minPoint.z - 0.6 > tb.maxPoint.z or fb.maxPoint.z + 0.6 < tb.minPoint.z):
                continue
            rr = X.mm.measureMinimumDistance(T, f); dd = rr.value * 10.0
            if best is None or dd < best[0]:
                best = (dd, k.r2(k.W(rr.positionOne), 2), k.r2(k.W(rr.positionTwo), 2))
        print('   T to the nearest face of the cloth reference within 6: %s' % (best,))
        ht0 = M10['height'](k, part, F); F2 = tuple(F[i] + o[i] * d for i in range(3)); ht1 = M10['height'](k, part, F2)
        up = M10['up_dir'](k, part); dd = sum(o[i] * up[i] for i in range(3)); lh = M10['PRINT'][part][3]
        looks = 'upright (the hole lies in the layers)' if abs(dd) < 0.02 else ('down' if dd > 0 else 'up')
        lean = math.degrees(math.acos(min(1.0, abs(dd))))
        row = '   in the print (%s, layers %.2f): the floor\'s middle at height %.3f now, %.3f after; its face looks %s; the axis leans %.1f deg from the print\'s upright' % (
            M10['PRINT'][part][0], lh, ht0, ht1, looks, lean)
        if abs(dd) >= 0.02:
            row += '; middle lands %s now, %s after; across the hole the floor spans %.2f of height' % (
                M10['land'](ht0, lh, looks)[0], M10['land'](ht1, lh, looks)[0], 2 * r * math.sin(math.radians(lean)))
        print(row)
        if k.late():
            print('time'); return


def _main(what, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'read': st_read}[what](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(what, tag='', **kw):
    L['out']('s30_%s%s.txt' % (what, ('_' + tag) if tag else ''), _main, what, **kw)
# END
