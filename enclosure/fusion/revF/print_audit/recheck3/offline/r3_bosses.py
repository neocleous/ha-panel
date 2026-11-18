"""recheck3: bosses and posts with an insert hole standing along the print height (cap, carrier, base plate, door): the section as sliced against the model,
and the shear between layers under the tightening torque, tau = T r / J (T 0.5 N.m about the hole's axis, all of it in the boss), at several heights."""
import sys, numpy as np
from r3_gq import *
T = 500.0
def rings(bp, zmid, dmin=1.4, dmax=4.4):
    out = []
    for p in polys_of(bp.layer(zmid)):
        for r in p.interiors:
            H = shapely.geometry.Polygon(r); d = 2 * math.sqrt(H.area / math.pi)
            if dmin <= d <= dmax and H.length ** 2 / (4 * math.pi * H.area) < 1.1:
                out.append((H.centroid.x, H.centroid.y, d))
    return out
def boss_table(job, tag, pos, obj, zs, rcap=None, label=''):
    g = G(job); bp = BedPart(tag, pos)
    cs = rings(bp, zs[0][1])
    print('%s (%s): %d holes found at bed z %.2f' % (label or tag, job, len(cs), zs[0][1]))
    for cx, cy, d in cs:
        w = bp.to_world([[cx, cy, zs[0][1]]])[0]
        for name, zb in zs:
            li = g.layer_at(zb); zm = float(g.L[li]) - g.lh_of(li) / 2
            Mo = bp.layer(zm)
            # the boss = the piece of the section that holds the hole, cut to a circle that just contains it (or rcap)
            P0 = shapely.Point(cx, cy)
            piece = [p for p in polys_of(Mo) if any(shapely.geometry.Polygon(ri).buffer(0.05).contains(P0) for ri in p.interiors)]
            if not piece: continue
            pc = min(piece, key=lambda p: p.area); rr = max(P0.distance(shapely.Point(q)) for q in pc.exterior.coords)
            r = min(rr, rcap or 8.0)
            circ = shapely.Point(cx, cy).buffer(r + 0.02, quad_segs=32); win = (cx - r - 0.1, cx + r + 0.1, cy - r - 0.1, cy + r + 0.1)
            mo = gprops(pc.intersection(circ), win, step=0.03, about=(cx, cy)); pr = gprops(foot(g, li, win, obj=obj).intersection(circ), win, step=0.03, about=(cx, cy))
            s = props(g, li, win, obj=obj)
            print('   hole d %.2f at world (%.1f, %.1f, %.1f) %-18s bed z %.2f: model r %.2f A %.1f J %.0f tau %.2f | as sliced A %.0f%% J %.0f%% tau %.2f | %s' % (
                d, w[0], w[1], w[2], name, zb, r, mo['A'], mo['Jo'], T * mo['ro'] / mo['Jo'], 100 * pr['A'] / mo['A'], 100 * pr['Jo'] / mo['Jo'], T * pr['ro'] / pr['Jo'], mixstr(s, 3)))
if __name__ == '__main__':
    boss_table('H6_P4_capthin', 'cap', (0, -28, 0), 0, [('top', 7.3), ('insert mid', 5.0), ('insert end', 3.2), ('flare', 2.7)], label='cap bosses (M3 inserts)')
    boss_table('H2_P2', 'carrier', (-38, 0, 0), 0, [('top', 15.8), ('insert mid', 13.0), ('below the insert', 9.0), ('mid cone', 6.0), ('at the slab', 2.3)], rcap=6.1, label='carrier posts')
