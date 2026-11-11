"""Rev 3.1: the floor plan data (floorplan.json) read back from the routed board, in the form sitecheck.py reads.
Geometry comes from the board file; value, footprint name and how the part was placed come from rev3/floorplan.json.
Run: python3 plan_from_board.py <board.kicad_pcb> <rev3/floorplan.json> <out floorplan.json>   (needs KiCad's pcbnew)"""
import json
import sys

import pcbnew

U0, V0 = 43.5, 28.95
TO = pcbnew.ToMM
WIRE_PADS = ('J3', 'J4', 'J7')        # no body: their box is the pads plus 0.3, as in the rev 3 plan (rev3/floorplan.py)


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
    json.dump({'outline': old['outline'], 'amp_keep': old['amp_keep'], 'parts': parts}, open(out, 'w'), indent=1)
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


if __name__ == '__main__':
    main(*sys.argv[1:4])
