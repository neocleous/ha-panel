#!/usr/bin/env python3
"""HA panel model audit (2026-11-05), offline mesh analysis (runs where ~/Documents/audit is mounted).

Meshes are the binary STL files written by v5f_a1b_meshes.py: world mm, x_rel = x - XC, y toward the viewer, z up.

  a_mesh.py validity  PART...                      watertight, winding, components, volume vs the body (vols.json)
  a_mesh.py thick     PART [--da 0.5] [--tmax 6]   inward-normal ray thickness map -> data/thick_<PART>.npz + clusters
  a_mesh.py knife     PART [--deg 30]              convex edges with interior angle < deg (knife edges), clustered
  a_mesh.py overhang  PART UX UY UZ [--deg 45]     faces > deg down for build direction U (bed faces excluded), clustered,
                                                   each cluster with where a vertical drop from it lands (bed / part)
Clusters: points binned on a 1.0 mm grid, 26-connected; each cluster reports n, min value, the point of the minimum, bbox.
"""
import sys, os, json, time, argparse
import numpy as np
import trimesh

ROOT = os.path.expanduser('~/mnt/audit') if os.path.isdir(os.path.expanduser('~/mnt/audit')) else os.path.expanduser('~/Documents/audit')
MESH = os.path.join(ROOT, 'mesh'); DATA = os.path.join(ROOT, 'data'); os.makedirs(DATA, exist_ok=True)


def load(part, sub='mesh'):
    m = trimesh.load(os.path.join(ROOT, sub, part + '.stl'), process=True)
    return m


def clusters(P, val, cell=1.0, top=40):
    """Group points P (n×3) by a cell grid with 26-connectivity; return clusters sorted by min value."""
    if len(P) == 0:
        return []
    key = np.floor(P / cell).astype(np.int64)
    uk, inv = np.unique(key, axis=0, return_inverse=True)
    inv = inv.reshape(-1)
    idx = {tuple(k): i for i, k in enumerate(uk)}
    parent = list(range(len(uk)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    offs = [(i, j, k) for i in (-1, 0, 1) for j in (-1, 0, 1) for k in (-1, 0, 1) if (i, j, k) != (0, 0, 0)]
    for a, k in enumerate(uk):
        for o in offs:
            b = idx.get((k[0] + o[0], k[1] + o[1], k[2] + o[2]))
            if b is not None:
                ra, rb = find(a), find(b)
                if ra != rb:
                    parent[ra] = rb
    root = np.array([find(a) for a in range(len(uk))])[inv]
    out = []
    for r in np.unique(root):
        s = root == r
        i = np.argmin(np.where(s, val, np.inf))
        out.append({'n': int(s.sum()), 'min': round(float(val[i]), 3), 'at': [round(float(v), 2) for v in P[i]],
                    'bb': [round(float(v), 1) for v in np.concatenate([P[s].min(0), P[s].max(0)])]})
    return sorted(out, key=lambda c: c['min'])[:top]


def cmd_validity(parts):
    vols = json.load(open(os.path.join(DATA, 'vols.json')))
    res = {}
    for p in parts:
        m = load(p)
        comps = m.split(only_watertight=False)
        v = float(m.volume); vb = vols.get(p)
        res[p] = {'tris': int(len(m.faces)), 'verts': int(len(m.vertices)), 'watertight': bool(m.is_watertight),
                  'winding_consistent': bool(m.is_winding_consistent), 'components': len(comps),
                  'euler': int(m.euler_number), 'mesh_vol': round(v, 2), 'body_vol': vb,
                  'dvol_pct': None if not vb else round(100 * (v - vb) / vb, 4),
                  'comp_vols': sorted([round(float(c.volume), 3) for c in comps])[:6]}
    print(json.dumps(res, indent=0))


def sample(m, da):
    """Triangle centroids plus extra uniform points in triangles larger than da (mm²): (points, normals)."""
    A = m.area_faces; N = m.face_normals; T = m.triangles
    pts = [T.mean(1)]; nrm = [N]
    k = np.floor(A / da).astype(int)
    big = np.nonzero(k > 0)[0]
    if len(big):
        rep = np.repeat(big, k[big])
        r1 = np.random.default_rng(1).random(len(rep)); r2 = np.random.default_rng(2).random(len(rep))
        s = np.sqrt(r1)
        w = np.stack([1 - s, s * (1 - r2), s * r2], 1)
        pts.append((T[rep] * w[:, :, None]).sum(1)); nrm.append(N[rep])
    return np.concatenate(pts), np.concatenate(nrm)


def cmd_thick(part, da, tmax, eps=1e-3):
    t0 = time.time(); m = load(part)
    P, N = sample(m, da)
    org = P - eps * N; d = -N
    loc, iray, itri = m.ray.intersects_location(org, d, multiple_hits=False)
    t = np.full(len(P), np.inf)
    t[iray] = np.linalg.norm(loc - org[iray], axis=1) + eps
    np.savez_compressed(os.path.join(DATA, 'thick_%s.npz' % part), P=P.astype(np.float32), N=N.astype(np.float32), t=t.astype(np.float32))
    sel = t < tmax
    res = {'part': part, 'samples': int(len(P)), 'miss': int(np.isinf(t).sum()), 'min': round(float(t.min()), 3),
           't_s': round(time.time() - t0, 1)}
    for thr in (0.4, 0.8, 1.2, 1.5, 2.5):
        res['n_below_%s' % thr] = int((t < thr).sum())
    res['clusters_below_2p5'] = clusters(P[t < 2.5], t[t < 2.5], cell=1.0, top=60)
    print(json.dumps(res))


def cmd_knife(part, deg):
    m = load(part)
    ang = m.face_adjacency_angles; cvx = m.face_adjacency_convex
    lim = np.radians(180.0 - deg)
    s = cvx & (ang > lim)
    e = m.face_adjacency_edges[s]
    P = m.vertices[e].mean(1); interior = 180.0 - np.degrees(ang[s])
    L = np.linalg.norm(m.vertices[e[:, 0]] - m.vertices[e[:, 1]], axis=1)
    print(json.dumps({'part': part, 'edges': int(s.sum()), 'length_mm': round(float(L.sum()), 1),
                      'clusters': clusters(P, interior, cell=1.0, top=60)}))


def cmd_overhang(part, U, deg):
    m = load(part); U = np.array(U, float); U /= np.linalg.norm(U)
    N = m.face_normals; h = m.vertices @ U; h0 = h.min()
    down = (N @ U) < -np.cos(np.radians(90.0 - deg))
    bed = (h[m.faces] - h0 < 0.3).all(1)
    s = down & ~bed
    A = m.area_faces
    C = m.triangles_center[s]
    # where a vertical drop (−U) from each overhang face centre lands: on the part (distance) or on the bed
    loc, iray, itri = m.ray.intersects_location(C - 1e-3 * U, np.tile(-U, (len(C), 1)), multiple_hits=False)
    drop = np.full(len(C), np.inf); drop[iray] = np.linalg.norm(loc - C[iray], axis=1)
    on_part = np.isfinite(drop)
    cl = clusters(C, (C @ U) - h0, cell=1.0, top=80)
    # per cluster: area and how much of it drops onto the part
    key = {tuple(c['at']): c for c in cl}
    res = {'part': part, 'U': [round(float(v), 4) for v in U], 'height': round(float(h.max() - h0), 2),
           'support_mm2': round(float(A[s].sum()), 1), 'on_part_mm2': round(float(A[s][on_part].sum()), 1),
           'bed_mm2': round(float(A[down & bed].sum()), 1)}
    # cluster areas (recompute membership by the same grid)
    if len(C):
        cell = 1.0; kk = np.floor(C / cell).astype(np.int64)
        res['clusters'] = []
        for c in cl:
            lo = np.floor(np.array(c['bb'][:3]) / cell) - 0; hi = np.floor(np.array(c['bb'][3:]) / cell)
            inb = ((kk >= lo) & (kk <= hi)).all(1)
            c2 = dict(c); c2['area'] = round(float(A[s][inb].sum()), 1); c2['on_part_area'] = round(float(A[s][inb & on_part].sum()), 1)
            c2['drop_min'] = round(float(drop[inb & on_part].min()), 2) if (inb & on_part).any() else None
            res['clusters'].append(c2)
    print(json.dumps(res))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('cmd'); ap.add_argument('args', nargs='*')
    ap.add_argument('--da', type=float, default=0.5); ap.add_argument('--tmax', type=float, default=6.0)
    ap.add_argument('--deg', type=float, default=None)
    a = ap.parse_args()
    if a.cmd == 'validity':
        cmd_validity(a.args)
    elif a.cmd == 'thick':
        cmd_thick(a.args[0], a.da, a.tmax)
    elif a.cmd == 'knife':
        cmd_knife(a.args[0], a.deg or 30.0)
    elif a.cmd == 'overhang':
        cmd_overhang(a.args[0], [float(v) for v in a.args[1:4]], a.deg or 45.0)
