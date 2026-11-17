# change2/offline/model.py - version 65's bodies as meshes (slab frame and world), section plots for the study.
import sys, os, math, pickle
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np, trimesh, geo
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
D = os.path.join(os.path.dirname(__file__), '..', 'data')
_M = {}


def raw():
    if not _M:
        for f in ('mesh_shell.bin', 'mesh_parts.bin', 'mesh_rest.bin'):
            for n, (v, t, it) in geo.unpack(open(os.path.join(D, f), 'rb').read()).items():
                _M[n] = (v, t)
    return _M


def mesh(name, frame='s'):                            # frame 's' slab (x, d, up) or 'w' world; faces turned outward in both
    v, t = raw()[name]
    m = trimesh.Trimesh(geo.d2s(v) if frame == 's' else geo.d2w(v), t[:, ::-1] if frame == 's' else t, process=False)
    m.merge_vertices(digits_vertex=4)
    return m


AX = {'s': ('x', 'd', 'up'), 'w': ('x', 'y', 'z')}
COL = {'HOUSING_F_front': '#9aa0a6', 'HOUSING_F_plate': '#222222', 'SLAB_frame': '#3b5bdb', 'LCD_glass': '#74c0fc', 'HOUSING_F_cap': '#e8590c',
       'HOUSING_F_door': '#2f9e44', 'REF_F_outer': '#e03131', 'FLOOR_PLATE': '#845ef7', 'SPKBOX_L': '#f08c00', 'SPKBOX_R': '#f08c00'}


def cut(names, axis, val, frame='s'):                 # {name: [polyline Nx2 in the two other axes]}
    n = [0.0, 0.0, 0.0]; n[axis] = 1.0; o = [0.0, 0.0, 0.0]; o[axis] = val
    keep = [i for i in range(3) if i != axis]; out = {}
    for nm in names:
        out[nm] = [p[:, keep] for p in geo.sect(mesh(nm, frame), o, n)]
    return out, keep


def plot(names, axis, val, box, fname, frame='s', title='', flipx=False, marks=(), size=9):
    res, keep = cut(names, axis, val, frame)
    fig, ax = plt.subplots(figsize=(size, size * (box[3] - box[2]) / (box[1] - box[0]) + 0.6))
    for nm, pls in res.items():
        for p in pls:
            ax.plot(p[:, 0], p[:, 1], '-', lw=1.0, color=COL.get(nm, '#555555'))
    for (a, b, lab) in marks:
        ax.plot([a], [b], 'k+'); ax.annotate(lab, (a, b), fontsize=7)
    ax.set_xlim(box[0], box[1]); ax.set_ylim(box[2], box[3]); ax.set_aspect('equal'); ax.grid(True, lw=0.3)
    if flipx:
        ax.invert_xaxis()
    ax.set_xlabel(AX[frame][keep[0]]); ax.set_ylabel(AX[frame][keep[1]])
    ax.set_title(title or '%s = %g (%s)' % (AX[frame][axis], val, ', '.join(names)), fontsize=9)
    fig.tight_layout(); fig.savefig(fname, dpi=110); plt.close(fig)
