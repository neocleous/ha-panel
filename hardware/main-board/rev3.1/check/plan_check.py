import os
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')) + os.sep
import pcb, math
b = pcb.load(ROOT + 'rev3/main-board-rev3.kicad_pcb')
U0, V0 = 43.5, 28.95
def uvbox(f):
    c = f['crt']; return [c[0] - U0, V0 - c[3], c[2] - U0, V0 - c[1]]
box = {r: uvbox(f) for r, f in b['fps'].items() if f['crt']}
def shift(r, du, dv): c = box[r]; box[r] = [c[0] + du, c[1] + dv, c[2] + du, c[3] + dv]
def place(r, cu, cv, w, h): box[r] = [cu - w / 2, cv - h / 2, cu + w / 2, cv + h / 2]
orig = {r: list(c) for r, c in box.items()}
# --- plan ---
HOLE = (19.5, 25.0); del box['H2']
place('R26', 15.0, 22.9, 1.46, 2.96); place('R27', 15.0, 26.2, 1.46, 2.96)
shift('J10', 4.0, 0.0)
w = orig['F3'][3] - orig['F3'][1]; l = orig['F3'][2] - orig['F3'][0]
place('F3', -34.24, -16.80, w, l)
cw = orig['C10'][2] - orig['C10'][0]; cl = orig['C10'][3] - orig['C10'][1]
place('C10', -34.24, -11.90, cl, cw); place('TP12', -34.24, -9.40, 2.5, 2.5)
shift('F4', 1.2, 0.0); shift('C11', 0.4, 0.0)
shift('J11', 0.0, -1.0); shift('TP3', 0.0, -0.5)
moved = ['R26', 'R27', 'J10', 'F3', 'C10', 'TP12', 'F4', 'C11', 'J11', 'TP3']
for r in moved:
    c, o = box[r], orig[r]; print('%-5s crt u %+7.2f..%+7.2f v %+7.2f..%+7.2f   (was u %+7.2f..%+7.2f v %+7.2f..%+7.2f)' % (r, c[0], c[2], c[1], c[3], o[0], o[2], o[1], o[3]))
def gap(a, c):
    du = max(a[0] - c[2], c[0] - a[2]); dv = max(a[1] - c[3], c[1] - a[3])
    if du < 0 and dv < 0: return max(du, dv)                      # overlap (negative)
    return math.hypot(max(du, 0), max(dv, 0))
holes = {'H1': (-37.0, 22.0), 'H2': HOLE, 'H3': (-31.0, -25.25), 'H4': (31.0, -25.25)}
print('nearest neighbour of each moved part (courtyard to courtyard; negative = overlap):')
for r in moved:
    ds = sorted((gap(box[r], c), o) for o, c in box.items() if o != r and not o.startswith('H'))[:3]
    hd = []
    for h, (hu, hv) in holes.items():
        c = box[r]; d = math.hypot(max(c[0] - hu, 0, hu - c[2]), max(c[1] - hv, 0, hv - c[3])) + (0.55 if r.startswith('TP') else 0)
        hd.append((round(d - 3.5, 2), h))
    print('  %-5s' % r, [(round(d, 2), o) for d, o in ds], '| to the nearest dia 7 hole zone:', min(hd))
print('all parts against the new hole zone (dia 7), inside:', [r for r, c in box.items() if not r.startswith('H') and math.hypot(max(c[0] - HOLE[0], 0, HOLE[0] - c[2]), max(c[1] - HOLE[1], 0, HOLE[1] - c[3])) + (0.55 if r.startswith('TP') else 0) < 3.5])
print('edge: any moved part outside the outline:', [r for r in moved if box[r][0] < -43.5 or box[r][2] > 43.5 or box[r][3] > 28.95 or box[r][1] < -28.95])
# copper now lying where the moved header pins will stand (pad 1.7 across + 0.2), all layers
def near(pts, rad, skipref):
    out = set()
    for (u, v) in pts:
        x, y = u + U0, V0 - v
        for sg in b['segs']:
            dx, dy = sg['x2'] - sg['x1'], sg['y2'] - sg['y1']; L2 = dx * dx + dy * dy
            t = 0 if L2 == 0 else max(0, min(1, ((x - sg['x1']) * dx + (y - sg['y1']) * dy) / L2))
            if math.hypot(x - sg['x1'] - t * dx, y - sg['y1'] - t * dy) - sg['w'] / 2 < rad: out.add((sg['layer'][0] + ' track', sg['net'].split('/')[-1]))
        for vv in b['vias']:
            if math.hypot(vv['x'] - x, vv['y'] - y) - vv['size'] / 2 < rad: out.add(('via', vv['net'].split('/')[-1]))
        for r, f in b['fps'].items():
            if r == skipref: continue
            for p in f['pads']:
                if p['n'] and math.hypot(max(abs(p['x'] - x) - p['sx'] / 2, 0), max(abs(p['y'] - y) - p['sy'] / 2, 0)) < rad: out.add(('pad', r + '.' + p['n']))
    return sorted(out)
print('at the new BME680 pins:', near([(-30.30, v) for v in (-10.30, -12.84, -15.38, -17.92)], 0.85 + 0.2, 'J10'))
print('at the new VEML6030 pins:', near([(u, -13.0) for u in (-4.50, -1.96, 0.58, 3.12)], 0.85 + 0.2, 'J11'))
# inner-layer areas at the new header pins and hole
for z in b['zones']:
    if z['keepout']: continue
    xs = [p[0] for p in z['outline']]; ys = [p[1] for p in z['outline']]
    print('area', z['net'].split('/')[-1], z['layers'][0], 'u %+.1f..%+.1f v %+.1f..%+.1f' % (min(xs) - U0, max(xs) - U0, V0 - max(ys), V0 - min(ys)))
