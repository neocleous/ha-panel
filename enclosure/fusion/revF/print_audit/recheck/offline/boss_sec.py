import numpy as np, trimesh, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
E = '/mnt/user-data/uploads/print_audit_recheck/exports/'
f = trimesh.load(E + 'front.stl'); bl = trimesh.load(E + 'spkbox_L.stl'); br = trimesh.load(E + 'spkbox_R.stl')
fig, axs = plt.subplots(2, 3, figsize=(15, 9))
for row, (xc, box) in enumerate(((58.55, bl), (-58.61, br))):
    # plan section z = 80, 78, 82
    for col, z in enumerate((78.0, 80.0, 82.0)):
        ax = axs[row, col]
        for m, c in ((f, 'tab:red'), (box, 'tab:green')):
            s = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
            if s is None:
                continue
            for e in s.entities:
                P = s.vertices[e.points]; ax.plot(P[:, 0], P[:, 1], color=c, lw=0.8)
        ax.set_xlim(xc - 9, xc + 9); ax.set_ylim(-12, 6); ax.set_aspect('equal'); ax.grid(alpha=0.3)
        ax.set_title('z = %.1f, boss at x %.2f' % (z, xc), fontsize=8)
fig.tight_layout(); fig.savefig('g/boss_secs.png', dpi=100); print('ok')
