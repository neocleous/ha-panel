# rev F k2c (2026-11-12): fix pass, block 2 - the band tool of k2b built another way. k2b's band_tool() unions 68 moved copies of the
#   wall's section (curved faces); that ran for minutes and was given up. Here the wall's inner bottom edge is sampled with needles,
#   the allowed edge of the raised field is computed (the wall's edge grown by GAP and swept SMAX toward the screen), and the tool is a
#   chain of plain boxes outside that edge. Run through k.step(sha, name, kb=<k2b's namespace>); then kb['band_tool'] = band_tool.
#   The field is convex in plan, so a box standing on a chord of the allowed edge takes at most the sliver between chord and curve
#   (under 0.03 for 2 mm chords) and its ends, which run on along the chord's line, stay outside the field.
#   At the wall's rear end (the door joint) the wall's edge is run on 4 mm along its own direction instead of wrapping round the end:
#   the allowed edge stays convex there; the tool is cut off GAP behind the wall's end.
import math
STEP = 0.25; EXT = 2.0; DEP = 14.0; NTH = 8; RUN_ON = 4.0


def edge(X, sx, y0=-58.0, y1=3.0):                   # the wall's inner bottom edge: [(y, |x|)] every STEP from needles at z 2.9, rear end first
    q = ('k2c_edge', sx, round(X.body('HOUSING_F_front').volume, 6))
    if q in k.c:
        return k.c[q]
    w = kb['wall'](X, sx); out = []
    n = int(round((y1 - y0) / STEP))
    for i in range(n + 1):
        y = y0 + i * STEP
        a = k.needle_t(X, w, (sx * 60.0, y, 2.9), (sx * 100.0, y, 2.9))
        if a:
            out.append((round(y, 3), 60.0 + a[0][0]))
    k.c[q] = out
    return out


def run_on(ed):                                      # drop the end face's samples, run the edge on behind its end; returns (samples, end y)
    m = min(range(len(ed)), key=lambda i: ed[i][1] if ed[i][0] < -40.0 else 1e9)
    ym, xm = ed[m]
    j = m + int(round(2.0 / STEP))
    slope = (ed[j][1] - xm) / (ed[j][0] - ym)
    ext = [(round(ym - i * STEP, 3), xm - slope * i * STEP) for i in range(int(round(RUN_ON / STEP)), 0, -1)]
    return ext + ed[m:], ym, slope


def limit(ed, gap, smax, ya, yb, dy=0.25):           # the largest |x| the raised field may have at each plate y: [(y, |x|)]
    out = []
    n = int(math.floor((yb - ya) / dy + 1e-6))
    for i in range(n + 1):
        y = ya + i * dy; best = None
        for (yw, xw) in ed:                          # a wall point stands anywhere from yw to yw + smax in the plate's frame
            d = 0.0 if yw <= y <= yw + smax else min(abs(y - yw), abs(y - yw - smax))
            if d <= gap:
                x = xw - math.sqrt(gap * gap - d * d)
                if best is None or x < best:
                    best = x
        if best is not None:
            out.append((round(y, 3), best))
    return out


def band_tool(X, sx):
    q = ('k2c_tool', sx, round(X.body('HOUSING_F_front').volume, 6))
    if q in k.c:
        return X.cp(k.c[q])
    ed, ym, slope = run_on(edge(X, sx))
    lim = limit(ed, kb['GAP'], kb['SMAX'], ym - kb['GAP'], kb['YB'])
    pts = lim[::NTH]
    if pts[-1] != lim[-1]:
        pts.append(lim[-1])
    out = None; turn = []
    for i in range(len(pts) - 1):
        a = (sx * pts[i][1], pts[i][0]); b = (sx * pts[i + 1][1], pts[i + 1][0])
        t = k.unit((b[0] - a[0], b[1] - a[1], 0.0)); n = (t[1], -t[0], 0.0)
        if n[0] * sx < 0:
            n = (-n[0], -n[1], 0.0)
        L = math.hypot(b[0] - a[0], b[1] - a[1]) + 2.0 * EXT
        cen = ((a[0] + b[0]) / 2.0 + n[0] * DEP / 2.0, (a[1] + b[1]) / 2.0 + n[1] * DEP / 2.0, 2.5)
        bx = X.obox(cen, t, n, L, DEP, 1.4)
        out = bx if out is None else X.uni(out, bx)
        turn.append(round(math.degrees(math.atan2(t[0] * sx, t[1])), 1))   # the chord's direction from +y toward the outside, deg
    X.sec(out, X.wbox(sx * kb['XMIN'], sx * 100.0, lim[0][0], kb['YB'], 1.8, 3.2))
    k.c[('k2c_lim', sx)] = lim; k.c[('k2c_turn', sx)] = turn; k.c[('k2c_end', sx)] = (ym, slope)
    k.c[q] = out
    return X.cp(out)
