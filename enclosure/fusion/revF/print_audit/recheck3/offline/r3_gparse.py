# recheck3: parse a Bambu Studio G-code into extrusion segments in bed mm (recheck2's r2_gparse.py, plus the object each line belongs to).
#   Usage: python3 r3_gparse.py <out dir of a job> [...]   -> <job>/seg.npz and <job>/gsum.json
#   npz: seg float32 [N, 10] = x0, y0, x1, y1, z (layer top), e (mm of 1.75 filament), w (line width), layer index, tool, object (index into objs, -1 none);
#        feat uint8 [N] (index into names); names; layers (z of each layer); objs (object names, in label order); header.
#   gsum.json: time, filament, volume by feature and by object (part = every feature but support, brim, skirt, prime tower).
#   Only extruding moves with X or Y (E > 0) are kept. Masses: Bambu ABS 1.04 g/cm3 (the preset).
import sys, re, json, math, os
import numpy as np
RX = re.compile(r'([XYZEF])([-+]?\d*\.?\d+)')
A = math.pi * 0.875 ** 2

def parse(path):
    feats = []; fidx = {}; seg = []; ftag = []
    x = y = 0.0; z = 0.0; zl = 0.0; w = 0.42; f = None; li = -1; layers = []; hdr = {}; tool = 0; obj = -1; labels = []
    with open(path, 'r', errors='replace') as fh:
        for line in fh:
            c = line[0]
            if c == ';':
                if line.startswith('; FEATURE:'):
                    nm = line[10:].strip()
                    if nm not in fidx:
                        fidx[nm] = len(feats); feats.append(nm)
                    f = fidx[nm]
                elif line.startswith('; LINE_WIDTH:'):
                    w = float(line[13:])
                elif line.startswith('; Z_HEIGHT:'):
                    zl = float(line[11:]); li += 1; layers.append(zl)
                elif line.startswith('; start printing object, unique label id:'):
                    lab = int(line.split(':')[1])
                    if lab not in labels: labels.append(lab)
                    obj = lab
                elif line.startswith('; stop printing object'):
                    obj = -1
                elif line.startswith('; model printing time:'):
                    hdr['time'] = line.strip()[2:]
                elif line.startswith('; total filament weight [g]'):
                    hdr['g'] = float(line.split(':')[1])
                elif line.startswith('; total layer number:'):
                    hdr['n_layers'] = int(line.split(':')[1])
                elif line.startswith('; model label id:'):
                    hdr['labels'] = [int(v) for v in line.split(':')[1].split(',')]
                elif line.startswith('; EXECUTABLE_BLOCK_END'):
                    break
                continue
            if c == 'T' and line[1:].strip().isdigit() and int(line[1:].strip()) < 16:
                tool = int(line[1:].strip()); continue
            if c != 'G' or not (line.startswith('G1 ') or line.startswith('G0 ')):
                continue
            k = line.find(';'); body = line if k < 0 else line[:k]
            nx, ny, e = x, y, None
            for a, v in RX.findall(body):
                if a == 'X': nx = float(v)
                elif a == 'Y': ny = float(v)
                elif a == 'Z': z = float(v)
                elif a == 'E': e = float(v)
            if e is not None and e > 0 and (nx != x or ny != y) and li >= 0 and f is not None:
                seg.append((x, y, nx, ny, zl, e, w, li, tool, obj)); ftag.append(f)
            x, y = nx, ny
    S = np.array(seg, np.float32); F = np.array(ftag, np.uint8)
    order = hdr.get('labels') or labels
    if len(S):
        lab = S[:, 9].astype(int); idx = np.full(len(S), -1, np.int32)
        for i, l in enumerate(order): idx[lab == l] = i
        S[:, 9] = idx
    return S, F, feats, np.array(layers, np.float32), hdr, order

def cls_of(n):
    return 'support' if 'Support' in n else ('brim' if n in ('Brim', 'Skirt') else ('tower' if 'tower' in n.lower() else ('custom' if n in ('Custom',) else 'part')))

for d in sys.argv[1:]:
    job = os.path.basename(d.rstrip('/'))
    S, F, names, L, hdr, order = parse(os.path.join(d, 'plate_1.gcode'))
    res = json.load(open(os.path.join(d, 'result.json'))); pl = res['sliced_plates'][0]
    objs = [o['name'] for o in pl.get('objects', [])]
    objs = [o for o in objs if 'blk' not in o] if len(objs) != len(order) else objs
    np.savez_compressed(os.path.join(d, 'seg.npz'), seg=S, feat=F, names=np.array(names), layers=L, objs=np.array(objs), header=json.dumps(hdr))
    out = {'job': job, 'print_min': round(pl['main_predication'] / 60, 1), 'with_prep_min': round(pl['total_predication'] / 60, 1), 'g': [round(f['total_used_g'], 2) for f in pl['filaments']],
           'warning': pl.get('warning_message', ''), 'layers': hdr.get('n_layers'), 'n_seg': int(len(S)), 'feature_s': {k: round(v, 1) for k, v in pl.get('feature_type_times', {}).items()}, 'objects': {}}
    tot = {}
    for oi in [-1] + list(range(len(order))):
        m = S[:, 9] == oi if len(S) else np.zeros(0, bool)
        if not m.any(): continue
        fv = {}; cv = {}
        for i, n in enumerate(names):
            v = float(S[m & (F == i), 5].sum() * A)
            if v > 0:
                fv[n] = round(v, 1); cv[cls_of(n)] = cv.get(cls_of(n), 0.0) + v; tot[cls_of(n)] = tot.get(cls_of(n), 0.0) + v
        nm = objs[oi] if 0 <= oi < len(objs) else ('(no object)' if oi < 0 else 'obj%d' % oi)
        s = S[m]
        out['objects'][nm] = {'feat_mm3': fv, 'cls_mm3': {k: round(v, 1) for k, v in cv.items()}, 'part_g': round(cv.get('part', 0.0) * 1.04 / 1000, 2), 'support_g': round(cv.get('support', 0.0) * 1.04 / 1000, 2),
                              'bbox': [round(float(min(s[:, 0].min(), s[:, 2].min())), 1), round(float(min(s[:, 1].min(), s[:, 3].min())), 1), round(float(max(s[:, 0].max(), s[:, 2].max())), 1), round(float(max(s[:, 1].max(), s[:, 3].max())), 1)]}
    out['cls_mm3'] = {k: round(v, 1) for k, v in tot.items()}
    json.dump(out, open(os.path.join(d, 'gsum.json'), 'w'), indent=1)
    print(job, out['print_min'], out['with_prep_min'], out['g'], {k: (v['part_g'], v['support_g']) for k, v in out['objects'].items()}, out['cls_mm3'])
