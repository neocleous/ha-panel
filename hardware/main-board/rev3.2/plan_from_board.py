"""Rev 3.2: the floor plan data (floorplan.json) read back from the routed board, in the form sitecheck.py reads.
As rev 3.1's script, with the board outline read back as well: the outline polygon and the relief in the +u side edge.
Geometry comes from the board file; value, footprint name and how the part was placed come from rev3.1/floorplan.json.
Run: python3 plan_from_board.py <board.kicad_pcb> <rev3.1/floorplan.json> <out floorplan.json>   (needs KiCad's pcbnew)"""
import json
import math
import sys

import pcbnew

U0, V0 = 43.5, 28.95
TO = pcbnew.ToMM
WIRE_PADS = ('J3', 'J4', 'J7')        # no body: their box is the pads plus 0.3, as in the rev 3 plan (rev3/floorplan.py)


def uv(p):
    return (round(TO(p.x) - U0, 4), round(V0 - TO(p.y), 4))


def outline(b):
    """The board outline as KiCad builds it (arcs as polygons, 0.005 error), and the Edge.Cuts shapes themselves."""
    sps = pcbnew.SHAPE_POLY_SET()
    b.GetBoardPolygonOutlines(sps)
    ol = sps.Outline(0)
    poly = [uv(ol.CPoint(k)) for k in range(ol.PointCount())]
    shapes = []
    for d in b.GetDrawings():
        if d.GetLayer() != pcbnew.Edge_Cuts:
            continue
        if d.GetShape() == pcbnew.SHAPE_T_ARC:
            c = uv(d.GetCenter())
            shapes.append({'arc': [uv(d.GetStart()), uv(d.GetArcMid()), uv(d.GetEnd())], 'centre': c, 'r': round(TO(d.GetRadius()), 4)})
        else:
            shapes.append({'line': [uv(d.GetStart()), uv(d.GetEnd())]})
    return poly, shapes


def relief(shapes):
    """The relief in the +u side edge, from the Edge.Cuts shapes: the floor (the line inside u +43.5 that runs along v),
    the two side walls (lines along u) and the two inner corners (arcs)."""
    near_edge = lambda u: U0 - 5.0 < u < U0 - 1e-6           # inside the +u edge, within 5 of it
    floor = [s['line'] for s in shapes if 'line' in s and abs(s['line'][0][0] - s['line'][1][0]) < 1e-6 and near_edge(s['line'][0][0])]
    walls = [s['line'] for s in shapes if 'line' in s and abs(s['line'][0][1] - s['line'][1][1]) < 1e-6
             and max(s['line'][0][0], s['line'][1][0]) > U0 - 1e-6 and near_edge(min(s['line'][0][0], s['line'][1][0]))]
    arcs = [s for s in shapes if 'arc' in s and near_edge(s['centre'][0])]
    if not floor:
        return None
    f = floor[0]
    return {'floor_u': f[0][0], 'floor_v': sorted([f[0][1], f[1][1]]), 'depth': round(U0 - f[0][0], 4),
            'side_walls_v': sorted(w[0][1] for w in walls), 'corner_radius': sorted({a['r'] for a in arcs}),
            'corner_centres': sorted(a['centre'] for a in arcs)}


def main(board, old_json, out):
    b = pcbnew.LoadBoard(board)
    old = json.load(open(old_json))
    parts = {}
    for fp in b.GetFootprints():
        ref = fp.GetReference()
        o = old['parts'][ref]
        cy = fp.GetCourtyard(pcbnew.F_CrtYd)
        bb = cy.BBox() if cy.OutlineCount() else fp.GetBoundingBox(False)
        c = fp.GetPosition()
        pads = []
        for p in fp.Pads():
            q = p.GetPosition()
            pb = p.GetBoundingBox()
            if not p.GetNumber() and not p.HasHole():
                continue                                   # paste-only and mask-only shapes
            pads.append({'n': p.GetNumber(), 'u': round(TO(q.x) - U0, 3), 'v': round(V0 - TO(q.y), 3), 'tht': bool(p.HasHole()),
                         'sx': round(TO(pb.GetWidth()), 3), 'sy': round(TO(pb.GetHeight()), 3), 'net': p.GetNetname()})
        box = [round(TO(bb.GetX()) - U0, 3), round(V0 - TO(bb.GetBottom()), 3), round(TO(bb.GetRight()) - U0, 3), round(V0 - TO(bb.GetY()), 3)]
        if ref in WIRE_PADS:
            box = [round(min(p['u'] - p['sx'] / 2 for p in pads) - 0.3, 3), round(min(p['v'] - p['sy'] / 2 for p in pads) - 0.3, 3),
                   round(max(p['u'] + p['sx'] / 2 for p in pads) + 0.3, 3), round(max(p['v'] + p['sy'] / 2 for p in pads) + 0.3, 3)]
        parts[ref] = {'value': o['value'], 'footprint': o['footprint'], 'u': round(TO(c.x) - U0, 3), 'v': round(V0 - TO(c.y), 3),
                      'rot': fp.GetOrientationDegrees() % 360, 'crt': box,
                      'placed': o['placed'], 'from_anchor': o['from_anchor'], 'side': 'B' if fp.IsFlipped() else 'F', 'pads': pads}
    poly, shapes = outline(b)
    rel = relief(shapes)
    us, vs = [p[0] for p in poly], [p[1] for p in poly]
    json.dump({'outline': [round(min(us), 3), round(min(vs), 3), round(max(us), 3), round(max(vs), 3)], 'outline_polygon': poly,
               'edge_cuts': shapes, 'relief': rel, 'amp_keep': old['amp_keep'], 'parts': parts}, open(out, 'w'), indent=1)
    print('outline: box u %+.2f ... %+.2f, v %+.2f ... %+.2f; polygon of %d points' % (min(us), max(us), min(vs), max(vs), len(poly)))
    print('relief:', rel)
    # what moved against the old plan
    moved = []
    for ref in sorted(parts, key=lambda r: (r.rstrip('0123456789'), int(''.join(ch for ch in r if ch.isdigit()) or 0))):
        n, o = parts[ref], old['parts'][ref]
        if abs(n['u'] - o['u']) > 0.02 or abs(n['v'] - o['v']) > 0.02 or abs((n['rot'] - o['rot'] + 180) % 360 - 180) > 0.1:
            moved.append((ref, o['u'], o['v'], o['rot'], n['u'], n['v'], n['rot']))
    print('%d parts; moved against the old plan: %d' % (len(parts), len(moved)))
    for m in moved:
        print('  %-5s u %+7.2f v %+7.2f rot %3.0f  ->  u %+7.2f v %+7.2f rot %3.0f' % m)
    worst = max(max(abs(a - c) for a, c in zip(parts[r]['crt'], old['parts'][r]['crt'])) for r in parts if r not in [m[0] for m in moved])
    print('parts that did not move: largest difference between the two courtyard boxes %.3f' % worst)
    padmax = max(abs(a[k] - c[k]) for r in parts for a, c in zip(parts[r]['pads'], old['parts'][r]['pads']) for k in ('u', 'v', 'sx', 'sy'))
    print('pads: largest difference of position or size against the old plan %.3f' % padmax)


if __name__ == '__main__':
    main(*sys.argv[1:4])
