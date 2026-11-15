import sys
sys.path.insert(0, '/home/claude/bal')
import geo
from shapely.geometry import box, Point
from shapely.ops import unary_union
REAR = box(-100, -90, 100, -50)
def tag(p):
    x = p.centroid.x
    return 'D' if x < -60 else 'B' if x < -10 else 'M' if x < 9 else 'A'
res = {}
for t in (3, 4, 5, 6, 8, 10, 12):
    free = geo.free_col(2.5, 2.5 + t + 0.5, clear=0.0).intersection(REAR)
    shape = free.buffer(-0.5).buffer(-2.0).buffer(2.0)        # 0.5 clear all round, no part under 4 wide
    parts = [p for p in (shape.geoms if hasattr(shape, 'geoms') else [shape]) if p.area > 60]
    agg = {}
    for p in parts:
        a = agg.setdefault(tag(p), [0.0, 0.0, 0.0, []]); a[0] += p.area; a[1] += p.area * p.centroid.y; a[2] += p.area * p.centroid.x; a[3].append(p)
    out = []
    for k, (A, Ay, Ax, ps) in sorted(agg.items()):
        out.append('%s %4.0f mm2 %5.1f g (y %.1f)' % (k, A, A * t * 7.85 / 1000, Ay / A))
        res[(t, k)] = (A, Ax / A, Ay / A)
    print('steel %2d thick: %s' % (t, ' | '.join(out)))
