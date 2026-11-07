"""Grid maze router (A*, 2 outer layers, vias) for the connections Freerouting leaves open.
Obstacles are rasterised at RES with per-netclass clearance; zones on F/B are ignored (refilled afterwards)."""
import heapq
import math

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
import pcbnew

T = 1e-6
MM = pcbnew.FromMM
RES = 0.05
LAYERS = {'F': pcbnew.F_Cu, 'B': pcbnew.B_Cu}
EDGE_CLR = 0.3
GRAVE = []


def remove(board, item):
    board.Remove(item)
    GRAVE.append(item)


def board_box(board, m=1.0):
    bb = board.GetBoardEdgesBoundingBox()
    return (bb.GetX() * T - m, bb.GetY() * T - m, bb.GetRight() * T + m, bb.GetBottom() * T + m)


def net_clearance(name, classes):
    for _, (tw, cl, vd, vdr, nets) in classes.items():
        if name in nets:
            return cl
    return 0.2


class Region:
    def __init__(self, x0, y0, x1, y1):
        self.x0, self.y0 = x0, y0
        self.W = int(math.ceil((x1 - x0) / RES))
        self.H = int(math.ceil((y1 - y0) / RES))

    def px(self, x, y):
        return ((x - self.x0) / RES, (y - self.y0) / RES)

    def mm(self, i, j):
        return (self.x0 + (i + 0.5) * RES, self.y0 + (j + 0.5) * RES)


def _poly_px(reg, ps):
    out = []
    for k in range(ps.OutlineCount()):
        ch = ps.Outline(k)
        out.append([reg.px(ch.CPoint(i).x * T, ch.CPoint(i).y * T) for i in range(ch.PointCount())])
    return out


def _draw_stadium(dr, reg, x0, y0, x1, y1, w):
    a, b = reg.px(x0, y0), reg.px(x1, y1)
    r = w / 2 / RES
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    if L > 1e-6:
        nx, ny = -dy / L * r, dx / L * r
        dr.polygon([(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)], fill=1)
    for c in (a, b):
        dr.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=1)


def build(board, reg, netname, classes):
    """Return dict layer -> {clearance: obstacle bool array}, edge distance array, and same-net copper masks."""
    groups = {}
    same = {}
    for ln in LAYERS:
        groups[ln] = {}
        same[ln] = Image.new('1', (reg.W, reg.H), 0)

    def img(ln, cl):
        if cl not in groups[ln]:
            groups[ln][cl] = Image.new('1', (reg.W, reg.H), 0)
        return groups[ln][cl]

    bx0, by0 = reg.x0 - 2, reg.y0 - 2
    bx1, by1 = reg.x0 + reg.W * RES + 2, reg.y0 + reg.H * RES + 2

    def inside(bb):
        return not (bb.GetRight() * T < bx0 or bb.GetX() * T > bx1 or bb.GetBottom() * T < by0 or bb.GetY() * T > by1)

    for fp in board.GetFootprints():
        if not inside(fp.GetBoundingBox(False)):
            continue
        for p in fp.Pads():
            if not inside(p.GetBoundingBox()):
                continue
            nn = p.GetNetname()
            for ln, lid in LAYERS.items():
                if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                    d = p.GetDrillSize().x * T + 0.1
                    c = reg.px(p.GetPosition().x * T, p.GetPosition().y * T)
                    ImageDraw.Draw(img(ln, 0.25)).ellipse([c[0] - d / 2 / RES, c[1] - d / 2 / RES, c[0] + d / 2 / RES, c[1] + d / 2 / RES], fill=1)
                    continue
                if not p.IsOnLayer(lid):
                    continue
                polys = _poly_px(reg, p.GetEffectivePolygon(lid, pcbnew.ERROR_INSIDE))
                target = same[ln] if nn == netname else img(ln, net_clearance(nn, classes))
                dr = ImageDraw.Draw(target)
                for pl in polys:
                    if len(pl) > 2:
                        dr.polygon(pl, fill=1)
    for t in board.GetTracks():
        if not inside(t.GetBoundingBox()):
            continue
        nn = t.GetNetname()
        if t.GetClass() == 'PCB_VIA':
            for ln, lid in LAYERS.items():
                target = same[ln] if nn == netname else img(ln, net_clearance(nn, classes))
                c = reg.px(t.GetPosition().x * T, t.GetPosition().y * T)
                r = t.GetWidth(lid) * T / 2 / RES
                ImageDraw.Draw(target).ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=1)
            continue
        for ln, lid in LAYERS.items():
            if t.GetLayer() != lid:
                continue
            target = same[ln] if nn == netname else img(ln, net_clearance(nn, classes))
            s, e = t.GetStart(), t.GetEnd()
            _draw_stadium(ImageDraw.Draw(target), reg, s.x * T, s.y * T, e.x * T, e.y * T, t.GetWidth() * T)
    for z in board.Zones():                       # rule areas that forbid tracks: obstacles on their layers
        if not z.GetIsRuleArea() or not z.GetDoNotAllowTracks():
            continue
        for ln, lid in LAYERS.items():
            if z.IsOnLayer(lid):
                dr = ImageDraw.Draw(img(ln, 0.0))
                for pl in _poly_px(reg, z.Outline()):
                    if len(pl) > 2:
                        dr.polygon(pl, fill=1)
    edge = Image.new('1', (reg.W, reg.H), 1)
    ol = pcbnew.SHAPE_POLY_SET()
    board.GetBoardPolygonOutlines(ol)
    for pl in _poly_px(reg, ol):
        ImageDraw.Draw(edge).polygon(pl, fill=0)
    dist = {}
    for ln in LAYERS:
        dist[ln] = {cl: ndimage.distance_transform_edt(~np.array(im, dtype=bool)) * RES for cl, im in groups[ln].items()}
    edist = ndimage.distance_transform_edt(~np.array(edge, dtype=bool)) * RES
    samem = {ln: np.array(same[ln], dtype=bool) for ln in LAYERS}
    return dist, edist, samem


def hole_mask(board, reg, drill, gap=0.3):
    """True where a new hole of `drill` would sit closer than `gap` (edge to edge) to any existing hole."""
    im = Image.new('1', (reg.W, reg.H), 0)
    dr = ImageDraw.Draw(im)
    holes = [(t.GetPosition(), t.GetDrillValue()) for t in board.GetTracks() if t.GetClass() == 'PCB_VIA']
    holes += [(p.GetPosition(), p.GetDrillSize().x) for f in board.GetFootprints() for p in f.Pads() if p.HasHole()]
    for pos, d in holes:
        c = reg.px(pos.x * T, pos.y * T)
        r = (d * T / 2 + gap + drill / 2) / RES
        if -r <= c[0] <= reg.W + r and -r <= c[1] <= reg.H + r:
            dr.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=1)
    return np.array(im, dtype=bool)


def allowed(dist, edist, ln, w, cl_route, margin=RES * 0.75):
    ok = edist >= EDGE_CLR + w / 2 + margin
    for cl, d in dist[ln].items():
        ok &= d >= max(cl, cl_route) + w / 2 + margin
    return ok


def astar(okmap, viaok, starts, goals, via_cost):
    """okmap: {ln: bool[H,W]}, viaok: bool[H,W]; starts/goals: sets of (ln,i,j)."""
    lns = list(okmap)
    H, W = viaok.shape
    gl = list(goals)
    gi = np.array([g[1] for g in gl]); gj = np.array([g[2] for g in gl])
    gx0, gx1, gy0, gy1 = gi.min(), gi.max(), gj.min(), gj.max()

    def h(i, j):
        dx = max(gx0 - i, 0, i - gx1); dy = max(gy0 - j, 0, j - gy1)
        return max(dx, dy) + 0.41421356 * min(dx, dy)
    openh = []
    g = {}
    par = {}
    for s in starts:
        g[s] = 0.0
        heapq.heappush(openh, (h(s[1], s[2]), 0.0, s))
    moves = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, 1.41421356), (1, -1, 1.41421356),
             (-1, 1, 1.41421356), (-1, -1, 1.41421356)]
    n = 0
    while openh:
        f, gc, s = heapq.heappop(openh)
        if gc > g.get(s, 1e18):
            continue
        n += 1
        if s in goals:
            path = [s]
            while path[-1] in par:
                path.append(par[path[-1]])
            return path[::-1], n
        ln, i, j = s
        for di, dj, c in moves:
            ii, jj = i + di, j + dj
            if 0 <= ii < W and 0 <= jj < H and okmap[ln][jj, ii]:
                t = (ln, ii, jj); ng = gc + c
                if ng < g.get(t, 1e18):
                    g[t] = ng; par[t] = s; heapq.heappush(openh, (ng + h(ii, jj), ng, t))
        if viaok[j, i]:
            for l2 in lns:
                if l2 != ln and okmap[l2][j, i]:
                    t = (l2, i, j); ng = gc + via_cost
                    if ng < g.get(t, 1e18):
                        g[t] = ng; par[t] = s; heapq.heappush(openh, (ng + h(i, j), ng, t))
    return None, n


def _clear_line(ok, a, b):
    (i0, j0), (i1, j1) = a, b
    n = int(max(abs(i1 - i0), abs(j1 - j0)) * 2) + 1
    for k in range(n + 1):
        t = k / n
        i = int(round(i0 + (i1 - i0) * t)); j = int(round(j0 + (j1 - j0) * t))
        if not ok[j, i]:
            return False
    return True


def smooth(run, ok):
    pts = [(p[1], p[2]) for p in run]
    out = [pts[0]]
    k = 0
    while k < len(pts) - 1:
        m = len(pts) - 1
        while m > k + 1 and not _clear_line(ok, pts[k], pts[m]):
            m -= 1
        out.append(pts[m]); k = m
    return out


def route(board, netname, a, b, w, classes, via=(0.45, 0.2), margin=6.0, layers=('F', 'B'), via_cost_mm=1.5,
          neck=None, commit=True, lock=True, box=None, forbid=()):
    """a, b: (x, y) points inside same-net copper (pad/track/via) to join. Returns (ok, info)."""
    if box:
        x0, y0, x1, y1 = box
    else:
        bx0, by0, bx1, by1 = board_box(board)
        x0 = max(bx0, min(a[0], b[0]) - margin); x1 = min(bx1, max(a[0], b[0]) + margin)
        y0 = max(by0, min(a[1], b[1]) - margin); y1 = min(by1, max(a[1], b[1]) + margin)
    reg = Region(x0, y0, x1, y1)
    dist, edist, same = build(board, reg, netname, classes)
    clr = net_clearance(netname, classes)
    okmap = {ln: allowed(dist, edist, ln, w, clr) for ln in layers}
    viaok = np.ones((reg.H, reg.W), dtype=bool)
    for ln in LAYERS:
        viaok &= allowed(dist, edist, ln, via[0], clr)
    viaok &= ~hole_mask(board, reg, via[1])
    for fl, fx0, fy0, fx1, fy1 in forbid:          # keep-out boxes for this route ('F', 'B' or '*' = both + vias)
        i0, j0 = [max(0, int(v)) for v in reg.px(fx0, fy0)]
        i1, j1 = [int(math.ceil(v)) for v in reg.px(fx1, fy1)]
        for ln in (layers if fl == '*' else [fl]):
            if ln in okmap:
                okmap[ln][j0:j1, i0:i1] = False
        viaok[j0:j1, i0:i1] = False
    # start/goal: same-net copper cells connected to a / b (flood within same-net copper on the layer holding the point)
    def seeds(pt):
        out = set()
        i, j = [int(v) for v in reg.px(*pt)]
        for ln in layers:
            if 0 <= i < reg.W and 0 <= j < reg.H and same[ln][j, i]:
                lab, _ = ndimage.label(same[ln])
                comp = lab == lab[j, i]
                okc = comp & okmap[ln]
                if not okc.any() and neck:
                    okc = comp & allowed(dist, edist, ln, neck, clr)
                    okmap[ln] |= okc
                jj, ii = np.nonzero(okc)
                out |= {(ln, int(x), int(y)) for x, y in zip(ii, jj)}
        return out
    S, G = seeds(a), seeds(b)
    if not S or not G:
        return False, 'no seeds S%d G%d' % (len(S), len(G))
    path, n = astar(okmap, viaok, S, G, via_cost_mm / RES)
    if not path:
        return False, 'no path (%d expanded)' % n
    # split into layer runs
    runs, cur = [], [path[0]]
    for p in path[1:]:
        if p[0] != cur[-1][0]:
            runs.append(cur); cur = [p]
        else:
            cur.append(p)
    runs.append(cur)
    net = board.FindNet(netname)
    segs, vias = [], []
    for k, r in enumerate(runs):
        pts = smooth(r, okmap[r[0][0]])
        for p, q in zip(pts, pts[1:]):
            segs.append((r[0][0], reg.mm(*p), reg.mm(*q)))
        if k < len(runs) - 1:
            vias.append(reg.mm(r[-1][1], r[-1][2]))
    if commit:
        for ln, p, q in segs:
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pcbnew.VECTOR2I(MM(p[0]), MM(p[1]))); t.SetEnd(pcbnew.VECTOR2I(MM(q[0]), MM(q[1])))
            t.SetWidth(MM(w)); t.SetLayer(LAYERS[ln]); t.SetNet(net); t.SetLocked(lock)
            board.Add(t)
        for p in vias:
            v = pcbnew.PCB_VIA(board)
            v.SetPosition(pcbnew.VECTOR2I(MM(p[0]), MM(p[1]))); v.SetWidth(MM(via[0])); v.SetDrill(MM(via[1]))
            v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(net); v.SetLocked(lock)
            board.Add(v)
    length = sum(math.hypot(q[0] - p[0], q[1] - p[1]) for _, p, q in segs)
    return True, 'segs %d vias %d len %.1f mm (%d expanded)' % (len(segs), len(vias), length, n)


def rip_at(board, x, y, net=None, tol=0.02, chain=True):
    """Remove the via / track ends at (x, y) (optionally net-filtered); with chain, follow connected track segments
    until a pad or junction. Returns count removed."""
    tolv = MM(tol)
    items = [t for t in board.GetTracks() if not net or t.GetNetname() == net]
    gone = set()
    frontier = [pcbnew.VECTOR2I(MM(x), MM(y))]
    seen = set()
    while frontier:
        q = frontier.pop()
        key = (q.x // 1000, q.y // 1000)
        if key in seen:
            continue
        seen.add(key)
        ends_here = []
        for k, t in enumerate(items):
            if k in gone:
                continue
            if t.GetClass() == 'PCB_VIA':
                if (t.GetPosition() - q).EuclideanNorm() <= tolv:
                    gone.add(k)
                continue
            s, e = t.GetStart(), t.GetEnd()
            if (s - q).EuclideanNorm() <= tolv:
                ends_here.append((k, e))
            elif (e - q).EuclideanNorm() <= tolv:
                ends_here.append((k, s))
        for k, other in ends_here:
            gone.add(k)
            if chain and len(ends_here) <= 2:
                frontier.append(other)
    for k in sorted(gone):
        board.Remove(items[k])
        GRAVE.append(items[k])      # keep the wrapper alive: letting it die after Remove corrupts the SWIG type table
    return len(gone)


def tracks_near(board, x, y, r=0.3, net=None):
    P = pcbnew.VECTOR2I(MM(x), MM(y))
    out = []
    for t in board.GetTracks():
        if net and t.GetNetname() != net:
            continue
        if t.GetClass() == 'PCB_VIA':
            if (t.GetPosition() - P).EuclideanNorm() <= MM(r):
                out.append(t)
        else:
            s, e = t.GetStart(), t.GetEnd()
            d = e - s
            L2 = d.x * d.x + d.y * d.y
            u = 0 if L2 == 0 else max(0, min(1, ((P.x - s.x) * d.x + (P.y - s.y) * d.y) / L2))
            cx, cy = s.x + u * d.x, s.y + u * d.y
            if math.hypot(P.x - cx, P.y - cy) <= MM(r) + t.GetWidth() / 2:
                out.append(t)
    return out


def drop_via(board, netname, pt, classes, w=0.3, via=(0.6, 0.3), layer='B', margin=4.0):
    """Connect same-net copper at pt (on `layer`) to a new via (for plane nets): shortest path to a via-legal cell."""
    bx0, by0, bx1, by1 = board_box(board)
    x0, y0 = max(bx0, pt[0] - margin), max(by0, pt[1] - margin)
    x1, y1 = min(bx1, pt[0] + margin), min(by1, pt[1] + margin)
    reg = Region(x0, y0, x1, y1)
    dist, edist, same = build(board, reg, netname, classes)
    clr = net_clearance(netname, classes)
    ok = allowed(dist, edist, layer, w, clr)
    viaok = np.ones((reg.H, reg.W), dtype=bool)
    for ln in LAYERS:
        viaok &= allowed(dist, edist, ln, via[0], clr)
    viaok &= ~hole_mask(board, reg, via[1])
    i, j = [int(v) for v in reg.px(*pt)]
    lab, _ = ndimage.label(same[layer])
    comp = lab == lab[j, i]
    starts = {(layer, int(a), int(b)) for b, a in zip(*np.nonzero(comp & ok))}
    goals = {(layer, int(a), int(b)) for b, a in zip(*np.nonzero(viaok & ok & ~comp))}
    if not starts or not goals:
        return False, 'no seeds'
    path, n = astar({layer: ok}, np.zeros_like(viaok), starts, goals, 1e9)
    if not path:
        return False, 'no path'
    pts = smooth(path, ok)
    net = board.FindNet(netname)
    for p, q in zip(pts, pts[1:]):
        a, c = reg.mm(*p), reg.mm(*q)
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1]))); t.SetEnd(pcbnew.VECTOR2I(MM(c[0]), MM(c[1])))
        t.SetWidth(MM(w)); t.SetLayer(LAYERS[layer]); t.SetNet(net); t.SetLocked(True); board.Add(t)
    vx, vy = reg.mm(*pts[-1])
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I(MM(vx), MM(vy))); v.SetWidth(MM(via[0])); v.SetDrill(MM(via[1]))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(net); v.SetLocked(True); board.Add(v)
    return True, 'via at %.2f,%.2f' % (vx, vy)


def stitch(board, classes, netname='GND', via=(0.6, 0.3), min_area=1.0):
    """Give every F/B fill island of `netname` that holds no via of the net one stitching via (to the In1 plane)."""
    vias = [(t.GetPosition().x * T, t.GetPosition().y * T) for t in board.GetTracks()
            if t.GetClass() == 'PCB_VIA' and t.GetNetname() == netname]
    added = []
    todo = []
    for z in board.Zones():
        if z.GetNetname() != netname or z.GetLayer() not in (pcbnew.F_Cu, pcbnew.B_Cu):
            continue
        ps = z.GetFilledPolysList(z.GetLayer())
        for i in range(ps.OutlineCount()):
            ch = ps.Outline(i)
            pts = [(ch.CPoint(k).x * T, ch.CPoint(k).y * T) for k in range(ch.PointCount())]
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            todo.append((min(xs), min(ys), max(xs), max(ys), pts))
    for x0, y0, x1, y1, pts in todo:
        reg = Region(x0 - 1.0, y0 - 1.0, x1 + 1.0, y1 + 1.0)
        im = Image.new('1', (reg.W, reg.H), 0)
        ImageDraw.Draw(im).polygon([reg.px(*p) for p in pts], fill=1)
        inside = np.array(im, dtype=bool)
        if inside.sum() * RES * RES < min_area:
            print('stitch: small island %.1f,%.1f-%.1f,%.1f' % (x0, y0, x1, y1))
            continue
        if any(inside[int(reg.px(vx, vy)[1]), int(reg.px(vx, vy)[0])] for vx, vy in vias + [a for a in added]
               if 0 <= reg.px(vx, vy)[0] < reg.W and 0 <= reg.px(vx, vy)[1] < reg.H):
            continue
        dist, edist, same = build(board, reg, netname, classes)
        ok = np.ones_like(inside)
        for ln in LAYERS:
            ok &= allowed(dist, edist, ln, via[0], net_clearance(netname, classes))
        core = ndimage.distance_transform_edt(inside) * RES >= via[0] / 2 + 0.05
        cand = ok & core & ~hole_mask(board, reg, via[1])
        if not cand.any():
            print('stitch: no via spot in island %.1f,%.1f-%.1f,%.1f (%.1f mm2)' % (x0, y0, x1, y1, inside.sum() * RES * RES))
            continue
        score = ndimage.distance_transform_edt(cand)
        j, i = np.unravel_index(np.argmax(score), score.shape)
        x, y = [float(v) for v in reg.mm(int(i), int(j))]
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y))); v.SetWidth(MM(via[0])); v.SetDrill(MM(via[1]))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(board.FindNet(netname)); v.SetLocked(True)
        board.Add(v)
        added.append((x, y))
    return added


def relocate(board, ref, target, classes, within=None, rmax=8.0, step=0.25, layer='B'):
    """Move a single-pad footprint (test pad) to the nearest spot around target where its pad copper fits and its
    courtyard clears every other courtyard on that side; optional `within` polygon (mm points) for the pad centre."""
    import fanout as fo
    fp = board.FindFootprintByReference(ref)
    pad = list(fp.Pads())[0]
    side_cy = pcbnew.B_CrtYd if layer == 'B' else pcbnew.F_CrtYd
    others = []
    for f in board.GetFootprints():
        if f.GetReference() == ref:
            continue
        bb = f.GetCourtyard(side_cy).BBox() if f.GetCourtyard(side_cy).OutlineCount() else None
        if bb is not None:
            others.append((bb.GetX() * T, bb.GetY() * T, bb.GetRight() * T, bb.GetBottom() * T))
    bx0, by0, bx1, by1 = board_box(board)
    reg = Region(max(bx0, target[0] - rmax - 3), max(by0, target[1] - rmax - 3), min(bx1, target[0] + rmax + 3),
                 min(by1, target[1] + rmax + 3))
    old = fp.GetPosition()
    fp.SetPosition(pcbnew.VECTOR2I(MM(-50), MM(-50)))       # out of the way while rasterising
    dist, edist, same = build(board, reg, '__none__', classes)
    psz = pad.GetSize().x * T
    ok = allowed(dist, edist, layer, psz, max(0.2, net_clearance(pad.GetNetname(), classes)))
    r = 0.0
    while r <= rmax:
        n = max(1, int(2 * math.pi * r / step))
        for k in range(n):
            a = 2 * math.pi * k / n
            x, y = target[0] + r * math.cos(a), target[1] + r * math.sin(a)
            if within and not fo.inside(within, x, y):
                continue
            i, j = [int(v) for v in reg.px(x, y)]
            if not (0 <= i < reg.W and 0 <= j < reg.H) or not ok[j, i]:
                continue
            fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
            bb = fp.GetCourtyard(side_cy).BBox()
            c = (bb.GetX() * T, bb.GetY() * T, bb.GetRight() * T, bb.GetBottom() * T)
            if any(not (c[2] <= o[0] or c[0] >= o[2] or c[3] <= o[1] or c[1] >= o[3]) for o in others):
                continue
            return True, (round(x, 2), round(y, 2))
        r += step
    fp.SetPosition(old)
    return False, None


def remove_segments(board, net, pairs, tol=0.02):
    """Remove the tracks of `net` whose end points match one of the (x1, y1, x2, y2) pairs (either direction)."""
    n = 0
    tv = MM(tol)
    for t in list(board.GetTracks()):
        if t.GetNetname() != net or t.GetClass() == 'PCB_VIA':
            continue
        s, e = t.GetStart(), t.GetEnd()
        for x1, y1, x2, y2 in pairs:
            a, c = pcbnew.VECTOR2I(MM(x1), MM(y1)), pcbnew.VECTOR2I(MM(x2), MM(y2))
            if ((s - a).EuclideanNorm() <= tv and (e - c).EuclideanNorm() <= tv) or \
               ((s - c).EuclideanNorm() <= tv and (e - a).EuclideanNorm() <= tv):
                remove(board, t); n += 1
                break
    return n


def relocate_fp(board, ref, target, classes, rmax=6.0, step=0.25, rots=(0, 90, 180, 270)):
    """Move a (back-side) footprint to the nearest spot around target where every pad's copper (taken as the circle
    over its larger side) clears other copper and its courtyard clears every other back courtyard."""
    fp = board.FindFootprintByReference(ref)
    others = []
    for f in board.GetFootprints():
        if f.GetReference() == ref or not f.GetCourtyard(pcbnew.B_CrtYd).OutlineCount():
            continue
        bb = f.GetCourtyard(pcbnew.B_CrtYd).BBox()
        others.append((bb.GetX() * T, bb.GetY() * T, bb.GetRight() * T, bb.GetBottom() * T))
    bx0, by0, bx1, by1 = board_box(board)
    reg = Region(max(bx0, target[0] - rmax - 4), max(by0, target[1] - rmax - 4), min(bx1, target[0] + rmax + 4),
                 min(by1, target[1] + rmax + 4))
    old_pos, old_rot = fp.GetPosition(), fp.GetOrientationDegrees()
    fp.SetPosition(pcbnew.VECTOR2I(MM(-50), MM(-50)))
    dist, edist, same = build(board, reg, '__none__', classes)
    maps = {}
    r = 0.0
    while r <= rmax:
        n = max(1, int(2 * math.pi * r / step))
        for k in range(n):
            a = 2 * math.pi * k / n
            x, y = target[0] + r * math.cos(a), target[1] + r * math.sin(a)
            for rot in rots:
                fp.SetOrientationDegrees(rot)
                fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
                good = True
                for p in fp.Pads():
                    w = max(p.GetSize().x, p.GetSize().y) * T
                    cl = max(0.2, net_clearance(p.GetNetname(), classes))
                    key = (round(w, 3), cl)
                    if key not in maps:
                        maps[key] = allowed(dist, edist, 'B', w, cl)
                    i, j = [int(v) for v in reg.px(p.GetPosition().x * T, p.GetPosition().y * T)]
                    if not (0 <= i < reg.W and 0 <= j < reg.H and maps[key][j, i]):
                        good = False; break
                if not good:
                    continue
                bb = fp.GetCourtyard(pcbnew.B_CrtYd).BBox()
                c = (bb.GetX() * T, bb.GetY() * T, bb.GetRight() * T, bb.GetBottom() * T)
                if any(not (c[2] <= o[0] or c[0] >= o[2] or c[3] <= o[1] or c[1] >= o[3]) for o in others):
                    continue
                return True, (round(x, 2), round(y, 2), rot)
        r += step
    fp.SetPosition(old_pos); fp.SetOrientationDegrees(old_rot)
    return False, None
