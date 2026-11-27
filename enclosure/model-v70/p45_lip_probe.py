# Block 4, AA-C7: the slab's front (glass side, its print's bed at d 0) near its two x ends: where the slab's material begins
# along d, on a grid of (x, Zd), from needles along d. READ-ONLY (temporary bodies only).
# Slab frame: x = world x, d = depth behind the glass's front, Zd = design z (height along the screen).
# Run: runpy.run_path(D + 'p45_lip_probe.py')['main']()  -> p45_lip_probe.txt
import runpy

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def _main():
    k = L['load'](); X = k.K(); k.budget(78)
    print(L['stamp'](), 'before', X.state())
    S = X.body('SLAB_frame')
    for side, xs in (('+x', [97.0 + 0.5 * i for i in range(13)]), ('-x', [-103.0 + 0.5 * i for i in range(15)])):
        for zr in ([-89.5 + 1.0 * i for i in range(8)] + [-27.0], [27.0 + 1.0 * i for i in range(8)]):
            x0 = min(xs) - 0.5; x1 = max(xs) + 0.5
            crop = X.dbox(x0, x1, -0.5, 3.0, min(zr) - 0.5, max(zr) + 0.5); X.sec(crop, X.tbm.copy(S))
            print('%s end, d where the slab begins (- : none before d 3), x across, Zd down:' % side)
            print('   Zd \\ x ' + ' '.join('%6.2f' % x for x in xs))
            for z in zr:
                row = []
                for x in xs:
                    a = k.Dp(x, -0.5, z); b = k.Dp(x, 3.0, z)
                    s = k.needle_t(X, [crop], k.W(a), k.W(b), 0.02)
                    row.append('%6.3f' % (s[0][0] - 0.5) if s else '     -')
                print('   %7.2f ' % z + ' '.join(row))
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p45_lip_probe.txt', _main)
