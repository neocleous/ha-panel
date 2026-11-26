# Block 3, read-only: the material over each magnet pocket, today and after p34 (k.c['b3_door']): vertical needles from the
# pocket's axis up 8 mm, at three depths along the axis (0.3, 1.0, 1.7 from the floor). Nothing in the document changes.
# Run: runpy.run_path(D + 'p34b_pocket_check.py')['main']()  -> p34b_pocket_check.txt
import runpy, math

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def _main():
    k = L['load'](); X = k.K()
    door = X.body('HOUSING_F_door')
    old = [X.tbm.copy(door)]
    new = [k.c['b3_door']]
    for h in sorted([h for h in k.holes_of(door, 4.0, 4.3) if h['k'] == 'h'], key=lambda q: (q['A'][0] > 0, q['A'][2])):
        A, B = h['A'], h['B']
        if A[1] > B[1]:
            A, B = B, A
        n = math.sqrt(sum((B[i] - A[i]) ** 2 for i in range(3))); a = [(B[i] - A[i]) / n for i in range(3)]
        print('pocket A %s B %s length %.2f' % (A, B, n))
        for t in (0.3, 1.0, 1.7):
            p = [A[i] + a[i] * t for i in range(3)]
            s0 = k.needle_t(X, old, (p[0], p[1], p[2]), (p[0], p[1], p[2] + 8.0))
            s1 = k.needle_t(X, new, (p[0], p[1], p[2]), (p[0], p[1], p[2] + 8.0))
            print('   t %.1f axis z %.2f: today %s  after %s' % (t, p[2], s0, s1))


def main():
    L['out']('p34b_pocket_check.txt', _main)
