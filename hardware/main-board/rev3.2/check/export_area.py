"""Export the copper, pads, courtyards and silkscreen of an area of the board to JSON (board frame u, v), for plotting.
    python3.12 export_area.py <board.kicad_pcb> <out.json> [u0 u1 v0 v1]
"""
import json
import sys

import pcbnew

U0, V0 = 43.5, 28.95
TO = pcbnew.ToMM
MAXERR = pcbnew.FromMM(0.005)


def uv(p):
    return [round(TO(p.x) - U0, 4), round(V0 - TO(p.y), 4)]


def polys(sps):
    out = []
    for i in range(sps.OutlineCount()):
        ol = sps.Outline(i)
        outer = [uv(ol.CPoint(k)) for k in range(ol.PointCount())]
        holes = [[uv(sps.CHole(i, h).CPoint(k)) for k in range(sps.CHole(i, h).PointCount())] for h in range(sps.HoleCount(i))]
        out.append({'outer': outer, 'holes': holes})
    return out


def shape(item, layer):
    sps = pcbnew.SHAPE_POLY_SET()
    item.TransformShapeToPolygon(sps, layer, 0, MAXERR, pcbnew.ERROR_INSIDE)
    return polys(sps)


def main(path, out, area):
    u0, u1, v0, v1 = area
    b = pcbnew.LoadBoard(path)
    name = b.GetLayerName

    def inside(bb):
        a = TO(bb.GetX()) - U0, TO(bb.GetRight()) - U0, V0 - TO(bb.GetBottom()), V0 - TO(bb.GetY())
        return a[1] >= u0 and a[0] <= u1 and a[3] >= v0 and a[2] <= v1

    items = []
    for t in b.GetTracks():
        if not inside(t.GetBoundingBox()):
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            items.append({'kind': 'via', 'layer': 'via', 'net': t.GetNetname(), 'polys': shape(t, pcbnew.F_Cu),
                          'at': uv(t.GetPosition()), 'dia': TO(t.GetWidth(pcbnew.F_Cu))})
        else:
            items.append({'kind': 'track', 'layer': name(t.GetLayer()), 'net': t.GetNetname(), 'polys': shape(t, t.GetLayer()),
                          'a': uv(t.GetStart()), 'b': uv(t.GetEnd()), 'w': TO(t.GetWidth())})
    for fp in b.GetFootprints():
        if not inside(fp.GetBoundingBox(False)):
            continue
        ref = fp.GetReference()
        for p in fp.Pads():
            for l in p.GetLayerSet().Seq():
                if name(l) in ('F.Cu', 'B.Cu', 'In1.Cu', 'In2.Cu'):
                    items.append({'kind': 'pad', 'layer': name(l), 'net': p.GetNetname(), 'ref': '%s.%s' % (ref, p.GetNumber()),
                                  'polys': shape(p, l), 'at': uv(p.GetPosition()), 'tht': bool(p.HasHole())})
        cy = fp.GetCourtyard(pcbnew.F_CrtYd)
        if cy.OutlineCount():
            items.append({'kind': 'courtyard', 'layer': 'F.CrtYd', 'ref': ref, 'polys': polys(cy), 'at': uv(fp.GetPosition())})
        for gi in fp.GraphicalItems():
            if name(gi.GetLayer()) in ('F.Silkscreen', 'B.Silkscreen'):
                try:
                    items.append({'kind': 'silk', 'layer': name(gi.GetLayer()), 'ref': ref, 'polys': shape(gi, gi.GetLayer())})
                except Exception:
                    pass
        for f in fp.GetFields():
            if f.IsVisible() and name(f.GetLayer()) in ('F.Silkscreen', 'B.Silkscreen'):
                items.append({'kind': 'silk', 'layer': name(f.GetLayer()), 'ref': ref, 'polys': shape(f, f.GetLayer()), 'text': f.GetText()})
    for d in b.GetDrawings():
        if inside(d.GetBoundingBox()) and name(d.GetLayer()) in ('F.Silkscreen', 'B.Silkscreen', 'Edge.Cuts'):
            items.append({'kind': 'drawing', 'layer': name(d.GetLayer()), 'polys': shape(d, d.GetLayer())})
    for z in b.Zones():
        for l in z.GetLayerSet().Seq():
            if z.GetIsRuleArea():
                items.append({'kind': 'rulearea', 'layer': name(l), 'net': '', 'name': z.GetZoneName(), 'polys': polys(z.Outline())})
            else:
                f = z.GetFilledPolysList(l)
                items.append({'kind': 'pour', 'layer': name(l), 'net': z.GetNetname(), 'name': z.GetZoneName(), 'polys': polys(f),
                              'outline': polys(z.Outline())})
    json.dump({'area': area, 'items': items}, open(out, 'w'))
    print('%d items' % len(items))


if __name__ == '__main__':
    a = [float(x) for x in sys.argv[3:7]] if len(sys.argv) > 6 else [28.0, 44.5, -4.0, 18.0]
    main(sys.argv[1], sys.argv[2], a)
