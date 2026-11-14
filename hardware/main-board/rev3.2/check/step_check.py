"""Rev 3.2: reads the STEP files back and compares them with the board files and with rev 3.1's files. Changes nothing.

    python3 step_check.py <rev 3.1 board> <rev 3.1 step> <rev 3.2 board> <rev 3.2 step> <rev 3.1 plug envelopes> <rev 3.2 plug envelopes>

What it checks:
  1. the board's solid: its box, the four holes against the board file, the relief (points inside and beside it, the inner
     corners' arcs), and the volume taken away against rev 3.1's solid;
  2. every part of the rev 3.2 file against the rev 3.1 file: the same box (no part moved);
  3. the heights above the door-side face and the pin ends beyond the back face in the rev 3.2 file, against the table in
     sitecheck.py (as rev 3.1's check);
  4. the plug envelopes written with rev 3.2 against rev 3.1's file: the same blocks (so rev 3.1's file stands).
Frame of the files: X = u, Y = v, Z up out of the door-side face (the board's solid from Z 0 to Z 1.51, parts at Z 1.595).
Uses the reader of ../../rev3.1/check/step_check.py.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))                      # rev3.2/sitecheck.py (height table)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'rev3.1', 'check'))
import step_check as R                                          # noqa: E402  rev 3.1's reader (read, holes, box, quiet)
import sitecheck as SC                                          # noqa: E402
from OCP.BRepClass3d import BRepClass3d_SolidClassifier         # noqa: E402
from OCP.BRepGProp import BRepGProp                             # noqa: E402
from OCP.GProp import GProp_GProps                              # noqa: E402
from OCP.gp import gp_Pnt                                       # noqa: E402
from OCP.STEPControl import STEPControl_Reader                  # noqa: E402
from OCP.TopAbs import TopAbs_IN, TopAbs_OUT, TopAbs_SOLID      # noqa: E402
from OCP.TopExp import TopExp_Explorer                          # noqa: E402

T = 1.6


def volume(shape):
    g = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, g)
    return g.Mass()


def inside(shape, u, v, z):
    c = BRepClass3d_SolidClassifier(shape, gp_Pnt(u, v, z), 1e-6)
    return c.State() == TopAbs_IN


def blocks(path):
    with R.quiet():
        r = STEPControl_Reader()
        r.ReadFile(path)
        r.TransferRoots()
        sh = r.OneShape()
    got = []
    ex = TopExp_Explorer(sh, TopAbs_SOLID)
    while ex.More():
        got.append(tuple(round(x, 4) for x in R.box(ex.Current())))
        ex.Next()
    return sorted(got)


def main(b31, s31, b32, s32, pl31, pl32):
    P31, P32 = R.board_parts(b31), R.board_parts(b32)
    S31, S32 = R.read(s31), R.read(s32)
    bad = 0

    print('== 1. The board solid, the holes and the relief')
    solids = {}
    for tag, S, P in (('rev 3.1', S31, P31), ('rev 3.2', S32, P32)):
        brd = [k for k in S if k not in P]
        print('%-8s parts in the file: %d, of them on the board file: %d, others: %s' % (tag, len(S), len(S) - len(brd), brd))
        bx, sh, _ = S[brd[0]]
        solids[tag] = sh
        print('         solid: X %.3f...%.3f  Y %.3f...%.3f  Z %.3f...%.3f  (thickness %.3f); volume %.2f mm3'
              % (bx[0], bx[3], bx[1], bx[4], bx[2], bx[5], bx[5] - bx[2], volume(sh)))
        hs = R.holes(sh)
        want = sorted((round(P[h][0], 3), round(P[h][1], 3)) for h in ('H1', 'H2', 'H3', 'H4'))
        ok = len(hs) == 4 and all(abs(a[0] - w[0]) < 0.005 and abs(a[1] - w[1]) < 0.005 for a, w in zip(hs, want))
        bad += not ok
        print('         holes of 3.2 in the solid: %s  board file: %s  %s' % (hs, want, 'agree' if ok else 'DIFFERENT'))
    sh = solids['rev 3.2']
    zc = 0.75                                               # middle of the solid's thickness
    probes = [   # (u, v, expected inside the board, what)
        (42.75, 7.25, False, 'middle of the relief'),
        (42.05, 2.0, False, 'just past the floor, near the lower end of the full depth'),
        (42.05, 12.5, False, 'just past the floor, near the upper end'),
        (42.05, 1.5, False, 'past the floor at v +1.5 (full depth holds there)'),
        (42.05, 13.0, False, 'past the floor at v +13.0'),
        (43.4, 0.6, False, 'inside the lower side wall'),
        (43.4, 13.9, False, 'inside the upper side wall'),
        (42.5, 1.0, False, 'lower inner corner, inside its arc'),
        (41.95, 7.25, True, 'just inside the floor'),
        (43.4, 0.4, True, 'just below the lower side wall'),
        (43.4, 14.1, True, 'just above the upper side wall'),
        (42.2, 0.7, True, 'lower inner corner, outside its arc (material the cutter leaves)'),
        (42.2, 13.8, True, 'upper inner corner, outside its arc'),
        (43.4, -10.0, True, 'the edge below the relief'),
        (43.4, 20.0, True, 'the edge above the relief'),
    ]
    for u, v, want, what in probes:
        got = inside(sh, u, v, zc)
        bad += got != want
        print('         (u %+.2f, v %+.2f): %-8s %s  %s' % (u, v, 'board' if got else 'cut away', '' if got == want else 'DIFFERENT', what))
    dv = volume(solids['rev 3.1']) - volume(sh)
    th = R.box(sh)[5] - R.box(sh)[2]
    print('         volume taken away: %.2f mm3 = %.2f mm2 of outline x %.3f thickness (the relief, rule 38 of the site check: 19.82 mm2)'
          % (dv, dv / th, th))
    bad += abs(dv / th - 19.82) > 0.05

    print('\n== 2. Every part: the same box as in rev 3.1 (no part moved)')
    worst, n, diff = 0.0, 0, []
    for ref in sorted(S32):
        if ref not in P32:
            continue
        if ref not in S31:
            diff.append(ref + ' (not in rev 3.1)')
            continue
        a, c = S31[ref][0], S32[ref][0]
        d = max(abs(x - y) for x, y in zip(a, c))
        worst = max(worst, d)
        n += 1
        if d > 0.001:
            diff.append('%s %.4f' % (ref, d))
    gone = sorted(k for k in S31 if k in P31 and k not in S32)
    bad += bool(diff) + bool(gone)
    print('parts compared: %d; largest difference of a part box %.4f; different: %s; in rev 3.1 only: %s' % (n, worst, diff or 'none', gone or 'none'))
    nobody = sorted(r for r in P32 if r not in S32)
    print('on the board, not in the file (no body, or not fitted): %d  %s' % (len(nobody), ' '.join(nobody)))

    print('\n== 3. Heights and pin ends in the rev 3.2 file')
    seat = min(v[0][2] for k, v in S32.items() if k in P32 and P32[k][3].startswith(('R_0603', 'C_0603')))
    print('  chip parts stand on Z %.3f (door-side face); back face at Z %.3f' % (seat, seat - T))
    print('  part   model                                        u                 v                top w   table   pin end   table')
    for ref in ('PS1', 'C5', 'C6', 'C7', 'L1', 'L100', 'J1', 'J5', 'J6', 'J8', 'J9', 'J10', 'J11', 'J2', 'LK1', 'F3', 'F5', 'R105', 'R100'):
        bx, _, model = S32[ref]
        fpn = P32[ref][3]
        h = SC.lookup(SC.HEIGHT, fpn, (None, None))[0]
        pr = SC.lookup(SC.PROTRUSION, fpn)
        top, below = bx[5] - seat, (seat - T) - bx[2]
        print('  %-5s  %-40s  %7.2f...%-7.2f  %7.2f...%-7.2f  %6.2f  %6s  %7s  %6s' % (
            ref, model[:40], bx[0], bx[3], bx[1], bx[4], top, '%.2f' % h if h else '-', '%.2f' % below if below > 0.05 else '-', '%.1f' % pr[0] if pr else '-'))
    near = sorted((42.0 - v[0][3], k) for k, v in S32.items() if k in P32 and v[0][4] > 0.5 and v[0][1] < 14.0)
    print('  part bodies nearest the relief\'s floor (u +42.0) over v +0.5...+14.0: %s' % ', '.join('%s %.2f' % (k, d) for d, k in near[:3]))
    bad += near[0][0] <= 0

    print('\n== 4. Plug envelopes')
    a, c = blocks(pl31), blocks(pl32)
    same = a == c
    bad += not same
    print('  rev 3.1 file: %d blocks; written with rev 3.2: %d blocks; %s' % (len(a), len(c), 'the same blocks: rev 3.1\'s file stands for rev 3.2' if same else 'DIFFERENT'))
    print('\n%s' % ('ALL AGREE' if not bad else '%d DIFFERENCES' % bad))


if __name__ == '__main__':
    main(*sys.argv[1:7])
