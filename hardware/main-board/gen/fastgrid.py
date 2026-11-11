"""Fast core for mroute.py: the grid search runs in scikit-image's compiled shortest-path code instead of Python.
Same interface as mroute.astar / mroute.smooth; install with fastgrid.patch(mroute)."""
import numpy as np
from skimage.graph import MCP_Geometric

CROWD = None               # set by a caller for one search: {layer: extra cost per cell}
VIA_LAYER_COST = 50.0      # moving sideways inside the via layer is never worth it
_OFFS3 = [(0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1), (0, 1, 1), (0, 1, -1), (0, -1, 1), (0, -1, -1), (1, 0, 0), (-1, 0, 0)]


def astar(okmap, viaok, starts, goals, via_cost, crowd=None):
    """okmap: {layer: bool[H, W]}, viaok: bool[H, W]; starts/goals: sets of (layer, i, j). Returns (path, cells).
    crowd: optional {layer: float[H, W]} extra cost (>= 0) that keeps tracks off busy places."""
    lns = list(okmap)
    H, W = viaok.shape
    # the obstacle picture stops at the region's rim, so copper just outside it is not seen: keep 1 mm off the rim
    pad = int(round(1.0 / _M.RES)) if _M else 0
    if pad and H > 4 * pad and W > 4 * pad:
        rim = np.zeros((H, W), dtype=bool)
        rim[pad:H - pad, pad:W - pad] = True
        okmap = {ln: m & rim for ln, m in okmap.items()}
        viaok = viaok & rim
    if len(lns) == 1:
        stack = np.where(okmap[lns[0]], 1.0, -1.0)[None, :, :]
        idx = {lns[0]: 0}
        samp = (1.0, 1.0, 1.0)
    else:
        a, c = okmap[lns[0]], okmap[lns[1]]
        mid = viaok & a & c
        stack = np.stack([np.where(a, 1.0, -1.0), np.where(mid, VIA_LAYER_COST, -1.0), np.where(c, 1.0, -1.0)])
        idx = {lns[0]: 0, lns[1]: 2}
        samp = (max(via_cost, 1.0) / (1.0 + VIA_LAYER_COST), 1.0, 1.0)
    crowd = crowd or CROWD
    if crowd:
        for ln, extra in crowd.items():
            if ln in idx and extra.shape == stack[idx[ln]].shape:
                lay = stack[idx[ln]]
                lay[lay > 0] += extra[lay > 0]
        if len(lns) == 2 and all(ln in crowd and crowd[ln].shape == stack[1].shape for ln in lns):
            mid_extra = crowd[lns[0]] + crowd[lns[1]]
            stack[1][stack[1] > 0] += mid_extra[stack[1] > 0]
    back = {v: k for k, v in idx.items()}
    S = [(idx[l], j, i) for (l, i, j) in starts if l in idx]
    G = [(idx[l], j, i) for (l, i, j) in goals if l in idx]
    if not S or not G:
        return None, 0
    m = MCP_Geometric(stack, offsets=_OFFS3, sampling=samp)
    costs, _ = m.find_costs(S, G, find_all_ends=False)
    g = np.array(G)
    cg = costs[g[:, 0], g[:, 1], g[:, 2]]
    k = int(np.argmin(cg))
    if not np.isfinite(cg[k]):
        return None, int(np.isfinite(costs).sum())
    tb = m.traceback(tuple(G[k]))
    path = [(back[l], int(i), int(j)) for (l, j, i) in tb if l in back]
    return path, len(tb)


def _clear(ok, a, b):
    (i0, j0), (i1, j1) = a, b
    n = int(max(abs(i1 - i0), abs(j1 - j0)) * 2) + 1
    t = np.linspace(0.0, 1.0, n + 1)
    ii = np.rint(i0 + (i1 - i0) * t).astype(int)
    jj = np.rint(j0 + (j1 - j0) * t).astype(int)
    return bool(ok[jj, ii].all())


def smooth(run, ok):
    """Any-angle shortening of one layer's run: from each kept point jump to the farthest point in line of sight."""
    pts = [(p[1], p[2]) for p in run]
    out = [pts[0]]
    k, n = 0, len(pts)
    while k < n - 1:
        lo, hi = k + 1, n - 1                 # pts[k+1] is always reachable (neighbouring cell)
        if _clear(ok, pts[k], pts[hi]):
            m = hi
        else:
            step = 1
            m = lo
            while m + step <= hi and _clear(ok, pts[k], pts[m + step]):
                m += step
                step *= 2
            hi2 = min(hi, m + step)
            while hi2 - m > 1:                # bisect between the last clear and the first blocked
                mid = (m + hi2) // 2
                if _clear(ok, pts[k], pts[mid]):
                    m = mid
                else:
                    hi2 = mid
        out.append(pts[m])
        k = m
    return out


_M = None


def patch(mroute):
    global _M
    _M = mroute
    mroute.astar = astar
    mroute.smooth = smooth
