# The close: the last pass's check 4, the magnet pockets, read on the saved version. READ-ONLY (temporary bodies only).
# Record (claude/report-enclosure-screws-block4-2026-11-23.md, check 4): the shell's lip has ten pockets 8.3 across, 1.60
# deep, with 0.50 of skin behind the floor on the door side.
# For the shell and the door: every hole 4.0 to 4.3 in radius with its axis, its depth, and the solid stretches along its axis
# from 3 before its first end to 3 beyond its second (the skin is the stretch that begins at the floor).
# Run: runpy.run_path(D + 'p98_close_magnets.py')['main']()  -> p98_magnets.txt
import runpy

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def _main():
    k = L['load'](); X = k.K(); k.budget(70)
    print(L['stamp'](), 'before', X.state())
    for nm in ('HOUSING_F_front', 'HOUSING_F_front_v69', 'HOUSING_F_door', 'HOUSING_F_door_v69'):
        b = X.body(nm)
        rows = []
        for h in k.holes_of(b, 4.0, 4.3):
            if h['k'] != 'h':
                continue
            A = h['A']; B = h['B']; Ln = h['L']
            ax = k.unit((B[0] - A[0], B[1] - A[1], B[2] - A[2]))
            p0 = tuple(A[i] - 3.0 * ax[i] for i in range(3)); p1 = tuple(B[i] + 3.0 * ax[i] for i in range(3))
            box = (min(p0[0], p1[0]) - 6, max(p0[0], p1[0]) + 6, min(p0[1], p1[1]) - 6, max(p0[1], p1[1]) + 6, min(p0[2], p1[2]) - 6, max(p0[2], p1[2]) + 6)
            c = X.wbox(*box); X.sec(c, X.tbm.copy(b))
            st = k.needle_t(X, [c], p0, p1, 0.02)
            rows.append((round(h['r'], 3), round(Ln, 2), round(h['cov'], 2), k.r2(A), [(round(a - 3.0, 2), round(e - 3.0, 2)) for a, e in st]))
        print('%s: %d holes of radius 4.0 to 4.3' % (nm, len(rows)))
        for r in sorted(rows, key=lambda q: (q[3][2], q[3][0])):
            print('   r %.3f, depth %.2f, cov %.2f, from %s; solid along the axis (0 = the first end): %s' % r)
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p98_magnets.txt', _main)
