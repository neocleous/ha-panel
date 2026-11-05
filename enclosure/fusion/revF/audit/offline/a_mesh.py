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
    """Triangle centroids plus extra uniform points in triangles larger than da (mm²): (points, normals, area weights)."""
    A = m.area_faces; N = m.face_normals; T = m.triangles
    k = np.floor(A / da).astype(int)
    w0 = A / (k + 1)                                  # each triangle's area shared by its centroid and its k extra points
    pts = [T.mean(1)]; nrm = [N]; wts = [w0]
    big = np.nonzero(k > 0)[0]
    if len(big):
        rep = np.repeat(big, k[big])
        r1 = np.random.default_rng(1).random(len(rep)); r2 = np.random.default_rng(2).random(len(rep))
        s = np.sqrt(r1)
        w = np.stack([1 - s, s * (1 - r2), s * r2], 1)
        pts.append((T[rep] * w[:, :, None]).sum(1)); nrm.append(N[rep]); wts.append(w0[rep])
    return np.concatenate(pts), np.concatenate(nrm), np.concatenate(wts)


def rays_first(m, org, d, chunk=4000, tmax=None):
    """Distance to the first hit for each ray (inf on a miss). With tmax the rays are segments: candidate triangles come
    from the r-tree of triangle bounds against each segment's box, then a vectorised Moller-Trumbore test."""
    t = np.full(len(org), np.inf)
    if tmax is None:
        for i in range(0, len(org), chunk):
            loc, iray, itri = m.ray.intersects_location(org[i:i + chunk], d[i:i + chunk], multiple_hits=False)
            t[i + iray] = np.linalg.norm(loc - org[i + iray], axis=1)
        return t
    tree = m.triangles_tree; T = m.triangles
    end = org + d * tmax; lo = np.minimum(org, end); hi = np.maximum(org, end)
    for i in range(0, len(org), chunk):
        ri = []; ti = []
        for k in range(i, min(i + chunk, len(org))):
            c = list(tree.intersection((lo[k, 0], lo[k, 1], lo[k, 2], hi[k, 0], hi[k, 1], hi[k, 2])))
            ri.extend([k] * len(c)); ti.extend(c)
        if not ri:
            continue
        ri = np.array(ri); ti = np.array(ti)
        v0 = T[ti, 0]; e1 = T[ti, 1] - v0; e2 = T[ti, 2] - v0; D = d[ri]; O = org[ri]
        pv = np.cross(D, e2); det = (e1 * pv).sum(1)
        ok = np.abs(det) > 1e-12
        inv = np.where(ok, 1.0 / np.where(ok, det, 1.0), 0.0)
        tv = O - v0; u = (tv * pv).sum(1) * inv
        qv = np.cross(tv, e1); v = (D * qv).sum(1) * inv; tt = (e2 * qv).sum(1) * inv
        hit = ok & (u >= -1e-9) & (v >= -1e-9) & (u + v <= 1 + 1e-9) & (tt > 1e-9) & (tt <= tmax)
        np.minimum.at(t, ri[hit], tt[hit])
    return t


def aclusters(P, val, W, cell, min_area, top=40):
    """clusters() with the summed sample area; only clusters of at least min_area mm²."""
    out = []
    for c in clusters(P, val, cell=cell, top=100000):
        lo = np.array(c['bb'][:3]) - 1e-6; hi = np.array(c['bb'][3:]) + 1e-6
        inb = ((P >= lo - cell) & (P <= hi + cell)).all(1)
        a = float(W[inb].sum())
        if a >= min_area:
            c['area'] = round(a, 2); c['p10'] = round(float(np.percentile(val[inb], 10)), 3); out.append(c)
    return sorted(out, key=lambda c: -c['area'])[:top]


def cmd_thick(part, da, tmax, eps=1e-3, shell=2.45, sub='mesh'):
    t0 = time.time(); m = load(part, sub)
    P, N, W = sample(m, da)
    org = P - eps * N; d = -N
    t = rays_first(m, org, d, tmax=tmax) + eps
    np.savez_compressed(os.path.join(DATA, 'thick_%s.npz' % part), P=P.astype(np.float32), N=N.astype(np.float32),
                        t=t.astype(np.float32), W=W.astype(np.float32))
    res = {'part': part, 'samples': int(len(P)), 'area': round(float(W.sum()), 1), 'miss': int(np.isinf(t).sum()),
           'min': round(float(t.min()), 3), 't_s': round(time.time() - t0, 1)}
    edges = [0, 0.2, 0.4, 0.8, 1.2, 1.5, 2.0, 2.45, 2.55, 3.5, 6, 1e9]
    res['area_hist'] = {'%s-%s' % (edges[i], edges[i + 1]): round(float(W[(t >= edges[i]) & (t < edges[i + 1])].sum()), 1)
                        for i in range(len(edges) - 1)}
    for thr, cell, amin in ((0.4, 0.5, 0.05), (0.8, 0.5, 0.2), (1.2, 0.5, 0.5), (shell, 1.0, 10.0)):
        s = t < thr
        res['cl_%s' % thr] = aclusters(P[s], t[s], W[s], cell, amin, top=40)
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
    drop = rays_first(m, C - 1e-3 * U, np.tile(-U, (len(C), 1)), tmax=float(h.max() - h0) + 1.0)
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
