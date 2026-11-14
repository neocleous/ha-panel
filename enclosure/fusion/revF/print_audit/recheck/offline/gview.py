# recheck: plot G-code extrusion (bed frame) for a layer range inside a world window (front/plate frames: bed = world + pos).
#   Usage: python3 gview.py job.npz out.png "L0,L1" "x0,x1,y0,y1" pos_x,pos_y [title]
import sys, json, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
d = np.load(sys.argv[1]); seg = d['seg']; feat = d['feat']; names = [str(s) for s in d['names']]
L0, L1 = [int(v) for v in sys.argv[3].split(',')]; W = [float(v) for v in sys.argv[4].split(',')]; px, py = [float(v) for v in sys.argv[5].split(',')]
title = sys.argv[6] if len(sys.argv) > 6 else ''
col = {'Outer wall': 'tab:red', 'Inner wall': 'tab:orange', 'Brim': 'tab:purple', 'Support': 'tab:green', 'Support interface': 'lime',
       'Bottom surface': 'tab:blue', 'Overhang wall': 'magenta', 'Bridge': 'cyan', 'Gap infill': 'gold', 'Sparse infill': 'grey',
       'Internal solid infill': 'tab:brown', 'Floating vertical shell': 'pink', 'Top surface': 'navy'}
li = seg[:, 7].astype(int)
m = (li >= L0) & (li <= L1)
S = seg[m]; F = feat[m]
x0, x1, y0, y1 = W[0] + px, W[1] + px, W[2] + py, W[3] + py
inw = (np.maximum(S[:, 0], S[:, 2]) >= x0) & (np.minimum(S[:, 0], S[:, 2]) <= x1) & (np.maximum(S[:, 1], S[:, 3]) >= y0) & (np.minimum(S[:, 1], S[:, 3]) <= y1)
S = S[inw]; F = F[inw]
fig, ax = plt.subplots(figsize=(8, 8 * (y1 - y0) / max(1e-6, (x1 - x0))) if (y1 - y0) < 2 * (x1 - x0) else (6, 10))
seen = set()
for i in np.unique(F):
    nm = names[i]; ss = S[F == i]
    lines = [[(a[0] - px, a[1] - py), (a[2] - px, a[3] - py)] for a in ss]
    lw = float(np.median(ss[:, 6]))
    # linewidth in points: data units -> points
    ax.add_collection(LineCollection(lines, colors=col.get(nm, 'k'), linewidths=1.2, label=nm, alpha=0.8))
ax.set_xlim(W[0], W[1]); ax.set_ylim(W[2], W[3]); ax.set_aspect('equal'); ax.grid(alpha=0.3)
ax.set_xlabel('world x (mm)'); ax.set_ylabel('world y (mm)'); ax.set_title(title + ' layers %d-%d' % (L0, L1), fontsize=9)
ax.legend(fontsize=7, loc='best')
fig.tight_layout(); fig.savefig(sys.argv[2], dpi=110)
print('ok', len(S))
