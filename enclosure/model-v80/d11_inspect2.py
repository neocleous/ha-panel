# Block 1, second look. READ-ONLY (temporary bodies and measurements between model bodies only).
# Stages:
#   tab      the box-top tabs against the screen plate and the shell: needles along y at the tab, and along the screw's line
#   clash    where the model's driver shares volume with its box (AA-A21): the shared lumps and their world boxes
#   polar    the room each box leaves round the driver's axis behind the flange: free radius by angle, for slices along y
#   pocket   the left box's plug pocket: its wall along rays from the driver's axis, and the USB-A plug beyond it
#   chamber  both chambers by the record's method (k4a chambers), as the model stands
#   bay      the shell under and round one driver: needles along y on a grid of x and z (what the ring would meet on the way)
#   boss     the box's four screw columns: wall round each insert hole, and what lies behind
# Run: runpy.run_path(D + 'd11_inspect2.py')['main'](stage)  -> d11_<stage>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
L = runpy.run_path(D + 'v80_lib.py')
AX = 70.5; AZ = 28.0


def ny(k, X, c, x, z, y0, y1):
    return [(round(y0 + a, 3), round(y0 + b, 3)) for a, b in k.needle_t(X, [c], (x, y0, z), (x, y1, z), 0.02)]


def st_tab(k, X):
    for sx, side in ((1, 'L'), (-1, 'R')):
        x0, x1 = sorted((sx * 50.0, sx * 66.0))
        box = (x0, x1, -12.0, 8.0, 70.0, 90.0)
        cs = {n: L['crop'](X, n, box) for n in ('SPKBOX_' + side, 'HOUSING_F_plate', 'HOUSING_F_front')}
        print('side %s, needles along y -12..8 at the tab' % side)
        for x in (sx * 55.0, sx * 58.5, sx * 62.0):
            for z in (76.5, 78.0, 80.0, 82.0, 83.5):
                row = ['%s %s' % (k.sn(n), ny(k, X, c, x, z, -12.0, 8.0)) for n, c in cs.items()]
                print('  x %+6.1f z %5.1f  %s' % (x, z, ' | '.join(r for r in row if '[]' not in r)))
        for n in ('SPKBOX_' + side, 'HOUSING_F_plate'):
            b = X.body(n)
            for h in k.holes_of(b, 0.7, 4.0):
                if x0 <= h['A'][0] <= x1 and 70.0 <= h['A'][2] <= 92.0:
                    print('  %-16s %s' % (n, h))


def st_clash(k, X):
    for side in ('L', 'R'):
        t = X.tbm.copy(X.body('SPK_' + side)); X.sec(t, X.tbm.copy(X.body('SPKBOX_' + side)))
        print('SPK_%s in SPKBOX_%s: %.3f mm3 in %d lumps' % (side, side, X.vol(t), t.lumps.count))
        for v, bb in X.lumps(t):
            print('   %.3f  box %s' % (v, bb))


def free_r(k, X, c, sx, y, th, r0=6.0, r1=30.0):
    cx = sx * AX; ca = math.cos(math.radians(th)); sa = math.sin(math.radians(th))
    s = k.needle_t(X, [c], (cx + r0 * ca, y, AZ + r0 * sa), (cx + r1 * ca, y, AZ + r1 * sa), 0.02)
    return (r0 + s[0][0], r0 + s[0][1]) if s else (None, None)


def st_polar(k, X, step=5):
    k.budget(75)
    for sx, side in ((1, 'L'), (-1, 'R')):
        x0, x1 = sorted((sx * 38.0, sx * 102.0))
        c = L['crop'](X, 'SPKBOX_' + side, (x0, x1, -34.0, -2.0, -4.0, 62.0))
        print('SPKBOX_%s: free radius round the axis (x %+.1f, z %.1f); angle 0 = +x, 90 = up; the ten tightest angles per slice' % (side, sx * AX, AZ))
        for y in (-5.0, -8.0, -11.0, -14.0, -16.0, -17.0, -18.0, -19.0, -20.0, -22.0, -24.0, -26.0, -28.0, -28.7, -29.0, -29.5, -30.5):
            rows = []
            for th in range(0, 360, step):
                a, b = free_r(k, X, c, sx, y, th)
                rows.append((a if a is not None else 99.0, th))
            rows.sort()
            wide = [th for r, th in sorted(rows, key=lambda q: q[1]) if r >= 18.55]
            print('  y %6.1f  least %.2f at %d deg; tightest: %s' % (y, rows[0][0], rows[0][1], ', '.join('%d:%.2f' % (th, r) for r, th in rows[:10])))
            print('            angles free to 18.55 or more: %s' % ranges(wide, step))
            if k.late():
                print('time used up'); return


def ranges(a, step):
    if not a:
        return 'none'
    out = []; s = a[0]; p = a[0]
    for v in a[1:]:
        if v != p + step:
            out.append((s, p)); s = v
        p = v
    out.append((s, p))
    return ', '.join('%d..%d' % q for q in out)


def st_pocket(k, X):
    c = L['crop'](X, 'SPKBOX_L', (38.0, 102.0, -52.0, -2.0, -4.0, 62.0))
    pl = X.tbm.copy(X.body('USBA_plug_env')); cb = X.tbm.copy(X.body('LEAD_USB_RESP'))
    print('USBA_plug_env box %s; LEAD_USB_RESP box %s' % (k.wbb(X, X.body('USBA_plug_env')), k.wbb(X, X.body('LEAD_USB_RESP'))))
    for y in (-18.0, -19.0, -20.0, -20.5, -21.0, -22.0, -24.0, -26.0, -28.0, -28.7, -29.5, -31.0):
        print('  y %.1f: angle, box stretches (radius from..to), plug, USB lead' % y)
        for th in range(185, 266, 5):
            ca = math.cos(math.radians(th)); sa = math.sin(math.radians(th))
            p0 = (AX + 6.0 * ca, y, AZ + 6.0 * sa); p1 = (AX + 34.0 * ca, y, AZ + 34.0 * sa)
            sb = [(round(6 + a, 2), round(6 + b, 2)) for a, b in k.needle_t(X, [c], p0, p1, 0.02)]
            sp = [(round(6 + a, 2), round(6 + b, 2)) for a, b in k.needle_t(X, [pl], p0, p1, 0.02)]
            sc = [(round(6 + a, 2), round(6 + b, 2)) for a, b in k.needle_t(X, [cb], p0, p1, 0.02)]
            if sb and sb[0][0] < 21.0:
                print('     %3d  box %s  plug %s  lead %s' % (th, sb, sp, sc))
    r = X.mm.measureMinimumDistance(X.body('USBA_plug_env'), X.body('SPKBOX_L'))
    print('USBA_plug_env to SPKBOX_L, body to body: %.4f at %s / %s' % (r.value * 10, k.r2(k.W(r.positionOne), 3), k.r2(k.W(r.positionTwo), 3)))
    r = X.mm.measureMinimumDistance(X.body('LEAD_USB_RESP'), X.body('SPKBOX_L'))
    print('LEAD_USB_RESP to SPKBOX_L, body to body: %.4f at %s / %s' % (r.value * 10, k.r2(k.W(r.positionOne), 3), k.r2(k.W(r.positionTwo), 3)))


def st_chamber(k, X):
    for n, v in k.K4NS['chambers'](X).items():
        print(n, v)


def st_bay(k, X, sx=1):
    x0, x1 = sorted((sx * 40.0, sx * 100.0))
    sh = L['crop'](X, 'HOUSING_F_front', (x0, x1, -6.0, 8.0, 0.0, 60.0))
    fp = L['crop'](X, 'FLOOR_PLATE', (x0, x1, -6.0, 8.0, -1.0, 12.0))
    zs = (2.9, 3.3, 3.8, 4.3, 4.8, 5.15, 6.5, 7.85, 8.5, 9.5, 11.0, 14.0, 20.0, 28.0, 36.0, 44.0, 47.0, 48.15, 49.5, 50.85, 51.5, 53.0, 56.0)
    xs = (47.0, 48.0, 50.0, 52.5, 55.0, 58.5, 64.0, 70.5, 77.0, 82.5, 86.0, 88.5, 91.0, 93.0, 94.5)
    print('shell (and base plate, marked P): first solid y, looking from behind (needle y -6 -> +8); x across, z down the page')
    print('   z    ' + ' '.join('%6.1f' % (sx * x) for x in xs))
    for z in reversed(zs):
        row = []
        for x in xs:
            s = ny(k, X, sh, sx * x, z, -6.0, 8.0)
            p = ny(k, X, fp, sx * x, z, -6.0, 8.0) if z < 12.0 else []
            v = '%6.2f' % s[0][0] if s else '   -  '
            if p:
                v = ('P%5.2f' % p[0][1]) if not s or p[0][0] < s[0][0] else v
            row.append(v)
        print(' %5.2f  %s' % (z, ' '.join(row)))
    print('the same, the last solid y of the shell (its outer face):')
    for z in reversed(zs):
        row = []
        for x in xs:
            s = ny(k, X, sh, sx * x, z, -6.0, 8.0)
            row.append('%6.2f' % s[-1][1] if s else '   -  ')
        print(' %5.2f  %s' % (z, ' '.join(row)))


def st_boss(k, X):
    for sx, side in ((1, 'L'), (-1, 'R')):
        x0, x1 = sorted((sx * 38.0, sx * 102.0))
        c = L['crop'](X, 'SPKBOX_' + side, (x0, x1, -20.0, -2.0, -4.0, 62.0))
        for bx, bz in ((52.75, 10.25), (88.25, 10.25), (52.75, 45.75), (88.25, 45.75)):
            print('SPKBOX_%s column at (%+.2f, %.2f): solid along y on the axis %s' % (side, sx * bx, bz, ny(k, X, c, sx * bx, bz, -20.0, -2.0)))
            for y in (-3.3, -4.5, -5.0, -5.5, -6.0, -7.0, -8.0, -9.0, -9.6, -10.0, -11.0, -11.6, -12.5):
                walls = []
                for th in range(0, 360, 30):
                    ca = math.cos(math.radians(th)); sa = math.sin(math.radians(th))
                    s = k.needle_t(X, [c], (sx * bx + 0.0 * ca, y, bz + 0.0 * sa), (sx * bx + 9.0 * ca, y, bz + 9.0 * sa), 0.02)
                    s = [q for q in s if q[1] > 1.9]
                    walls.append(round(s[0][1] - max(s[0][0], 2.0), 2) if s else 0.0)
                print('    y %6.1f  plastic outward from the hole radius 2.0, every 30 deg from +x: %s' % (y, walls))


def _main(stage, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'tab': st_tab, 'clash': st_clash, 'polar': st_polar, 'pocket': st_pocket, 'chamber': st_chamber, 'bay': st_bay, 'boss': st_boss}[stage](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(stage, tag=None, **kw):
    L['out']('d11_%s.txt' % (tag or stage), _main, stage, **kw)
# END
