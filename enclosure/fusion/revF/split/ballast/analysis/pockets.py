import sys
sys.path.insert(0, '/home/claude/bal')
import geo
from shapely.geometry import box
REAR = box(-100, -90, 100, -50)
WALL, GAP, LID = 1.2, 0.5, 2.0
def regions(ztop, floor_z=2.5):
    free = geo.free_col(2.5, ztop, clear=0.0).intersection(REAR)
    cav = free.buffer(-(GAP + WALL)).buffer(-1.5).buffer(1.5)   # cavities, no slivers under 3 wide
    parts = [p for p in (cav.geoms if hasattr(cav, 'geoms') else [cav]) if p.area > 40]
    h = ztop - LID - floor_z
    return [(p, p.area * h) for p in parts], h
def tag(p):
    x = p.centroid.x
    return 'D' if x < -60 else 'B' if x < -10 else 'M' if x < 9 else 'A'
best = {}
for ztop in (8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 24, 26):
    parts, h = regions(ztop)
    line = []
    agg = {}
    for p, v in parts:
        t = tag(p); a = agg.setdefault(t, [0, 0, 0, 0]); a[0] += p.area; a[1] += v; a[2] += v * p.centroid.y; a[3] += v * p.centroid.x
    for t, (A, V, Vy, Vx) in sorted(agg.items()):
        line.append('%s %4.0f mm2 %5.1f cm3' % (t, A, V / 1000))
        if V > best.get(t, (0,))[0]:
            best[t] = (V, ztop, A, Vy / V, Vx / V)
    print('lid top z %4.1f (fill %4.1f high): %s' % (ztop, h, ' | '.join(line)))
print('best per region (volume cm3, lid top z, area, centroid y, x):')
tot = 0
for t, (V, z, A, y, x) in sorted(best.items()):
    tot += V
    print('  %s %5.2f cm3 at lid top z %g, cavity area %.0f mm2, centroid (%.1f, %.1f)' % (t, V / 1000, z, A, x, y))
print('total %.2f cm3' % (tot / 1000))
