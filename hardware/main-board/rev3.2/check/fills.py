"""Helpers: the filled pours of a board as shapely geometry in the board frame, and a comparison of two boards' fills.
Used from the block 0 trial and the block 1 check (the pours change only next to the relief)."""
import pcbnew
from shapely.geometry import Polygon
from shapely.ops import unary_union

U0, V0 = 43.5, 28.95
TO = pcbnew.ToMM


def uv(p):
    return (TO(p.x) - U0, V0 - TO(p.y))


def sps_to_geom(sps):
    polys = []
    for i in range(sps.OutlineCount()):
        ol = sps.Outline(i)
        outer = [uv(ol.CPoint(k)) for k in range(ol.PointCount())]
        holes = [[uv(sps.CHole(i, h).CPoint(k)) for k in range(sps.CHole(i, h).PointCount())] for h in range(sps.HoleCount(i))]
        if len(outer) >= 3:
            polys.append(Polygon(outer, holes).buffer(0))
    return unary_union(polys) if polys else Polygon()


def fills(board):
    """{(zone name or net, layer name, priority): geometry} for every copper pour (rule areas left out)."""
    out = {}
    for z in board.Zones():
        if z.GetIsRuleArea():
            continue
        for l in z.GetLayerSet().Seq():
            key = (z.GetZoneName() or z.GetNetname(), board.GetLayerName(l), z.GetAssignedPriority())
            g = sps_to_geom(z.GetFilledPolysList(l))
            out[key] = g if key not in out else out[key].union(g)
    return out


def _drop_slivers(g, tol):
    """Keep only the pieces of a difference larger than tol (mm2): the rest is rounding where a track was replaced by
    one on the same line."""
    parts = list(g.geoms) if hasattr(g, 'geoms') else ([g] if not g.is_empty else [])
    keep = [p for p in parts if p.area > tol]
    return unary_union(keep) if keep else Polygon()


def compare(fa, fb, tol=0.001):
    """Per pour: area in a, area in b, area gained, area lost, and the bounds of what changed (pieces under tol mm2
    left out of the bounds)."""
    rows = []
    for k in sorted(set(fa) | set(fb)):
        a, b = fa.get(k, Polygon()), fb.get(k, Polygon())
        lost, gained = _drop_slivers(a.difference(b), tol), _drop_slivers(b.difference(a), tol)
        ch = lost.union(gained)
        rows.append((k, a.area, b.area, gained.area, lost.area, None if ch.is_empty else tuple(round(x, 2) for x in ch.bounds), lost, gained))
    return rows
