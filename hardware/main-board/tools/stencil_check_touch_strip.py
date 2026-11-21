"""Check the touch + strip stencil against the two boards' own files, aperture by aperture, as shapes.

    python3 stencil_check_touch_strip.py <stencil F_Paste.gtp> <stencil Edge_Cuts.gm1>
        <touch B_Paste.gbp> <touch Edge_Cuts.gm1> <strip B_Paste.gbp> <strip Edge_Cuts.gm1>
        <size mm> <thickness mm> [preview.png]

  1. the stencil's outline file holds two closed loops, and each is its board's own outline mirrored left-right (both
     boards lie front-down) and moved; that move is the board's shift on the stencil;
  2. every aperture of each board's own back paste file is in the stencil, mirrored left-right and moved by that same
     shift: same place, same shape, same part. Shapes are compared as areas, so the microphone's custom apertures (the
     sealing ring in six pieces) are checked as well as the rectangles;
  3. nothing else: the stencil's apertures are the two boards' together, flashes only, nothing drawn or filled, each
     inside its own board's outline;
  4. the two outlines apart; together they fit a square stencil of <size> mm;
  5. the smallest aperture, for JLC's limit (larger than 0.08 mm), and every aperture's area ratio at <thickness>
     (aperture area / wall area; 0.66 is the usual lower limit).
Everything is read in the files' own frame (y up); the mirror is x -> -x."""
import math
import re
import sys

from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import polygonize_full, unary_union

SHAPE_TOL = 1e-5   # mm^2 of area two apertures may differ by (the files carry 6 decimals)
POS_TOL = 1e-3     # mm
EDGE_TOL = 1e-3    # mm^2 for outlines; their arcs are drawn as chords here, from different ends after a mirror


def _num(tok, params):
    tok = tok.strip()
    if tok.startswith('$'):
        return params[int(tok[1:]) - 1]
    return float(tok)


def _aperture(kind, v, macros):
    if kind == 'C':
        return Point(0, 0).buffer(v[0] / 2, quad_segs=64)
    if kind == 'R':
        return box(-v[0] / 2, -v[1] / 2, v[0] / 2, v[1] / 2)
    if kind == 'O':
        w, h = v[0], v[1]
        r = min(w, h) / 2
        if w == h:
            return Point(0, 0).buffer(r, quad_segs=64)
        ends = [(-(w / 2 - r), 0), (w / 2 - r, 0)] if w > h else [(0, -(h / 2 - r)), (0, h / 2 - r)]
        return LineString(ends).buffer(r, quad_segs=64)
    if kind == 'RoundRect':
        if len(v) > 9 and abs(v[9]) > 1e-9:
            raise SystemExit('turned RoundRect: %s' % v)
        return Polygon(list(zip(v[1:9:2], v[2:9:2]))).buffer(v[0], quad_segs=64)
    if kind in macros:
        parts = []
        for prim in macros[kind]:
            t = prim.split(',')
            if t[0].strip() != '4' or t[1].strip() != '1':
                raise SystemExit('macro %s: only outline primitives handled, got %s' % (kind, prim[:20]))
            n = int(t[2])
            xy = [_num(a, v) for a in t[3:3 + 2 * (n + 1)]]
            rot = _num(t[3 + 2 * (n + 1)], v)
            parts.append(affinity.rotate(Polygon(list(zip(xy[0::2], xy[1::2]))), rot, origin=(0, 0)))
        return unary_union(parts)
    raise SystemExit('aperture %s not handled' % kind)


def read(path):
    """Flashes (x, y, shape placed, part), draws, regions and the drawn line work of a gerber file."""
    txt = open(path).read()
    macros = {}
    for name, body in re.findall(r'%AM([A-Za-z0-9_]+)\*(.*?)%', txt, re.S):
        prims = [p.replace('\n', '').replace('\r', '').strip() for p in body.split('*')]
        macros[name] = [p for p in prims if p and not p.startswith('0 ') and p != '0']
    aps = {}
    for num, kind, par in re.findall(r'%ADD(\d+)([A-Za-z0-9_]+),?([^*]*)\*%', txt):
        aps[int(num)] = _aperture(kind, [float(a) for a in par.split('X') if a != ''], macros)
    flashes, lines, draws, regions = [], [], 0, 0
    cur, part, mode, x, y = None, None, 'G01', 0.0, 0.0
    for raw in txt.split('\n'):
        line = raw.strip()
        m = re.match(r'^%TO\.C,([^*]*)\*%$', line)
        if m:
            part = m.group(1)
            continue
        if line == '%TD*%':
            part = None
            continue
        if line.startswith('%') or line.startswith('G04'):
            continue
        if line.startswith('G36'):
            regions += 1
        m = re.match(r'^(?:G54)?D(\d+)\*$', line)
        if m and int(m.group(1)) >= 10:
            cur = int(m.group(1))
            continue
        g = re.match(r'^(G0[123])', line)
        if g:
            mode = g.group(1)
            line = line[3:].lstrip('*')
        m = re.match(r'^(?:X(-?\d+))?(?:Y(-?\d+))?(?:I(-?\d+))?(?:J(-?\d+))?D0([123])\*$', line)
        if not m:
            continue
        nx = int(m.group(1)) / 1e6 if m.group(1) is not None else x
        ny = int(m.group(2)) / 1e6 if m.group(2) is not None else y
        if m.group(5) == '3':
            flashes.append((nx, ny, affinity.translate(aps[cur], nx, ny), part))
        elif m.group(5) == '1':
            draws += 1
            if mode == 'G01':
                lines.append(LineString([(x, y), (nx, ny)]))
            else:
                cx = x + (int(m.group(3)) / 1e6 if m.group(3) else 0)
                cy = y + (int(m.group(4)) / 1e6 if m.group(4) else 0)
                r = math.hypot(x - cx, y - cy)
                a0, a1 = math.atan2(y - cy, x - cx), math.atan2(ny - cy, nx - cx)
                sweep = (a1 - a0) % (2 * math.pi) if mode == 'G03' else -((a0 - a1) % (2 * math.pi))
                pts = [(cx + r * math.cos(a0 + sweep * k / 32), cy + r * math.sin(a0 + sweep * k / 32)) for k in range(33)]
                pts[0], pts[-1] = (x, y), (nx, ny)
                lines.append(LineString(pts))
        x, y = nx, ny
    return dict(flashes=flashes, lines=lines, draws=draws, regions=regions)


def loops(g):
    polys, cuts, dangles, invalid = polygonize_full(g['lines'])
    return list(polys.geoms), len(cuts.geoms) + len(dangles.geoms) + len(invalid.geoms)


def mirror(geom):
    return affinity.scale(geom, xfact=-1, yfact=1, origin=(0, 0))


def main(st_paste, st_edge, t_paste, t_edge, s_paste, s_edge, size, thick, png=None):
    S, SE = read(st_paste), read(st_edge)
    boards = [('touch board', '', read(t_paste), read(t_edge)), ('mic strip', 'S-', read(s_paste), read(s_edge))]
    ok = True

    def say(cond, text):
        nonlocal ok
        ok &= bool(cond)
        print(('  ok   ' if cond else '  FAIL ') + text)

    st_loops, loose = loops(SE)
    say(len(st_loops) == 2 and loose == 0, '1. the stencil outline file: %d closed loops, %d loose pieces' % (len(st_loops), loose))
    used = set()
    found = []
    for name, prefix, P, E in boards:
        own, own_loose = loops(E)
        if len(own) != 1 or own_loose:
            raise SystemExit('%s: its own outline is not one closed loop' % name)
        mo = mirror(own[0])
        w, h = mo.bounds[2] - mo.bounds[0], mo.bounds[3] - mo.bounds[1]
        cand = [i for i, L in enumerate(st_loops)
                if abs((L.bounds[2] - L.bounds[0]) - w) < POS_TOL and abs((L.bounds[3] - L.bounds[1]) - h) < POS_TOL]
        if len(cand) != 1:
            say(False, '   %s: no single stencil loop of %.2f x %.2f' % (name, w, h))
            continue
        L = st_loops[cand[0]]
        dx, dy = L.bounds[0] - mo.bounds[0], L.bounds[1] - mo.bounds[1]
        diff = L.symmetric_difference(affinity.translate(mo, dx, dy)).area
        say(diff < EDGE_TOL, '   %s: its outline %.2f x %.2f, mirrored left-right and moved by (%.4f, %.4f), is a loop '
            'of the stencil (area apart %.1e mm2)' % (name, w, h, dx, dy, diff))
        exp = [(-fx + dx, fy + dy, affinity.translate(mirror(sh), dx, dy), part) for fx, fy, sh, part in P['flashes']]
        mine, missing, worst, wrong_part = [], 0, 0.0, 0
        for ex, ey, esh, epart in exp:
            hit = [i for i, f in enumerate(S['flashes']) if i not in used and abs(f[0] - ex) < POS_TOL and abs(f[1] - ey) < POS_TOL
                   and f[2].symmetric_difference(esh).area < SHAPE_TOL]
            if not hit:
                missing += 1
                continue
            i = hit[0]
            used.add(i)
            mine.append(S['flashes'][i])
            worst = max(worst, S['flashes'][i][2].symmetric_difference(esh).area)
            if S['flashes'][i][3] != (prefix + epart if epart else None):
                wrong_part += 1
        say(missing == 0 and wrong_part == 0, '2. %s: %d of %d apertures in the stencil, mirrored and moved by its shift, '
            'same shape (largest area apart %.1e mm2), same part (%d differ)' % (
                name, len(exp) - missing, len(exp), worst, wrong_part))
        say(all(f[2].within(L) for f in mine), '   every one of them inside its own outline')
        found.append((name, L, len(exp), mine))
    n_all = sum(f[2] for f in found)
    say(len(S['flashes']) == n_all and len(used) == n_all and S['draws'] == 0 and S['regions'] == 0,
        '3. nothing else: %d apertures in the stencil = %s; drawn pieces %d, filled regions %d' % (
            len(S['flashes']), ' + '.join(str(f[2]) for f in found), S['draws'], S['regions']))
    if len(found) == 2:
        gap = found[0][1].distance(found[1][1])
        u = unary_union([f[1] for f in found]).bounds
        w, h = u[2] - u[0], u[3] - u[1]
        say(gap > 5, '4. the outlines %.2f apart' % gap)
        say(w < size and h < size, '   together %.2f x %.2f: they fit %g x %g, margins %.2f and %.2f a side when centred' % (
            w, h, size, size, (size - w) / 2, (size - h) / 2))
    small, worst_ar = None, None
    for name, L, n, fl in found:
        dims = []
        for fx, fy, sh, part in fl:
            mr = sh.minimum_rotated_rectangle
            c = list(mr.exterior.coords)
            a, b = math.dist(c[0], c[1]), math.dist(c[1], c[2])
            ar = sh.area / (sh.length * thick)
            dims.append((min(a, b), max(a, b), ar, part))
        if not dims:
            continue
        s = min(dims)
        r = min(dims, key=lambda d: d[2])
        print('       %s: smallest aperture %.3f x %.3f (%s); lowest area ratio %.2f (%s, %.3f x %.3f)' % (
            name, s[0], s[1], s[3], r[2], r[3], r[0], r[1]))
        small = s if small is None or s[0] < small[0] else small
        worst_ar = r if worst_ar is None or r[2] < worst_ar[2] else worst_ar
    if small is None:
        say(False, '5. no aperture matched, so no sizes to check')
    else:
        say(small[0] > 0.08, '5. smallest aperture %.3f across (JLC: larger than 0.08)' % small[0])
        say(worst_ar[2] >= 0.66, '   lowest area ratio at %.2f mm: %.2f (0.66 or more)' % (thick, worst_ar[2]))
    if png:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.patches import Polygon as MP, Rectangle
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 5.6), dpi=200, gridspec_kw={'width_ratios': [1, 1.15]})
        u = unary_union([f[1] for f in found]).bounds
        cx, cy = (u[0] + u[2]) / 2, (u[1] + u[3]) / 2
        a1.add_patch(Rectangle((cx - size / 2, cy - size / 2), size, size, fc='#e8e8e8', ec='#888888', lw=0.8))
        for ax in (a1, a2):
            for name, L, n, fl in found:
                ax.plot(*L.exterior.xy, color='#2a6fba', lw=0.8)
                for fx, fy, sh, part in fl:
                    for g in getattr(sh, 'geoms', [sh]):
                        ax.add_patch(MP(list(g.exterior.coords), closed=True, fc='#222222', ec='none'))
            ax.set_aspect('equal')
            ax.axis('off')
        a1.set_xlim(cx - size / 2 - 2, cx + size / 2 + 2)
        a1.set_ylim(cy - size / 2 - 2, cy + size / 2 + 2)
        a1.set_title('the %g x %g sheet: touch board above, mic strip below\n(grey: the sheet; blue: the outlines; '
                     'seen from the boards\' backs)' % (size, size), fontsize=7)
        sb = [f for f in found if f[0] == 'mic strip'][0][1].bounds
        a2.set_xlim(sb[0] - 1, sb[2] + 1)
        a2.set_ylim(sb[1] - 1, sb[3] + 1)
        a2.set_title('the mic strip\'s pattern, enlarged: %d apertures; the microphone\'s ring in six pieces round '
                     'the port' % [f for f in found if f[0] == 'mic strip'][0][2], fontsize=7)
        fig.savefig(png, bbox_inches='tight')
    print('RESULT: %s' % ('all checks passed' if ok else 'CHECK FAILED'))
    return ok


if __name__ == '__main__':
    a = sys.argv
    if len(a) < 9:
        raise SystemExit(__doc__)
    sys.exit(0 if main(a[1], a[2], a[3], a[4], a[5], a[6], float(a[7]), float(a[8]), a[9] if len(a) > 9 else None) else 1)
