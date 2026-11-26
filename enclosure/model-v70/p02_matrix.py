# Block 0 (and block 10): the interference table of the unit as it stands, by the last pass's method:
# c3k.K4NS['matrix'] (v5f_k4a_unit_checks.py at 45a38e4): every current body against every other - boxes, then the
# smallest distance, then the shared volume where they touch. A pair counts as "not zero" above 0.0005 mm3, the
# threshold of v69_checks.matrix. READ-ONLY: temporary bodies only.
# The function stops when its time is used up; call main(tag) again until it reports nothing left.
# Before a fresh table the library's temporary copies of the unit's bodies are dropped (it keeps them by name and
# volume, so a body changed at the same volume would be read as it was: lesson 1 of the last pass).
# Output: p02_matrix_<tag>.txt (progress) and, when finished, p02_matrix_<tag>.json (every pair not zero, and the count
# with no threshold).
import runpy, time

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')


def _main(tag, sec, fresh):
    k = L['load']()
    X = k.K()
    q = ('k4m', tag)
    if fresh and q not in k.c:
        h = k.hc()
        n = 0
        for key in list(h.keys()):
            if isinstance(key, tuple) and key and key[0] in ('tc', 'tile'):
                del h[key]; n += 1
        for key in list(k.c.keys()):
            if isinstance(key, tuple) and len(key) == 3 and key[0] == 'k4p' and key[1] == tag:
                del k.c[key]
        print('dropped %d cached copies and slabs before a fresh table' % n)
    t0 = time.time()
    k.budget(sec)
    res, left, nb = k.K4NS['matrix'](X, tag)
    print('%s  tag %s: bodies %d, pairs done %d, left this call %d, %.1f s' % (L['stamp'](), tag, nb, len(res), left, time.time() - t0))
    if left == 0:
        nz = {'%s | %s' % p: v for p, v in res.items() if abs(v) > L['THRESH']}
        nz0 = {'%s | %s' % p: v for p, v in res.items() if v != 0.0}
        print('FINISHED: %d pairs, %d not zero (above %.4f mm3), %d not zero with no threshold' % (len(res), len(nz), L['THRESH'], len(nz0)))
        L['jdump']('p02_matrix_%s.json' % tag, {'tag': tag, 'read': L['stamp'](), 'bodies': nb, 'pairs': len(res),
                                                 'not_zero': dict(sorted(nz.items())), 'not_zero_no_threshold': dict(sorted(nz0.items()))})
        for p, v in sorted(nz0.items(), key=lambda r: -r[1]):
            print('  %12.6f  %s%s' % (v, p, '' if p in nz else '   (under the threshold)'))


def main(tag='v69ref', sec=55, fresh=True):
    L['out']('p02_matrix_%s.txt' % tag, _main, tag, sec, fresh)
