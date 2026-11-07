"""Plot the extrusion paths of chosen layers in a world box from PrusaSlicer G-codes (object centred at 128, 128).
Usage: layer_view.py out.png cx cy x0 x1 y0 y1 z1,z2,... file1.gcode[:label] file2.gcode[:label] ..."""
import sys, re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
out = sys.argv[1]; cx, cy = float(sys.argv[2]), float(sys.argv[3]); x0, x1, y0, y1 = map(float, sys.argv[4:8])
ZS = [float(z) for z in sys.argv[8].split(',')]; FILES = sys.argv[9:]
COL = {'Support material': '#d62728', 'Support material interface': '#ff7f0e', 'Bridge infill': '#1f77b4',
       'Overhang perimeter': '#9467bd', 'External perimeter': '#333333', 'Perimeter': '#777777'}
fig, axs = plt.subplots(len(ZS), len(FILES), figsize=(6 * len(FILES), 5.4 * len(ZS)), squeeze=False)
for j, fl in enumerate(FILES):
    f, lab = (fl.split(':') + [fl])[:2]
    segs = {z: [] for z in ZS}; X = Y = Z = 0.0; ty = None; E = 0.0
    for line in open(f):
        if line.startswith(';TYPE:'): ty = line[6:].strip(); continue
        if line.startswith(';Z:'): Z = float(line[3:]); continue
        if not line.startswith('G1'): continue
        d = dict((k, float(v)) for k, v in re.findall(r'([XYE])([-\d.]+)', line))
        nX, nY = d.get('X', X), d.get('Y', Y)
        if d.get('E', 0) > 0 and ('X' in d or 'Y' in d):
            for z in ZS:
                if abs(Z - z) < 1e-3:
                    a = (X - 128 + cx, Y - 128 + cy); b = (nX - 128 + cx, nY - 128 + cy)
                    if x0 - 2 <= a[0] <= x1 + 2 and y0 - 2 <= a[1] <= y1 + 2:
                        segs[z].append((a, b, ty))
        X, Y = nX, nY
    for i, z in enumerate(ZS):
        ax = axs[i][j]; seen = set()
        for a, b, t in segs[z]:
            c = COL.get(t, '#bbbbbb'); ax.plot([a[0], b[0]], [a[1], b[1]], color=c, lw=1.0 if t in COL else 0.6,
                                               label=t if t not in seen else None); seen.add(t)
        ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect('equal'); ax.grid(True, lw=0.3)
        ax.set_title('%s  layer z %.2f' % (lab, z), fontsize=10); ax.legend(fontsize=6, loc='lower left')
fig.tight_layout(); fig.savefig(out, dpi=90); print('ok')
