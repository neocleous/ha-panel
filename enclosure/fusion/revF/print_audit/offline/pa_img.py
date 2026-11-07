# HA panel print audit: layer images for evidence. render(tag, orient, z_build, crop=(x0,x1,y0,y1) build mm, out=path)
#   grey = previous layer, black = this layer, red = this layer beyond 0.346 mm of the previous one (needs support at
#   Bambu's default 30 deg threshold), blue = lower layers' footprint (where a support would land) for context.
import sys, math, numpy as np
sys.path.insert(0, '/home/claude/pa')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import ndimage as ndi


def load_stack(tag, okey):
    z = np.load('/home/claude/pa/work/M_%s_%s.npz' % (tag, okey))
    Hh, W = [int(v) for v in z['shape']]; x0, y0, px = [float(v) for v in z['grid']]
    return z, Hh, W, x0, y0, px


def layer(z, Hh, W, k):
    return np.unpackbits(z['packed'][k])[:Hh * W].reshape(Hh, W).astype(bool)


def render(tag, okey, zb, crop=None, out=None, title=None, wtf=None, dpi=110, size=(6, 4.5)):
    z, Hh, W, x0, y0, px = load_stack(tag, okey)
    zs = z['zs']; k = int(np.argmin(np.abs(zs - zb)))
    m = layer(z, Hh, W, k); p = layer(z, Hh, W, k - 1) if k > 0 else np.zeros_like(m)
    d = ndi.distance_transform_edt(~p) * px if p.any() else np.full(m.shape, 1e9)
    u = m & (d > 0.3464)
    img = np.ones((Hh, W, 3))
    img[p] = (0.75, 0.75, 0.75)
    img[m] = (0.1, 0.1, 0.1)
    img[u] = (0.9, 0.1, 0.1)
    ext = (x0, x0 + W * px, y0, y0 + Hh * px)
    fig, ax = plt.subplots(figsize=size, dpi=dpi)
    ax.imshow(img, origin='lower', extent=ext, interpolation='nearest')
    if crop:
        ax.set_xlim(crop[0], crop[1]); ax.set_ylim(crop[2], crop[3])
    ax.set_title(title or '%s %s layer %d top z %.1f (build)' % (tag, okey, k, 0.2 * (k + 1)), fontsize=8)
    ax.set_xlabel('build x (mm)', fontsize=7); ax.set_ylabel('build y (mm)', fontsize=7); ax.tick_params(labelsize=6)
    ax.set_aspect('equal')
    fig.tight_layout()
    fig.savefig(out, dpi=dpi); plt.close(fig)
    return k, float(u.sum() * px * px)


if __name__ == '__main__':
    tag, okey, zb = sys.argv[1], sys.argv[2], float(sys.argv[3])
    crop = [float(v) for v in sys.argv[4].split(',')] if len(sys.argv) > 4 and sys.argv[4] != '-' else None
    out = sys.argv[5] if len(sys.argv) > 5 else '/home/claude/pa/img/%s_%s_z%.1f.png' % (tag, okey, zb)
    print(render(tag, okey, zb, crop, out))
