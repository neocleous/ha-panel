import os
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')) + os.sep
import pcb, math, sys
b = pcb.load(ROOT + 'main-board.kicad_pcb')
U0, V0 = 43.5, 28.95
def segdist(px, py, sg):
    x1, y1, x2, y2 = sg['x1'], sg['y1'], sg['x2'], sg['y2']
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / L2))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))
def check(u, v, verbose=True):
    x, y = u + U0, V0 - v
    out = {'F': set(), 'B': set(), 'vias': [], 'crt': [], 'tht': [], 'pads': []}
    for sg in b['segs']:
        d = segdist(x, y, sg) - sg['w'] / 2
        if sg['layer'] == 'F.Cu' and d < 3.5: out['F'].add(sg['net'].split('/')[-1])
        if sg['layer'] == 'B.Cu' and d < 4.1: out['B'].add(sg['net'].split('/')[-1])
    for vv in b['vias']:
        d = math.hypot(vv['x'] - x, vv['y'] - y) - vv['size'] / 2
        if d < 4.1: out['vias'].append((vv['net'].split('/')[-1], round(vv['x'] - U0, 2), round(V0 - vv['y'], 2), round(d, 2)))
    for r, f in b['fps'].items():
        if r.startswith('H') or not f['crt']: continue
        c = f['crt']
        du = max(c[0] - x, 0, x - c[2]); dv = max(c[1] - y, 0, y - c[3]); d = math.hypot(du, dv)
        if f['fp'].endswith('TestPoint_Pad_D1.5mm'): d += 0.55
        if d < 3.5 - 1e-6: out['crt'].append((r, round(d, 2)))
        for p in f['pads']:
            if p['type'] == 'thru_hole':
                d2 = math.hypot(max(abs(p['x'] - x) - p['sx'] / 2, 0), max(abs(p['y'] - y) - p['sy'] / 2, 0))
                if d2 < 4.5: out['tht'].append((r, p['n'], round(d2, 2)))
            elif p['n']:
                d2 = math.hypot(max(abs(p['x'] - x) - p['sx'] / 2, 0), max(abs(p['y'] - y) - p['sy'] / 2, 0))
                if d2 < 3.5: out['pads'].append((r, p['n'], round(d2, 2)))
    return out
if __name__ == '__main__':
    for (u, v) in [(16.1, 25.0), (17.6, 25.0), (19.0, 25.0), (19.5, 25.0), (20.0, 25.0), (20.0, 24.0), (22.0, 25.0), (-2.5, 24.5), (30.0, 25.0)]:
        o = check(u, v)
        print('hole at u %+.1f v %+.1f' % (u, v))
        print('   courtyards inside dia 7:', o['crt'])
        print('   F.Cu nets inside r 3.5:', sorted(o['F']))
        print('   B.Cu nets inside r 4.1:', sorted(o['B']))
        print('   vias with copper inside r 4.1:', o['vias'])
        print('   THT pads inside dia 9:', o['tht'], '| SMD pads inside r 3.5:', o['pads'])
