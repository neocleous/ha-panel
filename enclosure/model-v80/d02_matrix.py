# Block 0 and the close: the interference table of the unit as it stands, by the method of the last two passes:
# c3k.K4NS['matrix'] (v5f_k4a_unit_checks.py at 45a38e4): every current body against every other - boxes, then the
# smallest distance, then the shared volume where they touch. A pair counts as "not zero" above 0.0005 mm3.
# READ-ONLY: temporary bodies only. The function stops when its time is used up; call main(tag) again until it reports
# FINISHED. Before a fresh table the library's cached copies of the unit's bodies are dropped (it keeps them by name
# and volume, so a body changed at the same volume would be read as it was).
# Output: d02_matrix_<tag>.txt (progress) and, when finished, d02_matrix_<tag>.json.
#   compare(a, b)   plain Python: pairs new, gone and changed by more than 0.001 mm3 between two tables. A name ending in
#                   '.json' is read as a path; 'ref79' is the last close's table, ../audit_fixes_v70/p02_matrix_v79.json.
import runpy, time, json

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
L = runpy.run_path(D + 'v80_lib.py')


def _main(tag, sec, fresh):
    k = L['load'](); X = k.K()
    q = ('k4m', tag)
    if fresh and q not in k.c:
        h = k.hc(); n = 0
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
        L['jdump']('d02_matrix_%s.json' % tag, {'tag': tag, 'read': L['stamp'](), 'bodies': nb, 'pairs': len(res), 'state': X.state(),
                                                'not_zero': dict(sorted(nz.items())), 'not_zero_no_threshold': dict(sorted(nz0.items()))})
        for p, v in sorted(nz0.items(), key=lambda r: -r[1]):
            if p not in nz:
                print('  %12.6f  %s   (under the threshold)' % (v, p))


def main(tag, sec=55, fresh=True):
    L['out']('d02_matrix_%s.txt' % tag, _main, tag, sec, fresh)


def _norm(d):
    o = {}
    for p, v in d.items():
        a, b = [s.strip() for s in p.split('|')]
        o[tuple(sorted((a, b)))] = v
    return o


def _load(a):
    fn = L['D70'] + 'p02_matrix_v79.json' if a == 'ref79' else (a if a.endswith('.json') else D + 'd02_matrix_%s.json' % a)
    return _norm(json.load(open(fn))['not_zero'])


def compare(a='ref79', b='v79', full=False):
    A = _load(a); B = _load(b)
    lines = ['%s: %d pairs not zero; %s: %d' % (a, len(A), b, len(B))]
    for p in sorted(set(B) - set(A)):
        lines.append('NEW      %-58s %12.4f' % (' | '.join(p), B[p]))
    for p in sorted(set(A) - set(B)):
        lines.append('GONE     %-58s %12.4f' % (' | '.join(p), A[p]))
    for p in sorted(set(A) & set(B)):
        if abs(A[p] - B[p]) > 0.001:
            lines.append('CHANGED  %-58s %12.4f -> %12.4f' % (' | '.join(p), A[p], B[p]))
    lines.append('same pairs, same volumes within 0.001: %d' % sum(1 for p in set(A) & set(B) if abs(A[p] - B[p]) <= 0.001))
    if full:
        for p in sorted(B):
            lines.append('         %-58s %12.4f' % (' | '.join(p), B[p]))
    open(D + 'd02_compare_%s_%s.txt' % (a.replace('/', '_')[-20:], b), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))
# END
