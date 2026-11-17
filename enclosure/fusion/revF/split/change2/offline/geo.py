# change2/offline/geo.py - meshes sent by cp2.mesh_pack(): load, world / slab frames, sections.
# World mm: x (+ = viewer's left), y + toward the screen, z up from the base plate's underside.
# Slab frame (x, d, up): d = depth behind the glass along the screen's normal, up = along the screen.
import json, struct, math
import numpy as np
import trimesh
C, S, H, XC = math.cos(math.radians(12.0)), math.sin(math.radians(12.0)), 143.3, -2.55


def unpack(raw):
    n = struct.unpack('>I', raw[:4])[0]; head = json.loads(raw[4:4 + n]); o = 4 + n; out = {}
    for it in head['items']:
        v = np.frombuffer(raw, dtype='<f4', count=it['nv'] * 3, offset=o).reshape(-1, 3).astype(np.float64); o += it['nv'] * 12
        t = np.frombuffer(raw, dtype='<i4', count=it['nt'] * 3, offset=o).reshape(-1, 3); o += it['nt'] * 12
        out[it['name']] = (v, t, it)
    return out


def d2w(v):                                           # design cm -> world mm
    return np.c_[v[:, 0] * 10 - XC, (v[:, 1] * C - v[:, 2] * S) * 10, H + (v[:, 1] * S + v[:, 2] * C) * 10]


def d2s(v):                                           # design cm -> slab frame mm (x, d, up)
    return np.c_[v[:, 0] * 10 - XC, -v[:, 1] * 10, v[:, 2] * 10]


def w2s(p):
    p = np.atleast_2d(np.asarray(p, float)); y = p[:, 1]; z = p[:, 2] - H
    return np.c_[p[:, 0], -(y * C + z * S), -y * S + z * C]


def s2w(p):
    p = np.atleast_2d(np.asarray(p, float)); d = p[:, 1]; u = p[:, 2]
    return np.c_[p[:, 0], -d * C - u * S, H - d * S + u * C]


def tm(v, t, frame='s'):
    m = trimesh.Trimesh(d2s(v) if frame == 's' else d2w(v), t, process=False)
    m.merge_vertices(digits_vertex=4)
    return m


def load(path, frame='s'):
    return {n: tm(v, t, frame) for n, (v, t, it) in unpack(open(path, 'rb').read()).items()}


def sect(mesh, origin, normal):                       # polylines (3D) of a mesh cut by a plane
    s = mesh.section(plane_origin=origin, plane_normal=normal)
    return [] if s is None else [np.asarray(p) for p in s.discrete]
