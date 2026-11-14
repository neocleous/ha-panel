# recheck: support extrusion of a job projected on the three world planes (bed -> world by the job's translation).
import sys, json, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
d = np.load(sys.argv[1]); seg = d['seg']; feat = d['feat']; names = [str(s) for s in d['names']]
t = np.array([float(v) for v in sys.argv[2].split(',')])
sup = np.isin(feat, [i for i, n in enumerate(names) if n.startswith('Support')])
inter = np.isin(feat, [i for i, n in enumerate(names) if n == 'Support interface'])
S = seg[sup]; I = seg[inter]
def mid(a):
    return np.stack([(a[:, 0] + a[:, 2]) / 2 - t[0], (a[:, 1] + a[:, 3]) / 2 - t[1], a[:, 4] - 0.1 - t[2]], 1)
P = mid(S); Q = mid(I)
fig, axs = plt.subplots(1, 3, figsize=(18, 7))
for ax, (i, j, lab) in zip(axs, ((0, 2, 'x-z (front view; +x = viewer left)'), (1, 2, 'y-z (side view)'), (0, 1, 'x-y (plan)'))):
    ax.scatter(P[:, i], P[:, j], s=0.05, c='tab:green', alpha=0.3)
    ax.scatter(Q[:, i], Q[:, j], s=0.3, c='red', alpha=0.6)
    ax.set_title(lab, fontsize=9); ax.grid(alpha=0.3); ax.set_aspect('equal')
fig.suptitle(sys.argv[4] if len(sys.argv) > 4 else '', fontsize=10)
fig.tight_layout(); fig.savefig(sys.argv[3], dpi=90); print('ok', len(P), len(Q))
