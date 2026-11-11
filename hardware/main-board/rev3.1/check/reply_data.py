"""The numbers of the rev 3.1 reply to the enclosure that are not in the site check. Reads two board files, changes nothing.

    python3 reply_data.py <rev 3 board> <rev 3.1 board>

1. parts list of rev 3.1 against rev 3 (reference, value, footprint, fitted or not);
2. everything that moved: position, turn, box on the board (courtyard), height;
3. nearest copper to each hole's centre on the two outer layers (the copper-free circles);
4. where the copper named in the reply lies on the back layer and on the door side (board frame);
5. the two sensor headers: probe points and distances.
Board frame: u = X - 43.5, v = 28.95 - Y.
"""
import math
import os
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import sitecheck as SC                                   # noqa: E402  (height table)

TO = pcbnew.ToMM
FR = pcbnew.FromMM


def uv(p):
    return TO(p.x) - 43.5, 28.95 - TO(p.y)


def crt(fp):
    bb = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()
    if bb.GetWidth() == 0:
        bb = fp.GetBoundingBox(False)
    return (TO(bb.GetX()) - 43.5, 28.95 - TO(bb.GetBottom()), TO(bb.GetRight()) - 43.5, 28.95 - TO(bb.GetY()))


def parts(b):
    return {f.GetReference(): f for f in b.GetFootprints()}


def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0.0 if L == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def poly_dist(ps, px, py):
    """Distance in mm from a point to the edges of a SHAPE_POLY_SET (0 if the point is inside copper)."""
    if ps.Contains(pcbnew.VECTOR2I(FR(px), FR(py))):
        return 0.0
    best = 1e9
    for i in range(ps.OutlineCount()):
        rings = [ps.Outline(i)] + [ps.Hole(i, h) for h in range(ps.HoleCount(i))]
        for ch in rings:
            n = ch.PointCount()
            pts = [(TO(ch.CPoint(k).x), TO(ch.CPoint(k).y)) for k in range(n)]
            for k in range(n):
                a, c = pts[k], pts[(k + 1) % n]
                best = min(best, seg_dist(px, py, a[0], a[1], c[0], c[1]))
    return best


def nearest_copper(b, hole, layer):
    """(distance, what) of the nearest copper on a layer to the centre of a hole footprint."""
    p = hole.GetPosition()
    px, py = TO(p.x), TO(p.y)
    best = (1e9, '')
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            d = math.hypot(TO(t.GetPosition().x) - px, TO(t.GetPosition().y) - py) - TO(t.GetWidth(layer)) / 2
            what = 'via ' + t.GetNetname()
        elif t.GetLayer() == layer:
            a, c = t.GetStart(), t.GetEnd()
            d = seg_dist(px, py, TO(a.x), TO(a.y), TO(c.x), TO(c.y)) - TO(t.GetWidth()) / 2
            what = 'track ' + t.GetNetname()
        else:
            continue
        best = min(best, (d, what))
    for f in b.GetFootprints():
        if f.GetReference() == hole.GetReference():
            continue
        for pad in f.Pads():
            if not pad.IsOnLayer(layer):
                continue
            if math.hypot(TO(pad.GetPosition().x) - px, TO(pad.GetPosition().y) - py) > 12:
                continue
            ps = pcbnew.SHAPE_POLY_SET()
            pad.TransformShapeToPolygon(ps, layer, 0, FR(0.005), pcbnew.ERROR_INSIDE)
            best = min(best, (poly_dist(ps, px, py), 'pad %s.%s' % (f.GetReference(), pad.GetNumber())))
    for z in b.Zones():
        if z.GetIsRuleArea() or not z.IsOnLayer(layer):
            continue
        ps = z.GetFilledPolysList(layer)
        if ps.OutlineCount():
            best = min(best, (poly_dist(ps, px, py), 'filled area ' + z.GetNetname()))
    return best


def extent(b, layer, nets, with_zones=True):
    xs, ys, n, wid = [], [], 0, set()
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T or t.GetLayer() != layer or t.GetNetname().split('/')[-1] not in nets:
            continue
        w = TO(t.GetWidth()) / 2
        for q in (t.GetStart(), t.GetEnd()):
            u, v = uv(q)
            xs += [u - w, u + w]
            ys += [v - w, v + w]
        n += 1
        wid.add(round(TO(t.GetWidth()), 2))
    za = 0.0
    if with_zones:
        for z in b.Zones():
            if z.GetIsRuleArea() or not z.IsOnLayer(layer) or z.GetNetname().split('/')[-1] not in nets:
                continue
            bb = z.GetFilledPolysList(layer).BBox()
            if bb.GetWidth():
                u0, v1 = uv(pcbnew.VECTOR2I(bb.GetX(), bb.GetY()))
                u1, v0 = uv(pcbnew.VECTOR2I(bb.GetRight(), bb.GetBottom()))
                xs += [u0, u1]
                ys += [v0, v1]
                za += z.GetFilledPolysList(layer).Area() / 1e12
    if not xs:
        return 'none'
    return 'u %+.1f...%+.1f, v %+.1f...%+.1f; %d track pieces, widths %s%s' % (
        min(xs), max(xs), min(ys), max(ys), n, sorted(wid), '; filled area %.0f mm2' % za if za else '')


def main(p3, p31):
    b3, b31 = pcbnew.LoadBoard(p3), pcbnew.LoadBoard(p31)
    for b in (b3, b31):
        b.BuildConnectivity()
    A, B = parts(b3), parts(b31)

    print('== 1. Parts list, rev 3.1 against rev 3')
    diff = []
    for r in sorted(set(A) | set(B)):
        if r not in A or r not in B:
            diff.append('%s only on %s' % (r, 'rev 3' if r in A else 'rev 3.1'))
            continue
        a = (A[r].GetValue(), A[r].GetFPID().GetLibItemName().wx_str(), A[r].IsDNP())
        c = (B[r].GetValue(), B[r].GetFPID().GetLibItemName().wx_str(), B[r].IsDNP())
        if a != c:
            diff.append('%s: %s -> %s' % (r, a, c))
    print('parts: rev 3 %d, rev 3.1 %d; not fitted: %d and %d; differences in reference, value, footprint or fitted: %s' % (
        len(A), len(B), sum(f.IsDNP() for f in A.values()), sum(f.IsDNP() for f in B.values()), diff or 'none'))

    print('\n== 2. What moved (u, v of the part origin; box = courtyard; height from the table)')
    for r in sorted(B):
        pa, pb = uv(A[r].GetPosition()), uv(B[r].GetPosition())
        ra, rb = A[r].GetOrientationDegrees(), B[r].GetOrientationDegrees()
        if abs(pa[0] - pb[0]) < 0.001 and abs(pa[1] - pb[1]) < 0.001 and abs(ra - rb) < 0.01:
            continue
        ca, cb = crt(A[r]), crt(B[r])
        name = B[r].GetFPID().GetLibItemName().wx_str()
        h = SC.lookup(SC.HEIGHT, name, (None, None))[0]
        print('  %-5s %-22s %-34s (%+.2f, %+.2f) rot %-3.0f -> (%+.2f, %+.2f) rot %-3.0f | box u %+.2f...%+.2f v %+.2f...%+.2f -> u %+.2f...%+.2f v %+.2f...%+.2f | height %s | %s' % (
            r, B[r].GetValue()[:22], name[:34], pa[0], pa[1], ra, pb[0], pb[1], rb, ca[0], ca[2], ca[1], ca[3], cb[0], cb[2], cb[1], cb[3],
            '%.2f' % h if h is not None else '?', 'not fitted' if B[r].IsDNP() else 'fitted'))

    print('\n== 3. Nearest copper to the centre of each hole (mm)')
    for tag, b, P in (('rev 3', b3, A), ('rev 3.1', b31, B)):
        for h in ('H1', 'H2', 'H3', 'H4'):
            f = nearest_copper(b, P[h], pcbnew.F_Cu)
            k = nearest_copper(b, P[h], pcbnew.B_Cu)
            print('  %-7s %s (%+.2f, %+.2f): door side %.2f (%s); back %.2f (%s)' % (tag, h, *uv(P[h].GetPosition()), f[0], f[1], k[0], k[1]))

    print('\n== 4. Where the copper named in the reply lies (rev 3.1; rev 3 in brackets where it differs)')
    rows = (
        ('right speaker pair, back', pcbnew.B_Cu, ('SPK_R_P', 'SPK_R_N'), False),
        ("the Pi's 5 V, back", pcbnew.B_Cu, ('VBUS_PI',), True),
        ("the Pi's 5 V, door side", pcbnew.F_Cu, ('5V_PI_F', 'VBUS_PI'), True),
        ('5 V branches, back', pcbnew.B_Cu, ('+5V',), True),
        ('20 V into the supply module, back', pcbnew.B_Cu, ('+20V',), True),
        ('20 V inlet, door side', pcbnew.F_Cu, ('VIN_PIGTAIL', 'VIN_EF'), True),
        ('ground pour, back', pcbnew.B_Cu, ('GND',), True),
        ('ground pour, door side', pcbnew.F_Cu, ('GND',), True),
    )
    for what, layer, nets, wz in rows:
        e31, e3 = extent(b31, layer, nets, wz), extent(b3, layer, nets, wz)
        print('  %-36s %s%s' % (what, e31, '' if e31 == e3 else '\n  %-36s (rev 3: %s)' % ('', e3)))
    names = sorted({t.GetNetname() for t in b31.GetTracks() if t.Type() != pcbnew.PCB_VIA_T and t.GetLayer() == pcbnew.B_Cu and TO(t.GetWidth()) >= 0.6})
    print('  nets with a track 0.6 or wider on the back:', ', '.join(n.split('/')[-1] for n in names))

    print('\n== 5. The two sensor headers and their neighbours (rev 3.1)')
    for r in ('J10', 'J11', 'J5'):
        pads = [uv(p.GetPosition()) for p in B[r].Pads()]
        cu, cv = sum(p[0] for p in pads) / len(pads), sum(p[1] for p in pads) / len(pads)
        c = crt(B[r])
        print('  %-4s pins u %+.2f...%+.2f, v %+.2f...%+.2f; middle of the pin row (%+.2f, %+.2f); box u %+.2f...%+.2f, v %+.2f...%+.2f' % (
            r, min(p[0] for p in pads), max(p[0] for p in pads), min(p[1] for p in pads), max(p[1] for p in pads), cu, cv, c[0], c[2], c[1], c[3]))
    ps1 = crt(B['PS1'])
    for r in ('J10', 'J11'):
        pads = [uv(p.GetPosition()) for p in B[r].Pads()]
        cv = sum(p[1] for p in pads) / len(pads)
        print('  %-4s middle of the pin row to the supply module\'s box (v %+.2f): %.2f; box to box %.2f' % (r, ps1[1], ps1[1] - cv, ps1[1] - crt(B[r])[3]))
    c5, c10 = crt(B['J5']), crt(B['J10'])
    print('  between the boxes of J5 and J10: %.2f (u %+.2f...%+.2f)' % (c10[0] - c5[2], c5[2], c10[0]))
    for r in ('F3', 'C10', 'TP12', 'R26', 'R27', 'TP19', 'TP20', 'F5', 'C119', 'C120'):
        c = crt(B[r])
        name = B[r].GetFPID().GetLibItemName().wx_str()
        h = SC.lookup(SC.HEIGHT, name, (None, None))[0]
        hp = uv(B['H2'].GetPosition())
        dx = max(c[0] - hp[0], 0, hp[0] - c[2])
        dy = max(c[1] - hp[1], 0, hp[1] - c[3])
        print('  %-5s box u %+.2f...%+.2f, v %+.2f...%+.2f, height %s, box to the centre of H2 %.2f%s' % (
            r, c[0], c[2], c[1], c[3], '%.2f' % h if h is not None else '?', math.hypot(dx, dy), ' (not fitted)' if B[r].IsDNP() else ''))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
