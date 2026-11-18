import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from s2_gcode import *
def panel(ax, tag, h, win, title):
    a = load(tag); zs = np.unique(a[:, 0]); z = zs[np.argmin(np.abs(zs - h))]; b = a[a[:, 0] == z]
    u0, u1, v0, v1 = win
    col = {0: '#d95f02', 1: '#e6ab02', 2: '#a6761d', 3: '#9a9a9a', 4: '#1b9e77', 5: '#7570b3', 6: '#7570b3', 7: '#66a61e', 8: '#e7298a', 9: '#1f78b4'}
    fig = ax.figure; bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    ppm = bbox.width * 72 / (u1 - u0)
    for t in np.unique(b[:, 2]).astype(int):
        s = b[b[:, 2] == t]
        m = (np.minimum(s[:, 4], s[:, 6]) < u1) & (np.maximum(s[:, 4], s[:, 6]) > u0) & (np.minimum(s[:, 5], s[:, 7]) < v1) & (np.maximum(s[:, 5], s[:, 7]) > v0)
        s = s[m]
        if len(s) == 0: continue
        segs = np.stack([s[:, 4:6], s[:, 6:8]], axis=1)
        ax.add_collection(LineCollection(segs, colors=col.get(t, '#000'), linewidths=float(np.median(s[:, 3])) * ppm * 0.9, capstyle='round', label=TYPES[t]))
    ax.set_xlim(u0, u1); ax.set_ylim(v0, v1); ax.set_aspect('equal'); ax.tick_params(labelsize=6)
    ax.set_title('%s, layer top %.1f' % (title, z), fontsize=8); ax.legend(fontsize=5, loc='lower left')
def sheet(out, specs, ncol=4):
    n = len(specs); nrow = (n + ncol - 1) // ncol
    fig, axs = plt.subplots(nrow, ncol, figsize=(3.4 * ncol, 3.5 * nrow), dpi=100, squeeze=False)
    fig.tight_layout(pad=1.5)
    for ax in axs.ravel()[n:]: ax.axis('off')
    for ax, s in zip(axs.ravel(), specs):
        panel(ax, s[0], s[1], s[2], s[3])
    fig.savefig(out); plt.close(fig)
if __name__ == '__main__':
    T = (67.45, 23.7); B = (82.45, -82.9)
    w = lambda c, r: (c[0] - r, c[0] + r, c[1] - r, c[1] + r)
    sheet('../img/gc_posts.png', [
        ('shell', 26.0, w(T, 9), 'top post, insert'), ('shell', 30.0, w(T, 9), 'top post, insert end'),
        ('shell', 33.0, w(T, 9), 'top post, cone'), ('shell', 37.0, w(T, 9), 'top post, root'),
        ('shell', 2.0, w(B, 10), 'bottom post, peg'), ('shell', 4.0, w(B, 10), 'bottom post, insert'),
        ('shell', 7.0, w(B, 10), 'bottom post, insert end'), ('shell', 9.4, w(B, 10), 'bottom post, rear')])
