# Block 4, its first part: the +x cradle boss's wall round its insert hole after the relief of p43b, measured in its print
# layers (the base plate prints underside down: layers 0.2 from z 0). READ-ONLY (temporary bodies only).
# Level rays from the hole's axis (6.5, -72.5) toward the grommet's ear, 40 directions over +-40 deg about the line to the ear's
# axis (9.0, -78.72); the first solid stretch is the wall. On k.c['b4_plate'] and, for comparison, on the model's FLOOR_PLATE.
# Run: runpy.run_path(D + 'p44d_boss.py')['main']()  -> p44d_boss.txt
import runpy, math

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
AX = (6.5, -72.5)
EAR = (9.0, -78.72)


def _main():
    k = L['load'](); X = k.K(); k.budget(70)
    print(L['stamp'](), 'before', X.state())
    a0 = math.atan2(EAR[1] - AX[1], EAR[0] - AX[0])
    for name, body in (('b4', k.c['b4_plate']), ('model', X.body('FLOOR_PLATE'))):
        c = X.wbox(AX[0] - 6, AX[0] + 6, AX[1] - 6, AX[1] + 6, 6.0, 14.0); X.sec(c, X.tbm.copy(body))
        print(name + ':')
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
            print('   z %.1f: least %s' % (z, best))
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p44d_boss.txt', _main)
