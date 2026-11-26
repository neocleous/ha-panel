# Block 2: checks on the drivers' seat, before the put (on d20's temporary bodies, pre=True) and after it (on the model).
# READ-ONLY but where a stage says it adds TMP_ bodies (deleted again before it returns).
#   diff     each changed body against version 79's (the model's body before the put, its hidden _v79 copy after it): what was
#            added and what was removed, as lumps with their world boxes
#   walls    the wall round each insert hole of the eight driver columns (12 directions, stations along the hole), the plastic
#            behind each hole's end, and the wall round each clip pilot (12 directions, stations along it)
#   small    flat faces under 0.3 mm2 in each changed printed body, new against old
# Run: runpy.run_path(D + 'd25_checks.py')['main'](stage, pre=True|False)  -> d25_<stage>_<pre|put>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
L = runpy.run_path(D + 'v80_lib.py')
B20 = runpy.run_path(D + 'd20_build.py')
AX = 70.5; AZ = 28.0
KEYS = {'HOUSING_F_front': 'ds_shell', 'SPKBOX_L': 'ds_box_L', 'SPKBOX_R': 'ds_box_R', 'TOUCH_CLIP_L': 'ds_clip_L', 'TOUCH_CLIP_R': 'ds_clip_R',
        'SPK_L': 'ds_spk_L', 'SPK_R': 'ds_spk_R', 'DRV_screw_heads_env': 'ds_heads', 'LEAD_SPK_L': 'ds_lead_L', 'LEAD_SPK_R': 'ds_lead_R'}


def new(k, X, name, pre):
    return X.tbm.copy(k.c[KEYS[name]]) if pre else X.tbm.copy(X.body(name))


def old(k, X, name, pre):
    return X.tbm.copy(X.body(name)) if pre else X.tbm.copy(X.body(name + '_v79'))


def st_diff(k, X, pre, names=None):
    for n in (names or list(KEYS)):
        a = new(k, X, n, pre); b = old(k, X, n, pre)
        add = X.tbm.copy(a); X.dif(add, X.tbm.copy(b))
        rem = X.tbm.copy(b); X.dif(rem, X.tbm.copy(a))
        la = X.lumps(add) if add.faces.count else []; lr = X.lumps(rem) if rem.faces.count else []
        print('%-20s new %.3f, old %.3f; added %.3f in %d lumps, removed %.3f in %d lumps' % (n, X.vol(a), X.vol(b), sum(q[0] or 0 for q in la), len(la), sum(q[0] or 0 for q in lr), len(lr)))
        for tag, ls in (('+', la), ('-', lr)):
            for v, bb in ls[:14]:
                print('      %s %9.3f  %s' % (tag, v, bb))
            if len(ls) > 14:
                print('      %s ... %d more, the largest of them %.3f' % (tag, len(ls) - 14, ls[14][0]))


def ring_min(k, X, c, p, e1, e2, r0, reach=9.0):
    """Least plastic outward from radius r0 round point p, in 12 directions in the plane (e1, e2); None where a direction is open."""
    out = []
    for j in range(12):
        a = math.radians(30 * j)
        d = tuple(e1[i] * math.cos(a) + e2[i] * math.sin(a) for i in range(3))
        s = k.needle_t(X, [c], k.along(p, d, r0 - 0.3), k.along(p, d, reach), 0.02)
        s = [q for q in s if q[0] <= 0.35 and q[1] > 0.32]
        out.append(round(s[0][1] - 0.3, 2) if s else 0.0)
    return out


def st_walls(k, X, pre):
    k.budget(75)
    for sx, side in ((1, 'L'), (-1, 'R')):
        bx = new(k, X, 'SPKBOX_' + side, pre)
        a, b = sorted((sx * 38.0, sx * 102.0))
        c = X.wbox(a, b, -22.0, -2.0, 0.0, 60.0); X.sec(c, bx)
        for px, pz in B20['screws'](sx):
            lo = (99.0, None); stop = (99.0, None)
            for y in [-4.05 - 0.3 * i for i in range(0, 23)]:
                w = ring_min(k, X, c, (px, y, pz), (1, 0, 0), (0, 0, 1), 2.0)
                m = min(w)
                if y > -5.0:
                    stop = min(stop, (m, y))
                else:
                    lo = min(lo, (m, y))
            ax = [(round(-22.0 + p, 2), round(-22.0 + q, 2)) for p, q in k.needle_t(X, [c], (px, -22.0, pz), (px, -2.0, pz), 0.02)]
            print('SPKBOX_%s column (%+.2f, %.2f): least wall round the insert hole in the stop %.2f (y %.2f), below it %.2f (y %.2f); solid on the axis %s' % (
                side, px, pz, stop[0], stop[1], lo[0], lo[1], ax))
        py = B20['CLIP_Y']; pzc = B20['CLIP_Z']
        cc = X.wbox(*sorted((sx * 40.0, sx * 56.0)), -16.0, -2.0, 26.0, 50.0); X.sec(cc, new(k, X, 'SPKBOX_' + side, pre))
        rows = []
        for xs in (43.7, 44.5, 45.5, 46.5, 47.5, 48.5, 49.1):
            w = ring_min(k, X, cc, (sx * xs, py, pzc), (0, 1, 0), (0, 0, 1), 1.35)
            rows.append('x %.1f: least %.2f (front %.2f, rear %.2f)' % (sx * xs, min(w), w[0], w[6]))
        end = [(round(p, 2), round(q, 2)) for p, q in k.needle_t(X, [cc], (sx * 43.0, py, pzc), (sx * 56.0, py, pzc), 0.02)]
        print('SPKBOX_%s clip pilot at y %.2f: %s; solid along its axis from x %.1f: %s' % (side, py, '; '.join(rows), sx * 43.0, end))
        cl = new(k, X, 'TOUCH_CLIP_' + side, pre)
        s1 = [(round(-14.0 + p, 2), round(-14.0 + q, 2)) for p, q in k.needle_t(X, [cl], (sx * 42.0, -14.0, pzc), (sx * 42.0, 4.0, pzc), 0.02)]
        s2 = [(round(-14.0 + p, 2), round(-14.0 + q, 2)) for p, q in k.needle_t(X, [cl], (sx * 44.3, -14.0, pzc), (sx * 44.3, 4.0, pzc), 0.02)]
        print('TOUCH_CLIP_%s along y at x %.1f (through the slot): %s; at x %.1f (the tongue): %s' % (side, sx * 42.0, s1, sx * 44.3, s2))
        if k.late():
            print('time'); return


def st_small(k, X, pre):
    for n in ('HOUSING_F_front', 'SPKBOX_L', 'SPKBOX_R', 'TOUCH_CLIP_L', 'TOUCH_CLIP_R'):
        res = []
        for t in (new(k, X, n, pre), old(k, X, n, pre)):
            rows = []
            for f in t.faces:
                ar = f.area * 100.0
                if ar < 0.3:
                    rows.append((round(ar, 4), tuple(k.r2(k.W(f.pointOnFace), 1))))
            res.append(rows)
        was = set(q[1] for q in res[1])
        fresh = [q for q in res[0] if q[1] not in was]
        print('%-16s faces under 0.3 mm2: new %d, old %d; not at an old place: %s' % (n, len(res[0]), len(res[1]), fresh[:20]))


def _main(stage, pre, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'diff': st_diff, 'walls': st_walls, 'small': st_small}[stage](k, X, pre, **kw)
    print(L['stamp'](), 'after', X.state())


def main(stage, pre=True, **kw):
    L['out']('d25_%s_%s.txt' % (stage, 'pre' if pre else 'put'), _main, stage, pre, **kw)
# END
