# Block 6, after the change: the cap's way on and off before the display module (D399), the cap's four M3 x 8 on straight keys, and
# the clamps' two M2 x 6 on the bench. READ-ONLY (temporary bodies only).
#   'capway'   the cap set (cap, both clamps, both strip envelopes, the VEML6030 board, the clamps' screws cropped from the screw
#              body) lifted straight up from home by h, against every body present before the display module rides in: the unit
#              less the module (slab, display, carrier, ReSpeaker, main board), the leads, the keep-outs and the screw body
#   'capkeys'  the 2.0 key (k.KEY20: shaft 2.4 x 101, then the short arm's sweep 34.4 x 4) and the key alone (KEY20L) straight
#              down each cap screw's axis from its head, against the same bodies (model bodies, k.line: clearance less the key's
#              radius; 'free' when nothing is met)
#   'clampkeys' a precision Phillips driver (k.MICRO: shaft 3.0 x 60, handle 13 x 97) straight out of each clamp screw's head, cap
#              upside down on the bench: against the cap, the clamps, the strips, the VEML6030 board and the leads on the cap
# Run: runpy.run_path(D + 'p64_b6_ways.py')['main'](stage)  -> p64_<stage>.txt
import runpy, re

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
CAPSET = ['HOUSING_F_cap', 'MIC_CLAMP_L', 'MIC_CLAMP_R', 'MIC_strip_L_env', 'MIC_strip_R_env', 'VEML_env']
MODULE = ('SLAB_frame', 'LCD_', 'RESP_', 'MAIN_')
CAPSCREWS = [(25.91, -37.8), (-25.91, -37.8), (43.36, -32.85), (-43.36, -32.85)]


def fixed(k, X):
    out = []
    for b in k.current(X, leads=False, kos=False):
        n = b.name
        if n in CAPSET or n.startswith(MODULE) or n == 'SCREWS_M2x6_env' or n.startswith('LEAD_'):
            continue
        out.append(b)
    return out


def capway(k, X):
    fx = fixed(k, X)
    print('fixed bodies (%d): %s' % (len(fx), sorted(b.name for b in fx)))
    movers = [X.tbm.copy(X.body(n)) for n in CAPSET]
    for sx in (1, -1):
        c = X.cyl((sx * 15.5, -35.2, 171.5), (sx * 15.5, -35.2, 180.0), 2.6); X.sec(c, X.tbm.copy(X.body('SCREWS_M2x6_env'))); movers.append(c)
    zone = X.wbox(-110, 110, -70, 10, 150, 215)
    fixc = []
    for b in fx:
        t = X.tbm.copy(b)
        if not t.boundingBox.intersects(zone.boundingBox):
            continue
        X.sec(t, X.tbm.copy(zone))
        if t.faces.count:
            fixc.append((b.name, t))
    print('within reach of the cap (z 150..215): %s' % [n for n, t in fixc])
    for h in (0.0, 0.1, 0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 15.0, 20.0, 30.0):
        hit = {}
        for m in movers:
            mv = X.move(X.tbm.copy(m), 0, 0, h)
            for n, t in fixc:
                v = X.xv(mv, t)
                if abs(v) > 0.0005:
                    hit[n] = round(hit.get(n, 0.0) + v, 4)
        print('lift %5.2f: %s' % (h, hit if hit else 'clear'))

def capkeys(k, X):
    fx = fixed(k, X)
    sh = X.body('HOUSING_F_front')
    for x, y in CAPSCREWS:
        c = X.wbox(x - 3, x + 3, y - 3, y + 3, 150, 180); X.sec(c, X.tbm.copy(sh))
        st = k.needle_t(X, [c], (x, y, 150.0), (x, y, 180.0), 0.02)
        cap = k.needle_t(X, [X.tbm.copy(X.body('HOUSING_F_cap'))], (x, y, 165.0), (x, y, 181.0), 0.02)
        print('screw at (%.2f, %.2f): shell along z %s; cap along z %s' % (x, y, [(round(150 + a, 2), round(150 + b, 2)) for a, b in st],
                                                                       [(round(165 + a, 2), round(165 + b, 2)) for a, b in cap]))
        # the head's underside: the lowest shell stretch's lower end on the axis is the hole; take the shell's underside round it
        ring = []
        for dx, dy in ((2.2, 0), (-2.2, 0), (0, 2.2), (0, -2.2)):
            s2 = k.needle_t(X, [c], (x + dx, y + dy, 150.0), (x + dx, y + dy, 180.0), 0.02)
            ring.append([(round(150 + a, 2), round(150 + b, 2)) for a, b in s2])
        print('   shell 2.2 off the axis: %s' % ring)
        z0 = min(r[-1][0] for r in ring if r)  # the flange's underside under the head
        head = z0 - 1.65
        o = (x, y, head)
        print('   head taken from z %.2f (flange underside %.2f, head 1.65 high); key down -z:' % (head, z0))
        print('     KEY20  ', k.fm(k.line(X, o, (0, 0, -1), k.KEY20, fx, st0=1.0, step=2.0)))
        print('     KEY20L ', k.fm(k.line(X, o, (0, 0, -1), k.KEY20L, fx, st0=1.0, step=2.0)))


def clampkeys(k, X):
    bench = [X.body(n) for n in CAPSET + ['LEAD_MIC_L', 'LEAD_MIC_R', 'LEAD_VEML']]
    for sx in (1, -1):
        o = (sx * 15.5, -35.2, 172.7)
        print('clamp screw at x %+.1f, head at z 172.7, driver along -z:' % (sx * 15.5))
        print('   MICRO ', k.fm(k.line(X, o, (0, 0, -1), k.MICRO, bench, st0=0.5, step=1.0)))


def _main(stage):
    k = L['load'](); X = k.K(); k.budget(78)
    print(L['stamp'](), 'before', X.state())
    {'capway': capway, 'capkeys': capkeys, 'clampkeys': clampkeys}[stage](k, X)
    print(L['stamp'](), 'after', X.state())


def main(stage):
    L['out']('p64_%s.txt' % stage, _main, stage)
