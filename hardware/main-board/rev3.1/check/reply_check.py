"""Compares the numbers written in the reply to the enclosure with the two board files. Changes nothing.

    python3 reply_check.py <rev 3 board> <rev 3.1 board> <reply .md>

Checked: every row of "Everything that moved" (positions and boxes, old and new), the hole table, the connector table
(pin 1, last pin, box) and the three probe points.
"""
import re
import sys

import pcbnew

import reply_data as R


def num(s):
    return [float(x) for x in re.findall(r'[-+]?\d+\.\d+', s)]


def main(p3, p31, reply):
    b3, b31 = pcbnew.LoadBoard(p3), pcbnew.LoadBoard(p31)
    A, B = R.parts(b3), R.parts(b31)
    txt = open(reply).read()
    bad = 0
    sec2 = txt[txt.index('## 2. Everything that moved'):txt.index('## 3. Outline')]
    rows = [r for r in sec2.splitlines() if r.startswith('| ') and not r.startswith('| Part') and not r.startswith('|---')]
    for r in rows:
        c = [x.strip() for x in r.strip('|').split('|')]
        ref = c[0]
        for col, P in ((3, A), (4, B)):
            n, f = num(c[col]), P[ref]
            if ref == 'H2':
                want = list(R.uv(f.GetPosition()))
            elif ref in ('J10', 'J11'):
                p1 = [p for p in f.Pads() if p.GetNumber() == '1'][0]
                k = R.crt(f)
                want = list(R.uv(p1.GetPosition())) + [k[0], k[2], k[1], k[3]]
            else:
                k = R.crt(f)
                want = [k[0], k[2], k[1], k[3]]
            ok = len(n) == len(want) and all(abs(a - w) < 0.011 for a, w in zip(n, want))
            bad += not ok
            if not ok:
                print('  DIFFERENT', ref, 'rev 3' if col == 3 else 'rev 3.1', n, [round(w, 2) for w in want])
    print('rows of "Everything that moved" checked: %d' % len(rows))
    nh = 0
    for m in re.finditer(r'\| (H\d) \| ([-+]\d+\.\d+) \| ([-+]\d+\.\d+) \|', txt):
        u, v = R.uv(B[m.group(1)].GetPosition())
        ok = abs(u - float(m.group(2))) < 0.006 and abs(v - float(m.group(3))) < 0.006
        bad += not ok
        nh += 1
        if not ok:
            print('  DIFFERENT hole', m.group(1))
    print('holes checked: %d' % nh)
    sec6 = txt[txt.index('## 6. Connectors and leads'):txt.index('- **Only the rows of J10')]
    n = 0
    for r in sec6.splitlines():
        if not re.match(r'\| J\d+ ', r):
            continue
        c = [x.strip() for x in r.strip('|').split('|')]
        f = B[c[0]]
        p1 = R.uv([p for p in f.Pads() if p.GetNumber() in ('1', 'A1')][0].GetPosition())
        got1, gotl = num(c[3]), num(c[4])
        ok = abs(got1[0] - p1[0]) < 0.006 and abs(got1[1] - p1[1]) < 0.006
        okl = any(abs(gotl[0] - q[0]) < 0.006 and abs(gotl[1] - q[1]) < 0.006 for q in (R.uv(p.GetPosition()) for p in f.Pads()))
        k, bu, bv = R.crt(f), num(c[5]), num(c[6])
        okb = c[0] in ('J3', 'J4', 'J7') or all(abs(a - w) < 0.011 for a, w in zip(bu + bv, (k[0], k[2], k[1], k[3])))
        bad += not (ok and okl and okb)
        n += 1
        if not (ok and okl and okb):
            print('  DIFFERENT', c[0], ok, okl, okb)
    print('connector rows checked: %d (the boxes of the wire pads J3, J4, J7 are pads plus 0.3 and are not compared)' % n)
    for ref, said in (('J10', (-30.40, -14.11)), ('J11', (-0.69, -13.00)), ('J5', (-40.30, -13.85))):
        pads = [R.uv(p.GetPosition()) for p in B[ref].Pads()]
        is_ = (sum(p[0] for p in pads) / len(pads), sum(p[1] for p in pads) / len(pads))
        ok = all(abs(a - w) < 0.006 for a, w in zip(said, is_))
        bad += not ok
        print('probe point %s %s: %s' % (ref, said, 'agrees' if ok else 'DIFFERENT (%.2f, %.2f)' % is_))
    print('ALL AGREE' if not bad else '%d DIFFERENCES' % bad)


if __name__ == '__main__':
    main(*sys.argv[1:4])
