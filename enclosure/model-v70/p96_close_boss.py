# The close: the +x cradle boss's wall round its insert hole, read again on the saved version by p44d's method.
# p44d_boss.py cannot run again: it reads block 4's built plate from the cache (k.c['b4_plate']), and the cache went with
# Fusion's restart. This is the same measurement on the model's FLOOR_PLATE alone, compared line by line with the 'b4:'
# lines of p44d's output as block 4 left it (p44d_boss.txt; a copy is kept as p44d_boss_block4.txt).
# READ-ONLY (temporary bodies only).
# Level rays from the hole's axis (6.5, -72.5) toward the grommet's ear, 41 directions over +-40 deg about the line to the
# ear's axis (9.0, -78.72), at every print layer from z 6.4 to 13.0; the first solid stretch is the wall.
# Run: runpy.run_path(D + 'p96_close_boss.py')['main']()  -> p96_boss.txt
import runpy, math

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
AX = (6.5, -72.5)
EAR = (9.0, -78.72)


def _main():
    k = L['load'](); X = k.K(); k.budget(70)
    print(L['stamp'](), 'before', X.state())
    old = {}
    sec = None
    for l in open(D + 'p44d_boss_block4.txt').read().splitlines():
        if l.strip() in ('b4:', 'model:'):
            sec = l.strip()[:-1]
        elif sec == 'b4' and l.strip().startswith('z '):
            z, v = l.strip()[2:].split(': least ')
            old[float(z)] = v
    a0 = math.atan2(EAR[1] - AX[1], EAR[0] - AX[0])
    c = X.wbox(AX[0] - 6, AX[0] + 6, AX[1] - 6, AX[1] + 6, 6.0, 14.0); X.sec(c, X.tbm.copy(X.body('FLOOR_PLATE')))
    n = 0; diff = 0; least = None
    for z in [round(6.4 + 0.2 * i, 1) for i in range(0, 34)]:
        best = None
        for j in range(41):
            a = a0 + math.radians(-40 + 2 * j)
            p0 = (AX[0], AX[1], z); p1 = (AX[0] + 7 * math.cos(a), AX[1] + 7 * math.sin(a), z)
            s = k.needle_t(X, [c], p0, p1, 0.02)
            if not s or s[0][0] < 1.0:
                continue
            w = round(s[0][1] - s[0][0], 3)
            if best is None or w < best[0]:
                best = (w, round(math.degrees(a)), round(s[0][0], 2))
        n += 1
        same = (str(best) == old.get(z))
        diff += 0 if same else 1
        if best and (least is None or best[0] < least[0]):
            least = (best[0], z, best[1])
        print('   z %.1f: least %s%s' % (z, best, '' if same else '   (block 4: %s)' % old.get(z)))
    print('layers read %d, block 4 lines %d, different from block 4: %d' % (n, len(old), diff))
    print('least wall %.3f at z %.1f, direction %d deg' % least)
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p96_boss.txt', _main)
