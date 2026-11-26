# Block 7, AA-A12: the shell's way down with the shell off to one side, at the right box, before (the box's _v69 copy, the same as
# version 75's) and after (the model's box). READ-ONLY but for 'TMP_*' bodies, deleted again.
# The unit is moved against the shell: b behind (-y), h below its place (-z), and s toward the right wall (-x), which is the shell
# off by s toward the left. The shell is cropped to the right front corner (x -100..-80, y -12..4, z 40..100), the box to its top
# front outboard corner (x -96..-85, y -12..-3, z 60..85).
# Run: runpy.run_path(D + 'p72_b7_side.py')['main']()  -> p72_b7_side.txt
import runpy

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def _main():
    k = L['load'](); X = k.K(); k.budget(78)
    print(L['stamp'](), 'before', X.state())
    sh = X.wbox(-100, -80, -12, 4, 40, 100); X.sec(sh, X.tbm.copy(X.body('HOUSING_F_front')))
    ts = X.add(sh, 'TMP_sh', show=False)
    for tag, nm in (('v75', 'SPKBOX_R_v69'), ('new', 'SPKBOX_R')):
        bx = X.wbox(-96, -85, -12, -3, 60, 85); X.sec(bx, X.tbm.copy(X.body(nm)))
        for s in (0.25, 0.35, 0.5):
            for b in (0.95, 1.3, 1.6):
                best = None
                for h in (0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 14.0, 18.0):
                    t = X.move(X.tbm.copy(bx), -s, -b, -h)
                    v = X.xv(t, sh)
                    if v > 0.0005:
                        best = ('meets', h, round(v, 4)); break
                    tb = X.add(t, 'TMP_b', show=False)
                    r = X.mm.measureMinimumDistance(tb, ts); dd = r.value * 10
                    if best is None or dd < best[2]:
                        best = ('clear', h, round(dd, 3), k.r2(k.W(r.positionOne)))
                    tb.deleteMe()
                print('%s  off %.2f toward the right wall, %.2f behind: %s' % (tag, s, b, best))
    ts.deleteMe()
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p72_b7_side.txt', _main)
