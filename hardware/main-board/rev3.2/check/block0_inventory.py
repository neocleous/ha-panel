"""Main board rev 3.2, block 0: everything within 2.5 of the +u side edge between v 0 and v +14.5, on every layer,
and how near each item comes to the relief for a depth of 1.5, 1.25 and 1.0 (inner corners drawn at radius R_CORNER).

    python3.12 block0_inventory.py <board.kicad_pcb>

Board frame (site document): u = x - 43.5, v = 28.95 - y (mm). The +u edge is at u +43.5.
The relief: u > 43.5 - depth over v 1.5 - R_CORNER ... 13.0 + R_CORNER, inner corners rounded at R_CORNER,
so that the full depth holds over v +1.5 ... +13.0. Copper must keep EDGE_CLEAR from the new edge.
"""
import sys
from collections import defaultdict

import pcbnew
import shapely
from shapely.geometry import Polygon, MultiPolygon, box, Point
from shapely.ops import unary_union

U0, V0 = 43.5, 28.95
TO = pcbnew.ToMM
R_CORNER = 1.0          # radius drawn at the relief's two inner corners
EDGE_CLEAR = 0.3        # the board's copper-to-edge rule (design settings: min_copper_edge_clearance)
REGION = box(41.0, 0.0, 43.5 + 1.0, 14.5)   # u 41.0 ... beyond the edge, v 0 ... 14.5
DEPTHS = (1.5, 1.25, 1.0)
MAXERR = pcbnew.FromMM(0.002)


def uv(p):
    return (TO(p.x) - U0, V0 - TO(p.y))


def relief(depth, r=R_CORNER, v1=1.5, v2=13.0):
    """The removed area: a rectangle u (43.5 - depth) ... 45, v (v1 - r) ... (v2 + r), its two corners at u = 43.5 - depth
    rounded at r (seen from the board these are the inner corners); the corners at the old edge stay sharp."""
    ue = 43.5 - depth
    lo, hi = v1 - r, v2 + r
    rect = box(ue, lo, 45.0, hi)
    # cut the two corner squares and add back quarter discs: the removed area keeps a rounded corner
    sq = unary_union([box(ue, lo, ue + r, lo + r), box(ue, hi - r, ue + r, hi)])
    discs = unary_union([Point(ue + r, lo + r).buffer(r, 256), Point(ue + r, hi - r).buffer(r, 256)])
    return rect.difference(sq).union(discs.intersection(sq))


def to_shapely(sps):
    """SHAPE_POLY_SET -> shapely geometry (outlines with holes), board frame."""
    polys = []
    for i in range(sps.OutlineCount()):
        ol = sps.Outline(i)
        outer = [uv(ol.CPoint(k)) for k in range(ol.PointCount())]
        holes = []
        for h in range(sps.HoleCount(i)):
            hl = sps.CHole(i, h)
            holes.append([uv(hl.CPoint(k)) for k in range(hl.PointCount())])
        if len(outer) >= 3:
            polys.append(Polygon(outer, holes).buffer(0))
    return unary_union(polys) if polys else None


def item_poly(item, layer):
    sps = pcbnew.SHAPE_POLY_SET()
    item.TransformShapeToPolygon(sps, layer, 0, MAXERR, pcbnew.ERROR_INSIDE)
    return to_shapely(sps)


def main(path):
    b = pcbnew.LoadBoard(path)
    name = b.GetLayerName
    rel = {d: relief(d) for d in DEPTHS}
    rows = []

    def add(kind, ref, layer, net, geom, note=''):
        if geom is None or geom.is_empty:
            return
        part = geom.intersection(REGION)
        if part.is_empty:
            return
        x0, y0, x1, y1 = part.bounds
        dist = {d: geom.distance(rel[d]) for d in DEPTHS}
        rows.append((kind, ref, layer, net, x0, x1, y0, y1, dist, note))

    cu = [l for l in b.GetEnabledLayers().CuStack()]
    # tracks, arcs, vias
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            v = t.Cast()
            g = item_poly(v, pcbnew.F_Cu)
            add('via', '', 'all copper (through)', v.GetNetname(), g, 'dia %.2f drill %.2f' % (TO(v.GetWidth(pcbnew.F_Cu)), TO(v.GetDrillValue())))
        else:
            g = item_poly(t, t.GetLayer())
            add('track' if t.Type() == pcbnew.PCB_TRACE_T else 'arc', '', name(t.GetLayer()), t.GetNetname(), g, 'width %.2f' % TO(t.GetWidth()))
    # pads, footprint graphics and texts
    for fp in b.GetFootprints():
        ref = fp.GetReference()
        for p in fp.Pads():
            for l in p.GetLayerSet().Seq():
                if l in cu or l in (pcbnew.F_Mask, pcbnew.B_Mask, pcbnew.F_Paste, pcbnew.B_Paste):
                    g = item_poly(p, l)
                    add('pad', '%s.%s' % (ref, p.GetNumber()), name(l), p.GetNetname(), g, 'through-hole' if p.HasHole() else 'SMD')
        for gi in fp.GraphicalItems():
            l = gi.GetLayer()
            try:
                g = item_poly(gi, l)
            except Exception:
                continue
            add('footprint ' + ('text' if gi.Type() in (pcbnew.PCB_TEXT_T, pcbnew.PCB_FIELD_T) else 'shape'), ref, name(l), '', g)
        for f in fp.GetFields():
            if f.IsVisible():
                g = item_poly(f, f.GetLayer())
                add('footprint text', ref, name(f.GetLayer()), '', g, f.GetText())
        # courtyard as KiCad builds it
        for side, lay in ((pcbnew.F_CrtYd, 'F.Courtyard'), (pcbnew.B_CrtYd, 'B.Courtyard')):
            cy = fp.GetCourtyard(side)
            if cy.OutlineCount():
                add('courtyard', ref, lay, '', to_shapely(cy))
    # board-level drawings (silk, fab, user, edge)
    for d in b.GetDrawings():
        l = d.GetLayer()
        try:
            g = item_poly(d, l)
        except Exception:
            continue
        add('board ' + ('text' if d.Type() == pcbnew.PCB_TEXT_T else 'shape'), '', name(l), '', g, getattr(d, 'GetText', lambda: '')() if d.Type() == pcbnew.PCB_TEXT_T else '')
    # zones: outlines and fills
    for z in b.Zones():
        zn = z.GetZoneName() or '(no name)'
        ol = to_shapely(z.Outline())
        for l in z.GetLayerSet().Seq():
            if z.GetIsRuleArea():
                add('rule area', zn, name(l), '', ol)
                continue
            fill = z.GetFilledPolysList(l)
            g = to_shapely(fill) if fill.OutlineCount() else None
            add('pour (filled)', zn, name(l), z.GetNetname(), g, 'priority %d' % z.GetAssignedPriority())
            add('pour outline', zn, name(l), z.GetNetname(), ol, 'priority %d' % z.GetAssignedPriority())

    rows.sort(key=lambda r: (r[2], r[0], r[1], -r[5]))
    hdr = '%-15s %-10s %-12s %-28s %15s %15s  %6s %6s %6s  %s' % ('kind', 'ref', 'layer', 'net', 'u (in region)', 'v (in region)',
                                                                  'd1.5', 'd1.25', 'd1.0', 'note')
    print('Region: u +41.0 ... +43.5, v 0 ... +14.5. Relief drawn with inner corners at radius %.2f, span v %.2f ... %.2f at the side walls.'
          % (R_CORNER, 1.5 - R_CORNER, 13.0 + R_CORNER))
    print('dN = smallest distance from the whole item to the relief of depth N (0 = it overlaps the removed area).')
    print('Copper must keep %.2f from the new edge.' % EDGE_CLEAR)
    print(hdr)
    for k, ref, lay, net, x0, x1, y0, y1, dist, note in rows:
        flag = ''
        is_cu = lay.endswith('.Cu') or lay.startswith('all copper')
        if is_cu and k not in ('pour outline',):
            flag = ' <-- copper inside %.2f of the 1.5 relief' % EDGE_CLEAR if dist[1.5] < EDGE_CLEAR - 1e-6 else ''
        print('%-15s %-10s %-12s %-28s %+7.2f..%+6.2f %+7.2f..%+6.2f  %6.2f %6.2f %6.2f  %s%s' % (
            k, ref, lay, net[-28:], x0, min(x1, 43.5), y0, y1, dist[1.5], dist[1.25], dist[1.0], note, flag))
    # summary per depth
    print()
    for d in DEPTHS:
        hit = [r for r in rows if (r[2].endswith('.Cu') or r[2].startswith('all copper')) and r[0] != 'pour outline' and r[8][d] < EDGE_CLEAR - 1e-6]
        fixed = [r for r in hit if r[0] not in ('pour (filled)',)]
        pours = [r for r in hit if r[0] == 'pour (filled)']
        print('depth %.2f: copper closer than %.2f to the new edge: %d items (%d tracks/vias/pads, %d pour fills)' % (d, EDGE_CLEAR, len(hit), len(fixed), len(pours)))
        for r in hit:
            print('   %-15s %-10s %-8s %-30s nearest %.2f' % (r[0], r[1], r[2], r[3][-30:], r[8][d]))


if __name__ == '__main__':
    main(sys.argv[1])
