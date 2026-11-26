# Block 1c (the plan, on temporary bodies) and block 2 (the build): the two speaker boxes' margins. Builds temporary bodies and keeps
# them in the library's cache k.c; NOTHING IS PUT INTO THE DOCUMENT here (m16_put.py does that).
# World mm: x + = viewer's left, y + toward the screen, z up. Side 'L' x > 0. A box prints rear face down: bed = y + 52.
# Sources: the driver as the model draws it (D481; ../model-v80/d20_build.py); the aims (D517); the readings of block 1
# (m10_stack_*.txt, m12_*.txt, m13_cut_v85.txt, m14_*.txt). Figures marked (c) below are this pass's choices under D150.
#   E        the aim-2 envelope: the driver grown 1.0 all round (basket 40 -> 37.5 at y -15.8; the band 37.5 to y -18.8, and 1.0 behind
#            it; the magnet 32 to y -28.8; the connector's envelope up), and its rear end carried 2.0 back (to y -30.8)
#   build    each box: from the hidden copy SPKBOX_<s>_v85 where it exists, else the body itself (so a second run after the put
#            builds the same body), in this order:
#            1. walls added where E would open a box into a pocket (c): left, the plug pocket's corner filled to 18.5 from the
#               driver's axis from y -31.4 forward to its end wall, on a lead-in of 26 deg from y -35.7 (16.4 -> 18.5), and the end
#               wall thickened from y -20.8 to -21.2 within 20.0 of the axis; right, the empty pocket's front face from y -31.0 back
#               to -32.4 within 17.5 of the axis
#            2. the outer driver columns 0.2 longer (rear ends y -12.6 -> -12.8, bed 39.2) (c); the floor bosses with 1.0 over their
#               holes 0.3 taller (z 11.2 -> 11.5) (c); the right clip block 0.5 out round its pilot (x -50.5 -> -51.0, r 3.35) (c)
#            3. E taken out
#            4. the holes: the eight driver insert holes to y -11.6 (bed 40.4; the 2.5 holes behind the outer pair go into them);
#               the four floor insert holes to z 10.5; the holder's pilot to x 46.5; the left clip's pilot to x 49.5, the right's
#               to x -50.0
#   check    the new bodies against the model: volume, lumps, E inside them, the driver's zones (m12), the plug, the leads, the
#            chamber (d27's method), the holes' depths and the walls beyond them (needles), what they share with every body of
#            the unit, the level faces that are new and their bed heights
# Run: L.checked('m15_build.py', sha)['main'](stage, tag, **kw)  -> m15_<stage>_<tag>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/box_margins_v85/'
L = runpy.run_path(D + 'm00_lib.py')
AX = 70.5; AZ = 28.0; HALF = 17.75
Y_BACK = -3.8; Y_REAR = -28.8
PLN = adsk.core.SurfaceTypes.PlaneSurfaceType


def screws(sx):
    return [(sx * (AX + a * HALF), AZ + b * HALF) for a in (-1, 1) for b in (-1, 1)]


def E(k, X, sx, g=1.0, behind=2.0):
    cx = sx * AX
    e = X.cyl((cx, Y_BACK + 0.3, AZ), (cx, Y_REAR + 13.0, AZ), 20.0 + g, 18.75 + g)              # basket
    X.uni(e, X.cyl((cx, Y_REAR + 13.0, AZ), (cx, Y_REAR + 10.0 - g, AZ), 18.75 + g))               # band, and 1.0 behind it
    X.uni(e, X.cyl((cx, Y_REAR + 10.0, AZ), (cx, Y_REAR - g, AZ), 16.0 + g))                       # magnet
    X.uni(e, X.cyl((cx, Y_REAR, AZ), (cx, Y_REAR - behind, AZ), 16.0))                             # behind the magnet
    X.uni(e, X.wbox(cx - 16.0 - g, cx + 16.0 + g, Y_REAR + 10.0 + g, Y_REAR - g, AZ - g, AZ + 18.25 + g))   # connector
    X.uni(e, X.wbox(cx - 16.0, cx + 16.0, Y_REAR, Y_REAR - behind, AZ, AZ + 18.25))                # behind the connector
    return e


def src(X, name):
    return X.body(name + '_v85') or X.body(name)


def build(k, X, sx):
    s = 'L' if sx > 0 else 'R'; cx = sx * AX
    t = X.tbm.copy(src(X, 'SPKBOX_' + s))
    # 1. walls where E would open the box into a pocket
    if sx > 0:
        f = X.cyl((cx, -31.4, AZ), (cx, -20.7, AZ), 18.5)
        X.uni(f, X.cyl((cx, -35.7, AZ), (cx, -31.4, AZ), 16.4, 18.5))
        X.sec(f, X.wbox(44.0, 55.65, -52.0, -20.8, 3.8, 20.7)); X.uni(t, f)
        f2 = X.cyl((cx, -21.2, AZ), (cx, -20.7, AZ), 20.0)
        X.sec(f2, X.wbox(40.0, 55.65, -21.2, -20.8, 3.8, 20.7)); X.uni(t, f2)
    else:
        f = X.cyl((cx, -32.4, AZ), (cx, -30.9, AZ), 17.5)
        X.sec(f, X.wbox(-64.0, -46.0, -32.4, -31.0, 3.8, 16.0)); X.uni(t, f)
    # 2. columns, bosses, the right clip block
    for px, pz in screws(sx):
        if abs(abs(px) - (AX + HALF)) < 0.01:
            X.uni(t, X.cyl((px, -12.8, pz), (px, -12.5, pz), 4.0))
    for bx, by in ((64.0, -45.0),) if sx > 0 else ((-72.0, -38.0),):
        X.uni(t, X.cyl((bx, by, 11.1), (bx, by, 11.5), 4.0))
    if sx < 0:
        X.uni(t, X.cyl((-50.4, -9.45, 41.0), (-51.0, -9.45, 41.0), 3.35))
    # 3. E out
    X.dif(t, E(k, X, sx))
    # 4. holes
    for px, pz in screws(sx):
        X.dif(t, X.cyl((px, -11.6, pz), (px, -10.5, pz), 2.0))
    for bx, by in ((51.0, -14.0), (64.0, -45.0)) if sx > 0 else ((-51.0, -14.0), (-72.0, -38.0)):
        X.dif(t, X.cyl((bx, by, 10.1), (bx, by, 10.5), 2.0))
    if sx > 0:
        X.dif(t, X.cyl((45.25, -7.35, 57.6), (46.5, -7.35, 57.6), 1.35))
        X.dif(t, X.cyl((49.15, -9.45, 35.0), (49.5, -9.45, 35.0), 1.35))
    else:
        X.dif(t, X.cyl((-49.15, -9.45, 41.0), (-50.0, -9.45, 41.0), 1.35))
    return t


def st_build(k, X, sides=('L', 'R')):
    k.budget(70)
    for sx, s in ((1, 'L'), (-1, 'R')):
        if s not in sides:
            continue
        t = build(k, X, sx)
        k.c['bm_box_' + s] = t
        o = src(X, 'SPKBOX_' + s)
        print('bm_box_%s %.3f mm3, lumps %d, faces %d | built from %s %.3f mm3, lumps %d, faces %d' % (
            s, X.vol(t), t.lumps.count, t.faces.count, o.name, o.volume * 1000, o.lumps.count, o.faces.count))
        a = X.tbm.copy(t); X.dif(a, X.tbm.copy(o)); b = X.tbm.copy(o); X.dif(b, X.tbm.copy(t))
        print('   added %.3f in %d lumps: %s' % (X.vol(a), a.lumps.count, X.lumps(a)[:14]))
        print('   removed %.3f in %d lumps: %s' % (X.vol(b), b.lumps.count, X.lumps(b)[:24]))


def dist(k, X, a, b):
    r = X.mm.measureMinimumDistance(a, b)
    return r.value * 10.0, k.r2(k.W(r.positionOne), 2), k.r2(k.W(r.positionTwo), 2)


def st_check(k, X, sides=('L', 'R'), parts=('drv', 'plug', 'chamber', 'holes', 'walls')):
    k.budget(72)
    Z = runpy.run_path(D + 'm12_driver.py')
    F27 = runpy.run_path('/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/d27_fits.py')
    for sx, s in ((1, 'L'), (-1, 'R')):
        if s not in sides:
            continue
        t = k.c['bm_box_' + s]; cx = sx * AX
        print('bm_box_%s: %.3f mm3, lumps %d; E inside it %.4f' % (s, X.vol(t), t.lumps.count, X.xv(E(k, X, sx), X.tbm.copy(t))))
        if 'drv' in parts:
            for nm, z in Z['zones'](k, X, sx).items():
                if nm == 'ring':
                    continue
                d, p, q = dist(k, X, z, t)
                print('   driver %-10s to the box %.4f  %s / %s' % (nm, d, p, q))
            d, p, q = dist(k, X, X.body('SPK_' + s), t)
            print('   SPK_%s (the model\'s driver) to the box %.4f  %s / %s' % (s, d, p, q))
            rr = X.cyl((cx, Y_REAR + 0.01, AZ), (cx, Y_REAR, AZ), 16.0); X.uni(rr, X.wbox(cx - 16.0, cx + 16.0, Y_REAR + 0.01, Y_REAR, AZ, AZ + 18.25))
            for dy in (1.99, 2.0, 2.1):
                m = X.tbm.copy(rr); X.move(m, 0.0, -dy, 0.0)
                print('   the rear face (magnet and connector) moved %.2f back: shares %.4f with the box' % (dy, X.xv(m, X.tbm.copy(t))))
        if 'plug' in parts and sx > 0:
            for nm in ('USBA_plug_env', 'USBA_cable_env', 'LEAD_USB_RESP', 'LEAD_SPK_L', 'FLOOR_PLATE', 'RADAR_HOLDER', 'TOUCH_CLIP_L'):
                b = X.body(nm)
                if b is not None:
                    d, p, q = dist(k, X, b, t)
                    print('   %-16s to the box %.4f  %s / %s' % (nm, d, p, q))
            o = X.tbm.copy(src(X, 'SPKBOX_L')); X.dif(o, X.tbm.copy(t))
            n = X.tbm.copy(t); X.dif(n, X.tbm.copy(src(X, 'SPKBOX_L')))
            pl = X.body('USBA_plug_env')
            print('   the plug to what was added %.4f; the end wall\'s face: the plug to the box at its nose %s' % (
                dist(k, X, pl, n)[0] if n.faces.count else -1, dist(k, X, pl, t)))
        if 'plug' in parts and sx < 0:
            for nm in ('LEAD_SPK_R', 'FLOOR_PLATE', 'TOUCH_CLIP_R'):
                d, p, q = dist(k, X, X.body(nm), t)
                print('   %-16s to the box %.4f  %s / %s' % (nm, d, p, q))
        if 'chamber' in parts:
            a, bb, n = F27['chamber'](k, X, t, sx, -5.0, -4.0, 52.2)
            if a is None:
                print('   chamber: no lump (%d lumps)' % n)
            else:
                va = X.vol(a) / 1000.0; dv = X.xv(X.tbm.copy(X.body('SPK_' + s)), a) / 1000.0
                ld = X.xv(X.tbm.copy(X.body('LEAD_SPK_' + s)), a) / 1000.0
                a0, bb0, n0 = F27['chamber'](k, X, X.tbm.copy(src(X, 'SPKBOX_' + s)), sx, -5.0, -4.0, 52.2)
                v0 = X.vol(a0) / 1000.0 - X.xv(X.tbm.copy(X.body('SPK_' + s)), a0) / 1000.0
                print('   chamber: air %.3f cm3, the driver in it %.3f, the lead %.3f: %.3f less the driver (%.3f less both); the box it was built from %.3f less the driver' % (
                    va, dv, ld, va - dv, va - dv - ld, v0))
        if 'holes' in parts:
            rows = []
            for px, pz in screws(sx):
                rows.append(('driver hole (%.2f, %.2f)' % (px, pz), (px, -3.0, pz), (px, -16.0, pz)))
            for bx, by in ((51.0, -14.0), (64.0, -45.0)) if sx > 0 else ((-51.0, -14.0), (-72.0, -38.0)):
                rows.append(('floor hole (%.0f, %.0f)' % (bx, by), (bx, by, 3.0), (bx, by, 16.0)))
            rows.append(('clip pilot', (sx * 42.0, -9.45, 35.0 if sx > 0 else 41.0), (sx * 56.0, -9.45, 35.0 if sx > 0 else 41.0)))
            if sx > 0:
                rows.append(('holder pilot', (38.5, -7.35, 57.6), (52.0, -7.35, 57.6)))
            for lab, p0, p1 in rows:
                st = k.needle_t(X, [t], p0, p1, 0.02)
                print('   %-28s on its axis from %s: solid %s' % (lab, k.r2(p0, 2), st))
        if 'walls' in parts:
            for ang in (200, 210, 215, 220, 225):
                if sx < 0:
                    continue
                r = math.radians(ang); d = (math.cos(r), 0.0, math.sin(r))
                for y in (-34.0, -32.5, -31.0, -30.0, -27.0, -24.0, -21.0, -20.5, -20.0):
                    st = k.needle_t(X, [t], (cx + 12.0 * d[0], y, AZ + 12.0 * d[2]), (cx + 24.0 * d[0], y, AZ + 24.0 * d[2]), 0.02)
                    rows = [(round(12.0 + a, 2), round(12.0 + b, 2)) for a, b in st]
                    print('   left pocket corner, radial at %d deg, y %.1f: solid %s (from the axis)' % (ang, y, rows))
            if sx < 0:
                for x in (-64.0, -62.0, -60.0, -58.0, -56.0):
                    for z in (12.0, 14.0, 15.5):
                        st = k.needle_t(X, [t], (x, -26.0, z), (x, -40.0, z), 0.02)
                        print('   right pocket front wall at x %.1f, z %.1f, along -y from y -26: solid %s' % (x, z, [(round(-26.0 - a, 2), round(-26.0 - b, 2)) for a, b in st]))
        if k.late():
            print('time'); return


def st_share(k, X, sides=('L', 'R')):
    """What the new box shares with every body of the unit, beside what the box in the model shares."""
    k.budget(72)
    for sx, s in ((1, 'L'), (-1, 'R')):
        if s not in sides:
            continue
        t = k.c['bm_box_' + s]; o = src(X, 'SPKBOX_' + s); tb = k.wbb(X, o)
        for b in k.current(X, leads=True, kos=True):
            if b.name.startswith('SPKBOX_'):
                continue
            q = k.wbb(X, b)
            if q[1] < tb[0] - 1 or q[0] > tb[1] + 1 or q[3] < tb[2] - 1 or q[2] > tb[3] + 1 or q[5] < tb[4] - 1 or q[4] > tb[5] + 1:
                continue
            parts = k.parts(X, b.name)
            vn = sum(X.xv(X.tbm.copy(t), p) for p in parts); vo = sum(X.xv(X.tbm.copy(o), p) for p in parts)
            if abs(vn) > 0.0005 or abs(vo) > 0.0005:
                print('   bm_box_%s | %-22s %10.4f  (the box in the model: %10.4f)' % (s, b.name, vn, vo))
            if k.late():
                print('time'); return
        print('   bm_box_%s: done' % s)


def st_grid(k, X, sides=('L', 'R')):
    """Level faces (square to y) of the new box that the box in the model does not have: bed height, off the grid, look, area."""
    for sx, s in ((1, 'L'), (-1, 'R')):
        if s not in sides:
            continue
        t = k.c['bm_box_' + s]; o = src(X, 'SPKBOX_' + s)
        def lv(body):
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
        a = lv(t); b = lv(o)
        print('bm_box_%s: level faces (y, looks up or down in the print, bed height, off the grid, mm2 new / mm2 in the model):' % s)
        for key in sorted(set(a) | set(b)):
            na = a.get(key, 0.0); nb = b.get(key, 0.0)
            if abs(na - nb) < 0.05:
                continue
            h = key[0] + 52.0; off = h - round(h / 0.2) * 0.2
            print('   y %8.3f %-4s bed %7.3f off %+.3f   %9.2f / %9.2f' % (key[0], key[1], h, off, na, nb))


def _main(stage, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'build': st_build, 'check': st_check, 'share': st_share, 'grid': st_grid}[stage](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(stage, tag='', **kw):
    L['out']('m15_%s%s.txt' % (stage, ('_' + tag) if tag else ''), _main, stage, **kw)
# END
