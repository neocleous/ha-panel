# The close: compares outputs of check scripts as they stood before the close (close_before/<file>) with the outputs read again on
# version 79. Plain Python, no Fusion call. Run in the folder: python3 p94b_diff.py <file> [<file> ...] [--cap N]
import sys, difflib
def body(t):
    return [l for l in t.splitlines() if not l[:5] in ('2026-',) and 'before {' not in l and 'after {' not in l]
cap = 30
files = []
a = sys.argv[1:]
while a:
    x = a.pop(0)
    if x == '--cap': cap = int(a.pop(0))
    else: files.append(x)
for f in files:
    try: old = open('close_before/' + f).read()
    except FileNotFoundError: old = ''
    new = open(f).read()
    A = body(old); B = body(new)
    d = [l for l in difflib.unified_diff(A, B, lineterm='', n=0) if l[:1] in '+-' and l[:3] not in ('+++', '---')]
    print('%s: %d lines (%d before the close), changed lines %d%s' % (f, len(B), len(A), len(d), '' if old else ' (no earlier output)'))
    for l in d[:cap]: print('   ' + l[:400])
    if len(d) > cap: print('   ... %d more' % (len(d) - cap))
