# recheck2: queries on parsed G-code (r2_gparse.py npz) in WORLD coordinates of the unit.
#   load(job, tag) -> G with seg (bed mm), names, M (world->bed) and helpers:
#   G.world(seg) -> (p0, p1) world points of segment ends; G.sel(feat_names) mask; G.rast(mask, layer, box2d, px) raster of
#   extrusions (lines with their width) in BED xy for one layer; G.layers (top z of each layer).
import json, math, numpy as np


class G:
    def __init__(self, job, tag, okey='plan'):
        z = np.load('/home/claude/r2/gc/%s.npz' % job, allow_pickle=True)
        self.S = z['seg']; self.F = z['feat']; self.names = list(z['names']); self.L = z['layers']
        self.M = np.array(json.load(open('/home/claude/r2/data/orient_%s_%s.json' % (tag, okey)))['M_world_to_bed'])
        self.Mi = np.linalg.inv(self.M)

    def fmask(self, *keys, exclude=()):
        ok = [i for i, n in enumerate(self.names) if (not keys or any(k in n for k in keys)) and not any(x in n for x in exclude)]
        return np.isin(self.F, ok)

    def to_world(self, P):                      # P (n,3) bed -> world
        P = np.c_[P, np.ones(len(P))]
        return (P @ self.Mi.T)[:, :3]

    def to_bed(self, W):
        W = np.c_[np.asarray(W, float), np.ones(len(W))]
        return (W @ self.M.T)[:, :3]

    def raster(self, mask, ztop, x0, y0, W, H, px):
        """Bool raster (H, W) of extrusion lines (with their width) of one layer (top z == ztop) in bed xy."""
        m = mask & (np.abs(self.S[:, 4] - ztop) < 1e-3)
        R = np.zeros((H, W), bool)
        s = self.S[m]
        if not len(s):
            return R
        yy, xx = np.mgrid[0:H, 0:W]
        cx = x0 + (xx + 0.5) * px; cy = y0 + (yy + 0.5) * px
        for a in s:
            ax, ay, bx, by, w = a[0], a[1], a[2], a[3], a[6]
            lo_x, hi_x = min(ax, bx) - w, max(ax, bx) + w; lo_y, hi_y = min(ay, by) - w, max(ay, by) + w
            i0 = max(0, int((lo_x - x0) / px)); i1 = min(W, int((hi_x - x0) / px) + 2)
            j0 = max(0, int((lo_y - y0) / px)); j1 = min(H, int((hi_y - y0) / px) + 2)
            if i0 >= i1 or j0 >= j1:
                continue
            X = cx[j0:j1, i0:i1]; Y = cy[j0:j1, i0:i1]
            dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
            if L2 < 1e-12:
                d2 = (X - ax) ** 2 + (Y - ay) ** 2
            else:
                t = np.clip(((X - ax) * dx + (Y - ay) * dy) / L2, 0, 1)
                d2 = (X - ax - t * dx) ** 2 + (Y - ay - t * dy) ** 2
            R[j0:j1, i0:i1] |= d2 <= (w / 2.0) ** 2
        return R
