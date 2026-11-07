# vertical section of a world mesh at x = const (y-z plane) or y = const (x-z plane); faces facing down >= 60 deg in red
import sys, numpy as np, trimesh
sys.path.insert(0, '/home/claude/pa')
from pa_geom import load_world
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
def vsec(tag, axis, val, lims, out, title='', U=(0,0,1)):
    m = load_world(tag)
    n = np.zeros(3); n[axis] = 1.0; o = np.zeros(3); o[axis] = val
    lines, fi = trimesh.intersections.mesh_plane(m, n, o, return_faces=True)
    fn = m.face_normals[fi]; U = np.array(U, float); U /= np.linalg.norm(U)
    d = fn @ U
    ang = np.degrees(np.arcsin(np.clip(-d, -1, 1)))
    ax2 = [i for i in range(3) if i != axis]
    fig, ax = plt.subplots(figsize=(5.5, 4.2), dpi=100)
    for L, a in zip(lines, ang):
        c = 'r' if a >= 60 else ('orange' if a >= 45 else 'k')
        ax.plot(L[:, ax2[0]], L[:, ax2[1]], c, lw=0.8)
    ax.set_xlim(lims[0], lims[1]); ax.set_ylim(lims[2], lims[3]); ax.set_aspect('equal')
    ax.set_title(title or '%s section %s=%.2f' % (tag, 'xyz'[axis], val), fontsize=8); ax.tick_params(labelsize=6)
    ax.set_xlabel('xyz'[ax2[0]] + ' (world mm)', fontsize=7); ax.set_ylabel('xyz'[ax2[1]] + ' (world mm)', fontsize=7)
    ax.grid(True, lw=0.3)
    fig.tight_layout(); fig.savefig(out); plt.close(fig)
if __name__ == '__main__':
    tag, axis, val = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]); lims = [float(v) for v in sys.argv[4].split(',')]
    vsec(tag, axis, val, lims, sys.argv[5], sys.argv[6] if len(sys.argv) > 6 else '')
