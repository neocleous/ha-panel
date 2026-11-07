# HA panel print audit (P11): G-code layer views. Parses a PrusaSlicer G-code into extrusion segments (z, x0, y0, x1, y1,
#   type) once (cached .npz), then draws chosen layers in build coordinates (PrusaSlicer centres the object on the bed:
#   build = bed - (128 - cx, 128 - cy) with c the build bbox centre). Colours: support red, support interface magenta,
#   bridge infill blue, overhang perimeter orange, other extrusion black.
import sys, re, os, math, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
TYPES = ['Support material', 'Support material interface', 'Bridge infill', 'Overhang perimeter', 'other']
COL = {0: (0.85, 0.1, 0.1), 1: (0.8, 0.1, 0.8), 2: (0.1, 0.3, 0.95), 3: (1.0, 0.55, 0.0), 4: (0.1, 0.1, 0.1)}


def parse(path):
    cache = path + '.seg.npz'
    if os.path.exists(cache):
        d = np.load(cache); return d['S']
    z = 0.0; ty = 4; E = 0.0; X = Y = 0.0; segs = []
    for line in open(path):
        if line.startswith(';TYPE:'):
            t = line[6:].strip(); ty = TYPES.index(t) if t in TYPES else 4; continue
        if line.startswith(';Z:'):
            z = float(line[3:]); continue
        if line.startswith('G92'):
            m = re.search(r'E([-\d.]+)', line)
            if m: E = float(m.group(1))
            continue
        if line.startswith('G1') or line.startswith('G0'):
            mx = re.search(r'X([-\d.]+)', line); my = re.search(r'Y([-\d.]+)', line); me = re.search(r'E([-\d.]+)', line)
            nx = float(mx.group(1)) if mx else X; ny = float(my.group(1)) if my else Y
            if me:
                e = float(me.group(1)); de = e - E; E = e
                if de > 0 and (mx or my):
                    segs.append((z, X, Y, nx, ny, ty))
            X, Y = nx, ny
    S = np.array(segs, dtype=np.float32)
    np.savez_compressed(cache, S=S)
    return S


def view(path, zb, offset, crop=None, out=None, title=None, size=(5, 4), dpi=100, below=None):
    S = parse(path)
    zs = np.unique(S[:, 0]); z = zs[np.argmin(np.abs(zs - zb))]
    fig, ax = plt.subplots(figsize=size, dpi=dpi)
    if below is not None:
        zb2 = zs[np.argmin(np.abs(zs - below))]
        L = S[S[:, 0] == zb2]
        ax.add_collection(LineCollection([[(r[1] - offset[0], r[2] - offset[1]), (r[3] - offset[0], r[4] - offset[1])] for r in L],
                                         colors=[(0.75, 0.75, 0.75)], linewidths=0.6))
    L = S[S[:, 0] == z]
    ax.add_collection(LineCollection([[(r[1] - offset[0], r[2] - offset[1]), (r[3] - offset[0], r[4] - offset[1])] for r in L],
                                     colors=[COL[int(r[5])] for r in L], linewidths=0.7))
    if crop:
        ax.set_xlim(crop[0], crop[1]); ax.set_ylim(crop[2], crop[3])
    else:
        ax.autoscale()
    ax.set_aspect('equal'); ax.tick_params(labelsize=6)
    ax.set_title(title or '%s z %.2f' % (os.path.basename(path), z), fontsize=7)
    fig.tight_layout(); fig.savefig(out); plt.close(fig)
    return float(z)
