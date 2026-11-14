# like gview.py but for layers chosen by world z, frame given by an orient json (translation only), with a model section overlay.
#   Usage: python3 gview2.py job.npz orient.json stl world_z "x0,x1,y0,y1" out.png [title]
import sys, json, numpy as np, trimesh, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
d = np.load(sys.argv[1]); seg = d['seg']; feat = d['feat']; names = [str(s) for s in d['names']]; layers = d['layers']
M = np.array(json.load(open(sys.argv[2]))['M_world_to_bed']); t = M[:3, 3]
mesh = trimesh.load(sys.argv[3]); wz = float(sys.argv[4]); W = [float(v) for v in sys.argv[5].split(',')]
bz = wz + t[2]
L = int(np.argmin(np.abs(layers - 0.1 - bz)))      # layer whose mid-plane is nearest
col = {'Outer wall': 'tab:red', 'Inner wall': 'tab:orange', 'Brim': 'tab:purple', 'Support': 'tab:green', 'Support interface': 'lime',
       'Bottom surface': 'tab:blue', 'Overhang wall': 'magenta', 'Bridge': 'cyan', 'Gap infill': 'gold', 'Sparse infill': 'grey',
       'Internal solid infill': 'tab:brown', 'Floating vertical shell': 'pink', 'Top surface': 'navy'}
li = seg[:, 7].astype(int); m = li == L; S = seg[m]; F = feat[m]
fig, ax = plt.subplots(figsize=(7, 7))
for i in np.unique(F):
    ss = S[F == i]
    lines = [[(a[0] - t[0], a[1] - t[1]), (a[2] - t[0], a[3] - t[1])] for a in ss]
    ax.add_collection(LineCollection(lines, colors=col.get(names[i], 'k'), linewidths=1.0, label=names[i]))
s = mesh.section(plane_origin=[0, 0, layers[L] - 0.1 - t[2]], plane_normal=[0, 0, 1])
if s is not None:
    for e in s.entities:
        P = s.vertices[e.points]; ax.plot(P[:, 0], P[:, 1], color='k', lw=0.6, ls='--')
ax.set_xlim(W[0], W[1]); ax.set_ylim(W[2], W[3]); ax.set_aspect('equal'); ax.grid(alpha=0.3)
ax.set_title((sys.argv[7] if len(sys.argv) > 7 else '') + ' layer %d (bed z %.2f, world z %.2f); dashed: model at mid-layer' % (L, layers[L], layers[L] - 0.1 - t[2]), fontsize=8)
ax.legend(fontsize=6, loc='best'); fig.tight_layout(); fig.savefig(sys.argv[6], dpi=120); print('layer', L)
