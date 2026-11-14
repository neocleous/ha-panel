"""Compare two boards (rev 3.1 and the relief board): parts, tracks, vias, pours, outline; and the copper nearest the
new edge in the relief's span.
    python3.12 compare_boards.py <old.kicad_pcb> <new.kicad_pcb>
"""
import os
import sys
from collections import defaultdict

import pcbnew
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fills as F          # noqa: E402

U0, V0 = 43.5, 28.95
TO = pcbnew.ToMM
MAXERR = pcbnew.FromMM(0.002)


def uv(p):
    return (round(TO(p.x) - U0, 4), round(V0 - TO(p.y), 4))


def segs(b):
    out = {}
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            out[('via', t.GetNetname(), uv(t.GetPosition()), round(TO(t.GetWidth(pcbnew.F_Cu)), 3))] = t
        else:
            a, c = sorted([uv(t.GetStart()), uv(t.GetEnd())])
            out[('track', t.GetNetname(), b.GetLayerName(t.GetLayer()), a, c, round(TO(t.GetWidth()), 3))] = t
    return out


def outline(b):
    sps = pcbnew.SHAPE_POLY_SET()
    b.GetBoardPolygonOutlines(sps)
    return F.sps_to_geom(sps)


def main(old, new):
    a, c = pcbnew.LoadBoard(old), pcbnew.LoadBoard(new)
    # parts
    moved = []
    for fa in a.GetFootprints():
        fc = c.FindFootprintByReference(fa.GetReference())
        if fc is None:
            moved.append((fa.GetReference(), 'missing'))
            continue
        if uv(fa.GetPosition()) != uv(fc.GetPosition()) or abs(fa.GetOrientationDegrees() - fc.GetOrientationDegrees()) > 1e-6:
            moved.append((fa.GetReference(), uv(fa.GetPosition()), uv(fc.GetPosition())))
    print('parts: %d and %d; moved: %s' % (len(a.GetFootprints()), len(c.GetFootprints()), moved or 'none'))
    # tracks and vias
    sa, sc = segs(a), segs(c)
    gone = [k for k in sa if k not in sc]
    added = [k for k in sc if k not in sa]
    by_net = defaultdict(lambda: [0.0, 0.0, 0, 0])
    for k in gone:
        if k[0] == 'via':
            by_net[k[1]][2] += 1
        else:
            by_net[k[1]][0] += LineString([k[3], k[4]]).length
    for k in added:
        if k[0] == 'via':
            by_net[k[1]][3] += 1
        else:
            by_net[k[1]][1] += LineString([k[3], k[4]]).length
    tot_a = sum(LineString([k[3], k[4]]).length for k in sa if k[0] == 'track')
    tot_c = sum(LineString([k[3], k[4]]).length for k in sc if k[0] == 'track')
    print('tracks: %.1f mm and %.1f mm; vias %d and %d' % (tot_a, tot_c, sum(1 for k in sa if k[0] == 'via'), sum(1 for k in sc if k[0] == 'via')))
    for n, (lg, la, vg, va) in sorted(by_net.items()):
        print('   %-24s taken out %6.2f mm, laid %6.2f mm; vias out %d, in %d' % (n, lg, la, vg, va))
    print('   pieces taken out:')
    for k in sorted(gone, key=str):
        print('     ', k[0], k[1], *(k[2:]))
    print('   pieces laid:')
    for k in sorted(added, key=str):
        print('     ', k[0], k[1], *(k[2:]))
    # pours
    print('pours:')
    for k, a0, a1, g, l, bb, lost, gained in F.compare(F.fills(a), F.fills(c)):
        print('   %-32s %-7s %8.2f -> %8.2f mm2  gained %6.2f lost %6.2f  where %s' % (k[0][:32], k[1], a0, a1, g, l, bb))
    # outline
    oa, oc = outline(a), outline(c)
    cut = oa.difference(oc)
    print('outline: board area %.2f -> %.2f mm2; removed %.3f mm2 within u %.3f..%.3f v %.3f..%.3f; added %.4f mm2'
          % (oa.area, oc.area, cut.area, *[cut.bounds[i] for i in (0, 2, 1, 3)], oc.difference(oa).area))
    # copper nearest the new edge in the span
    edge = oc.exterior
    near_items = []
    span = box(40.0, -0.5, 43.6, 15.0)
    for t in c.GetTracks():
        layers = [pcbnew.F_Cu] if t.Type() == pcbnew.PCB_VIA_T else [t.GetLayer()]
        for l in layers:
            sps = pcbnew.SHAPE_POLY_SET()
            t.TransformShapeToPolygon(sps, l, 0, MAXERR, pcbnew.ERROR_INSIDE)
            g = F.sps_to_geom(sps)
            if g.intersects(span):
                near_items.append((g.distance(cut.buffer(0)) if False else g.distance(edge.intersection(span)),
                                   'via' if t.Type() == pcbnew.PCB_VIA_T else 'track ' + c.GetLayerName(l), t.GetNetname()))
    for fp in c.GetFootprints():
        for p in fp.Pads():
            for l in p.GetLayerSet().Seq():
                if c.GetLayerName(l).endswith('.Cu'):
                    sps = pcbnew.SHAPE_POLY_SET()
                    p.TransformShapeToPolygon(sps, l, 0, MAXERR, pcbnew.ERROR_INSIDE)
                    g = F.sps_to_geom(sps)
                    if g.intersects(span):
                        near_items.append((g.distance(edge.intersection(span)), 'pad %s.%s %s' % (fp.GetReference(), p.GetNumber(), c.GetLayerName(l)), p.GetNetname()))
    for k, g in F.fills(c).items():
        part = g.intersection(span)
        if not part.is_empty:
            near_items.append((part.distance(edge.intersection(span)), 'pour ' + k[1], k[0]))
    near_items.sort()
    print('copper nearest the edge between v -0.5 and +15.0 (new outline):')
    for d, what, net in near_items[:14]:
        print('   %.3f  %-22s %s' % (d, what, net))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
