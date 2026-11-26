# Block 6: the clamps' two M2 x 6 in SCREWS_M2x6_env follow their clamps 0.1 up (head flush with the clamp's underside, now z 172.7).
# The rest of the screw body is not touched. Temporary body only; CHANGES NOTHING IN THE DOCUMENT. Result in k.c['b6_screws'].
# Run: runpy.run_path(D + 'p62b_b6_screws.py')['main']()  -> p62b_b6_screws.txt
import runpy

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def _main():
    k = L['load'](); X = k.K(); k.budget(75)
    print(L['stamp'](), 'before', X.state())
    S = X.body('SCREWS_M2x6_env'); t = X.tbm.copy(S); v0 = X.vol(t)
    print('SCREWS_M2x6_env: %.4f mm3, %d lumps' % (v0, t.lumps.count))
    for sx in (1, -1):
        c = X.cyl((sx * 15.5, -35.2, 171.5), (sx * 15.5, -35.2, 180.0), 2.6)
        pc = X.tbm.copy(c); X.sec(pc, X.tbm.copy(S))
        print('  clamp screw at x %+.1f: %.4f mm3, %d lump(s), world box %s' % (sx * 15.5, X.vol(pc), pc.lumps.count, k.wbb(X, pc)))
        X.dif(t, c); X.move(pc, 0, 0, 0.1); X.uni(t, pc)
    print('after: %.4f mm3 (%+.4f), %d lumps' % (X.vol(t), X.vol(t) - v0, t.lumps.count))
    k.c['b6_screws'] = t
    for sx in (1, -1):
        pc = X.cyl((sx * 15.5, -35.2, 171.5), (sx * 15.5, -35.2, 180.0), 2.6); X.sec(pc, X.tbm.copy(t))
        print('  now at x %+.1f: world box %s; shared with the new clamp %.4f, with the new cap %.4f mm3' % (
            sx * 15.5, k.wbb(X, pc), X.xv(pc, k.c['b6_clamp' + ('L' if sx > 0 else 'R')]), X.xv(pc, k.c['b6_cap'])))
    print('whole new screw body with the new cap: %.4f mm3 (the table had 8.604 with the cap)' % X.xv(t, k.c['b6_cap']))
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p62b_b6_screws.txt', _main)
