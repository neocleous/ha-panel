# Block 2 and the close: checks on the two boxes in the model (after the put), against their hidden copies _v85. READ-ONLY.
#   walls    the wall round each driver insert hole (12 directions, stations along it, in the stop and below), the solid on its
#            axis; round each clip pilot and the holder's pilot; round each floor insert hole; least of each
#   small    flat faces under 0.3 mm2 in each box, new against the copy
#   grid     every level face (square to y) of each box: bed height (y + 52), off the 0.2 grid, area; those that differ from the copy
#   chamber  each box's chamber by the record's method (../model-v80/d27_fits.py chamber), the driver and the lead taken out
#   plug     the USB-A plug, its cable and lead to the left box; what the plug's box grown by g shares with the box
# Run: L.checked('m17_checks.py', sha)['main'](stage, tag, **kw)  -> m17_<stage>_<tag>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/box_margins_v85/'
L = runpy.run_path(D + 'm00_lib.py')
AX = 70.5; AZ = 28.0; HALF = 17.75
PLN = adsk.core.SurfaceTypes.PlaneSurfaceType


def screws(sx):
    return [(sx * (AX + a * HALF), AZ + b * HALF) for a in (-1, 1) for b in (-1, 1)]


def ring_min(k, X, c, p, e1, e2, r0, reach=9.0):
    out = []
    for j in range(12):
        a = math.radians(30 * j)
        d = tuple(e1[i] * math.cos(a) + e2[i] * math.sin(a) for i in range(3))
        s = k.needle_t(X, [c], k.along(p, d, r0 - 0.3), k.along(p, d, reach), 0.02)
        s = [q for q in s if q[0] <= 0.35 and q[1] > 0.32]
        out.append(round(s[0][1] - 0.3, 2) if s else 0.0)
    return out


def st_walls(k, X, sides=('L', 'R')):
    k.budget(75)
    for sx, s in ((1, 'L'), (-1, 'R')):
        if s not in sides:
            continue
        bx = X.tbm.copy(X.body('SPKBOX_' + s))
        a, b = sorted((sx * 38.0, sx * 102.0))
        c = X.wbox(a, b, -22.0, -2.0, 0.0, 62.0); X.sec(c, bx)
        for px, pz in screws(sx):
            lo = (99.0, None); stop = (99.0, None)
            for y in [-4.05 - 0.3 * i for i in range(0, 25)]:
                w = ring_min(k, X, c, (px, y, pz), (1, 0, 0), (0, 0, 1), 2.0)
                m = min(w)
                if y > -5.0:
                    stop = min(stop, (m, y))
                else:
                    lo = min(lo, (m, y))
            ax = [(round(-22.0 + p, 2), round(-22.0 + q, 2)) for p, q in k.needle_t(X, [c], (px, -22.0, pz), (px, -2.0, pz), 0.02)]
            print('SPKBOX_%s driver hole (%+.2f, %.2f): least wall round it in the stop %.2f (y %.2f), below %.2f (y %.2f); solid on its axis %s' % (
                s, px, pz, stop[0], stop[1], lo[0], lo[1], ax))
        pz = 35.0 if sx > 0 else 41.0
        rows = []
        for xs in (43.7, 45.0, 46.5, 48.0, 49.3, 49.8):
            if sx > 0 and xs > 49.4:
                continue
            w = ring_min(k, X, c, (sx * xs, -9.45, pz), (0, 1, 0), (0, 0, 1), 1.35)
            rows.append('x %.1f: %.2f' % (sx * xs, min(w)))
        end = [(round(p, 2), round(q, 2)) for p, q in k.needle_t(X, [c], (sx * 43.0, -9.45, pz), (sx * 56.0, -9.45, pz), 0.02)]
        print('SPKBOX_%s clip pilot (y -9.45, z %.1f): least wall round it %s; solid on its axis from x %.1f: %s' % (s, pz, '; '.join(rows), sx * 43.0, end))
        if sx > 0:
            ch = X.wbox(38.0, 52.0, -14.0, -2.0, 50.0, 66.0); X.sec(ch, X.tbm.copy(X.body('SPKBOX_L')))
            rows = []
            for xs in (40.3, 42.0, 44.0, 46.0, 46.4):
                w = ring_min(k, X, ch, (xs, -7.35, 57.6), (0, 1, 0), (0, 0, 1), 1.35)
                rows.append('x %.1f: %.2f' % (xs, min(w)))
            end = [(round(p, 2), round(q, 2)) for p, q in k.needle_t(X, [ch], (38.5, -7.35, 57.6), (52.0, -7.35, 57.6), 0.02)]
            print('SPKBOX_L holder pilot (y -7.35, z 57.6): least wall round it %s; solid on its axis from x 38.5: %s' % ('; '.join(rows), end))
        for bxy in ((51.0, -14.0), (64.0, -45.0)) if sx > 0 else ((-51.0, -14.0), (-72.0, -38.0)):
            cf = X.wbox(bxy[0] - 8, bxy[0] + 8, bxy[1] - 8, bxy[1] + 8, 3.0, 16.0); X.sec(cf, X.tbm.copy(X.body('SPKBOX_' + s)))
            w = min(min(ring_min(k, X, cf, (bxy[0], bxy[1], z), (1, 0, 0), (0, 1, 0), 2.0)) for z in (4.5, 6.5, 8.5, 10.3))
            ax = [(round(3.0 + p, 2), round(3.0 + q, 2)) for p, q in k.needle_t(X, [cf], (bxy[0], bxy[1], 3.0), (bxy[0], bxy[1], 16.0), 0.02)]
            print('SPKBOX_%s floor hole (%.0f, %.0f): least wall round it %.2f; solid on its axis (z) %s' % (s, bxy[0], bxy[1], w, ax))
        if k.late():
            print('time'); return


def st_small(k, X):
    for n in ('SPKBOX_L', 'SPKBOX_R'):
        res = []
        for t in (X.body(n), X.body(n + '_v85')):
            rows = []
            for f in t.faces:
                ar = f.area * 100.0
                if ar < 0.3:
                    rows.append((round(ar, 4), tuple(k.r2(k.W(f.pointOnFace), 1))))
            res.append(rows)
        was = set(q[1] for q in res[1])
        fresh = [q for q in res[0] if q[1] not in was]
        print('%-10s faces under 0.3 mm2: now %d, the copy %d; not at a place of the copy: %s' % (n, len(res[0]), len(res[1]), fresh[:30]))


def levels(k, body):
    out = {}
    for f in body.faces:
        if f.geometry.surfaceType != PLN:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); n = k.wv(nv)
        if abs(abs(n[1]) - 1) > 1e-4:
            continue
        y = round(k.W(f.pointOnFace)[1], 3); key = (y, 'up' if n[1] > 0 else 'down')
        out[key] = out.get(key, 0.0) + f.area * 100
    return out


def st_grid(k, X):
    for n in ('SPKBOX_L', 'SPKBOX_R'):
        a = levels(k, X.body(n)); b = levels(k, X.body(n + '_v85'))
        print('%s: level faces, bed = y + 52 (y, looks up or down in the print, bed, off the grid, mm2 now / mm2 in the copy)%s' % (n, ''))
        for key in sorted(set(a) | set(b)):
            na = a.get(key, 0.0); nb = b.get(key, 0.0); h = key[0] + 52.0; off = h - round(h / 0.2) * 0.2
            mark = '' if abs(na - nb) < 0.05 else '   CHANGED'
            print('   y %8.3f %-4s bed %7.3f off %+.3f   %9.2f / %9.2f%s%s' % (key[0], key[1], h, off, na, nb, '   OFF' if abs(off) > 0.002 else '', mark))


def st_chamber(k, X):
    F27 = runpy.run_path('/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/d27_fits.py')
    for sx, s in ((1, 'L'), (-1, 'R')):
        for bn in ('SPKBOX_' + s, 'SPKBOX_%s_v85' % s):
            a, bb, n = F27['chamber'](k, X, X.body(bn), sx, -5.0, -4.0, 52.2)
            if a is None:
                print('%s: no chamber lump (%d lumps)' % (bn, n)); continue
            va = X.vol(a) / 1000.0; dv = X.xv(X.tbm.copy(X.body('SPK_' + s)), a) / 1000.0; ld = X.xv(X.tbm.copy(X.body('LEAD_SPK_' + s)), a) / 1000.0
            print('%-14s air %.3f cm3 (%d lumps); the driver in it %.3f; the lead %.3f; less the driver %.3f; less both %.3f' % (bn, va, n, dv, ld, va - dv, va - dv - ld))


def st_plug(k, X):
    bx = X.body('SPKBOX_L')
    for nm in ('USBA_plug_env', 'USBA_cable_env', 'LEAD_USB_RESP', 'LEAD_SPK_L', 'SPK_L'):
        b = X.body(nm)
        if b is None:
            continue
        r = X.mm.measureMinimumDistance(b, bx)
        print('%-14s to SPKBOX_L %.4f at %s / %s' % (nm, r.value * 10, k.r2(k.W(r.positionOne), 2), k.r2(k.W(r.positionTwo), 2)))
    gb = k.wbb(X, X.body('USBA_plug_env'))
    for g in (0.6, 0.64, 0.7, 1.0, 2.0):
        t = X.wbox(gb[0] - g, gb[1] + g, gb[2] - g, gb[3] + g, gb[4] - g, gb[5] + g)
        print('   the plug\'s box grown %.2f shares %.4f with the box (the copy: %.4f)' % (g, X.xv(t, X.tbm.copy(bx)), X.xv(t, X.tbm.copy(X.body('SPKBOX_L_v85')))))


def _main(stage, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'walls': st_walls, 'small': st_small, 'grid': st_grid, 'chamber': st_chamber, 'plug': st_plug}[stage](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(stage, tag='', **kw):
    L['out']('m17_%s%s.txt' % (stage, ('_' + tag) if tag else ''), _main, stage, **kw)
# END
