# recheck2 (block 2): parse a Bambu Studio G-code into extrusion segments, in bed mm (from the 11-14 gparse.py; adds the tool).
#   Usage: python3 gparse.py <plate_1.gcode> <out.npz>
#   npz: seg float32 [N, 9] = x0, y0, x1, y1, z (layer top), e (mm of 1.75 filament), w (line width), layer index, tool;
#        feat uint8 [N] (index into names); names; layers (z of each layer); header (time, g, layers).
#   Only extruding moves with X or Y (E > 0) are kept; travel, retracts and wipes are dropped. Arc fitting is off in these
#   jobs (enable_arc_fitting = 0); G2/G3 in the files are Z-hop spirals without E.
import sys, re, json, math
import numpy as np

RX = re.compile(r'([XYZEF])([-+]?\d*\.?\d+)')


def parse(path):
    feats = []; fidx = {}
    seg = []; ftag = []
    x = y = 0.0; z = 0.0; zl = 0.0; w = 0.42; f = None; li = -1; layers = []
    rel = True; hdr = {}; tool = 0
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
                elif line.startswith('; model printing time:'):
                    hdr['time'] = line.strip()[2:]
                elif line.startswith('; total filament weight [g]'):
                    hdr['g'] = float(line.split(':')[1])
                elif line.startswith('; total layer number:'):
                    hdr['n_layers'] = int(line.split(':')[1])
                elif line.startswith('; EXECUTABLE_BLOCK_END'):
                    break
                continue
            if c == 'T' and line[1:].strip().isdigit() and int(line[1:].strip()) < 16:
                tool = int(line[1:].strip()); continue
            if c == 'M':
                if line.startswith('M83'):
                    rel = True
                elif line.startswith('M82'):
                    rel = False
                continue
            if c != 'G' or not (line.startswith('G1 ') or line.startswith('G0 ')):
                continue
            k = line.find(';')
            body = line if k < 0 else line[:k]
            nx, ny, e = x, y, None
            for a, v in RX.findall(body):
                if a == 'X':
                    nx = float(v)
                elif a == 'Y':
                    ny = float(v)
                elif a == 'Z':
                    z = float(v)
                elif a == 'E':
                    e = float(v)
            if e is not None and e > 0 and (nx != x or ny != y) and li >= 0 and f is not None:
                seg.append((x, y, nx, ny, zl, e, w, li, tool)); ftag.append(f)
            x, y = nx, ny
    return np.array(seg, np.float32), np.array(ftag, np.uint8), feats, np.array(layers, np.float32), hdr


if __name__ == '__main__':
    S, F, names, L, hdr = parse(sys.argv[1])
    np.savez_compressed(sys.argv[2], seg=S, feat=F, names=np.array(names), layers=L, header=json.dumps(hdr))
    A = math.pi * 0.875 ** 2
    vol = {}
    for i in range(len(names)):
        for t in np.unique(S[F == i, 8]).astype(int) if len(S) else []:
            vol['%s|T%d' % (names[i], t)] = round(float(S[(F == i) & (S[:, 8] == t), 5].sum() * A), 1)
    print(json.dumps({'n_seg': int(len(S)), 'n_layers': int(len(L)), 'hdr': hdr, 'vol_mm3': vol}))
