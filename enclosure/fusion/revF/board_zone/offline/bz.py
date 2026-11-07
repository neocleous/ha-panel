"""Board-zone column analysis: y-ray rasterisation of world-mm STL meshes (x_rel, y, z) on an x-z grid.

Each mesh -> per-cell occupied y-intervals (winding count along +y). Grid cell centres are jittered off round numbers so a
ray never runs exactly through a mesh edge.
"""
import numpy as np, struct, os

H = 0.5                              # grid pitch, mm
X0, X1 = -100.0, 100.0
Z0, Z1 = -20.0, 190.0
JX, JZ = 0.0123, 0.0371
NX = int(round((X1 - X0) / H)); NZ = int(round((Z1 - Z0) / H))
XS = X0 + H / 2 + JX + H * np.arange(NX)
ZS = Z0 + H / 2 + JZ + H * np.arange(NZ)


def load_stl(path):
    with open(path, 'rb') as f:
        f.read(80)
        n = struct.unpack('<I', f.read(4))[0]
        a = np.frombuffer(f.read(50 * n), dtype=np.dtype([('n', '<f4', 3), ('v', '<f4', (3, 3)), ('a', '<u2')]), count=n)
    return a['v'].astype(np.float64)


def signed_volume(V):
    return float(np.einsum('ij,ij->i', V[:, 0], np.cross(V[:, 1], V[:, 2])).sum() / 6.0)


def raster(V, chunk=400000):
    """Crossings of +y rays at the grid cell centres: (cell index, y, +1 entry / -1 exit)."""
    out_c, out_y, out_d = [], [], []
    for s in range(0, len(V), chunk):
        T = V[s:s + chunk]
        ax, az = T[:, 0, 0], T[:, 0, 2]
        ux, uz = T[:, 1, 0] - ax, T[:, 1, 2] - az
        vx, vz = T[:, 2, 0] - ax, T[:, 2, 2] - az
        d = ux * vz - uz * vx                                   # 2-D cross in x-z; n_y = -d
        ok = np.abs(d) > 1e-12
        xmin = T[:, :, 0].min(1); xmax = T[:, :, 0].max(1); zmin = T[:, :, 2].min(1); zmax = T[:, :, 2].max(1)
        i0 = np.ceil((xmin - (X0 + H / 2 + JX)) / H).astype(np.int64); i1 = np.floor((xmax - (X0 + H / 2 + JX)) / H).astype(np.int64)
        k0 = np.ceil((zmin - (Z0 + H / 2 + JZ)) / H).astype(np.int64); k1 = np.floor((zmax - (Z0 + H / 2 + JZ)) / H).astype(np.int64)
        i0 = np.maximum(i0, 0); k0 = np.maximum(k0, 0); i1 = np.minimum(i1, NX - 1); k1 = np.minimum(k1, NZ - 1)
        nx = np.maximum(i1 - i0 + 1, 0); nz = np.maximum(k1 - k0 + 1, 0)
        cnt = np.where(ok, nx * nz, 0)
        if cnt.sum() == 0:
            continue
        tri = np.repeat(np.arange(len(T)), cnt)
        off = np.arange(cnt.sum()) - np.repeat(np.cumsum(cnt) - cnt, cnt)
        ii = i0[tri] + off % nx[tri]; kk = k0[tri] + off // nx[tri]
        px = XS[ii] - ax[tri]; pz = ZS[kk] - az[tri]
        dd = d[tri]
        wb = (px * vz[tri] - pz * vx[tri]) / dd
        wc = (ux[tri] * pz - uz[tri] * px) / dd
        wa = 1.0 - wb - wc
        inside = (wa >= 0) & (wb >= 0) & (wc >= 0)
        tri = tri[inside]; ii = ii[inside]; kk = kk[inside]
        y = wa[inside] * T[tri, 0, 1] + wb[inside] * T[tri, 1, 1] + wc[inside] * T[tri, 2, 1]
        out_c.append(kk * NX + ii); out_y.append(y); out_d.append(np.where(d[tri] > 0, 1, -1))
    if not out_c:
        return np.zeros(0, np.int64), np.zeros(0), np.zeros(0, np.int64)
    return np.concatenate(out_c), np.concatenate(out_y), np.concatenate(out_d)


def intervals(c, y, d):
    """Occupied intervals per cell from the winding count; returns (cell, y0, y1) and the cells whose count is unbalanced."""
    o = np.lexsort((y, c)); c, y, d = c[o], y[o], d[o]
    # cumulative winding within each cell
    w = np.cumsum(d)
    start = np.r_[True, c[1:] != c[:-1]]
    base = np.maximum.accumulate(np.where(start, np.arange(len(c)), 0))      # index of each element's run start
    wcell = w - (w[base] - d[base])
    end = np.r_[c[1:] != c[:-1], True]
    bad = np.unique(c[end & (wcell != 0)])
    # interval starts where the winding goes 0 -> >0, ends where it returns to 0
    prev = wcell - d
    st = (prev <= 0) & (wcell > 0)
    en = (prev > 0) & (wcell <= 0)
    cs, ys = c[st], y[st]; ce, ye = c[en], y[en]
    if len(cs) != len(ce) or np.any(cs != ce):
        # drop unbalanced cells entirely and recompute
        good = ~np.isin(c, bad)
        return intervals(c[good], y[good], d[good])[0], bad
    return (cs, ys, ye), bad


def body_intervals(path, cache_dir):
    os.makedirs(cache_dir, exist_ok=True)
    key = os.path.join(cache_dir, os.path.basename(path) + '.npz')
    if os.path.exists(key) and os.path.getmtime(key) > os.path.getmtime(path):
        z = np.load(key)
        return (z['c'], z['y0'], z['y1']), z['bad'], float(z['vol'])
    V = load_stl(path)
    vol = signed_volume(V)
    (c, y0, y1), bad = intervals(*raster(V))
    np.savez(key, c=c, y0=y0, y1=y1, bad=bad, vol=vol)
    return (c, y0, y1), bad, vol


def cell_xz(c):
    return XS[c % NX], ZS[c // NX]
