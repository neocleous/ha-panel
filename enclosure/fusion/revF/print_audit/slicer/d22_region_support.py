"""Support extruded in boxes (world x_rel / y / z), from a PrusaSlicer G-code of an object centred at (128, 128).
Usage: region_support.py file.gcode cx cy  -> JSON {box: {type: mm3}}; cx, cy = world centre of the object's XY box."""
import sys, re, json, math
AREA = math.pi * 0.875 ** 2
f, cx, cy = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
BOX = {'SR_pad': (-50.0, -30.0, -47.0, -24.0, 150.0, 172.7), 'SL_pad': (30.0, 50.0, -47.0, -24.0, 150.0, 172.7),
       'SR_pad_z162up': (-50.0, -32.5, -47.0, -24.0, 162.0, 172.7), 'SL_pad_z162up': (32.5, 50.0, -47.0, -24.0, 162.0, 172.7),
       'SR_column_z28_160': (-50.0, -32.5, -47.0, -24.0, 28.0, 160.0), 'SL_column_z28_160': (32.5, 50.0, -47.0, -24.0, 28.0, 160.0),
       'SR_seat': (-47.0, -39.5, -36.5, -29.0, 168.8, 169.55), 'SL_seat': (39.5, 47.0, -36.5, -29.0, 168.8, 169.55),
       'SR_frontgap': (-48.0, -37.6, -29.0, -17.0, 140.0, 170.0), 'SL_frontgap': (37.6, 48.0, -29.0, -17.0, 140.0, 170.0)}
res = {k: {} for k in BOX}; tot = {}
X = Y = Z = E = 0.0; rel = False; ty = None
for line in open(f):
    if line.startswith(';TYPE:'):
        ty = line[6:].strip(); continue
    if line.startswith('M83'): rel = True; continue
    if line.startswith('M82'): rel = False; continue
    if line.startswith('G92'):
        m = re.search(r'E([-\d.]+)', line)
        if m: E = float(m.group(1))
        continue
    if not (line.startswith('G1') or line.startswith('G0')): continue
    d = dict((k, float(v)) for k, v in re.findall(r'([XYZE])([-\d.]+)', line))
    nX, nY = d.get('X', X), d.get('Y', Y)
    if 'Z' in d: Z = d['Z']
    if 'E' in d:
        de = d['E'] if rel else d['E'] - E
        if not rel: E = d['E']
        if de > 0 and ('X' in d or 'Y' in d) and ty and 'upport' in ty:
            mx, my = (X + nX) / 2 - 128 + cx, (Y + nY) / 2 - 128 + cy
            v = de * AREA; tot[ty] = tot.get(ty, 0) + v
            for k, (x0, x1, y0, y1, z0, z1) in BOX.items():
                if x0 <= mx <= x1 and y0 <= my <= y1 and z0 <= Z <= z1:
                    res[k][ty] = res[k].get(ty, 0) + v
    X, Y = nX, nY
out = {k: {t: round(v, 1) for t, v in r.items()} for k, r in res.items()}
out['total_support_mm3'] = {t: round(v, 1) for t, v in tot.items()}
print(json.dumps(out))
