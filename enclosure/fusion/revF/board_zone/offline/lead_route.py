"""V23b (e5): route a D3 lead centreline through the voxel distance field (lead_vox.py) from a start to a goal (minimum cost
path, cost 1 + k * max(0, pref - distance), voxels nearer than `need` closed, `relax` boxes reopened to a smaller
distance), then pull it into a short polyline whose segments keep `need`. Usage: lead_route.py name sx sy sz gx gy gz
['{"need": 4.0, "pref": 6.0, "relax": [[[lo], [hi]], r]}']. Work folder as lead_vox.py; writes route_<name>.json."""
import numpy as np, json, sys, os, time
from skimage.graph import MCP_Geometric
from scipy.ndimage import map_coordinates

D = os.environ.get('LEAD_WORK', os.getcwd())
d = np.load(os.path.join(D, 'occ_h0.50.npz')); O = d['origin']; Hh = float(d['h'])
DIST = np.load(os.path.join(D, 'dist_h0.50.npy'))
R_TUBE = 1.5


def idx(p):
    return tuple(int(round((p[k] - O[k]) / Hh - 0.5)) for k in range(3))


def pos(i):
    return np.array([O[k] + (i[k] + 0.5) * Hh for k in range(3)])


def dist_at(P):
    """trilinear distance at world points P (n, 3)."""
    c = ((np.asarray(P) - O) / Hh - 0.5).T
    return map_coordinates(DIST, c, order=1, mode='nearest')


def seg_ok(a, b, need, relax=None):
    n = max(2, int(np.ceil(np.linalg.norm(b - a) / (Hh * 0.5))) + 1)
    t = np.linspace(0, 1, n)[:, None]
    P = a + (b - a) * t
    dd = dist_at(P)
    req = np.full(len(P), need)
    if relax is not None:
        for (bx, r_) in relax:
            inb = np.all((P >= bx[0]) & (P <= bx[1]), axis=1)
            req[inb] = np.minimum(req[inb], r_)
    return bool(np.all(dd >= req)), float(dd.min())


def route(start, goal, need=2.45, pref=5.0, k=3.0, relax=None, avoid=None):
    valid = DIST >= need
    if relax:
        for (bx, r_) in relax:
            i0 = idx(bx[0]); i1 = idx(bx[1])
            sl = tuple(slice(max(0, i0[a]), i1[a] + 1) for a in range(3))
            valid[sl] |= DIST[sl] >= r_
    cost = np.where(valid, 1.0 + k * np.clip(pref - DIST, 0, None), np.inf)
    if avoid:
        for (bx, f) in avoid:
            i0 = idx(bx[0]); i1 = idx(bx[1])
            sl = tuple(slice(max(0, i0[a]), i1[a] + 1) for a in range(3))
            cost[sl] = cost[sl] * f
    s = idx(start); g = idx(goal)
    if not np.isfinite(cost[s]) or not np.isfinite(cost[g]):
        return {'error': 'start/goal invalid', 'd_start': float(DIST[s]), 'd_goal': float(DIST[g])}
    m = MCP_Geometric(cost, fully_connected=True)
    m.find_costs([s], [g])
    path = np.array([pos(i) for i in m.traceback(g)])
    path[0] = start; path[-1] = goal
    # string pulling
    poly = [path[0]]; i = 0
    while i < len(path) - 1:
        j = len(path) - 1
        while j > i + 1 and not seg_ok(poly[-1], path[j], need, relax)[0]:
            j -= 1
        poly.append(path[j]); i = j
    poly = np.array(poly)
    L = float(np.sum(np.linalg.norm(np.diff(poly, axis=0), axis=1)))
    mins = [seg_ok(poly[q], poly[q + 1], 0.0)[1] for q in range(len(poly) - 1)]
    return {'poly': np.round(poly, 2).tolist(), 'len': round(L, 1), 'raw_len': round(float(np.sum(np.linalg.norm(np.diff(path, axis=0), axis=1))), 1),
            'seg_min_dist': [round(v, 2) for v in mins]}


if __name__ == '__main__':
    a = sys.argv[1:]
    name = a[0]; st = np.array(list(map(float, a[1:4]))); gl = np.array(list(map(float, a[4:7])))
    kw = json.loads(a[7]) if len(a) > 7 else {}
    if 'relax' in kw:
        kw['relax'] = [((np.array(b[0]), np.array(b[1])), r) for b, r in kw['relax']]
    if 'avoid' in kw:
        kw['avoid'] = [((np.array(b[0]), np.array(b[1])), f) for b, f in kw['avoid']]
    t0 = time.time()
    r = route(st, gl, **kw)
    r['t_s'] = round(time.time() - t0, 1)
    json.dump(r, open(os.path.join(D, 'route_%s.json' % name), 'w'))
    print(json.dumps(r))
