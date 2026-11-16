"""JLC's three conditions for ink-plugged vias (capabilities page, row "Plugged vias", read 2026-11-16) against a board:
  1 no soldermask opening on either side of the via;  2 >= 0.35 mm from other soldermask openings (e.g. pads);
  3 no wider than 0.5 mm (JLC's help article 'pcb-via-covering': via holes <= 0.5 mm).
usage: plug_check.py board.kicad_pcb"""
import sys
from collections import Counter
import pcbnew
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from shapely.strtree import STRtree
TO = pcbnew.ToMM
b = pcbnew.LoadBoard(sys.argv[1])
def polys(sps):
    out = []
    for k in range(sps.OutlineCount()):
        o = sps.Outline(k); out.append(Polygon([(TO(o.CPoint(i).x), TO(o.CPoint(i).y)) for i in range(o.PointCount())]))
    return out
res = {}
vias = [t for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
print("vias:", len(vias), dict(Counter((TO(v.GetDrillValue()), TO(v.GetWidth(pcbnew.F_Cu))) for v in vias)))
print("3  widest via hole: %.2f mm (limit 0.5)" % max(TO(v.GetDrillValue()) for v in vias))
openings = {}
for side, mask in (('door side', pcbnew.F_Mask), ('back', pcbnew.B_Mask)):
    op = []
    for f in b.GetFootprints():
        for p in f.Pads():
            if not p.IsOnLayer(mask): continue
            sps = pcbnew.SHAPE_POLY_SET()
            p.TransformShapeToPolygon(sps, mask, p.GetSolderMaskExpansion(mask), pcbnew.FromMM(0.002), pcbnew.ERROR_OUTSIDE)
            for g in polys(sps): op.append((g, '%s.%s' % (f.GetReference(), p.GetNumber())))
        for d in f.GraphicalItems():
            if d.IsOnLayer(mask):
                sps = pcbnew.SHAPE_POLY_SET(); d.TransformShapeToPolygon(sps, mask, 0, pcbnew.FromMM(0.002), pcbnew.ERROR_OUTSIDE)
                for g in polys(sps): op.append((g, f.GetReference() + ' graphic'))
    for d in b.GetDrawings():
        if d.IsOnLayer(mask):
            sps = pcbnew.SHAPE_POLY_SET(); d.TransformShapeToPolygon(sps, mask, 0, pcbnew.FromMM(0.002), pcbnew.ERROR_OUTSIDE)
            for g in polys(sps): op.append((g, 'board graphic'))
    for z in b.Zones():
        if z.IsOnLayer(mask): print("   zone on mask layer:", z.GetZoneName())
    openings[side] = op
    print("%s: %d soldermask openings" % (side, len(op)))
tented_setting = (b.GetDesignSettings().m_TentViasFront, b.GetDesignSettings().m_TentViasBack)
print("1  board setting 'tent vias' front/back:", tented_setting)
rows = []
for v in vias:
    c = v.GetPosition(); pt = Point(TO(c.x), TO(c.y)); rh = TO(v.GetDrillValue()) / 2; rp = TO(v.GetWidth(pcbnew.F_Cu)) / 2
    best = (9e9, None, None)
    for side, op in openings.items():
        for g, name in op:
            d = g.distance(pt)
            if d < best[0]: best = (d, name, side)
    rows.append((best[0] - rh, best[0] - rp, best[0], v.GetNetname(), (round(pt.x - 43.5, 3), round(28.95 - pt.y, 3)), best[1], best[2], TO(v.GetDrillValue()), TO(v.GetWidth(pcbnew.F_Cu))))
inside = [r for r in rows if r[2] <= 0]
print("1  vias whose centre lies inside a soldermask opening (via in pad): %d" % len(inside))
for r in inside: print("     ", r[3], r[4], r[5], r[6])
hole_lt = [r for r in rows if r[0] < 0.35]; pad_lt = [r for r in rows if r[1] < 0.35]
print("2  vias with the HOLE's wall nearer than 0.35 to a soldermask opening: %d of %d" % (len(hole_lt), len(rows)))
print("2  vias with the via's COPPER RING nearer than 0.35 to a soldermask opening: %d of %d" % (len(pad_lt), len(rows)))
print("   smallest distances, hole wall / ring (mm):")
for r in sorted(rows)[:12]: print("     %.3f / %.3f  via %.1f/%.2f %-34s u %+.3f v %+.3f -> %s (%s)" % (r[0], r[1], r[7], r[8], r[3], r[4][0], r[4][1], r[5], r[6]))
print("   by net, ring nearer than 0.35:", dict(Counter(r[3] for r in pad_lt).most_common(12)))
# plated holes that are footprint pads, not vias (JLC treats holes with soldermask openings as pads; they are never plugged)
th = Counter()
for f in b.GetFootprints():
    for p in f.Pads():
        if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH and p.GetDrillSize().x > 0:
            th[(f.GetReference(), TO(p.GetDrillSize().x), TO(p.GetDrillSize().y), p.IsOnLayer(pcbnew.F_Mask), p.IsOnLayer(pcbnew.B_Mask))] += 1
small = {k: n for k, n in th.items() if k[1] <= 0.5}
print("plated footprint holes of 0.5 or less (ref, hole x, hole y, opening door side, opening back): count")
for k, n in sorted(small.items()): print("     ", k, n)
