"""Check the combined stencil's paste file against the two boards' own paste files, flash by flash.
    python3 stencil_check.py <stencil F_Paste.gtp> <stencil Edge_Cuts.gm1> <main board F_Paste.gtp> <touch board B_Paste.gbp> [preview.png]
  1. every aperture of the main board's door-side paste is in the stencil at the same place with the same size;
  2. every aperture of the touch board's back paste is in it mirrored left-right (the board lies front-down) and moved
     by one common shift;
  3. there is nothing else in it, and nothing drawn or filled (flashes only);
  4. the two outlines: the main board above, the touch board below, left edges in line, the gap between them;
  5. the smallest aperture, for JLC's limit.
Sizes are compared as outer width x height and corner radius, which do not change when a part is mirrored or turned
by a quarter turn."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fab_check import read_gerber   # noqa: E402


def sig(ap):
    kind, par = ap
    v = [float(x) for x in par.split('X') if x != '']
    if kind == 'R':
        return ('rect', round(v[0], 4), round(v[1], 4), 0.0)
    if kind == 'C':
        return ('round', round(v[0], 4), round(v[0], 4), round(v[0] / 2, 4))
    if kind == 'O':
        return ('oval', round(v[0], 4), round(v[1], 4), round(min(v[0], v[1]) / 2, 4))
    if kind == 'RoundRect':
        r, xs, ys = v[0], v[1:9:2], v[2:9:2]
        assert abs(v[9]) < 1e-9, 'turned aperture: %s' % par
        return ('rounded', round(max(xs) - min(xs) + 2 * r, 4), round(max(ys) - min(ys) + 2 * r, 4), round(r, 4))
    raise ValueError(kind)


def flashes(g):
    return [(x, y, sig(g['aps'][a])) for x, y, a in g['flashes']]


def main(st, edge, mainp, touchp, png=None):
    S, M, T = read_gerber(st), read_gerber(mainp), read_gerber(touchp)
    s, m, t = flashes(S), flashes(M), flashes(T)
    ok = True

    def say(c, text):
        nonlocal ok
        ok = ok and c
        print(('  ok   ' if c else '  FAIL ') + text)
    print('apertures: stencil %d, main board %d, touch board %d' % (len(s), len(m), len(t)))
    sset = set(s)
    miss = [f for f in m if f not in sset]
    say(not miss, '1. main board: %d of %d apertures are in the stencil, same place, same size' % (len(m) - len(miss), len(m)))
    rest = sorted(sset - set(m))
    say(len(rest) == len(t), '   left over for the touch board: %d (it has %d)' % (len(rest), len(t)))
    mir = [(-x, y, (k, w, h, r)) for x, y, (k, w, h, r) in t]          # seen from the back: left and right swapped
    dx = min(f[0] for f in rest) - min(f[0] for f in mir)
    dy = min(f[1] for f in rest) - min(f[1] for f in mir)
    moved = sorted((round(x + dx, 4), round(y + dy, 4), g) for x, y, g in mir)
    bad = [a for a, b in zip(moved, rest) if abs(a[0] - b[0]) > 1e-4 or abs(a[1] - b[1]) > 1e-4 or a[2] != b[2]]
    say(not bad, '2. touch board: all %d apertures mirrored left-right and moved by one shift (%.4f, %.4f)' % (len(t), dx, dy))
    say(len(s) == len(m) + len(t) and S['draws'] == 0 and S['regions'] == 0, '3. nothing else: %d = %d + %d apertures; drawn pieces %d, filled regions %d' % (len(s), len(m), len(t), S['draws'], S['regions']))
    # outlines: the drawn pieces of the outline file, joined end to end into closed loops (one per board)
    cur, segs = None, []
    for line in open(edge).read().splitlines():
        mm = re.match(r'^(?:G0[123])?X(-?\d+)Y(-?\d+)(?:I-?\d+J-?\d+)?D0([12])\*$', line)
        if not mm:
            continue
        pt = (int(mm.group(1)) / 1e6, -int(mm.group(2)) / 1e6)
        if mm.group(3) == '1':
            segs.append((cur, pt))
        cur = pt
    key = lambda q: (round(q[0], 3), round(q[1], 3))
    par = {}

    def find(k):
        while par.setdefault(k, k) != k:
            par[k] = par[par[k]]
            k = par[k]
        return k
    for p1, p2 in segs:
        par[find(key(p1))] = find(key(p2))
    loops = {}
    for p1, p2 in segs:
        loops.setdefault(find(key(p1)), []).extend([p1, p2])
    ends = {}
    for p1, p2 in segs:
        for q in (p1, p2):
            ends[key(q)] = ends.get(key(q), 0) + 1
    say(len(loops) == 2 and all(n == 2 for n in ends.values()), '4. outline file: %d closed loops (%d pieces, every end met by exactly one other)' % (len(loops), len(segs)))
    boxes = sorted(((min(q[0] for q in v), min(q[1] for q in v), max(q[0] for q in v), max(q[1] for q in v)) for v in loops.values()), key=lambda bx: bx[1])
    bu, bl = boxes[0], boxes[-1]
    print('   outlines: main board %.2f x %.2f above, touch board %.2f x %.2f below; gap %.2f; left edges %.3f and %.3f' % (
        bu[2] - bu[0], bu[3] - bu[1], bl[2] - bl[0], bl[3] - bl[1], bl[1] - bu[3], bu[0], bl[0]))
    say(abs(bu[0] - bl[0]) < 1e-3, '   left edges in line')
    inside_main = all(bu[0] - 1e-6 <= x <= bu[2] + 1e-6 and bu[1] - 1e-6 <= y <= bu[3] + 1e-6 for x, y, _ in m)
    inside_touch = all(bl[0] - 1e-6 <= x <= bl[2] + 1e-6 and bl[1] - 1e-6 <= y <= bl[3] + 1e-6 for x, y, _ in rest)
    say(inside_main and inside_touch, '   every aperture lies inside its own board\'s outline')
    xs = [f[0] for f in s]; ys2 = [f[1] for f in s]
    ext = (max(bu[2], bl[2]) - min(bu[0], bl[0]), bl[3] - bu[1])
    print('   pattern with both outlines: %.2f x %.2f; apertures alone: %.2f x %.2f' % (ext[0], ext[1], max(xs) - min(xs), max(ys2) - min(ys2)))
    small = min(s, key=lambda f: min(f[2][1], f[2][2]))
    area = sum(f[2][1] * f[2][2] - (4 - 3.14159265) * f[2][3] ** 2 for f in s)
    from collections import Counter
    print('5. smallest aperture %.3f x %.3f (%d of that size); paste area in all %.1f mm2' % (small[2][1], small[2][2], sum(1 for f in s if f[2] == small[2]), area))
    if png:
        from pygerber.gerberx3.api.v2 import GerberFile, ColorScheme, PixelFormatEnum, ImageFormatEnum
        from PIL import Image
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            a, b = os.path.join(d, 'p.png'), os.path.join(d, 'e.png')
            GerberFile.from_file(st).parse().render_raster(a, dpmm=16, color_scheme=ColorScheme.PASTE_MASK_ALPHA, pixel_format=PixelFormatEnum.RGBA, image_format=ImageFormatEnum.PNG)
            GerberFile.from_file(edge).parse().render_raster(b, dpmm=16, color_scheme=ColorScheme.SILK_ALPHA, pixel_format=PixelFormatEnum.RGBA, image_format=ImageFormatEnum.PNG)
            pe, pp = Image.open(b).convert('RGBA'), Image.open(a).convert('RGBA')
            # the outline picture covers the whole pattern; the paste picture starts at the first aperture
            canvas = Image.new('RGBA', pe.size, (30, 30, 30, 255))
            ox = int(round((min(f[0] - f[2][1] / 2 for f in s) - (min(bu[0], bl[0]) - 0.05)) * 16))
            oy = int(round((min(f[1] - f[2][2] / 2 for f in s) - (bu[1] - 0.05)) * 16))
            canvas.alpha_composite(pp, (max(ox, 0), max(oy, 0)))
            canvas.alpha_composite(pe)
            canvas.convert('RGB').save(png, optimize=True)
        print('drawn: %s' % png)
    print('RESULT: %s' % ('all checks passed' if ok else 'CHECK FAILED'))
    return ok


if __name__ == '__main__':
    sys.exit(0 if main(*sys.argv[1:]) else 1)
