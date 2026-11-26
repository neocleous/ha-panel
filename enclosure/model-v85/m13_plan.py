# Block 1c (plan, temporary bodies) and block 2 (the build's bodies): the boxes' margins. NOTHING IS PUT INTO THE DOCUMENT here.
# The aim-2 envelope E of each driver: the driver as the model draws it (m12_driver.zones: basket 40 -> 37.5, the band 37.5, the
# magnet 32, the connector's envelope up) grown 1.0 all round, and its rear end (magnet and connector) carried 2.0 back. A box keeps
# 1.0 to its driver all round and 2.0 behind when nothing of it lies in E.
#   cut      what of each box lies in E today: lumps, volume, world box; and on radial needles from the driver's axis through each
#            lump's place: the box's solid there, today and with E taken out (mm from the axis), so where a wall would thin
# Run: L.checked('m13_plan.py', sha)['main'](stage, tag)  -> m13_<stage>_<tag>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/box_margins_v85/'
L = runpy.run_path(D + 'm00_lib.py')
AX = 70.5; AZ = 28.0; Y_BACK = -3.8; Y_REAR = -28.8
G = 1.0; BEHIND = 2.0


def envelope(k, X, sx, g=G, behind=BEHIND):
    cx = sx * AX
    e = X.cyl((cx, Y_BACK + 0.3, AZ), (cx, Y_REAR + 13.0, AZ), 20.0 + g, 18.75 + g)            # basket, from 0.3 in front of the flange's back
    X.uni(e, X.cyl((cx, Y_REAR + 13.0, AZ), (cx, Y_REAR + 10.0, AZ), 18.75 + g))                 # the band 37.5
    X.uni(e, X.cyl((cx, Y_REAR + 10.0, AZ), (cx, Y_REAR - g, AZ), 16.0 + g))                     # magnet
    X.uni(e, X.cyl((cx, Y_REAR, AZ), (cx, Y_REAR - behind, AZ), 16.0))                           # behind the magnet's rear face
    X.uni(e, X.wbox(cx - 16.0 - g, cx + 16.0 + g, Y_REAR + 10.0 + g, Y_REAR - g, AZ - g, AZ + 18.25 + g))   # connector
    X.uni(e, X.wbox(cx - 16.0, cx + 16.0, Y_REAR, Y_REAR - behind, AZ, AZ + 18.25))              # behind the connector's rear face
    return e


def st_cut(k, X, sides=('L', 'R')):
    k.budget(72)
    for s in sides:
        sx = 1 if s == 'L' else -1; cx = sx * AX
        B = X.tbm.copy(X.body('SPKBOX_' + s))
        e = envelope(k, X, sx)
        c = X.tbm.copy(B); X.sec(c, X.tbm.copy(e))
        print('SPKBOX_%s in E: %.3f mm3 in %d lumps' % (s, X.vol(c), c.lumps.count))
        nb = X.tbm.copy(B); X.dif(nb, X.tbm.copy(e))
        for v, bb in k.lumps(c):
            if v is None or bb is None:
                print('   lump %s %s' % (v, bb)); continue
            q = ((bb[0] + bb[1]) / 2.0, (bb[2] + bb[3]) / 2.0, (bb[4] + bb[5]) / 2.0)
            dx = q[0] - cx; dz = q[2] - AZ; r = math.hypot(dx, dz)
            u = (dx / r, 0.0, dz / r) if r > 0.01 else (0.0, 0.0, 1.0)
            p0 = (cx + u[0] * 10.0, q[1], AZ + u[2] * 10.0); p1 = (cx + u[0] * 30.0, q[1], AZ + u[2] * 30.0)
            a = [(round(10 + x, 2), round(10 + y, 2)) for x, y in k.needle_t(X, [B], p0, p1, 0.02)]
            b = [(round(10 + x, 2), round(10 + y, 2)) for x, y in k.needle_t(X, [nb], p0, p1, 0.02)]
            ya = [(round(q[1] - x, 2), round(q[1] - y, 2)) for x, y in k.needle_t(X, [B], (q[0], q[1], q[2]), (q[0], q[1] - 12.0, q[2]), 0.02)]
            yb = [(round(q[1] - x, 2), round(q[1] - y, 2)) for x, y in k.needle_t(X, [nb], (q[0], q[1], q[2]), (q[0], q[1] - 12.0, q[2]), 0.02)]
            print('   lump %8.3f  box %s  r %.2f at %.0f deg\n      radial (from the axis): today %s; E out %s\n      back along -y from y %.2f: today %s; E out %s' % (
                v, bb, r, math.degrees(math.atan2(dz, dx)), a, b, q[1], ya, yb))
            if k.late():
                print('time'); return


def _main(stage, **kw):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'cut': st_cut}[stage](k, X, **kw)
    print(L['stamp'](), 'after', X.state())


def main(stage, tag='', **kw):
    L['out']('m13_%s%s.txt' % (stage, ('_' + tag) if tag else ''), _main, stage, **kw)
# END
