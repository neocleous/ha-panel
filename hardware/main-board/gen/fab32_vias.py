"""Main board rev 3.2, fab issue 2026-11-16: vias out of the pasted pads.

JLC plugs a via with soldermask ink only if it has no soldermask opening on either side, is at least 0.35 mm from other
soldermask openings and its hole is 0.5 mm or less (capabilities page, row "Plugged vias", read 2026-11-16). Rev 3's
router set vias on the ends of pads, so on rev 3.2 as left on 2026-11-14 the holes of 37 vias lie partly inside the
bare area of a pad that gets solder paste, and 3 more leave less than 0.20 of mask between hole and pad. Such a hole
is not plugged and can take the pad's solder on the hotplate.

This script moves each of those vias to the place that needs the shortest joining tracks and leaves at least DAM of
mask between the hole's wall and every pasted pad's opening. The via is joined to each pad it touched by a short
door-side track; the router's old stub from the pad to the via is taken out; any other track that ended on the via is
carried to its new place. A via whose pad is named on the command line is also made smaller. A via that finds no
place is taken out if a second via of its net stands beside it on the same door-side track; its back-face track is
carried to that via. No part, pad or hole of a part moves.

    python3 fab32_vias.py plan  <board.kicad_pcb> <plan.json> [pad ...]   find the moves (reads only); the vias at the
                                                                          named pads become 0.2/0.45
    python3 fab32_vias.py apply <board.kicad_pcb> <plan.json> <out.kicad_pcb>   make them and refill the pours
    python3 fab32_vias.py check <board.kicad_pcb> [limit]                 list every via nearer than the limit (DAM)
                                                                          to a pasted pad; the smallest mask width

KiCad 9's Python (pcbnew) and shapely. Board frame of the site document in the listings: u = X - 43.5, v = 28.95 - Y.
Vias in test pads (no paste) and the one in the amplifier's thermal pad (no paste aperture over it) are left alone.
The search is deterministic: the same board gives the same plan.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pcbnew                      # noqa: E402
import pcb_rev3 as pb              # noqa: E402
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import nearest_points, unary_union
from shapely.strtree import STRtree

MM, TO = pcbnew.FromMM, pcbnew.ToMM
U0, V0 = 43.5, 28.95
DAM = 0.20            # least soldermask between a hole's wall and a pasted pad's opening after the change
AIM = 0.25            # what the search aims at first; DAM is taken only if it shortens the tracks by 0.10 or more
OTHER = 0.20          # the same for openings without paste (test pads, connector pads), unless the via is already nearer
MARGIN = 0.02         # added to every clearance, so that KiCad's own check passes with room
HOLE_CLR, HOLE_HOLE, EDGE_CLR = 0.25, 0.25, 0.30
LAYERS = (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu)
MAXERR = MM(0.002)
RMAX = 3.0            # how far from the old place the search goes
NEAR = 0.3            # weight of the distance from the old place when two places need equally short tracks
SMALL = (0.2, 0.45)   # the board's small via; JLC charges nothing extra for it (hole 0.2, diameter not under 0.45)
MERGE = 1.0           # a second via of the same net within this distance can take a via's place
SHRINK = set()        # pads whose via is also made smaller (from the command line)


def rules(board):
    """The board's rules live in main-board.kicad_pro, and KiCad's Python reads them only when that file lies beside
    the board (pb.rules() alone leaves every item at KiCad's own 0.2 clearance). So the board has to be a copy named
    main-board.kicad_pcb beside the project file, as gen/fab32.sh makes it. This checks that it was."""
    pb.rules(board)
    got = {}
    for t in board.GetTracks():
        got.setdefault(t.GetNetname(), TO(t.GetOwnClearance(pcbnew.F_Cu)))
    assert abs(got['GND'] - 0.15) < 1e-6 and abs(got['+20V'] - 0.20) < 1e-6, \
        'the board was read without its project file (clearances %s): run it through gen/fab32.sh' % {k: got[k] for k in ('GND', '+20V')}


def uv(x, y):
    return (round(x - U0, 3), round(V0 - y, 3))


def polys(sps):
    out = []
    for k in range(sps.OutlineCount()):
        o = sps.Outline(k)
        holes = []
        for h in range(sps.HoleCount(k)):
            hh = sps.Hole(k, h)
            holes.append([(TO(hh.CPoint(i).x), TO(hh.CPoint(i).y)) for i in range(hh.PointCount())])
        out.append(Polygon([(TO(o.CPoint(i).x), TO(o.CPoint(i).y)) for i in range(o.PointCount())], holes))
    return out


def pad_shape(p, layer, grow=0):
    sps = pcbnew.SHAPE_POLY_SET()
    p.TransformShapeToPolygon(sps, layer, grow, MAXERR, pcbnew.ERROR_OUTSIDE)
    g = polys(sps)
    return unary_union(g) if g else None


def vpt(v):
    c = v.GetPosition()
    return Point(TO(c.x), TO(c.y))


class Model:
    """Everything a moved via has to stay clear of, read from the board."""

    def __init__(self, b):
        self.b = b
        self.vias = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
        self.tracks = [t for t in b.GetTracks() if t.Type() != pcbnew.PCB_VIA_T]
        self.open = []                               # soldermask openings of pads
        self.copper = {l: [] for l in LAYERS}        # (shape, net, clearance, what)
        self.holes = []                              # (point or line, radius, owner)
        for f in b.GetFootprints():
            for p in f.Pads():
                net = p.GetNetname()
                for l in LAYERS:
                    if p.IsOnLayer(l):
                        g = pad_shape(p, l)
                        if g is not None:
                            self.copper[l].append((g, net, TO(p.GetOwnClearance(l)), '%s.%s' % (f.GetReference(), p.GetNumber())))
                for side, mask, cu, paste in (('door side', pcbnew.F_Mask, pcbnew.F_Cu, pcbnew.F_Paste), ('back', pcbnew.B_Mask, pcbnew.B_Cu, pcbnew.B_Paste)):
                    if p.IsOnLayer(mask):
                        g = pad_shape(p, mask, p.GetSolderMaskExpansion(mask))
                        if g is not None:
                            on = p.IsOnLayer(cu)
                            self.open.append(dict(g=g, ref=f.GetReference(), pad=p.GetNumber(), side=side, paste=p.IsOnLayer(paste), net=net, value=f.GetValue(),
                                                  dnp=f.IsDNP(), cu=pad_shape(p, cu) if on else None, size=(TO(p.GetSize(cu).x), TO(p.GetSize(cu).y)) if on else None))
                if p.HasHole():
                    ds = p.GetDrillSize()
                    if ds.x == ds.y:
                        c = p.GetPosition()
                        self.holes.append((Point(TO(c.x), TO(c.y)), TO(ds.x) / 2, '%s.%s' % (f.GetReference(), p.GetNumber())))
                    else:                                  # a slot: its centre line and half its width
                        hs = p.GetEffectiveHoleShape()
                        self.holes.append((LineString([(TO(hs.GetSeg().A.x), TO(hs.GetSeg().A.y)), (TO(hs.GetSeg().B.x), TO(hs.GetSeg().B.y))]),
                                           TO(hs.GetWidth()) / 2, '%s.%s slot' % (f.GetReference(), p.GetNumber())))
        for t in self.tracks:
            l = t.GetLayer()
            if l in self.copper:
                a, c = t.GetStart(), t.GetEnd()
                g = LineString([(TO(a.x), TO(a.y)), (TO(c.x), TO(c.y))]).buffer(TO(t.GetWidth()) / 2, 16)
                self.copper[l].append((g, t.GetNetname(), TO(t.GetOwnClearance(l)), 'track'))
        self.keepout = {l: [] for l in LAYERS}
        self.zones = []
        self.supply = []
        for z in b.Zones():
            if z.GetIsRuleArea():
                if z.GetDoNotAllowVias() or z.GetDoNotAllowTracks():
                    for l in LAYERS:
                        if z.IsOnLayer(l):
                            self.keepout[l] += polys(z.Outline())
            else:
                for l in LAYERS:
                    if z.IsOnLayer(l):
                        self.zones.append((l, z.GetNetname(), unary_union(polys(z.Outline())), unary_union(polys(z.GetFilledPolysList(l)))))
                        if l in (pcbnew.F_Cu, pcbnew.B_Cu) and z.GetNetname() != 'GND':      # a supply pour on an outer layer
                            self.supply.append((l, z.GetNetname(), unary_union(polys(z.GetFilledPolysList(l))), TO(z.GetLocalClearance() or 0)))
        outl = pcbnew.SHAPE_POLY_SET()
        b.GetBoardPolygonOutlines(outl)
        self.board = unary_union(polys(outl))
        self.edge = self.board.boundary
        self.trees = {l: STRtree([c[0] for c in self.copper[l]]) for l in LAYERS}
        self.optree = STRtree([o['g'] for o in self.open])

    def via_rows(self, limit):
        """Every via whose hole wall is nearer than limit to a pasted pad's opening: (distance, via, opening)."""
        rows = []
        for v in self.vias:
            pt = vpt(v)
            rh = TO(v.GetDrillValue()) / 2
            best = None
            for i in self.optree.query(pt.buffer(rh + limit + 0.01)):
                o = self.open[i]
                if not o['paste']:
                    continue
                d = o['g'].distance(pt) - rh
                if d < limit - 1e-4 and (best is None or d < best[0]):
                    best = (d, o)
            if best:
                rows.append((best[0], v, best[1]))
        rows.sort(key=lambda r: (round(r[0], 4), r[1].GetPosition().x, r[1].GetPosition().y))
        return rows


def tracks_clear(m, v, moved, fstubs=(), bstubs=()):
    """None if the new tracks of via v's net keep their distance on their layers, else the reason."""
    net = v.GetNetname()
    for l, seg, w in [(pcbnew.F_Cu, s, w) for s, w in fstubs] + [(pcbnew.B_Cu, s, w) for s, w in bstubs]:
        own = TO(v.GetOwnClearance(l))
        for i in m.trees[l].query(seg.buffer(w / 2 + 0.6)):
            g, n2, c2, what = m.copper[l][i]
            if n2 != net and g.distance(seg) - w / 2 < max(own, c2) + MARGIN:
                return 'track to %s on %s' % (what, m.b.GetLayerName(l))
        for w2 in m.vias:
            if w2 is v or w2.GetNetname() == net:
                continue
            d = (moved.get(id(w2)) or vpt(w2)).distance(seg) - w / 2
            if d - TO(w2.GetWidth(l)) / 2 < max(own, TO(w2.GetOwnClearance(l))) + MARGIN or d - TO(w2.GetDrillValue()) / 2 < HOLE_CLR + MARGIN:
                return 'track to a via on %s' % m.b.GetLayerName(l)
        for hp, hr, who in m.holes:
            if hp.distance(seg) - hr - w / 2 < HOLE_CLR + MARGIN:
                return 'track to the hole of %s' % who
        for l2, zn, fill, zc in m.supply:
            if l2 == l and zn != net and fill.distance(seg) - w / 2 < max(zc, own) + MARGIN:
                return 'track cuts into the %s pour' % zn.split('/')[-1]
        body = seg.buffer(w / 2, 16)
        for k in m.keepout[l]:
            if k.intersects(body):
                return 'track in a keep-out'
        if m.edge.distance(seg) - w / 2 < EDGE_CLR + MARGIN:
            return 'track to the edge'
    return None


def clear_at(m, v, pt, moved, aim, fstubs=(), bstubs=(), size=None):
    """None if the via v may stand at pt (shapely Point, KiCad mm), else the reason. moved: {id(via): Point} so far.
    size: (hole, ring diameter) if the via is also made smaller."""
    rh = (size[0] if size else TO(v.GetDrillValue())) / 2
    rr = (size[1] if size else TO(v.GetWidth(pcbnew.F_Cu))) / 2
    net = v.GetNetname()
    old = vpt(v)
    for i in m.optree.query(pt.buffer(rh + 0.5)):
        o = m.open[i]
        d = o['g'].distance(pt) - rh
        if o['paste']:
            if d < aim - 1e-6:
                return 'opening %s.%s' % (o['ref'], o['pad'])
        elif d < OTHER - 1e-6 and d < o['g'].distance(old) - rh - 1e-6:
            return 'opening (no paste) %s.%s' % (o['ref'], o['pad'])
    if not m.board.contains(pt) or m.edge.distance(pt) - rr < EDGE_CLR + MARGIN:
        return 'edge'
    for hp, hr, who in m.holes:
        if hp.distance(pt) - hr - rh < HOLE_HOLE + MARGIN:
            return 'hole of %s' % who
    for w in m.vias:
        if w is v:
            continue
        d = (moved.get(id(w)) or vpt(w)).distance(pt)
        if d - TO(w.GetDrillValue()) / 2 - rh < HOLE_HOLE + MARGIN:
            return 'hole of a via'
        if w.GetNetname() != net:
            clr = max(TO(v.GetOwnClearance(pcbnew.F_Cu)), TO(w.GetOwnClearance(pcbnew.F_Cu))) + MARGIN
            if d - TO(w.GetWidth(pcbnew.F_Cu)) / 2 - rr < clr:
                return 'ring of a via'
            if d - TO(w.GetWidth(pcbnew.F_Cu)) / 2 - rh < HOLE_CLR + MARGIN or d - TO(w.GetDrillValue()) / 2 - rr < HOLE_CLR + MARGIN:
                return 'hole to a via ring'
    ring = pt.buffer(rr, 32)
    for l in LAYERS:
        own = TO(v.GetOwnClearance(l))
        for i in m.trees[l].query(pt.buffer(rr + 0.6)):
            g, n2, c2, what = m.copper[l][i]
            if n2 == net:
                continue
            d = g.distance(pt)
            if d - rr < max(own, c2) + MARGIN:
                return '%s on %s' % (what, m.b.GetLayerName(l))
            if d - rh < HOLE_CLR + MARGIN:
                return 'hole to %s on %s' % (what, m.b.GetLayerName(l))
        for k in m.keepout[l]:
            if k.intersects(ring):
                return 'keep-out on %s' % m.b.GetLayerName(l)
    # the supply pours on the outer layers (20 V inlet, the Pi's 5 V) are not cut into: their resistance was checked as they are
    for l, zn, fill, zc in m.supply:
        if zn != net and fill.distance(pt) - rr < max(zc, TO(v.GetOwnClearance(l))) + MARGIN:
            return 'cuts into the %s pour' % zn.split('/')[-1]
    # a via that stands in a pour of its own net on an inner layer has to stay well inside that pour's outline
    for l, zn, outline, fill in m.zones:
        if zn == net and l in (pcbnew.In1_Cu, pcbnew.In2_Cu) and fill.contains(old) and not outline.buffer(-(rr + 0.35)).contains(pt):
            return 'leaves the %s plane' % zn
    return tracks_clear(m, v, moved, fstubs, bstubs)


def plan(m):
    rows = m.via_rows(DAM)
    moved, gone, out = {}, set(), []
    for d0, v, o in rows:
        c = v.GetPosition()
        old = vpt(v)
        rh, rr = TO(v.GetDrillValue()) / 2, TO(v.GetWidth(pcbnew.F_Cu)) / 2
        net = v.GetNetname()
        # the door-side pads of the same net whose copper the via touches now: it is joined to each of them again
        mine = [q for q in m.open if q['net'] == net and q['side'] == 'door side' and q['cu'] is not None and q['cu'].distance(old) < rr]
        mine.sort(key=lambda q: q['cu'].distance(old))
        home = mine[0] if mine else o
        pads = mine or [home]
        # tracks that end on the via. A door-side track whose other end lies in a pad the via touches is the router's
        # fan-out stub: it is taken out and the new track takes its place. Every other track is carried to the new place.
        ends = {pcbnew.F_Cu: [], pcbnew.B_Cu: []}
        fdel = []
        for t in m.tracks:
            if t.GetNetname() == net and t.GetLayer() in ends:
                es = (t.GetStart(), t.GetEnd())
                for i, e in enumerate(es):
                    if abs(e.x - c.x) < MM(0.012) and abs(e.y - c.y) < MM(0.012):
                        far = Point(TO(es[1 - i].x), TO(es[1 - i].y))
                        if t.GetLayer() == pcbnew.F_Cu and any(q['cu'].buffer(0.01).contains(far) for q in pads):
                            fdel.append([[round(TO(es[0].x), 4), round(TO(es[0].y), 4)], [round(TO(es[1].x), 4), round(TO(es[1].y), 4)]])
                        else:
                            ends[t.GetLayer()].append((TO(t.GetWidth()), far))
        # the stub may bend on its way from the pad's middle: its other pieces inside the same pad go with it
        grew = True
        while grew:
            grew = False
            for a_, c_ in list(fdel):
                for jx, jy in (a_, c_):
                    if abs(jx - old.x) < 0.012 and abs(jy - old.y) < 0.012:
                        continue
                    at = []
                    for t in m.tracks:
                        if t.GetNetname() == net and t.GetLayer() == pcbnew.F_Cu:
                            seg = [[round(TO(t.GetStart().x), 4), round(TO(t.GetStart().y), 4)], [round(TO(t.GetEnd().x), 4), round(TO(t.GetEnd().y), 4)]]
                            if seg not in fdel and any(abs(e[0] - jx) < 0.012 and abs(e[1] - jy) < 0.012 for e in seg):
                                at.append(seg)
                    if len(at) == 1 and all(any(q['cu'].buffer(0.01).contains(Point(e)) for q in pads) for e in at[0]):
                        fdel.append(at[0])
                        grew = True
        # a via that stands in a small pour of its own net on the back (not the ground pour) is joined to its old
        # place by a back-face track, so that it stays in that pour whatever the refill does at the new place
        zcarry = (not ends[pcbnew.B_Cu] and net != 'GND'
                  and any(l == pcbnew.B_Cu and zn == net and fill.contains(old) for l, zn, outline, fill in m.zones))
        tag = '%s.%s' % (home['ref'], home['pad'])
        rec = dict(net=net, drill=2 * rh, dia=2 * rr, old=[round(old.x, 4), round(old.y, 4)], old_uv=uv(old.x, old.y), pad=tag, value=home['value'],
                   fitted=not home['dnp'], dam_old=round(d0, 3), worst='%s.%s' % (o['ref'], o['pad']), pads=['%s.%s' % (q['ref'], q['pad']) for q in pads])
        best = None
        size = SMALL if tag in SHRINK and 2 * rr > SMALL[1] else (2 * rh, 2 * rr)      # a named via is made smaller
        sh, sr = size[0] / 2, size[1] / 2
        for aim in (AIM, DAM):
            found = None
            for k in range(0, 61):                          # centre on a line at this distance from the pad's opening
                d = sh + aim + 0.025 * k
                if found and (d - sh - 0.01) > found[0]:            # no better place possible further out
                    break
                ring = home['g'].buffer(d, 32).exterior
                for i in range(int(ring.length / 0.04) + 1):
                    pt = ring.interpolate(0.04 * i)
                    if pt.distance(old) > RMAX:
                        continue
                    fst = []
                    for q in pads:                         # door side: from just inside each pad it touched, the shortest way
                        a_ = nearest_points(q['cu'], pt)[0]
                        inner = q['cu'].buffer(-min(0.12, min(q['size']) / 4))
                        a2 = nearest_points(inner, a_)[0] if not inner.is_empty else q['cu'].centroid
                        fst.append((LineString([(a2.x, a2.y), (pt.x, pt.y)]), max(0.25, min(2 * sr, min(q['size'])))))   # as wide as the via or the pad allows
                    npad = len(fst)
                    if ends[pcbnew.F_Cu]:                  # other door-side tracks that ended on the via
                        fst.append((LineString([(old.x, old.y), (pt.x, pt.y)]), min(w for w, far in ends[pcbnew.F_Cu])))
                    bst = [(LineString([(old.x, old.y), (pt.x, pt.y)]), min(w for w, far in ends[pcbnew.B_Cu]))] if ends[pcbnew.B_Cu] else []
                    if zcarry:
                        bst = [(LineString([(old.x, old.y), (pt.x, pt.y)]), min(2 * sr, 0.6))]
                    # the shortest joining tracks, and as near to the old place as that allows
                    cost = max(s_.length for s_, w_ in fst[:npad]) + (pt.distance(old) if (bst or len(fst) > npad) else 0.0) + NEAR * pt.distance(old)
                    if found and cost >= found[0] - 1e-9:
                        continue
                    if clear_at(m, v, pt, moved, aim, fst, bst, size) is None:
                        found = (cost, pt.distance(old), pt, fst, bst)
            if found and (best is None or found[0] < best[0] - 0.10):
                best = found + (aim,)
        if best is not None:
            cost, r, pt, fst, bst, aim = best
            moved[id(v)] = pt
            dam = min(q['g'].distance(pt) - sh for q in m.open if q['paste'])
            rec.update(how='moved', new=[round(pt.x, 4), round(pt.y, 4)], new_uv=uv(pt.x, pt.y), move=round(r, 3), dam_new=round(dam, 3), size=list(size),
                       fstub=[[[round(x, 4) for x in s_.coords[0]], [round(x, 4) for x in s_.coords[1]], w_] for s_, w_ in fst],
                       bstub=[[[round(x, 4) for x in s_.coords[0]], [round(x, 4) for x in s_.coords[1]], w_] for s_, w_ in bst], fdel=fdel)
            print('%-9s %-22s %.1f/%.2f%s  u %+7.3f v %+7.3f -> u %+7.3f v %+7.3f  moved %.3f  mask %+.3f -> %.3f  door-side track(s) %s x %.2f%s' % (
                tag, net.split('/')[-1][:22], 2 * rh, 2 * rr, ' -> %.1f/%.2f' % size if size[1] < 2 * rr - 1e-6 else '', rec['old_uv'][0], rec['old_uv'][1],
                rec['new_uv'][0], rec['new_uv'][1], r, d0, dam, '/'.join('%.2f' % s_.length for s_, w_ in fst), fst[0][1],
                '; back track carried %.2f' % bst[0][0].length if bst else ''))
        else:
            # no place: a second via of the same net close by, on a door-side track that runs through this via, takes its place
            twin = None
            fsegs = [LineString([(TO(t.GetStart().x), TO(t.GetStart().y)), (TO(t.GetEnd().x), TO(t.GetEnd().y))]) for t in m.tracks
                     if t.GetLayer() == pcbnew.F_Cu and t.GetNetname() == net]
            for w in m.vias:
                if w is v or id(w) in gone or w.GetNetname() != net:
                    continue
                wp = moved.get(id(w)) or vpt(w)
                if wp.distance(old) > MERGE or not any(g.distance(old) < 0.012 and g.distance(wp) < TO(w.GetWidth(pcbnew.F_Cu)) / 2 for g in fsegs):
                    continue
                dam_w = min(q['g'].distance(wp) - TO(w.GetDrillValue()) / 2 for q in m.open if q['paste'])
                bst = [(LineString([(old.x, old.y), (wp.x, wp.y)]), min(w_ for w_, far in ends[pcbnew.B_Cu]))] if ends[pcbnew.B_Cu] else []
                if dam_w >= DAM - 1e-6 and tracks_clear(m, v, moved, (), bst) is None and (twin is None or wp.distance(old) < twin[0]):
                    twin = (wp.distance(old), wp, bst, dam_w)
            if twin:
                dist, wp, bst, dam_w = twin
                gone.add(id(v))
                rec.update(how='taken out', twin=[round(wp.x, 4), round(wp.y, 4)], twin_uv=uv(wp.x, wp.y), move=round(dist, 3), dam_new=round(dam_w, 3),
                           bstub=[[[round(x, 4) for x in s_.coords[0]], [round(x, 4) for x in s_.coords[1]], w_] for s_, w_ in bst])
                print('%-9s %-22s %.1f/%.2f  u %+7.3f v %+7.3f  taken out: the via %.3f away on the same door-side track (u %+7.3f v %+7.3f, mask %.3f) serves%s' % (
                    tag, net.split('/')[-1][:22], 2 * rh, 2 * rr, rec['old_uv'][0], rec['old_uv'][1], dist, rec['twin_uv'][0], rec['twin_uv'][1], dam_w,
                    '; back track carried %.2f' % dist if bst else ''))
            else:
                rec.update(how='no place')
                print('NO PLACE  %-9s %-22s u %+7.3f v %+7.3f  (mask %+.3f)' % (tag, net.split('/')[-1], rec['old_uv'][0], rec['old_uv'][1], d0))
        out.append(rec)
    return out


def apply(b, recs):
    n = 0
    for rec in recs:
        if rec.get('how') not in ('moved', 'taken out'):
            continue
        ox, oy = rec['old']
        v = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and abs(TO(t.GetPosition().x) - ox) < 1e-3 and abs(TO(t.GetPosition().y) - oy) < 1e-3]
        assert len(v) == 1, 'via not found once at %s' % rec['old']
        v = v[0]
        assert v.GetNetname() == rec['net']
        net = v.GetNet()

        def track(a, c, layer, w):
            t = pcbnew.PCB_TRACK(b)
            t.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1])))
            t.SetEnd(pcbnew.VECTOR2I(MM(c[0]), MM(c[1])))
            t.SetLayer(layer)
            t.SetWidth(MM(w))
            t.SetNet(net)
            b.Add(t)
        if rec['how'] == 'moved':
            v.SetPosition(pcbnew.VECTOR2I(MM(rec['new'][0]), MM(rec['new'][1])))
            if abs(rec['size'][1] - rec['dia']) > 1e-6:
                v.SetDrill(MM(rec['size'][0]))
                v.SetWidth(pcbnew.F_Cu, MM(rec['size'][1]))
            for a, c, w in rec['fstub']:
                track(a, c, pcbnew.F_Cu, w)
            for a, c in rec['fdel']:                       # the router's fan-out stub from the pad to the old place
                hit = [t for t in b.GetTracks() if t.Type() != pcbnew.PCB_VIA_T and t.GetLayer() == pcbnew.F_Cu and t.GetNetname() == rec['net']
                       and abs(TO(t.GetStart().x) - a[0]) < 1e-3 and abs(TO(t.GetStart().y) - a[1]) < 1e-3
                       and abs(TO(t.GetEnd().x) - c[0]) < 1e-3 and abs(TO(t.GetEnd().y) - c[1]) < 1e-3]
                assert len(hit) == 1, 'fan-out stub not found once: %s' % [a, c]
                b.Remove(hit[0])
        else:
            b.Remove(v)
        for a, c, w in rec['bstub']:
            track(a, c, pcbnew.B_Cu, w)
        n += 1
    return n


if __name__ == '__main__':
    mode = sys.argv[1]
    board = pcbnew.LoadBoard(sys.argv[2])
    rules(board)
    if mode == 'plan':
        SHRINK.update(sys.argv[4:])
        recs = plan(Model(board))
        json.dump(recs, open(sys.argv[3], 'w'), indent=1)
        mv = [r for r in recs if r['how'] == 'moved']
        print('%d vias with less than %.2f of mask to a pasted pad: %d moved (%d of them made %.1f/%.2f), %d taken out, %d without a place; '
              'largest move %.3f; longest new door-side track %.2f' % (
                  len(recs), DAM, len(mv), sum(1 for r in mv if abs(r['size'][1] - r['dia']) > 1e-6), SMALL[0], SMALL[1], sum(1 for r in recs if r['how'] == 'taken out'),
                  sum(1 for r in recs if r['how'] == 'no place'), max(r['move'] for r in mv),
                  max(LineString([s[0], s[1]]).length for r in mv for s in r['fstub'])))
    elif mode == 'apply':
        recs = json.load(open(sys.argv[3]))
        print('vias changed: %d' % apply(board, recs))
        pcbnew.ZONE_FILLER(board).Fill(board.Zones())
        pcbnew.SaveBoard(sys.argv[4], board)
    elif mode == 'check':
        lim = float(sys.argv[3]) if len(sys.argv) > 3 else DAM
        m = Model(board)
        rows = m.via_rows(lim)
        print('vias: %d; with less than %.2f of mask between the hole and a pasted pad: %d' % (len(m.vias), lim, len(rows)))
        for d, v, o in rows:
            p = vpt(v)
            print('   %+.3f  %s.%s  %s  u %+.3f v %+.3f' % (d, o['ref'], o['pad'], v.GetNetname().split('/')[-1], p.x - U0, V0 - p.y))
        allp = sorted(min(q['g'].distance(vpt(v)) for q in m.open if q['paste']) - TO(v.GetDrillValue()) / 2 for v in m.vias)
        print('smallest mask width between a hole and a pasted pad, all vias: %.3f' % allp[0])
        nop = sorted(((min(q['g'].distance(vpt(v)) for q in m.open if not q['paste']) - TO(v.GetDrillValue()) / 2, i) for i, v in enumerate(m.vias)))
        inn = [(d, m.vias[i]) for d, i in nop if d < lim - 1e-4]
        print('vias with less than %.2f of mask to an opening without paste (test pads, the thermal pad, connector pads): %d' % (lim, len(inn)))
        for d, v in inn:
            p = vpt(v)
            o = min((q for q in m.open if not q['paste']), key=lambda q: q['g'].distance(p))
            print('   %+.3f  %s.%s  %s  u %+.3f v %+.3f' % (d, o['ref'], o['pad'], v.GetNetname().split('/')[-1], p.x - U0, V0 - p.y))
