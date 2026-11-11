import os
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')) + os.sep
import pcb, rnet, numpy as np
from matplotlib.path import Path
P = ROOT
NV = '/5 V supply and outputs/VBUS_PI'
VB = [('pin', 'J2.A4'), ('pin', 'J2.B9'), ('pin', 'J2.A9'), ('pin', 'J2.B4')]
b = pcb.load(P + 'rev3/main-board-rev3.kicad_pcb')
POLY = [(56.9, 39.0), (60.0, 39.0), (60.0, 45.0), (61.6, 46.7), (68.0, 46.7), (68.0, 48.7), (59.3, 48.7), (56.9, 45.6)]
def extra(n):
    m = Path(np.array(POLY)).contains_points(np.column_stack([n.X.ravel(), n.Y.ravel()])).reshape(n.X.shape)
    for x in (63.0, 67.25):
        m |= (np.abs(n.X - x) <= 0.35) & (n.Y >= 48.6) & (n.Y <= 50.64)          # 0.7 wide into both pins of the pair
    for q in n.barrels:
        m &= ~(np.hypot(n.X - q['x'], n.Y - q['y']) < q['drill'] / 2)
    n.mask['B.Cu'] |= m
# clearance check of the planned area against other back-layer copper (0.2 wanted)
import math
poly = Path(np.array(POLY))
worst = []
def d_poly(px, py):
    best = 1e9
    for (ax, ay), (bx, by) in zip(POLY, POLY[1:] + POLY[:1]):
        dx, dy = bx - ax, by - ay; t = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
        best = min(best, math.hypot(px - ax - t * dx, py - ay - t * dy))
    return -best if poly.contains_point((px, py)) else best
for v in b['vias']:
    if v['net'] != NV:
        d = d_poly(v['x'], v['y']) - v['size'] / 2
        if d < 0.6: worst.append(('via ' + v['net'].split('/')[-1], round(v['x'], 2), round(v['y'], 2), round(d, 2)))
for sg in b['segs']:
    if sg['layer'] == 'B.Cu' and sg['net'] != NV:
        for t in np.linspace(0, 1, 60):
            d = d_poly(sg['x1'] + t * (sg['x2'] - sg['x1']), sg['y1'] + t * (sg['y2'] - sg['y1'])) - sg['w'] / 2
            if d < 0.6: worst.append(('track ' + sg['net'].split('/')[-1], round(d, 2))); break
for r, f in b['fps'].items():
    for p in f['pads']:
        if p['net'] != NV and p['n'] and ('*.Cu' in p['layers'] or 'B.Cu' in p['layers']):
            d = min(d_poly(p['x'] + sx * p['sx'] / 2, p['y'] + sy * p['sy'] / 2) for sx in (-1, 0, 1) for sy in (-1, 0, 1))
            if d < 0.6: worst.append(('pad %s.%s %s' % (r, p['n'], (p['net'] or '').split('/')[-1]), round(d, 2)))
print('other back-layer copper within 0.6 of the planned area:', worst)
for label, ex in (('as routed', None), ('planned area', extra)):
    n = rnet.Net(b, [NV], (49, 35, 73, 52), 0.05)
    Re, pins = n.solve([('pin', 'LK1.2')], VB, mode='equal', extra_copper=ex)
    n2 = rnet.Net(b, [NV], (49, 35, 73, 52), 0.05)
    Rq = n2.solve([('pin', 'LK1.2')], VB, mode='equipotential', extra_copper=ex)[0]
    print('%-13s equal pin currents %.2f mohm  pins %s | equipotential %.2f' % (label, Re * 1e3, ['%.2f' % (x * 1e3) for x in pins], Rq * 1e3))
