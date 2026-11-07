"""Exact-ish clearances of a board outline (polygon in x_rel/z, slab y -65..-63.4) to the meshes: dense surface samples."""
import numpy as np, bz
from shapely.geometry import Polygon, Point
from shapely import prepared
import shapely
M = '/mnt/user-data/uploads/HA_panel_renders/board_zone/mesh/'
FRONT = '/mnt/user-data/uploads/HA_panel_renders/print_audit/exports/front_d22.stl'
def samples(path, step=0.25, box=None):
    V = bz.load_stl(path)
    if box is not None:
        lo, hi = box
        keep = np.all((V.max(1) >= lo) & (V.min(1) <= hi), axis=1); V = V[keep]
    a, b, c = V[:, 0], V[:, 1], V[:, 2]
    e = np.maximum(np.linalg.norm(b - a, axis=1), np.maximum(np.linalg.norm(c - a, axis=1), np.linalg.norm(c - b, axis=1)))
    n = np.clip(np.ceil(e / step).astype(int), 1, 200)
    pts = [V.reshape(-1, 3)]
    for k in np.unique(n):
        if k < 2: continue
        sel = n == k
        i, j = np.mgrid[0:k+1, 0:k+1]; m = i + j <= k
        u = (i[m] / k)[None, :, None]; v = (j[m] / k)[None, :, None]
        P = a[sel][:, None, :] + u * (b[sel] - a[sel])[:, None, :] + v * (c[sel] - a[sel])[:, None, :]
        pts.append(P.reshape(-1, 3))
    return np.concatenate(pts)
def clearance(poly, P):
    """min x-z distance from points P (x,y,z) to the polygon (0 if inside) and the closest point."""
    if len(P) == 0: return np.inf, None
    pg = Polygon(poly)
    xs, zs = P[:, 0], P[:, 2]
    pts = shapely.points(xs, zs)
    d = shapely.distance(pg, pts)
    i = int(np.argmin(d))
    return float(d[i]), P[i]
