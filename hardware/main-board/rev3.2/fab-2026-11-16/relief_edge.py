"""Copper near the relief in the +u side edge of the main board, layer by layer.
usage: relief_edge.py board.kicad_pcb [pullback_mm ...]
Board frame: u = X - 43.5, v = 28.95 - Y. Relief: floor u +42.0 over v +1.5 ... +13.0, arcs r 1.0, walls v +0.5 / +14.0.
For each copper layer: the nearest copper of each kind to the relief's contour, as drawn and with the cut 0.2 deeper,
and what a pull-back of the pours to D from the contour would take away."""
import sys
import pcbnew
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
TO = pcbnew.ToMM
U0, V0 = 43.5, 28.95
def uv(p): return (TO(p.x) - U0, V0 - TO(p.y))
b = pcbnew.LoadBoard(sys.argv[1])
Ds = [float(x) for x in sys.argv[2:]] or [0.4, 0.5]
# board outline as a polygon (KiCad's own, arcs approximated to 0.001)
outl = pcbnew.SHAPE_POLY_SET()
b.GetBoardPolygonOutlines(outl)
def poly_of(sps, k):
    o = sps.Outline(k); ext = [uv(o.CPoint(i)) for i in range(o.PointCount())]
    holes = []
    for h in range(sps.HoleCount(k)):
        hh = sps.Hole(k, h); holes.append([uv(hh.CPoint(i)) for i in range(hh.PointCount())])
    return Polygon(ext, holes)
board = unary_union([poly_of(outl, k) for k in range(outl.OutlineCount())])
print("board outline area %.2f mm2, bounds %s" % (board.area, tuple(round(x, 3) for x in board.bounds)))
# the relief's contour = the part of the outline inside the window u > 41.5, v 0.2 ... 14.3 and not on the old edge u 43.5
win = box(41.5, 0.45, 43.45, 14.05)
relief = board.exterior.intersection(win)
print("relief contour length %.3f, bounds %s" % (relief.length, tuple(round(x, 3) for x in relief.bounds)))
whole_edge = board.boundary
region = box(38.0, -3.0, 44.0, 17.5)
names = {pcbnew.F_Cu: 'F.Cu (door side)', pcbnew.In1_Cu: 'In1.Cu (layer 2)', pcbnew.In2_Cu: 'In2.Cu (layer 3)', pcbnew.B_Cu: 'B.Cu (back)'}
for lay, nm in names.items():
    print("==", nm)
    fills = []
    for z in b.Zones():
        if z.GetIsRuleArea() or not z.IsOnLayer(lay): continue
        sps = z.GetFilledPolysList(lay)
        polys = [poly_of(sps, k) for k in range(sps.OutlineCount())]
        g = unary_union(polys) if polys else None
        if g is None or g.is_empty: continue
        fills.append((z.GetNetname(), z.GetAssignedPriority(), g))
        d_rel = g.distance(relief); d_all = g.distance(whole_edge)
        if d_rel < 3:
            line = "  pour %-22s prio %d: to the relief %.3f; to any edge %.3f" % (z.GetNetname(), z.GetAssignedPriority(), d_rel, d_all)
            for D in Ds:
                band = relief.buffer(D, 64)
                lost = g.intersection(band)
                rest = g.difference(band)
                nparts_before = len(getattr(g, 'geoms', [g])); nparts_after = len(getattr(rest, 'geoms', [rest]))
                line += " | D %.2f: -%.3f mm2, islands %d -> %d" % (D, lost.area, nparts_before, nparts_after)
            print(line)
    items = []
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            c = uv(t.GetPosition()); g = Point(c).buffer(TO(t.GetWidth(lay)) / 2, 32); kind = 'via %.2f/%.2f' % (TO(t.GetDrillValue()), TO(t.GetWidth(lay)))
        elif t.IsOnLayer(lay):
            a, c2 = uv(t.GetStart()), uv(t.GetEnd()); g = LineString([a, c2]).buffer(TO(t.GetWidth()) / 2, 32); kind = 'track %.2f' % TO(t.GetWidth())
        else: continue
        d = g.distance(relief)
        if d < 2.0: items.append((d, kind, t.GetNetname(), tuple(round(x, 3) for x in g.centroid.coords[0])))
    for f in b.GetFootprints():
        for p in f.Pads():
            if not p.IsOnLayer(lay): continue
            sps = pcbnew.SHAPE_POLY_SET(); p.TransformShapeToPolygon(sps, lay, 0, pcbnew.FromMM(0.002), pcbnew.ERROR_INSIDE)
            if sps.OutlineCount() == 0: continue
            g = unary_union([poly_of(sps, k) for k in range(sps.OutlineCount())]); d = g.distance(relief)
            if d < 2.0: items.append((d, 'pad %s.%s' % (f.GetReference(), p.GetNumber()), p.GetNetname(), tuple(round(x, 3) for x in g.centroid.coords[0])))
    for d, kind, net, c in sorted(items)[:6]:
        print("  %-18s %-34s at u %+.3f v %+.3f: to the relief %.3f (cut 0.2 deeper: %.3f)" % (kind, net, c[0], c[1], d, d - 0.2))
