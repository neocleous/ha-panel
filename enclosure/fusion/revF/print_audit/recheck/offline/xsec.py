# recheck: y-z sections of several world meshes at given x (world), drawn together.  Usage: python3 xsec.py out.png "x1,x2,.." "y0,y1,z0,z1" name@color ...
import sys, numpy as np, trimesh, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
E = '/mnt/user-data/uploads/print_audit_recheck/exports/'
xs = [float(v) for v in sys.argv[2].split(',')]; W = [float(v) for v in sys.argv[3].split(',')]
meshes = []
for a in sys.argv[4:]:
    n, c = a.split('@'); meshes.append((n, c, trimesh.load(E + n + '.stl')))
fig, axs = plt.subplots(len(xs), 1, figsize=(9, 2.6 * len(xs)))
axs = np.atleast_1d(axs)
for ax, x in zip(axs, xs):
    for n, c, m in meshes:
        s = m.section(plane_origin=[x, 0, 0], plane_normal=[1, 0, 0])
        if s is None:
            continue
        for e in s.entities:
            P = s.vertices[e.points]
            ax.plot(P[:, 1], P[:, 2], color=c, lw=0.9)
    ax.set_xlim(W[0], W[1]); ax.set_ylim(W[2], W[3]); ax.set_aspect('equal'); ax.grid(alpha=0.3)
    ax.set_title('section x = %.1f (world)' % x, fontsize=8); ax.set_ylabel('z')
axs[-1].set_xlabel('y (world, + toward viewer)')
fig.tight_layout(); fig.savefig(sys.argv[1], dpi=110); print('ok')
