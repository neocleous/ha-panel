# Compares two interference tables of p02 (p02_matrix_<a>.json, p02_matrix_<b>.json): pairs new, gone, and changed by more than
# 0.001 mm3. Plain Python, no Fusion call. Run: runpy.run_path(D + 'p48_compare.py')['main']('b3b', 'b4')  -> p48_<a>_<b>.txt
import json

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'


def norm(d):
    out = {}
    for p, v in d.items():
        a, b = [s.strip() for s in p.split('|')]
        out[tuple(sorted((a, b)))] = v
    return out


def main(a='b3b', b='b4'):
    A = norm(json.load(open(D + 'p02_matrix_%s.json' % a))['not_zero'])
    B = norm(json.load(open(D + 'p02_matrix_%s.json' % b))['not_zero'])
    lines = ['%s: %d pairs not zero; %s: %d' % (a, len(A), b, len(B))]
    for p in sorted(set(B) - set(A)):
        lines.append('NEW      %-60s %12.4f' % (' | '.join(p), B[p]))
    for p in sorted(set(A) - set(B)):
        lines.append('GONE     %-60s %12.4f' % (' | '.join(p), A[p]))
    for p in sorted(set(A) & set(B)):
        if abs(A[p] - B[p]) > 0.001:
            lines.append('CHANGED  %-60s %12.4f -> %12.4f' % (' | '.join(p), A[p], B[p]))
    lines.append('same pairs, same volumes within 0.001: %d' % sum(1 for p in set(A) & set(B) if abs(A[p] - B[p]) <= 0.001))
    open(D + 'p48_%s_%s.txt' % (a, b), 'w').write('\n'.join(lines) + '\n')
    print('\n'.join(lines))
