# HA panel print audit (P11): parse a PrusaSlicer G-code: extrusion by ;TYPE (mm3, g ASA 1.05), layers, support z range,
#   print time and filament from the footer. Usage: python3 pa_gcode.py file.gcode [more ...]
import sys, re, json, math
AREA = math.pi * 0.875 ** 2


def parse(path):
    ty = None; z = 0.0; E = 0.0; rel = False
    vol = {}; sup_layers = set(); layers = 0; lastz = None
    seg = {}
    foot = {}
    with open(path) as f:
        for line in f:
            if line.startswith(';TYPE:'):
                ty = line[6:].strip(); continue
            if line.startswith(';Z:'):
                z = float(line[3:]); continue
            if line.startswith(';LAYER_CHANGE'):
                layers += 1; continue
            if line.startswith('; estimated printing time (normal mode)'):
                foot['time'] = line.split('=')[1].strip(); continue
            if line.startswith('; filament used [g]'):
                foot['g'] = float(line.split('=')[1]); continue
            if line.startswith('; filament used [cm3]'):
                foot['cm3'] = float(line.split('=')[1]); continue
            if line.startswith('M83'):
                rel = True; continue
            if line.startswith('M82'):
                rel = False; continue
            if line.startswith('G92'):
                m = re.search(r'E([-\d.]+)', line)
                if m:
                    E = float(m.group(1))
                continue
            if line.startswith('G1') or line.startswith('G0'):
                m = re.search(r'E([-\d.]+)', line)
                if not m:
                    continue
                e = float(m.group(1))
                de = e if rel else e - E
                if not rel:
                    E = e
                if de > 0 and ty and (' X' in line or ' Y' in line):
                    vol[ty] = vol.get(ty, 0.0) + de * AREA
                    if ty.startswith('Support'):
                        sup_layers.add(round(z, 2))
    sv = vol.get('Support material', 0) + vol.get('Support material interface', 0)
    out = {'file': path.split('/')[-1], 'layers': layers, 'time': foot.get('time'), 'g': foot.get('g'),
           'vol_mm3': {k: round(v, 1) for k, v in sorted(vol.items(), key=lambda kv: -kv[1])},
           'support_mm3': round(sv, 1), 'support_g_asa': round(sv * 1.05e-3, 2),
           'support_z': [min(sup_layers), max(sup_layers)] if sup_layers else None, 'support_layers': len(sup_layers)}
    return out


if __name__ == '__main__':
    res = [parse(p) for p in sys.argv[1:]]
    for r in res:
        print(json.dumps(r))
