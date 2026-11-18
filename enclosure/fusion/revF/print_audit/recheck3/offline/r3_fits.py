"""recheck3, point 12: the fits that rest on print accuracy, as sliced (final slices F4_P3a, F3_P3b, H1s_P1_solid).
   pegs      radius of the printed peg about its true axis, per layer (outline of the printed lines, samples beyond the land's plane)
   pocket    free radius of the plate's pocket and the slot's free half width / half length about their centres, per layer
   lands     printed underside of the four lands against the land's plane (d 12.8), along the normal
   groove    the cloth groove's width and depth as printed, at x 0, 30, 47 (0.8 deep) and 60, 80 (2.0 deep)
   stop      the door frame's faces at y -53.5: where they print, what lies under them
   edge      first-layer inset at the shell's bottom inner edge"""
import sys, json, math, numpy as np
from r3_gq import *
from r3_under import under, SUP
from shapely.geometry import Point, LineString, Polygon
C12, S12 = math.cos(math.radians(12)), math.sin(math.radians(12))
def slab_to_world(x, up, d): return np.array([x, -d * C12 - up * S12, 143.3 - d * S12 + up * C12])
def outline_pts(P, step=0.05):
    out = []
    for p in polys_of(P):
        for r in [p.exterior] + list(p.interiors):
            n = max(int(r.length / step), 8); out.append(np.array([r.interpolate(i / n, normalized=True).coords[0] for i in range(n)]))
    return np.vstack(out) if out else np.zeros((0, 2))
what = sys.argv[1]
if what == 'pegs':
    g = G('F4_P3a'); bp = BedPart('shell', (0, -30, 0))
    for nm, x in (('viewer left', 85), ('viewer right', -85)):
        a = bp.to_bed(slab_to_world(x, -82, 12.8))[0]; b = bp.to_bed(slab_to_world(x, -82, 11.6))[0]; ax = (b - a) / np.linalg.norm(b - a)   # land plane -> tip
        print('peg %s: land point bed %s, tip %s, axis %s (%.1f deg to the bed normal)' % (nm, np.round(a, 2), np.round(b, 2), np.round(ax, 3), math.degrees(math.acos(abs(ax[2])))))
        rows = []
        for li in g.PL:
            zt = float(g.L[li]); lh = g.lh_of(li)
            if zt < min(a[2], b[2]) - 4.5 or zt > max(a[2], b[2]) + 4.5: continue
            c = a + ax * ((zt - lh / 2 - a[2]) / ax[2]); win = (c[0] - 6.5, c[0] + 6.5, c[1] - 6.5, c[1] + 6.5)
            P = foot(g, li, win)
            if P.is_empty: continue
            pts = outline_pts(P); rr = []
            for z in (zt - lh, zt):
                Q = np.c_[pts, np.full(len(pts), z)] - a; t = Q @ ax; rad = np.linalg.norm(Q - np.outer(t, ax), axis=1)
                m = (t > 0.15) & (t < 1.25) & (rad > 3.0) & (rad < 4.8)                      # the peg's side, beyond the land's plane (the land's steps reach 0.1)
                rr.append(rad[m])
            rr = np.concatenate(rr)
            if len(rr) > 20: rows.append((zt, float(np.median(rr)), float(np.percentile(rr, 95)), float(rr.max()), len(rr)))
        for r in rows: print('   layer top %.1f: peg radius about its axis median %.3f, 95%% %.3f, max %.3f (%d samples)' % r)
if what == 'pocket':
    g = G('F3_P3b'); bp = BedPart('screen', (0, 0, 0)); L1 = bp.layer(0.1)
    holes = sorted([Polygon(r) for p in polys_of(L1) for r in p.interiors if 40 < Polygon(r).area < 100], key=lambda h: h.area)
    for nm, H in zip(('pocket', 'slot'), holes):
        c = np.array(H.centroid.coords[0]); b = H.bounds; print('%s: model %.2f x %.2f, area %.1f, centre bed %s' % (nm, b[2] - b[0], b[3] - b[1], H.area, np.round(c, 2)))
        for li in g.PL[:8]:
            zt = float(g.L[li]); win = (b[0] - 2, b[2] + 2, b[1] - 2, b[3] + 2); P = foot(g, li, win, exclude=())
            S = g.S; sup = np.isin(g.F, [i for i, n in enumerate(g.names) if n in SUP]) & (S[:, 7] == li)
            free = Point(c).distance(P) if not P.is_empty else float('nan')
            # free half extents along bed x and bed y through the centre
            def half(dx, dy):
                ln = LineString([tuple(c), (c[0] + 8 * dx, c[1] + 8 * dy)]); I = ln.intersection(P); return Point(c).distance(I) if not I.is_empty else float('nan')
            print('   layer top %.1f: free r %.3f | half +x %.3f -x %.3f +y %.3f -y %.3f | model section here: %s' % (zt, free, half(1, 0), half(-1, 0), half(0, 1), half(0, -1),
                  'hole' if not bp.layer(zt - 0.1).contains(Point(c)) else 'solid (floor)'))
if what == 'lands':
    g = G('F4_P3a'); bp = BedPart('shell', (0, -30, 0)); rng = np.random.default_rng(1)
    for nm, x, up, r0, r1 in (('top, viewer left', 70, 27, 2.3, 5.4), ('top, viewer right', -70, 27, 2.3, 5.4), ('bottom, viewer left', 85, -82, 4.25, 5.4), ('bottom, viewer right', -85, -82, 4.25, 5.4)):
        # sample points on the land's annulus in the slab frame (x, up) at d 12.8
        n = 4000; rad = np.sqrt(rng.uniform(r0 ** 2, r1 ** 2, n)); th = rng.uniform(0, 2 * math.pi, n)
        W = np.array([slab_to_world(x + rad[i] * math.cos(th[i]), up + rad[i] * math.sin(th[i]), 12.8) for i in range(n)]); Bd = bp.to_bed(W)
        zlo, zhi = Bd[:, 2].min(), Bd[:, 2].max(); off = np.full(n, np.nan); win = (Bd[:, 0].min() - 1, Bd[:, 0].max() + 1, Bd[:, 1].min() - 1, Bd[:, 1].max() + 1)
        for li in g.PL:
            zt = float(g.L[li]); lh = g.lh_of(li)
            if zt < zlo - 0.3 or zt - lh > zhi + 0.6: continue
            P = foot(g, li, win); todo = np.isnan(off) & (Bd[:, 2] < zt + 0.35)
            if P.is_empty or not todo.any(): continue
            ins = shapely.contains(P, shapely.points(Bd[todo, 0], Bd[todo, 1])); idx = np.where(todo)[0][ins]
            off[idx] = (Bd[idx, 2] - (zt - lh)) * C12                                    # + = the print stands proud of the land's plane (toward the plate)
        ok = ~np.isnan(off)
        print('land %-20s bed z %.2f..%.2f | printed underside against the plane, along the normal: max %+.3f, mean %+.3f, min %+.3f (%d of %d samples found)' % (
            nm, zlo, zhi, np.nanmax(off), np.nanmean(off), np.nanmin(off), ok.sum(), n))
if what == 'groove':
    g = G('F4_P3a'); bp = BedPart('shell', (0, -30, 0))
    for xw in (0.0, 47.0, 60.0):
        xb = float(bp.to_bed([[xw, 0, 0]])[0][0]); y0 = float(bp.to_bed([[0, 0, 47.0]])[0][1]); y1 = float(bp.to_bed([[0, 0, 52.5]])[0][1])
        r = vcut2(g, bp, 'x', xb, y0, y1, 0.0, 3.2, ds=0.01); s = r['s']
        print('cut at world x %+.0f (bed x %.2f), bed y %.2f..%.2f (world z 47.0..52.5):' % (xw, xb, y0, y1))
        for k, z in enumerate(r['z']):
            def gaps(o):
                o = np.asarray(o, bool); out = []; i = 0
                while i < len(o):
                    if not o[i]:
                        j = i
                        while j < len(o) and not o[j]: j += 1
                        if i > 0 and j < len(o): (out.append((s[i] - 0.005, s[j - 1] + 0.005)) if s[j - 1] - s[i] > 0.3 else None)
                        i = j
                    else: i += 1
                return out
            gm = gaps(r['model']['occ'][k]); gs = gaps(r['sliced']['occ'][k])
            fm = ', '.join('%.2f wide at world z %.2f' % (b - a, (a + b) / 2 - y0 + 47.0) for a, b in gm) or '-'
            fs = ', '.join('%.2f wide at world z %.2f' % (b - a, (a + b) / 2 - y0 + 47.0) for a, b in gs) or '-'
            print('   layer %.1f..%.1f: model gap %s | printed gap %s' % (z - 0.1, z + 0.1, fm, fs))
if what == 'stop':
    g = G('F4_P3a'); bp = BedPart('shell', (0, -30, 0))
    A = bp.layer(60.3).difference(bp.layer(60.1).buffer(0.02)); B = [p for p in polys_of(A) if p.area > 20]
    print('faces first printed in layer 60.2..60.4 (world y -53.4..-53.6):')
    for p in sorted(B, key=lambda p: -p.area):
        b = p.bounds; w = bp.to_world([[b[0], b[1], 60.3], [b[2], b[3], 60.3]])
        print('   %.1f mm2, world x %.1f..%.1f z %.1f..%.1f' % (p.area, w[:, 0].min(), w[:, 0].max(), w[:, 2].min(), w[:, 2].max()))
        under(g, bp, [w[:, 0].min() - 0.2, -53.65, w[:, 2].min() - 0.2], [w[:, 0].max() + 0.2, -53.35, w[:, 2].max() + 0.2], step=0.1, label='      under it')
if what == 'edge':
    g = G('F4_P3a'); bp = BedPart('shell', (0, -30, 0))
    for li in g.PL[:3]:
        zt = float(g.L[li]); Mo = bp.layer(zt - 0.1); b = Mo.bounds; P = foot(g, li, (b[0] - 1, b[2] + 1, b[1] - 1, b[3] + 1), exclude=('Brim',))
        d = [Point(q).distance(P.boundary) for q in outline_pts(Mo.buffer(0), 0.5) if not P.is_empty]
        ins = np.array([P.contains(Point(q)) for q in outline_pts(Mo.buffer(0), 0.5)])
        print('layer top %.1f: model %.0f mm2, printed %.0f mm2 | printed edge inside the model outline by median %.3f (5%% %.3f, 95%% %.3f); outline points covered by print %.0f%%' % (
            zt, Mo.area, P.area, np.median(d), np.percentile(d, 5), np.percentile(d, 95), 100 * ins.mean()))
if what == 'lands2':
    g = G('F4_P3a'); bp = BedPart('shell', (0, -30, 0)); rng = np.random.default_rng(1)
    for nm, x, up in (('top, viewer left', 70, 27), ('top, viewer right', -70, 27), ('bottom, viewer left', 85, -82), ('bottom, viewer right', -85, -82)):
        # the land = the model's face in the plane d 12.8 round the post's axis: sample a disc of r 6 and keep the points that lie on the model's surface there
        n = 6000; rad = np.sqrt(rng.uniform(0, 36, n)); th = rng.uniform(0, 2 * math.pi, n)
        W = np.array([slab_to_world(x + rad[i] * math.cos(th[i]), up + rad[i] * math.sin(th[i]), 12.8) for i in range(n)]); Bd = bp.to_bed(W)
        nrm = bp.to_bed([slab_to_world(0, 0, 1)])[0] - bp.to_bed([slab_to_world(0, 0, 0)])[0]            # +d in the bed frame (into the post)
        inside = bp.m.contains(Bd + 0.03 * nrm) & ~bp.m.contains(Bd - 0.03 * nrm); Bd = Bd[inside]; rad = rad[inside]; n = len(Bd)
        zlo, zhi = Bd[:, 2].min(), Bd[:, 2].max(); off = np.full(n, np.nan); win = (Bd[:, 0].min() - 1, Bd[:, 0].max() + 1, Bd[:, 1].min() - 1, Bd[:, 1].max() + 1)
        for li in g.PL:
            zt = float(g.L[li]); lh = g.lh_of(li)
            if zt < zlo - 0.3 or zt - lh > zhi + 0.6: continue
            P = foot(g, li, win); todo = np.isnan(off) & (Bd[:, 2] < zt + 0.35)
            if P.is_empty or not todo.any(): continue
            ins = shapely.contains(P, shapely.points(Bd[todo, 0], Bd[todo, 1])); idx = np.where(todo)[0][ins]
            off[idx] = (Bd[idx, 2] - (zt - lh)) * C12
        ok = ~np.isnan(off)
        print('land %-20s %d samples on the face (r %.2f..%.2f, about %.1f mm2), bed z %.2f..%.2f | printed underside against the plane, along the normal: max %+.3f, mean %+.3f, 5%% %+.3f, min %+.3f (%d found)' % (
            nm, n, rad.min(), rad.max(), 36 * math.pi * n / 6000, zlo, zhi, np.nanmax(off), np.nanmean(off), np.nanpercentile(off, 5), np.nanmin(off), ok.sum()))
if what == 'edge2':
    g = G('F4_P3a'); bp = BedPart('shell', (0, -30, 0))
    for xw in (0.0, 30.0, 60.0, 88.0):
        xb = float(bp.to_bed([[xw, 0, 0]])[0][0]); y0 = float(bp.to_bed([[0, 0, 1.5]])[0][1]); y1 = float(bp.to_bed([[0, 0, 9.0]])[0][1])
        r = vcut2(g, bp, 'x', xb, y0, y1, 0.0, 1.0, ds=0.01); s = r['s']
        print('cut at world x %+.0f, world z 1.5..9.0, first five layers: printed against modelled extent along world z' % xw)
        for k, z in enumerate(r['z']):
            def runs(o):
                o = np.asarray(o, bool); out = []; i = 0
                while i < len(o):
                    if o[i]:
                        j = i
                        while j < len(o) and o[j]: j += 1
                        out.append((s[i] - 0.005 - y0 + 1.5, s[j - 1] + 0.005 - y0 + 1.5)); i = j
                    else: i += 1
                return out
            print('   layer %.1f..%.1f: model %s | printed %s' % (z - 0.1, z + 0.1, ', '.join('%.2f..%.2f' % t for t in runs(r['model']['occ'][k])) or '-', ', '.join('%.2f..%.2f' % t for t in runs(r['sliced']['occ'][k])) or '-'))
