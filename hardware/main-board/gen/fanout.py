"""Fan-out vias for plane nets (In1 GND, In2 +5V/+20V/PVDD) and TAS5756M ground stubs to its thermal pad,
added (locked) before Freerouting so the router only handles signals."""
import math
import pcbnew

MM = pcbnew.FromMM
TO = pcbnew.ToMM
PLANE_NETS = ('GND', '+5V', '+20V', '/Amplifier/PVDD')
VIA_D, VIA_DR = 0.6, 0.3
CLR = 0.2


def inside(poly, x, y):
    n, c = len(poly), False
    for i in range(n):
        x1, y1 = poly[i]; x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def pad_boxes(board):
    out = []
    for fp in board.GetFootprints():
        for p in fp.Pads():
            bb = p.GetBoundingBox()
            out.append((TO(bb.GetX()), TO(bb.GetY()), TO(bb.GetRight()), TO(bb.GetBottom()), p.GetNetname(), p))
    return out


def seg_box_dist(ax, ay, bx, by, box):
    # distance from segment to an axis-aligned box (sampled)
    best = 1e9
    for k in range(11):
        t = k / 10.0
        x, y = ax + (bx - ax) * t, ay + (by - ay) * t
        dx = max(box[0] - x, 0, x - box[2]); dy = max(box[1] - y, 0, y - box[3])
        best = min(best, math.hypot(dx, dy))
    return best


def fanout(board, zones_in2, extra_obstacles=(), tas_ref='U100', skip=()):
    boxes = pad_boxes(board)
    vias = []
    tracks = []
    added = 0
    failed = []
    # TAS ground pins -> stub to the exposed pad
    tas = board.FindFootprintByReference(tas_ref)
    ep = [p for p in tas.Pads() if p.GetNumber() == '49' and p.GetAttribute() == pcbnew.PAD_ATTRIB_SMD]
    ep_bb = max(ep, key=lambda p: p.GetBoundingBox().GetWidth() * p.GetBoundingBox().GetHeight()).GetBoundingBox()
    ey0, ey1 = TO(ep_bb.GetY()), TO(ep_bb.GetBottom())
    gnet = board.FindNet('GND')
    for p in tas.Pads():
        if p.GetNetname() == 'GND' and p.GetNumber() != '49':
            x, y = TO(p.GetPosition().x), TO(p.GetPosition().y)
            ty = ey0 + 0.1 if y < ey0 else ey1 - 0.1
            tracks.append((pcbnew.F_Cu, x, y, x, ty, 0.25, gnet))
    for fp in board.GetFootprints():
        if fp.GetReference() in skip or fp.GetReference() == tas_ref:
            continue
        for p in fp.Pads():
            net = p.GetNetname()
            if net not in PLANE_NETS or p.HasHole() or p.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
                continue
            if not p.IsOnCopperLayer():
                continue
            lay = pcbnew.F_Cu if p.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
            px, py = TO(p.GetPosition().x), TO(p.GetPosition().y)
            bb = p.GetBoundingBox()
            hw, hh = TO(bb.GetWidth()) / 2, TO(bb.GetHeight()) / 2
            ok = None
            for dist in (0.55, 0.75, 1.0, 1.3):
                for ang in range(0, 360, 30):
                    a = math.radians(ang)
                    vx = px + math.cos(a) * (hw + dist)
                    vy = py + math.sin(a) * (hh + dist)
                    if not (0.8 < vx < 89.2 and 0.8 < vy < 49.2):
                        continue
                    if net != 'GND' and not inside(zones_in2[net], vx, vy):
                        continue
                    r = VIA_D / 2 + CLR
                    bad = False
                    for b in boxes:
                        if b[5] is p:
                            continue
                        dx = max(b[0] - vx, 0, vx - b[2]); dy = max(b[1] - vy, 0, vy - b[3])
                        if math.hypot(dx, dy) < r + (0.0 if b[4] == net else 0.0):
                            bad = True; break
                        if b[4] != net and seg_box_dist(px, py, vx, vy, b) < 0.125 + CLR:
                            bad = True; break
                    if bad:
                        continue
                    if any(math.hypot(vx - x2, vy - y2) < VIA_D + CLR for x2, y2 in vias):
                        continue
                    if any(o[0] - r < vx < o[2] + r and o[1] - r < vy < o[3] + r for o in extra_obstacles):
                        continue
                    ok = (vx, vy)
                    break
                if ok:
                    break
            if ok is None:
                failed.append('%s.%s' % (fp.GetReference(), p.GetNumber()))
                continue
            vias.append(ok)
            boxes.append((ok[0] - VIA_D / 2, ok[1] - VIA_D / 2, ok[0] + VIA_D / 2, ok[1] + VIA_D / 2, net, None))
            nobj = board.FindNet(net)
            tracks.append((lay, px, py, ok[0], ok[1], 0.3 if net != '+5V' else 0.5, nobj))
            v = pcbnew.PCB_VIA(board)
            v.SetPosition(pcbnew.VECTOR2I(MM(ok[0]), MM(ok[1])))
            v.SetWidth(MM(VIA_D)); v.SetDrill(MM(VIA_DR)); v.SetNet(nobj); v.SetLocked(True)
            board.Add(v)
            added += 1
    for lay, x1, y1, x2, y2, w, nobj in tracks:
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(MM(x1), MM(y1))); t.SetEnd(pcbnew.VECTOR2I(MM(x2), MM(y2)))
        t.SetWidth(MM(w)); t.SetLayer(lay); t.SetNet(nobj); t.SetLocked(True)
        board.Add(t)
    return added, failed
