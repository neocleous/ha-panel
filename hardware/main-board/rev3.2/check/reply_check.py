"""The numbers of the rev 3.2 reply (and rev3.2/README.md) computed again from the board files. Changes nothing.

    python3 reply_check.py <rev 3.1 board> <rev 3.2 board>

Each line: the figure as written, the figure from the files, agree or not. Needs KiCad 9's Python and shapely.
"""
import os
import sys

import pcbnew
from shapely.geometry import LineString, box

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fills as F                                        # noqa: E402

U0, V0 = 43.5, 28.95
TO = pcbnew.ToMM
bad = 0


def uv(p):
    return (TO(p.x) - U0, V0 - TO(p.y))


def check(what, written, got, tol):
    global bad
    ok = all(abs(a - b) <= tol for a, b in zip(written, got)) if isinstance(written, tuple) else abs(written - got) <= tol
    bad += not ok
    print('%-62s written %-22s files %-26s %s' % (what, written, tuple(round(x, 4) for x in got) if isinstance(got, tuple) else round(got, 4),
                                                   'agree' if ok else 'DIFFERENT'))


def main(b31, b32):
    a, c = pcbnew.LoadBoard(b31), pcbnew.LoadBoard(b32)
    # --- the relief: corner points of the Edge.Cuts shapes
    pts, arcs = set(), []
    for d in c.GetDrawings():
        if d.GetLayer() != pcbnew.Edge_Cuts:
            continue
        for p in (d.GetStart(), d.GetEnd()):
            q = uv(p)
            if q[0] > 41:
                pts.add((round(q[0], 4), round(q[1], 4)))
        if d.GetShape() == pcbnew.SHAPE_T_ARC:
            arcs.append((uv(d.GetCenter()), TO(d.GetRadius())))
    for p in [(43.5, 14.0), (43.0, 14.0), (42.0, 13.0), (42.0, 1.5), (43.0, 0.5), (43.5, 0.5)]:
        near = min(pts, key=lambda q: (q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2)
        check('relief corner point', p, near, 0.0005)
    for cen, r in sorted(arcs):
        check('inner corner: centre', min([(43.0, 1.5), (43.0, 13.0)], key=lambda q: abs(q[1] - cen[1])), cen, 0.0005)
        check('inner corner: radius', 1.0, r, 0.0005)
    oa, oc = F.sps_to_geom(_outline(a)), F.sps_to_geom(_outline(c))
    check('board area rev 3.1 (mm2)', 5037.30, oa.area, 0.006)
    check('board area rev 3.2 (mm2)', 5017.48, oc.area, 0.006)
    check('cut away (mm2)', 19.82, oa.area - oc.area, 0.006)
    # --- the GPIO2 via and tracks
    net = '/Amplifier/AMP_GPIO2'
    va = [uv(t.GetPosition()) for t in a.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() == net and uv(t.GetPosition())[0] > 40]
    vc = [uv(t.GetPosition()) for t in c.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() == net and uv(t.GetPosition())[0] > 40]
    check('GPIO2 via rev 3.1', (41.585, 4.589), va[0], 0.0006)
    check('GPIO2 via rev 3.2', (40.500, 4.750), vc[0], 0.0006)
    segs = {}
    for t in c.GetTracks():
        if t.Type() != pcbnew.PCB_VIA_T and t.GetNetname() in (net, 'I2C_SCL', 'I2C_SDA'):
            segs.setdefault((t.GetNetname(), c.GetLayerName(t.GetLayer())), []).append((uv(t.GetStart()), uv(t.GetEnd())))

    def has(netlayer, p, q, tol=0.0006):
        for s, e in segs[netlayer]:
            for x, y in ((s, e), (e, s)):
                if abs(x[0] - p[0]) <= tol and abs(x[1] - p[1]) <= tol and abs(y[0] - q[0]) <= tol and abs(y[1] - q[1]) <= tol:
                    return 1.0
        return 0.0
    for nl, p, q in [((net, 'F.Cu'), (40.867, 3.870), (40.867, 4.383)), ((net, 'F.Cu'), (40.867, 4.383), (40.500, 4.750)),
                     ((net, 'B.Cu'), (40.500, 4.750), (40.339, 4.589)), ((net, 'B.Cu'), (40.339, 4.589), (37.862, 4.589)),
                     (('I2C_SCL', 'B.Cu'), (41.52, 1.0243), (41.52, 6.0743)), (('I2C_SCL', 'B.Cu'), (41.52, 6.0743), (41.47, 6.1243)),
                     (('I2C_SDA', 'B.Cu'), (41.150, 2.8811), (41.150, 5.7277)), (('I2C_SDA', 'B.Cu'), (41.150, 5.7277), (38.875, 6.725))]:
        check('%s %s piece %s -> %s present' % (nl[0].split('/')[-1], nl[1], p, q), 1.0, has(nl, p, q), 0)
    # --- pours and nearest copper
    fa, fc = F.fills(a), F.fills(c)
    k = [k for k in fc if k[0] == '/Amplifier/PVDD' and k[2] == 1][0]
    check('amplifier supply plane rev 3.1 (mm2)', 814.09, fa[k].area, 0.006)
    check('amplifier supply plane rev 3.2 (mm2)', 804.81, fc[k].area, 0.006)
    corner = fa[k].difference(fc[k]).intersection(box(41.3, -1, 44, 7))
    check('plane: lost at its corner (mm2)', 8.81, corner.area, 0.006)
    for name, lay, old, new in (('GND', 'F.Cu', 3018.91, 2996.41), ('GND', 'In1.Cu', 4489.33, 4468.89), ('GND', 'B.Cu', 3347.36, 3331.06)):
        kk = [x for x in fc if x[0] == name and x[1] == lay][0]
        check('ground pour %s (mm2), rev 3.1 / rev 3.2' % lay, (old, new), (fa[kk].area, fc[kk].area), 0.006)
    floor = LineString([(42.0, 1.5), (42.0, 13.0)])
    span = box(39, 1.5, 44, 13.0)
    pour_d = min(g.intersection(span).distance(floor) for kk, g in fc.items() if not g.intersection(span).is_empty)
    check('pours to the floor, along the floor', 0.30, pour_d, 0.001)
    tr = []
    for t in c.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            continue
        sps = pcbnew.SHAPE_POLY_SET()
        t.TransformShapeToPolygon(sps, t.GetLayer(), 0, pcbnew.FromMM(0.002), pcbnew.ERROR_INSIDE)
        g = F.sps_to_geom(sps)
        if g.intersects(box(39, 0, 44, 15)):
            tr.append((g.distance(oc.exterior), t.GetNetname()))
    tr.sort()
    check('nearest track to the new edge (I2C clock)', 0.38, tr[0][0], 0.005)
    check('nearest data track to the new edge', 0.75, [d for d, n in tr if n == 'I2C_SDA'][0], 0.005)
    pd = []
    for fp in c.GetFootprints():
        for p in fp.Pads():
            sps = pcbnew.SHAPE_POLY_SET()
            p.TransformShapeToPolygon(sps, pcbnew.F_Cu, 0, pcbnew.FromMM(0.002), pcbnew.ERROR_INSIDE)
            g = F.sps_to_geom(sps)
            if not g.is_empty and g.intersects(box(39, 0, 44, 15)):
                pd.append((g.distance(oc.exterior), fp.GetReference()))
    pd.sort()
    check('nearest pads to the new edge (R105)', 0.66, pd[0][0], 0.005)
    # --- track totals
    la = sum(TO(t.GetLength()) for t in a.GetTracks() if t.Type() != pcbnew.PCB_VIA_T)
    lc = sum(TO(t.GetLength()) for t in c.GetTracks() if t.Type() != pcbnew.PCB_VIA_T)
    check('track length rev 3.1 / rev 3.2 (mm)', (2126.1, 2122.6), (la, lc), 0.05)
    print('\n%s' % ('ALL AGREE' if not bad else '%d DIFFERENT' % bad))


def _outline(b):
    sps = pcbnew.SHAPE_POLY_SET()
    b.GetBoardPolygonOutlines(sps)
    return sps


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
