"""Find round holes standing along the print height (insert holes, pilots) in a part's layers: centre (u, v), diameter, h range."""
import sys, numpy as np
from fdm_lib import *
def holes(name, dmin=1.4, dmax=4.3):
    p = Part(name); L = p.slice(); found = {}
    for h, g in L:
        for q in polys_of(g):
            for r in q.interiors:
                ring = Polygon(r); A = ring.area; d = 2 * math.sqrt(A / math.pi)
                if dmin <= d <= dmax and ring.length ** 2 / (4 * math.pi * A) < 1.08:
                    c = ring.centroid; key = (round(c.x), round(c.y))
                    found.setdefault(key, []).append((h, d, c.x, c.y))
    out = []
    for key, v in found.items():
        v = np.array(v)
        if len(v) < 8: continue
        w = p.uvh_to_world([[v[:, 2].mean(), v[:, 3].mean(), v[:, 0].mean()]])[0]
        out.append((name, round(v[:, 2].mean(), 2), round(v[:, 3].mean(), 2), round(float(np.median(v[:, 1])), 2), round(v[:, 0].min() - p.lh / 2, 1), round(v[:, 0].max() + p.lh / 2, 1), [round(float(x), 1) for x in w]))
    return out
if __name__ == '__main__':
    for n in sys.argv[1:]:
        for o in holes(n):
            print('%s hole at u %.2f v %.2f  d %.2f  h %.1f-%.1f  world mid %s' % o)
