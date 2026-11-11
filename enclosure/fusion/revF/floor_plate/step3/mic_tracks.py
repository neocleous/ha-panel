import re, json, math, sys
from frames import *
s = open('/home/claude/ha-panel/hardware/main-board/main-board.kicad_pcb').read()
X0, Y0 = 43.501, 28.95
segs = []
for m in re.finditer(r'\(segment\s+\(start ([-\d.]+) ([-\d.]+)\)\s+\(end ([-\d.]+) ([-\d.]+)\)\s+\(width ([\d.]+)\)\s+(?:\(locked yes\)\s+)?\(layer "([^"]+)"\)\s+\(net (\d+)\)', s):
    x1, y1, x2, y2, w, layer, net = m.groups()
    segs.append((float(x1) - X0, Y0 - float(y1), float(x2) - X0, Y0 - float(y2), float(w), layer, net))
print(len(segs), 'segments; layers', sorted(set(q[5] for q in segs)))
spk = [q for q in segs if q[6] in ('63', '64')]
print('right speaker segments', len(spk), 'by layer', {l: sum(1 for q in spk if q[5] == l) for l in set(q[5] for q in spk)})
back = [q for q in spk if q[5] == 'B.Cu']
L = sum(math.hypot(q[2] - q[0], q[3] - q[1]) for q in back)
print('on the back: n', len(back), 'length', round(L, 1), 'u', round(min(min(q[0], q[2]) for q in back), 1), round(max(max(q[0], q[2]) for q in back), 1),
      'v', round(min(min(q[1], q[3]) for q in back), 1), round(max(max(q[1], q[3]) for q in back), 1), 'widths', sorted(set(q[4] for q in back)))
R = json.load(open('h3_routes.json'))
MICL = [1.0, [['S', 39.0, 20.0, -30.7], ['S', 39.0, 19.6, -10.5], ['S', 37.0, 21.5, 2.5], ['S', 21.0, 21.7, 27.8], ['W', 21, -26, 172]]]
def closest(p, a, b):
    d = [b[k] - a[k] for k in range(3)]; dd = sum(x * x for x in d)
    t = 0 if dd == 0 else max(0, min(1, sum((p[k] - a[k]) * d[k] for k in range(3)) / dd))
    return [a[k] + d[k] * t for k in range(3)]
for name, (r, nodes) in (('MIC_R (right, new route)', R['LEAD_MIC_R']), ('MIC_L (left, unchanged)', MICL)):
    ps = [w2b(*P(n)) for n in nodes]
    best = (1e9, None, None); near5 = 0.0; near10 = 0.0; nearp = 0.0
    for i in range(len(ps) - 1):
        n = 200
        seglen = math.dist(ps[i], ps[i + 1])
        for j in range(n):
            a = [ps[i][k] + (ps[i + 1][k] - ps[i][k]) * (j + 0.5) / n for k in range(3)]
            dmin = 1e9; dpl = 1e9
            for q in back:
                b = closest(a, (q[0], q[1], -1.6), (q[2], q[3], -1.6))
                d = math.dist(a, b)
                if d < dmin: dmin = d; bb = b
                dp = math.hypot(a[0] - b[0], a[1] - b[1])
                dpl = min(dpl, dp)
            if dmin < best[0]: best = (dmin, a, bb)
            if dmin < 15: near10 += seglen / n
            if dpl < 5: nearp += seglen / n
    d, a, b = best
    print(name, '| centre to track centre %.1f' % d, '| lead surface to track edge %.1f' % (d - r - 0.5), '| lead point u %.1f v %.1f depth %.1f' % (a[0], a[1], 32.7 + a[2]),
          '| track point u %.1f v %.1f' % (b[0], b[1]), '| lead length within 15 mm of the tracks %.0f' % near10, '| lead length within 5 mm in plan %.0f' % nearp)
    print('   lead nodes (u, v, depth):', [(round(p[0], 1), round(p[1], 1), round(32.7 + p[2], 1)) for p in ps])
