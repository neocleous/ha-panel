"""Check a one-board stencil's paste file against that board's own paste file, flash by flash.
    python3 stencil_check_single.py main  <stencil F_Paste.gtp> <stencil Edge_Cuts.gm1> <main board F_Paste.gtp>  <size mm> [preview.png]
    python3 stencil_check_single.py touch <stencil F_Paste.gtp> <stencil Edge_Cuts.gm1> <touch board B_Paste.gbp> <size mm> [preview.png]
  1. every aperture of the board's paste file is in the stencil: at the same place (main), or mirrored left-right and
     moved by one common shift (touch: the board lies front-down), with the same size;
  2. nothing else is in it, and nothing drawn or filled (flashes only);
  3. the outline: one closed loop, every aperture inside it, and its extent fits a square stencil of <size> mm;
  4. the smallest aperture, for JLC's limit (larger than 0.08)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fab_check import read_gerber   # noqa: E402
from stencil_check import flashes   # noqa: E402


def main(kind, st, edge, board, size, png=None):
    S, B, E = read_gerber(st), read_gerber(board), read_gerber(edge)
    ok = True

    def say(cond, text):
        nonlocal ok
        ok &= bool(cond)
        print(('  ok   ' if cond else '  FAIL ') + text)
    s, b = flashes(S), flashes(B)
    if kind == 'touch':
        b = [(-x, y, g) for x, y, g in b]
    sx = min(x for x, y, g in s) - min(x for x, y, g in b)
    sy = min(y for x, y, g in s) - min(y for x, y, g in b)
    want = sorted((round(x + sx, 4), round(y + sy, 4), g) for x, y, g in b)
    have = sorted((round(x, 4), round(y, 4), g) for x, y, g in s)
    say(len(want) == len(have) and all(abs(a[0] - c[0]) < 1e-3 and abs(a[1] - c[1]) < 1e-3 and a[2] == c[2] for a, c in zip(want, have)),
        '%d apertures of the board file, %d in the stencil; %s; one common shift (%.4f, %.4f)' % (
            len(want), len(have), 'mirrored left-right' if kind == 'touch' else 'as drawn', sx, sy))
    say(S['draws'] == 0 and S['regions'] == 0, 'nothing drawn or filled in the paste file (%d pieces, %d regions)' % (S['draws'], S['regions']))
    x0, y0, x1, y1 = E['bbox']
    say(all(x0 < x < x1 and y0 < y < y1 for x, y, g in s), 'every aperture inside the outline')
    w, h = x1 - x0, y1 - y0
    say(w < size and h < size, 'outline %.2f x %.2f fits %d x %d, margins %.2f and %.2f a side' % (w, h, size, size, (size - w) / 2, (size - h) / 2))
    small = min((min(g[1], g[2]), g) for x, y, g in s)
    say(small[0] > 0.08, 'smallest aperture %.3f x %.3f (JLC: larger than 0.08)' % (small[1][1], small[1][2]))
    if png:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
        fig, ax = plt.subplots(figsize=(6, 6), dpi=200)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        ax.add_patch(Rectangle((cx - size / 2, cy - size / 2), size, size, fc='#e8e8e8', ec='#888888', lw=0.8))
        ax.add_patch(Rectangle((x0, y0), w, h, fc='none', ec='#2a6fba', lw=0.8))
        for x, y, g in s:
            ax.add_patch(Rectangle((x - g[1] / 2, y - g[2] / 2), g[1], g[2], fc='#222222', ec='none'))
        ax.set_xlim(cx - size / 2 - 2, cx + size / 2 + 2); ax.set_ylim(cy - size / 2 - 2, cy + size / 2 + 2)
        ax.set_aspect('equal'); ax.axis('off')
        ax.set_title('%s stencil, %d x %d mm: %d apertures (grey: the sheet, blue: the board outline)' % (kind, size, size, len(s)), fontsize=7)
        fig.savefig(png, bbox_inches='tight')
    print('RESULT: %s' % ('all checks passed' if ok else 'CHECK FAILED'))
    return ok


if __name__ == '__main__':
    a = sys.argv
    sys.exit(0 if main(a[1], a[2], a[3], a[4], float(a[5]), a[6] if len(a) > 6 else None) else 1)
