import sys, json, math
sys.path.insert(0, '/home/claude/bal')
import shapely
from shapely.geometry import box
from shapely import affinity
C = {k: shapely.from_geojson(v) for k, v in json.load(open('/home/claude/bal/cand.json')).items()}
def best_rect(poly, widths, step=0.5):
    best = None
    c = poly.centroid
    for ang in range(0, 180, 5):
        P = affinity.rotate(poly, -ang, origin=c)
        x0, y0, x1, y1 = P.bounds
        for w in widths:
            y = y0
            while y + w <= y1:
                # longest run of x along this band that stays inside
                band = box(x0 - 1, y, x1 + 1, y + w)
                inside = P.intersection(band)
                # scan x for the longest box fully inside
                xs = x0
                while xs < x1:
                    L = 0.0; lo = 0.0; hi = x1 - xs
                    # binary search the longest length from xs
                    if P.contains(box(xs, y, xs + 1.0, y + w)):
                        lo = 1.0
                        while hi - lo > 0.25:
                            mid = (lo + hi) / 2
                            if P.contains(box(xs, y, xs + mid, y + w)): lo = mid
                            else: hi = mid
                        if best is None or lo * w > best[0]:
                            best = (lo * w, w, lo, ang)
                    xs += step * 2
                y += step
    return best
for k, t, widths in (('rear', 10, (10, 12, 15, 20, 25, 30)), ('left', 2, (20, 25, 30, 40, 50)), ('right', 2, (20, 25, 30, 40, 50))):
    b = best_rect(C[k], widths)
    if b:
        print('%s: best stock piece %g wide x %.1f long (cut to %d), %g thick, at %d deg: %.1f g' % (k, b[1], b[2], int(b[2]), t, b[3], b[1] * int(b[2]) * t * 7.85 / 1000))
