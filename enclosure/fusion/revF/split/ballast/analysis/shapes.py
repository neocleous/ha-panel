import sys, json
sys.path.insert(0, '/home/claude/bal')
import geo
import shapely
from shapely.geometry import box, Point, Polygon
from shapely.ops import unary_union
S = geo.secs()
REAR = box(-100, -90, 100, -50)
# --- rear plate behind the Pi: 10 thick, top at z 12.5, 0.5 clear above and round
free = geo.free_col(2.5, 13.0, clear=0.0).intersection(REAR)
door_boss = [(50.0, -67.0), (-50.0, -67.0), (19.0, -74.5), (-19.0, -77.0)]
shadow = unary_union([box(x - 4.6, -90, x + 4.6, y) for x, y in door_boss])   # what each boss sweeps as the door comes on from behind
shape = free.difference(shadow).buffer(-0.5).buffer(-2.0).buffer(2.0)
parts = [p for p in (shape.geoms if hasattr(shape, 'geoms') else [shape]) if p.area > 60 and p.centroid.x > 9]
rear = max(parts, key=lambda p: p.area).simplify(0.15)
print('rear plate: area %.0f mm2, %.1f g at 10 thick, centroid (%.1f, %.1f), bounds %s' % (rear.area, rear.area * 10 * 7.85 / 1000, rear.centroid.x, rear.centroid.y, [round(v, 1) for v in rear.bounds]))
print('   other rear parts left out:', [(round(p.area), round(p.centroid.x, 1), round(p.centroid.y, 1)) for p in parts if p is not max(parts, key=lambda q: q.area)])
# --- sheets under the boxes, 2.5 thick in floor pockets
pads = S[3.2]['FLOOR_PLATE']
feet = unary_union([Point(x, y).buffer(6.5 + 2.0) for x, y in ((80, -5.5), (-80, -5.5), (30, -70.6), (-30, -70.6))])
cbore = unary_union([Point(x, y).buffer(3.25 + 1.0) for x, y in ((51, -14), (64, -45), (-51, -14), (-72, -38))])
channel = box(-64.0, -84.0, -44.0, -24.0)
antenna = box(-42.4, -10.0, -30.0, -2.0)            # the Pi's corner by the GPIO header's far end (Pi docs: top-left corner by the 40-pin header)
keep_ant = antenna.buffer(20.0)
out = {'rear': rear}
for side, n in (('left', 'SPKBOX_L'), ('right', 'SPKBOX_R')):
    under = S[4.0][n]
    sh = under.difference(pads.buffer(1.0)).difference(feet).difference(cbore).difference(channel).difference(keep_ant)
    sh = sh.buffer(-0.3).buffer(-2.0).buffer(2.0)
    ps = [p for p in (sh.geoms if hasattr(sh, 'geoms') else [sh]) if p.area > 60]
    p = max(ps, key=lambda q: q.area).simplify(0.15)
    out[side] = p
    print('%s sheet: area %.0f mm2, %.1f g at 2.5 thick, centroid (%.1f, %.1f), bounds %s, parts %s' % (side, p.area, p.area * 2.5 * 7.85 / 1000, p.centroid.x, p.centroid.y, [round(v, 1) for v in p.bounds], [round(q.area) for q in ps]))
    print('   nearest to the antenna corner: %.1f' % p.distance(antenna))
json.dump({k: shapely.to_geojson(v) for k, v in out.items()}, open('/home/claude/bal/cand.json', 'w'))
