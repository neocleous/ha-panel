"""Main board rev 3 - routing (KiCad 9 pcbnew). No external autorouter: the repository's own maze router (mroute.py)
routes every connection, in this order:
  1 power   wide paths laid by hand (coordinates below) or maze-routed wide, vias into the layer-3 plane areas
  2 planes  one via per surface-mount pad of GND, +5V, +20V and PVDD
  3 signals every other net, shortest open connection first
  4 finish  GND pours on both outer layers, stitching vias, loose ends removed
Run: python3 route_rev3.py <board in> <board out> [stage ...]      stages: power planes signals finish (default: all)
"""
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault('HA_PRETTY', os.path.join(HERE, '..', 'lib', 'ha_panel.pretty'))
import pcbnew                      # noqa: E402
import mroute                      # noqa: E402
import fastgrid                    # noqa: E402
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw
import fanout as fo                # noqa: E402
import route_main as rm            # noqa: E402
import pcb_rev3 as pb              # noqa: E402

fastgrid.patch(mroute)             # compiled grid search (scikit-image) in place of the Python A*
MM, TO = pcbnew.FromMM, pcbnew.ToMM
X, Y = pb.X, pb.Y
N5 = '/5 V supply and outputs/'
NEF = '/20 V inlet and eFuse/'
N3 = '/3.3 V, Pi link, sensors, radar, echo-ref/'
NA = '/Amplifier/'
CLASSES = dict(rm.CLASSES)
PLANE = ('GND', '+5V', '+20V', NA + 'PVDD')


def cls(net):
    for name, (tw, cl, vd, vdr, nets) in CLASSES.items():
        if net in nets:
            return tw, cl, vd, vdr
    return 0.2, 0.15, 0.45, 0.2            # signals


def pad_xy(b, ref, num):
    fp = b.FindFootprintByReference(ref)
    p = [q for q in fp.Pads() if q.GetNumber() == num][0].GetPosition()
    return (TO(p.x), TO(p.y))


def trk(b, net, pts_uv, w, layer):
    n = b.FindNet(net)
    for a, c in zip(pts_uv, pts_uv[1:]):
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(pcbnew.VECTOR2I(MM(X(a[0])), MM(Y(a[1])))); t.SetEnd(pcbnew.VECTOR2I(MM(X(c[0])), MM(Y(c[1]))))
        t.SetWidth(MM(w)); t.SetLayer(layer); t.SetNet(n); t.SetLocked(True)
        b.Add(t)


def via(b, net, u, v, d=0.8, drill=0.4):
    x = pcbnew.PCB_VIA(b)
    x.SetPosition(pcbnew.VECTOR2I(MM(X(u)), MM(Y(v)))); x.SetWidth(MM(d)); x.SetDrill(MM(drill))
    x.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); x.SetNet(b.FindNet(net)); x.SetLocked(True)
    b.Add(x)


def uvpad(b, ref, num):
    x, y = pad_xy(b, ref, num)
    return (x - pb.U0, pb.V0 - y)


def anchor_ends(b, net, before):
    """The search starts and stops anywhere in copper of the net, often at its rim. Run each new free end on to the
    centre of what it touches (via centre, centre line of a track, pad centre) so that KiCad counts the joint."""
    from collections import Counter
    new = [t for t in b.GetTracks() if t.m_Uuid.AsString() not in before]
    segs = [t for t in new if t.Type() != pcbnew.PCB_VIA_T]
    nv = [(TO(v.GetPosition().x), TO(v.GetPosition().y)) for v in new if v.Type() == pcbnew.PCB_VIA_T]
    ends = Counter()
    wid = {}
    for t in segs:
        lns, p, q, w = _geom(t)
        for pt in (p, q):
            k = (lns[0], round(pt[0], 4), round(pt[1], 4))
            ends[k] += 1
            wid[k] = w
    others = [_geom(t) for t in b.GetTracks() if t.GetNetname() == net and t.m_Uuid.AsString() in before]
    pads = [p for fp in b.GetFootprints() for p in fp.Pads() if p.GetNetname() == net]
    added = 0
    for (ln, x, y), cnt in ends.items():
        if cnt != 1 or any(math.hypot(x - vx, y - vy) < 1e-3 for vx, vy in nv):
            continue
        best = None
        for lns, p, q, w in others:
            if ln not in lns:
                continue
            dx, dy = q[0] - p[0], q[1] - p[1]
            L2 = dx * dx + dy * dy
            tt = 0.0 if L2 < 1e-12 else max(0.0, min(1.0, ((x - p[0]) * dx + (y - p[1]) * dy) / L2))
            pr = (p[0] + tt * dx, p[1] + tt * dy)
            d = math.hypot(pr[0] - x, pr[1] - y)
            if d <= w / 2 + 0.04 and (best is None or d < best[0]):
                best = (d, pr, w)
        P = pcbnew.VECTOR2I(MM(x), MM(y))
        if best is None:
            for pd in pads:
                if pd.IsOnLayer(mroute.LAYERS[ln]) and pd.HitTest(P, MM(0.04)):
                    c = (TO(pd.GetPosition().x), TO(pd.GetPosition().y))
                    d = math.hypot(c[0] - x, c[1] - y)
                    if best is None or d < best[0]:
                        best = (d, c, wid[(ln, x, y)])
        if best is None or best[0] < 1e-3:
            continue
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(P); t.SetEnd(pcbnew.VECTOR2I(MM(best[1][0]), MM(best[1][1])))
        t.SetWidth(MM(max(0.15, min(wid[(ln, x, y)], best[2])))); t.SetLayer(mroute.LAYERS[ln]); t.SetNet(b.FindNet(net)); t.SetLocked(True)
        b.Add(t)
        added += 1
    return added


def _ids(b):
    return {t.m_Uuid.AsString() for t in b.GetTracks()}


def maze(b, net, a, c, w=None, layers=('F', 'B'), via_=None, res=0.05, margin=6.0, neck=None, via_cost=1.5):
    tw, cl, vd, vdr = cls(net)
    mroute.RES = res
    before = _ids(b)
    ok, info = mroute.route(b, net, a, c, w or tw, CLASSES, via=via_ or (vd, vdr), layers=layers, margin=margin, neck=neck,
                            via_cost_mm=via_cost)
    if ok:
        anchor_ends(b, net, before)
    return ok, info


def bridge(b, net, a, c, w=0.2, res=0.05, layers=('F', 'B')):
    """a and c sit in copper of one net that already touches, but no track end lands on the other piece, so KiCad
    does not count them as joined. Lay a thin track inside that copper from a to c."""
    mroute.RES = res
    reg = mroute.Region(min(a[0], c[0]) - 3, min(a[1], c[1]) - 3, max(a[0], c[0]) + 3, max(a[1], c[1]) + 3)
    dist, edist, same = mroute.build(b, reg, net, CLASSES)
    clr = mroute.net_clearance(net, CLASSES)
    ia, ja = [int(v) for v in reg.px(*a)]
    ic, jc = [int(v) for v in reg.px(*c)]
    best = None
    for ln in layers:
        inner = ndimage.distance_transform_edt(same[ln]) * res >= w / 2
        ok = mroute.allowed(dist, edist, ln, w, clr) | inner
        if not (same[ln][ja, ia] and same[ln][jc, ic]):
            continue
        ok[ja, ia] = ok[jc, ic] = True
        path, _ = fastgrid.astar({ln: ok}, np.zeros_like(ok), {(ln, ia, ja)}, {(ln, ic, jc)}, 0)
        if not path:
            continue
        pts = [reg.mm(*p) for p in fastgrid.smooth(path, ok)]
        pts[0], pts[-1] = a, c
        length = sum(math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(pts, pts[1:]))
        if best is None or length < best[0]:
            best = (length, ln, pts)
    if not best:
        return False, 'touching copper, no way through it'
    _, ln, pts = best
    for p, q in zip(pts, pts[1:]):
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(pcbnew.VECTOR2I(MM(p[0]), MM(p[1]))); t.SetEnd(pcbnew.VECTOR2I(MM(q[0]), MM(q[1])))
        t.SetWidth(MM(w)); t.SetLayer(mroute.LAYERS[ln]); t.SetNet(b.FindNet(net)); t.SetLocked(True)
        b.Add(t)
    return True, 'bridge %s %.1f mm' % (ln, best[0])


def pin_stubs(b, ref, length=0.6, w=0.2):
    """Fine-pitch chip: give every single signal pin a short straight track out past the pad row, so that the route
    of one pin cannot turn across the way out of its neighbour."""
    fp = b.FindFootprintByReference(ref)
    c = fp.GetPosition()
    count = {}
    for p in fp.Pads():
        count[p.GetNetname()] = count.get(p.GetNetname(), 0) + 1
    n = 0
    for p in fp.Pads():
        net = p.GetNetname()
        if not net or net == 'GND' or net.startswith('unconnected') or count[net] > 1 or p.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
            continue
        bb = p.GetBoundingBox()
        px, py = p.GetPosition().x, p.GetPosition().y
        if bb.GetWidth() > bb.GetHeight():           # pad lies along x: leave along x, away from the chip centre
            ex = bb.GetRight() + MM(length) if px > c.x else bb.GetX() - MM(length)
            end = pcbnew.VECTOR2I(ex, py)
        else:
            ey = bb.GetBottom() + MM(length) if py > c.y else bb.GetY() - MM(length)
            end = pcbnew.VECTOR2I(px, ey)
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(p.GetPosition()); t.SetEnd(end); t.SetWidth(MM(w)); t.SetLayer(pcbnew.F_Cu); t.SetNet(p.GetNet()); t.SetLocked(True)
        b.Add(t)
        n += 1
    return n


# ------------------------------------------------------------------ 1 power
def stage_power(b):
    F, B = pcbnew.F_Cu, pcbnew.B_Cu
    log = []
    # Right speaker: both conductors side by side on the back, 1.0 wide, from beside the amplifier to J9.
    # They run in the strip under the supply module's pin row and then down between the radar and BME680 connectors;
    # everything that has to cross them does so on the door side.
    trk(b, '/Amplifier/SPK_R_P', [(13.0, -2.25), (-37.9, -2.25), (-37.9, -21.5), (-40.25, -23.85), (-40.25, -25.0)], 1.0, B)
    trk(b, '/Amplifier/SPK_R_N', [(13.0, -3.55), (-36.6, -3.55), (-36.6, -22.5), (-37.75, -23.65), (-37.75, -25.0)], 1.0, B)
    # 20 V in: socket pin 1 -> fuse F1 (door-side copper, 1.0 wide)
    a, c = uvpad(b, 'J1', '1'), uvpad(b, 'F1', '1')
    trk(b, NEF + 'VIN_PIGTAIL', [a, (a[0] - 1.2, c[1]), c], 1.0, F)
    # fuse F1 -> inlet protection U1 input pins (maze, 0.6 wide; pins 1-3 are already bridged)
    log.append(('VIN_EF F1-U1', maze(b, NEF + 'VIN_EF', pad_xy(b, 'F1', '2'), pad_xy(b, 'U1', '2'), w=0.6, layers=('F',), neck=0.3)))
    # U1 output pins (bridged) -> three vias into the +20V area of layer 3, wherever the router finds room next to the pins
    for num in ('19', '20', '18'):
        mroute.RES = 0.05
        log.append(('+20V via at U1.' + num, mroute.drop_via(b, '+20V', pad_xy(b, 'U1', num), CLASSES, w=0.4, via=(0.8, 0.4), layer='F')))
    # 20 V filter coil L1 pad 1 and amplifier fuse F5 pad 1 -> +20V area; F5 pad 2 -> PVDD area
    for ref, num, net, side in (('L1', '1', '+20V', 1), ('F5', '1', '+20V', -1), ('F5', '2', NA + 'PVDD', 1)):
        p = uvpad(b, ref, num)
        hw = TO([q for q in b.FindFootprintByReference(ref).Pads() if q.GetNumber() == num][0].GetBoundingBox().GetWidth()) / 2
        for dv in (-1.6, 0.0, 1.6):
            u = p[0] + side * (hw + 0.75)
            trk(b, net, [(p[0], p[1] + dv), (u, p[1] + dv)], 0.8, F)
            via(b, net, u, p[1] + dv)
    # supply module input: coil L1 pad 2 -> C6 pad 1 on the door side; C6 pad 1 -> module pins 9 and 10 on the back, 1.8 wide
    c6, l1 = uvpad(b, 'C6', '1'), uvpad(b, 'L1', '2')
    trk(b, N5 + 'NID_VIN', [(l1[0] - 0.6, c6[1]), c6], 1.5, F)
    p9, p10 = uvpad(b, 'PS1', '9'), uvpad(b, 'PS1', '10')
    mid = ((p9[0] + p10[0]) / 2, p9[1])
    trk(b, N5 + 'NID_VIN', [p10, p9], 1.6, B)
    trk(b, N5 + 'NID_VIN', [mid, (mid[0], c6[1] - 2.4), c6], 1.8, B)
    # 5 V: fuse F2 pad 1 -> four vias into the +5V area (supply module pins 1-4 and C7 are through-hole in that area)
    f21 = uvpad(b, 'F2', '1')
    for (du, dv) in ((-1.75, 1.0), (-1.75, -0.9), (-0.55, 2.3), (0.55, 2.3)):
        trk(b, '+5V', [(f21[0] + (0 if abs(du) < 1 else -0.6), f21[1] + (1.2 if abs(du) < 1 else dv)), (f21[0] + du, f21[1] + dv)], 0.8, F)
        via(b, '+5V', f21[0] + du, f21[1] + dv)
    # Pi branch: fuse F2 pad 2 -> wire link LK1 pad 1 (door side, 1.5 wide)
    log.append(('5V_PI_F F2-LK1', maze(b, N5 + '5V_PI_F', pad_xy(b, 'F2', '2'), pad_xy(b, 'LK1', '1'), w=1.5, layers=('F',))))
    # wire link LK1 pad 2 -> USB-C socket VBUS pins: bar on the back, two 0.6 necks into pins A4 and A9
    lk = uvpad(b, 'LK1', '2'); a4, a9 = uvpad(b, 'J2', 'A4'), uvpad(b, 'J2', 'A9')
    bar_v = a4[1] + 1.75
    trk(b, N5 + 'VBUS_PI', [lk, (lk[0], lk[1] - 5.0), (lk[0] + 1.6, bar_v)], 2.0, B)
    trk(b, N5 + 'VBUS_PI', [(lk[0] + 1.6, bar_v), (a9[0], bar_v)], 1.4, B)
    for p in (a4, a9):
        trk(b, N5 + 'VBUS_PI', [(p[0], bar_v), p], 0.6, B)
    return log


# ------------------------------------------------------------------ 2 planes
def connected_to_via(b, pad):
    conn = b.GetConnectivity()
    seen, todo = set(), list(conn.GetConnectedTracks(pad))
    while todo:
        t = todo.pop()
        k = t.m_Uuid.AsString()
        if k in seen:
            continue
        seen.add(k)
        if t.Type() == pcbnew.PCB_VIA_T:
            return True
        todo += list(conn.GetConnectedTracks(t))
    return False


def stage_planes(b):
    """One via for every surface-mount pad of a plane net that has none yet."""
    b.BuildConnectivity()
    todo = []
    for fp in b.GetFootprints():
        for p in fp.Pads():
            n = p.GetNetname()
            if n in PLANE and not p.HasHole() and p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD and p.IsOnLayer(pcbnew.F_Cu):
                if not connected_to_via(b, p):
                    todo.append((fp.GetReference(), p.GetNumber(), n, (TO(p.GetPosition().x), TO(p.GetPosition().y))))
    zones = {'+5V': [pb.P5], '+20V': [pb.P20], NA + 'PVDD': [pb.PPV, pb.PPV_FEED]}
    ok_n, bad = 0, []
    done_pads = set()
    for ref, num, n, pt in todo:
        if (ref, n) in done_pads and ref.startswith(('U1', 'U100')):
            continue
        before = {t.m_Uuid.AsString() for t in b.GetTracks()}
        mroute.RES = 0.05
        ok, info = mroute.drop_via(b, n, pt, CLASSES, w=0.3 if n == 'GND' else 0.5, via=(0.6, 0.3), layer='F', margin=3.0)
        if ok and n != 'GND':
            vx, vy = [float(s) for s in info.split('at ')[1].split(',')]
            if not any(fo.inside(z, vx, vy) for z in zones[n]):
                for t in list(b.GetTracks()):
                    if t.m_Uuid.AsString() not in before:
                        b.Remove(t)
                ok, info = False, 'nearest via spot is outside the %s area' % n.split('/')[-1]
        if ok:
            ok_n += 1
            done_pads.add((ref, n))
        else:
            bad.append('%s.%s %s (%s)' % (ref, num, n.split('/')[-1], info))
        b.BuildConnectivity()
    return ok_n, bad


# ------------------------------------------------------------------ 3 signals
def clusters(b, net):
    """Connected groups of a net's pads/tracks: list of point lists (KiCad mm)."""
    conn = b.GetConnectivity()
    items = {}
    parent = {}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def add(k, pts):
        if k not in parent:
            parent[k] = k
            items[k] = pts
    pads = [p for fp in b.GetFootprints() for p in fp.Pads() if p.GetNetname() == net]
    tracks = [t for t in b.GetTracks() if t.GetNetname() == net]
    for p in pads:
        add('P' + p.m_Uuid.AsString() + p.GetNumber() + str(p.GetPosition().x) + str(p.GetPosition().y), [(TO(p.GetPosition().x), TO(p.GetPosition().y))])
    key = {}
    for p in pads:
        key[(p.GetParentFootprint().GetReference(), p.GetNumber(), p.GetPosition().x, p.GetPosition().y)] = \
            'P' + p.m_Uuid.AsString() + p.GetNumber() + str(p.GetPosition().x) + str(p.GetPosition().y)
    for t in tracks:
        if t.Type() == pcbnew.PCB_VIA_T:
            pts = [(TO(t.GetPosition().x), TO(t.GetPosition().y))]
        else:
            pts = [(TO(t.GetStart().x), TO(t.GetStart().y)), (TO(t.GetEnd().x), TO(t.GetEnd().y))]
        add('T' + t.m_Uuid.AsString(), pts)
    for t in tracks:
        kt = 'T' + t.m_Uuid.AsString()
        for q in conn.GetConnectedTracks(t):
            kq = 'T' + q.m_Uuid.AsString()
            if kq in parent:
                parent[find(kt)] = find(kq)
        for p in conn.GetConnectedPads(t):
            kp = key.get((p.GetParentFootprint().GetReference(), p.GetNumber(), p.GetPosition().x, p.GetPosition().y))
            if kp:
                parent[find(kt)] = find(kp)
    for p in pads:                                   # pads of one footprint that share a number and touch (exposed pads)
        for q in conn.GetConnectedPads(p):
            kq = key.get((q.GetParentFootprint().GetReference(), q.GetNumber(), q.GetPosition().x, q.GetPosition().y))
            kp = key[(p.GetParentFootprint().GetReference(), p.GetNumber(), p.GetPosition().x, p.GetPosition().y)]
            if kq:
                parent[find(kp)] = find(kq)
    # copper areas on the inner layers join every via and through-hole pad of their net that sits in their filled copper
    zs = [(z, lid) for z in b.Zones() if z.GetNetname() == net and not z.GetIsRuleArea() for lid in (pcbnew.In1_Cu, pcbnew.In2_Cu)
          if z.IsOnLayer(lid)]
    if zs:
        thru = [(key[(p.GetParentFootprint().GetReference(), p.GetNumber(), p.GetPosition().x, p.GetPosition().y)], p.GetPosition())
                for p in pads if p.HasHole()]
        thru += [('T' + t.m_Uuid.AsString(), t.GetPosition()) for t in tracks if t.Type() == pcbnew.PCB_VIA_T]
        for z, lid in zs:
            first = None
            for k, pos in thru:
                if z.HitTestFilledArea(lid, pos):
                    if first is None:
                        first = k
                    else:
                        parent[find(k)] = find(first)
    groups = {}
    for k in parent:
        groups.setdefault(find(k), []).extend(items[k])
    return list(groups.values())


def closest(g1, g2):
    best = None
    for a in g1:
        for c in g2:
            d = math.hypot(a[0] - c[0], a[1] - c[1])
            if best is None or d < best[0]:
                best = (d, a, c)
    return best


def open_edges(b, net):
    """Minimum spanning set of open connections between the net's groups: [(length, a, c)]."""
    gs = clusters(b, net)
    if len(gs) < 2:
        return []
    done, rest, edges = [gs[0]], gs[1:], []
    while rest:
        best = None
        for i, g in enumerate(rest):
            for h in done:
                c = closest(h, g)
                if best is None or c[0] < best[0][0]:
                    best = (c, i)
        edges.append(best[0])
        done.append(rest.pop(best[1]))
    return edges


def signal_nets(b):
    nets = set()
    for fp in b.GetFootprints():
        for p in fp.Pads():
            n = p.GetNetname()
            if n and not n.startswith('unconnected') and n != 'GND':
                nets.add(n)
    return sorted(nets)


def layers_at(b, net, pt, tol=0.02):
    """Copper layers of the net's own items (pad, track end, via) that sit at pt."""
    L = set()
    P = pcbnew.VECTOR2I(MM(pt[0]), MM(pt[1]))
    near = lambda q: (q - P).EuclideanNorm() < MM(tol)
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.GetNetname() == net and near(p.GetPosition()):
                L |= {ln for ln, lid in mroute.LAYERS.items() if p.IsOnLayer(lid)}
    for t in b.GetTracks():
        if t.GetNetname() != net:
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            if near(t.GetPosition()):
                L |= {'F', 'B'}
        elif near(t.GetStart()) or near(t.GetEnd()):
            L |= {ln for ln, lid in mroute.LAYERS.items() if t.GetLayer() == lid}
    return L


WIDE = {'SPK_L_P': (0.8, 0.4), 'SPK_L_N': (0.8, 0.4), 'SPK_R_P': (1.0, 0.7, 0.4), 'SPK_R_N': (1.0, 0.7, 0.4)}
THIN = []          # connections that had to be made narrower than their class: (net, width, length text)


def join(b, n, a, c):
    """One open connection of net n between points a and c. Returns (ok, info)."""
    tw, cl, vd, vdr = cls(n)
    short = n.split('/')[-1]
    widths = list(WIDE.get(short, (tw,)))
    for w in (0.3, 0.2):
        if widths[-1] > w:
            widths.append(w)
    info = ''
    for w in widths:
        for margin in (6.0, 20.0):
            ok, info = maze(b, n, a, c, w=w, margin=margin, neck=0.15 if w > 0.15 else None,
                            via_cost=6.0 if short in WIDE else 1.5, via_=(0.8, 0.4) if short in WIDE else None)
            if ok and info.startswith('segs 0'):       # the two pieces already touch somewhere
                common = layers_at(b, n, a) & layers_at(b, n, c)
                if common:
                    return bridge(b, n, a, c, layers=common)
                pt = a if layers_at(b, n, a) == {'F'} else c
                before = _ids(b)
                res = mroute.drop_via(b, n, pt, CLASSES, w=min(w, 0.3), via=(vd, vdr), layer='F')
                anchor_ends(b, n, before)
                return res
            if ok:
                if w < tw:
                    THIN.append((short, w, info))
                return ok, info
    return False, info


def _segdist(p1, p2, q1, q2):
    """Shortest distance between two segments (points allowed as zero-length segments)."""
    def pt_seg(p, a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L2 = dx * dx + dy * dy
        t = 0.0 if L2 < 1e-12 else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
        return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)

    def ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) - (b[1] - a[1]) * (c[0] - a[0])
    if (ccw(p1, q1, q2) > 0) != (ccw(p2, q1, q2) > 0) and (ccw(p1, p2, q1) > 0) != (ccw(p1, p2, q2) > 0):
        return 0.0
    return min(pt_seg(p1, q1, q2), pt_seg(p2, q1, q2), pt_seg(q1, p1, p2), pt_seg(q2, p1, p2))


def _geom(t):
    """(layers, start, end, width) of a track or via in mm."""
    if t.Type() == pcbnew.PCB_VIA_T:
        p = (TO(t.GetPosition().x), TO(t.GetPosition().y))
        return ('F', 'B'), p, p, TO(t.GetWidth(pcbnew.F_Cu))
    ln = 'F' if t.GetLayer() == pcbnew.F_Cu else 'B'
    return (ln,), (TO(t.GetStart().x), TO(t.GetStart().y)), (TO(t.GetEnd().x), TO(t.GetEnd().y)), TO(t.GetWidth())


def ripup_join(b, n, a, c, soft_ids, w, penalty=10.0):
    """Route n from a to c as if the tracks laid in this stage for other nets were not there (at a cost), then take
    out the nets it had to cross. Returns (ok, info, nets taken out)."""
    tw, cl, vd, vdr = cls(n)
    softs = [t for t in b.GetTracks() if t.m_Uuid.AsString() in soft_ids and t.GetNetname() != n]
    mroute.RES = 0.05
    box = mroute.board_box(b)
    reg = mroute.Region(*box)
    imgs = {ln: Image.new('1', (reg.W, reg.H), 0) for ln in ('F', 'B')}
    for t in softs:
        lns, p, q, tw_ = _geom(t)
        grow = tw_ + 2 * (max(cl, cls(t.GetNetname())[1]) + w / 2)
        for ln in lns:
            mroute._draw_stadium(ImageDraw.Draw(imgs[ln]), reg, p[0], p[1], q[0], q[1], grow)
    crowd = {ln: np.array(im, dtype=float) * penalty for ln, im in imgs.items()}
    before = {t.m_Uuid.AsString() for t in b.GetTracks()}
    for t in softs:
        b.Remove(t)
    fastgrid.CROWD = crowd
    try:
        ok, info = mroute.route(b, n, a, c, w, CLASSES, via=(vd, vdr), box=box, neck=0.15 if w > 0.15 else None)
    finally:
        fastgrid.CROWD = None
        for t in softs:
            b.Add(t)
    if not ok or info.startswith('segs 0'):
        return False, info, []
    anchor_ends(b, n, before | {t.m_Uuid.AsString() for t in softs if t.GetNetname() == n})
    fresh = [_geom(t) for t in b.GetTracks() if t.m_Uuid.AsString() not in before]
    hit = set()
    for t in softs:
        nn = t.GetNetname()
        if nn in hit:
            continue
        lns, p, q, tw_ = _geom(t)
        need = max(cl, cls(nn)[1])
        for flns, fp_, fq, fw in fresh:
            if set(lns) & set(flns) and _segdist(p, q, fp_, fq) < need + tw_ / 2 + fw / 2 - 0.005:
                hit.add(nn)
                break
    for t in softs:
        if t.GetNetname() in hit:
            b.Remove(t)
    return True, info, sorted(hit)


def stage_signals(b, first=(), max_rips=10):
    b.BuildConnectivity()
    start_ids = {t.m_Uuid.AsString() for t in b.GetTracks()}
    failed = []
    stats = {'routed': 0, 'taken out': 0}
    t0 = time.time()
    work = []
    for n in signal_nets(b):
        for d, a, c in open_edges(b, n):
            work.append((d, n))
    queue = [n for n in signal_nets(b) if n.split('/')[-1] in WIDE and any(n == m for _, m in work)]
    # the protection chip's small nets next: they sit in the tightest corner and need the first pick of the space
    queue += [n for d, n in sorted(work) if n.split('/')[-1].startswith('EF_') and n not in queue]
    queue += [n for n in first if n not in queue]
    for d, n in sorted(work):
        if n not in queue:
            queue.append(n)
    rips = {}
    while queue:
        n = queue.pop(0)
        bad_pairs, tried = set(), set()
        failed = [f for f in failed if f[0] != n]
        while True:
            edges = [e for e in open_edges(b, n) if (round(e[1][0], 2), round(e[1][1], 2), round(e[2][0], 2), round(e[2][1], 2)) not in bad_pairs]
            if not edges:
                break
            d, a, c = min(edges)
            ok, info = join(b, n, a, c)
            pk = (round(a[0], 2), round(a[1], 2), round(c[0], 2), round(c[1], 2))
            if not ok and rips.get(n, 0) < max_rips:
                tw = cls(n)[0]
                soft = {t.m_Uuid.AsString() for t in b.GetTracks() if t.GetNetname().split('/')[-1] not in WIDE} - start_ids
                ok, info, out = ripup_join(b, n, a, c, soft, tw if tw <= 0.25 else 0.3)
                if ok:
                    rips[n] = rips.get(n, 0) + 1
                    stats['taken out'] += len(out)
                    if tw > 0.3:
                        THIN.append((n.split('/')[-1], 0.3, info))
                    for m in out:
                        if m not in queue:
                            queue.append(m)
                    print('  %-18s made room by taking out %s' % (n.split('/')[-1], [m.split('/')[-1] for m in out]), flush=True)
            if ok:
                stats['routed'] += 1
                if pk in tried:                      # routed before and still open: do not loop on it
                    bad_pairs.add(pk)
                    failed.append((n, a, c, 'routed but still open: ' + info))
                tried.add(pk)
            else:
                bad_pairs.add(pk)
                failed.append((n, a, c, info))
            b.BuildConnectivity()
        if bad_pairs:
            print('  %-22s OPEN %d  (%.0f s)' % (n.split('/')[-1], len(bad_pairs), time.time() - t0), flush=True)
    return stats, failed


def signals_loop(src, dst, rounds=1):
    """Route every signal; nets that could not be finished go to the front of the queue and everything is routed again."""
    import shutil
    first, best = [], None
    for it in range(rounds):
        shutil.copy(src, dst)
        shutil.copy(src.replace('.kicad_pcb', '.kicad_pro'), dst.replace('.kicad_pcb', '.kicad_pro'))
        b = pcbnew.LoadBoard(dst)
        pb.rules(b)
        del THIN[:]
        stats, failed = stage_signals(b, first)
        print('round %d: %s, open %d' % (it + 1, stats, len(failed)), flush=True)
        if best is None or len(failed) < best:
            best = len(failed)
            pcbnew.SaveBoard(dst.replace('.kicad_pcb', '_best.kicad_pcb'), b)
            keep = (list(failed), list(THIN))
        if not failed:
            break
        new = []
        for n, a, c, info in failed:
            if n not in new:
                new.append(n)
        first = new + [n for n in first if n not in new]
    shutil.copy(dst.replace('.kicad_pcb', '_best.kicad_pcb'), dst)
    os.remove(dst.replace('.kicad_pcb', '_best.kicad_pcb'))
    for n, a, c, info in keep[0]:
        print('  OPEN', n.split('/')[-1], '(%.1f,%.1f)-(%.1f,%.1f)' % (a[0] - pb.U0, pb.V0 - a[1], c[0] - pb.U0, pb.V0 - c[1]), info)
    for t in keep[1]:
        print('  THIN', t)
    return pcbnew.LoadBoard(dst)


def clean_loose(path, drc_json):
    """Remove vias and track pieces that end in nothing (unused fan-outs carried over from rev 2.1, router leftovers).
    One pass: drc_json is KiCad's check of the saved board (run it first, outside this process: the KiCad Python
    library stops handing out usable track objects once kicad-cli has been started from inside it)."""
    import json
    d = json.load(open(drc_json))
    import re
    hits = []
    for x in d['violations']:
        if x['type'] in ('track_dangling', 'via_dangling'):
            it = x['items'][0]
            mlen = re.search(r'length ([0-9.]+) mm', it['description'])
            hits.append((x['type'], it['pos']['x'], it['pos']['y'], float(mlen.group(1)) if mlen else None))
    if not hits:
        return 0
    b = pcbnew.LoadBoard(path)
    pb.rules(b)
    tracks = list(b.GetTracks())
    info = []                                   # (item, is via, net, layers, start, end, width)
    for t in tracks:
        lns, p, q, w = _geom(t)
        info.append((t, t.Type() == pcbnew.PCB_VIA_T, t.GetNetname(), lns, p, q, w))
    pads = [(p, p.GetNetname()) for fp in b.GetFootprints() for p in fp.Pads()]

    def held(k, pt):
        """Is point pt of track k touched by other copper of its net? (another track's end or body, a via, a pad)"""
        t, _, net, lns, p, q, w = info[k]
        for m, (t2, isvia2, net2, lns2, p2, q2, w2) in enumerate(info):
            if m == k or m in gone or net2 != net or not (set(lns) & set(lns2)):
                continue
            if _segdist(pt, pt, p2, q2) <= w2 / 2 + 0.005:
                return True
        P = pcbnew.VECTOR2I(MM(pt[0]), MM(pt[1]))
        return any(n2 == net and pd.IsOnLayer(mroute.LAYERS[lns[0]]) and pd.HitTest(P) for pd, n2 in pads)

    def taps(k):
        """Points along track k where other copper of its net joins it."""
        t, _, net, lns, p, q, w = info[k]
        out = []
        for m, (t2, isvia2, net2, lns2, p2, q2, w2) in enumerate(info):
            if m == k or m in gone or net2 != net or not (set(lns) & set(lns2)):
                continue
            for pt in (p2, q2):
                if _segdist(pt, pt, p, q) <= w / 2 + 0.005:
                    out.append(pt)
        for pd, n2 in pads:
            if n2 == net and pd.IsOnLayer(mroute.LAYERS[lns[0]]):
                c = (TO(pd.GetPosition().x), TO(pd.GetPosition().y))
                if _segdist(c, c, p, q) <= w / 2 + 0.005:
                    out.append(c)
        return out

    gone, n = set(), 0
    for typ, x, y, length in hits:
        for k, (t, isvia, net, lns, p, q, w) in enumerate(info):
            if k in gone or isvia != (typ == 'via_dangling'):
                continue
            mid = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
            if min(math.hypot(a[0] - x, a[1] - y) for a in (p, q, mid)) > 0.01:
                continue
            if length is not None and abs(math.hypot(q[0] - p[0], q[1] - p[1]) - length) > 0.002:
                continue                                # another track that ends at the same point
            if isvia:
                # tracks that started somewhere on the via's ring lose their joint with it: bring their ends to its centre
                for m, (t2, isvia2, net2, lns2, p2, q2, w2) in enumerate(info):
                    if m == k or m in gone or isvia2 or net2 != net:
                        continue
                    for which, pt in (('s', p2), ('e', q2)):
                        dd = math.hypot(pt[0] - p[0], pt[1] - p[1])
                        if 1e-4 < dd <= w / 2 + 0.005:
                            V = pcbnew.VECTOR2I(MM(p[0]), MM(p[1]))
                            if which == 's':
                                t2.SetStart(V); info[m] = (t2, False, net2, lns2, p, info[m][5], w2)
                            else:
                                t2.SetEnd(V); info[m] = (t2, False, net2, lns2, info[m][4], p, w2)
                gone.add(k); n += 1
                break
            hp, hq = held(k, p), held(k, q)
            if hp and hq:
                # both ends sit in copper of the net, but off its centre line: move each end onto the centre line
                moved = False
                for which, pt in (('s', p), ('e', q)):
                    best = None
                    for m, (t2, isvia2, net2, lns2, p2, q2, w2) in enumerate(info):
                        if m == k or m in gone or net2 != net or not (set(lns) & set(lns2)):
                            continue
                        dx, dy = q2[0] - p2[0], q2[1] - p2[1]
                        L2 = dx * dx + dy * dy
                        tt = 0.0 if L2 < 1e-12 else max(0.0, min(1.0, ((pt[0] - p2[0]) * dx + (pt[1] - p2[1]) * dy) / L2))
                        pr = (p2[0] + tt * dx, p2[1] + tt * dy)
                        dd = math.hypot(pr[0] - pt[0], pr[1] - pt[1])
                        if dd <= w2 / 2 + 0.005 and (best is None or dd < best[0]):
                            best = (dd, pr)
                    if best and best[0] > 1e-4:
                        V = pcbnew.VECTOR2I(MM(best[1][0]), MM(best[1][1]))
                        if which == 's':
                            t.SetStart(V); info[k] = (t, isvia, net, lns, best[1], info[k][5], w)
                        else:
                            t.SetEnd(V); info[k] = (t, isvia, net, lns, info[k][4], best[1], w)
                        moved = True
                n += 1 if moved else 0
                break
            if not hp and not hq:
                gone.add(k); n += 1
                break
            fixed, loose = (p, q) if hp else (q, p)
            js = [a for a in taps(k) if math.hypot(a[0] - fixed[0], a[1] - fixed[1]) > 0.02]
            if not js:
                gone.add(k); n += 1
                break
            far = max(js, key=lambda a: math.hypot(a[0] - fixed[0], a[1] - fixed[1]))   # keep the track up to its last joint
            if math.hypot(far[0] - loose[0], far[1] - loose[1]) < 0.02:
                break
            V = pcbnew.VECTOR2I(MM(far[0]), MM(far[1]))
            if hp:
                t.SetEnd(V); info[k] = (t, isvia, net, lns, p, far, w)
            else:
                t.SetStart(V); info[k] = (t, isvia, net, lns, far, q, w)
            n += 1
            break
    for k in gone:
        b.Remove(info[k][0])
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    pcbnew.SaveBoard(path, b)
    return n


# ------------------------------------------------------------------ 4 finish
def stage_finish(b):
    rm.outer_pours(b)
    for _ in range(2):
        mroute.RES = 0.05
        print('stitch vias', len(mroute.stitch(b, CLASSES)))
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())


# ------------------------------------------------------------------ 5 silkscreen
LABELS = [('J8', 'SPK L'), ('J9', 'SPK R'), ('J1', '20V IN'), ('J2', 'PI USB-C'), ('J3', 'PI 1-15'), ('J4', 'PI 35-40'),
          ('J5', 'RADAR'), ('J6', 'TOUCH'), ('J7', 'ECHO'), ('J10', 'BME680'), ('J11', 'VEML6030'), ('LK1', 'LINK')]
PLUS = [('J8', '1'), ('J9', '1'), ('J1', None)]            # '+' beside this pin (None: the pin that is not GND)


def stage_silk(b):
    import silk
    import pcb_main as pm
    W, H = 87.0, 57.9
    rm.trim_silk_past_edge(b, H=H)
    silk.trim_edge(b, W, H, margin=0.3, keep=mroute.GRAVE)
    shown, hidden = silk.place(b, W=W, H=H)
    box = lambda bb, g=0.0: (TO(bb.GetX()) - g, TO(bb.GetY()) - g, TO(bb.GetRight()) + g, TO(bb.GetBottom()) + g)
    obst = {pcbnew.F_SilkS: [], pcbnew.B_SilkS: []}
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.IsOnLayer(pcbnew.F_Cu):
                obst[pcbnew.F_SilkS].append(box(p.GetBoundingBox(), 0.25))
            if p.IsOnLayer(pcbnew.B_Cu):
                obst[pcbnew.B_SilkS].append(box(p.GetBoundingBox(), 0.25))
        cy = fp.GetCourtyard(pcbnew.F_CrtYd)
        if cy.OutlineCount():                      # under a part nothing can be read; connector courtyards are the body + 0.5
            obst[pcbnew.F_SilkS].append(box(cy.BBox(), -0.4 if fp.GetReference().startswith(('J', 'LK')) else 0.05))
        for g in fp.GraphicalItems():
            if g.GetLayer() in obst and g.GetClass() not in ('PCB_FIELD', 'PCB_TEXT'):
                obst[g.GetLayer()].append(box(g.GetBoundingBox(), 0.12))
        if fp.Reference().IsVisible() and fp.Reference().GetLayer() in obst:
            obst[fp.Reference().GetLayer()].append(box(fp.Reference().GetBoundingBox(), 0.15))

    def put(s, x, y, size=1.0, rmax=9.0, rots=(0, 90), layers=(pcbnew.F_SilkS, pcbnew.B_SilkS)):
        """Text s as near (x, y) as there is free silkscreen, door side first, else the back. Returns (side, x, y) or None."""
        cands = sorted(((dx * 0.5, dy * 0.5) for dx in range(-int(rmax * 2), int(rmax * 2) + 1) for dy in range(-int(rmax * 2), int(rmax * 2) + 1)),
                       key=lambda d: d[0] * d[0] + d[1] * d[1])
        for lay in layers:
            t = pm.text(b, s, x, y, lay, size=size)
            O = np.array(obst[lay])
            for dx, dy in cands:
                for rot in rots:
                    t.SetTextAngleDegrees(rot)
                    t.SetPosition(pcbnew.VECTOR2I(MM(x + dx), MM(y + dy)))
                    tb = box(t.GetBoundingBox())
                    if tb[0] < 0.6 or tb[1] < 0.6 or tb[2] > W - 0.6 or tb[3] > H - 0.6:
                        continue
                    if (~((tb[2] < O[:, 0]) | (O[:, 2] < tb[0]) | (tb[3] < O[:, 1]) | (O[:, 3] < tb[1]))).any():
                        continue
                    obst[lay].append(box(t.GetBoundingBox(), 0.15))
                    return ('door side' if lay == pcbnew.F_SilkS else 'back', x + dx, y + dy)
            b.Remove(t)
        return None
    out = []
    for ref, pin in PLUS:
        fp = b.FindFootprintByReference(ref)
        pp = [p for p in fp.Pads() if (p.GetNumber() == pin if pin else p.GetNetname() != 'GND')][0]
        out.append((ref + ' +', put('+', TO(pp.GetPosition().x), TO(pp.GetPosition().y), size=1.2, rmax=5.0, rots=(0,))))
    for ref, s_ in LABELS:
        fp = b.FindFootprintByReference(ref)
        c = fp.GetBoundingBox(False).Centre()
        out.append((s_, put(s_, TO(c.x), TO(c.y), rmax=10.0)))
    out.append(('title', put('HA PANEL MAIN', X(-12.0), Y(21.0), rmax=30.0, rots=(0,))))
    out.append(('rev', put('REV 3 2026-11-11', X(-12.0), Y(19.2), rmax=30.0, rots=(0,))))
    return shown, hidden, out


def main(src, dst, stages):
    if stages and stages[0] == 'loose':          # route_rev3.py board.kicad_pcb drc.json loose
        print('loose ends removed', clean_loose(src, dst))
        return
    if src != dst:                       # work on a copy: KiCad keeps the rules in the .kicad_pro beside the board
        import shutil
        shutil.copy(src, dst)
        if os.path.exists(src.replace('.kicad_pcb', '.kicad_pro')):
            shutil.copy(src.replace('.kicad_pcb', '.kicad_pro'), dst.replace('.kicad_pcb', '.kicad_pro'))
    b = pcbnew.LoadBoard(dst)
    pb.rules(b)
    if 'power' in stages:
        for name, (ok, info) in stage_power(b):
            print('power', name, ok, info)
        print('pin stubs at U1:', pin_stubs(b, 'U1'))
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        pcbnew.SaveBoard(dst, b)
    if 'planes' in stages:
        n, bad = stage_planes(b)
        print('plane vias added', n, '| not placed:', bad)
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        pcbnew.SaveBoard(dst, b)
    if 'signals' in stages:
        b = signals_loop(src, dst)
        pb.rules(b)
    if 'fill' in stages:
        pcbnew.ZONE_FILLER(b).Fill(b.Zones())
        pcbnew.SaveBoard(dst, b)
    if 'finish' in stages:
        stage_finish(b)
    if 'silk' in stages:
        shown, hidden, out = stage_silk(b)
        print('silk: part names shown', shown, 'hidden', hidden)
        print('silk: labels not placed:', [k for k, v in out if v is None])
        print('silk: labels at (side, u, v):', [(k, v[0], round(v[1] - pb.U0, 1), round(pb.V0 - v[2], 1)) for k, v in out if v])
        pcbnew.SaveBoard(dst, b)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3:] or ['power', 'planes', 'signals', 'finish'])
