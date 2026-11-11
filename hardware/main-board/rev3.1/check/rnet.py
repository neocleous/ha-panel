"""Resistance of a copper net between terminals, by a finite-difference solve on the board's own copper
(tracks, pads, via rings and filled areas of the named nets on all four layers; plated barrels between layers).
Read-only on the KiCad file. Units: mm in, ohm out. Resistivity at 20 C."""
import math, sys
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
from scipy.sparse.csgraph import connected_components
from matplotlib.path import Path
import pcb

RHO = 1.724e-8                      # ohm m, annealed copper at 20 C
LAYERS = ['F.Cu', 'In1.Cu', 'In2.Cu', 'B.Cu']
T = {'F.Cu': 35e-6, 'In1.Cu': 15.2e-6, 'In2.Cu': 15.2e-6, 'B.Cu': 35e-6}     # JLC04161H-7628, finished
DZ = [0.2104 + (0.035 + 0.0152) / 2, 1.065 + 0.0152, 0.2104 + (0.035 + 0.0152) / 2]   # mm between layer mid-planes
TPL = 18e-6                         # hole-wall plating, m (JLC: average 18 um)

def barrel_R(drill_mm, dz_mm):
    d = drill_mm * 1e-3
    return RHO * dz_mm * 1e-3 / (math.pi * (d - TPL) * TPL)

class Net:
    def __init__(self, b, nets, box, h):
        self.b, self.nets, self.h = b, set(nets), h
        self.x0, self.y0, self.x1, self.y1 = box
        self.nx = int(round((self.x1 - self.x0) / h)); self.ny = int(round((self.y1 - self.y0) / h))
        xs = self.x0 + (np.arange(self.nx) + 0.5) * h; ys = self.y0 + (np.arange(self.ny) + 0.5) * h
        self.X, self.Y = np.meshgrid(xs, ys)              # shape (ny, nx)
        self.mask = {L: np.zeros((self.ny, self.nx), bool) for L in LAYERS}
        self.barrels = []                                 # dict(x, y, drill, kind, name)
        self._raster()

    def _win(self, xa, ya, xb, yb):
        i0 = max(0, int((xa - self.x0) / self.h) - 1); i1 = min(self.nx, int((xb - self.x0) / self.h) + 2)
        j0 = max(0, int((ya - self.y0) / self.h) - 1); j1 = min(self.ny, int((yb - self.y0) / self.h) + 2)
        return slice(j0, j1), slice(i0, i1)

    def _raster(self):
        b = self.b
        for z in b['zones']:
            if z['keepout'] or z['net'] not in self.nets: continue
            for lay, pts in z['fills']:
                p = np.array(pts)
                sj, si = self._win(p[:, 0].min(), p[:, 1].min(), p[:, 0].max(), p[:, 1].max())
                XX = self.X[sj, si]; YY = self.Y[sj, si]
                if XX.size == 0: continue
                inside = Path(p).contains_points(np.column_stack([XX.ravel(), YY.ravel()])).reshape(XX.shape)
                self.mask[lay][sj, si] |= inside
        for sg in b['segs']:
            if sg['net'] not in self.nets: continue
            r = sg['w'] / 2
            sj, si = self._win(min(sg['x1'], sg['x2']) - r, min(sg['y1'], sg['y2']) - r, max(sg['x1'], sg['x2']) + r, max(sg['y1'], sg['y2']) + r)
            XX = self.X[sj, si]; YY = self.Y[sj, si]
            if XX.size == 0: continue
            dx, dy = sg['x2'] - sg['x1'], sg['y2'] - sg['y1']; L2 = dx * dx + dy * dy
            t = np.zeros_like(XX) if L2 == 0 else np.clip(((XX - sg['x1']) * dx + (YY - sg['y1']) * dy) / L2, 0, 1)
            d = np.hypot(XX - (sg['x1'] + t * dx), YY - (sg['y1'] + t * dy))
            self.mask[sg['layer']][sj, si] |= d <= r
        holes = []
        for ref, f in b['fps'].items():
            for p in f['pads']:
                if p['net'] not in self.nets or not p['n']: continue
                lays = LAYERS if '*.Cu' in p['layers'] else [l for l in p['layers'] if l in LAYERS]
                sj, si = self._win(p['x'] - p['sx'] / 2, p['y'] - p['sy'] / 2, p['x'] + p['sx'] / 2, p['y'] + p['sy'] / 2)
                XX = self.X[sj, si]; YY = self.Y[sj, si]
                if XX.size == 0: continue
                if p['shape'] == 'circle' or (p['shape'] == 'oval' and abs(p['sx'] - p['sy']) < 1e-9):
                    m = np.hypot(XX - p['x'], YY - p['y']) <= p['sx'] / 2
                elif p['shape'] == 'oval':
                    r = min(p['sx'], p['sy']) / 2
                    ax = max(p['sx'] / 2 - r, 0); ay = max(p['sy'] / 2 - r, 0)
                    ddx = np.maximum(np.abs(XX - p['x']) - ax, 0); ddy = np.maximum(np.abs(YY - p['y']) - ay, 0)
                    m = np.hypot(ddx, ddy) <= r
                else:
                    m = (np.abs(XX - p['x']) <= p['sx'] / 2) & (np.abs(YY - p['y']) <= p['sy'] / 2)
                for l in lays:
                    self.mask[l][sj, si] |= m
                if p['type'] == 'thru_hole' and p['drill']:
                    self.barrels.append(dict(x=p['x'], y=p['y'], drill=p['drill'][0], kind='pin', name='%s.%s' % (ref, p['n'])))
        for v in b['vias']:
            if v['net'] not in self.nets: continue
            if not (self.x0 <= v['x'] <= self.x1 and self.y0 <= v['y'] <= self.y1): continue
            sj, si = self._win(v['x'] - v['size'] / 2, v['y'] - v['size'] / 2, v['x'] + v['size'] / 2, v['y'] + v['size'] / 2)
            XX = self.X[sj, si]; YY = self.Y[sj, si]
            m = np.hypot(XX - v['x'], YY - v['y']) <= v['size'] / 2
            for l in LAYERS:
                self.mask[l][sj, si] |= m
            self.barrels.append(dict(x=v['x'], y=v['y'], drill=v['drill'], kind='via', name='via(%.2f,%.2f)' % (v['x'], v['y'])))
        self.barrels = [q for q in self.barrels if self.x0 <= q['x'] <= self.x1 and self.y0 <= q['y'] <= self.y1]
        for q in self.barrels:            # the hole itself is not copper
            sj, si = self._win(q['x'] - q['drill'], q['y'] - q['drill'], q['x'] + q['drill'], q['y'] + q['drill'])
            XX = self.X[sj, si]; YY = self.Y[sj, si]
            hole = np.hypot(XX - q['x'], YY - q['y']) < q['drill'] / 2
            for l in LAYERS:
                self.mask[l][sj, si] &= ~hole

    def solve(self, sources, sinks, ideal=(), mode='equipotential', I=1.0, extra_copper=None, verbose=False):
        """sources / sinks: lists of terminals. A terminal is ('pin', 'PS1.1') = that barrel on every layer,
        or ('pad', ref, n, layer) = the whole SMD pad as one node. ideal: barrel names whose layers are tied
        (a soldered component pin or wire). mode 'equipotential': sinks tied together; 'equal': I/len(sinks) drawn at each."""
        if extra_copper: extra_copper(self)
        h = self.h
        idx = {}; n = 0
        for L in LAYERS:
            a = -np.ones(self.mask[L].shape, np.int64)
            k = int(self.mask[L].sum()); a[self.mask[L]] = np.arange(n, n + k); n += k
            idx[L] = a
        parent = np.arange(n + 4 * len(self.barrels) + 64)
        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]; a = parent[a]
            return a
        def union(a, c):
            ra, rc = find(a), find(c)
            if ra != rc: parent[rc] = ra
        bnode = {}
        rows, cols, vals = [], [], []
        def link(a, c, g):
            rows.extend([a, c, a, c]); cols.extend([a, c, c, a]); vals.extend([g, g, -g, -g])
        for bi, q in enumerate(self.barrels):
            ids = []
            for li, L in enumerate(LAYERS):
                nid = n; n += 1; ids.append(nid)
                sj, si = self._win(q['x'] - q['drill'] / 2 - 2.5 * h, q['y'] - q['drill'] / 2 - 2.5 * h, q['x'] + q['drill'] / 2 + 2.5 * h, q['y'] + q['drill'] / 2 + 2.5 * h)
                d = np.hypot(self.X[sj, si] - q['x'], self.Y[sj, si] - q['y'])
                rim = (d >= q['drill'] / 2) & (d <= q['drill'] / 2 + 1.5 * h) & self.mask[L][sj, si]
                for pid in idx[L][sj, si][rim]:
                    union(nid, int(pid))
            bnode[q['name']] = ids
            if q['name'] in ideal or q['kind'] == 'ideal':
                for a, c in zip(ids, ids[1:]): union(a, c)
            else:
                for li in range(3):
                    link(ids[li], ids[li + 1], 1.0 / barrel_R(q['drill'], DZ[li]))
        def term_nodes(t):
            if t[0] == 'pin':
                ids = bnode[t[1]]
                for a, c in zip(ids, ids[1:]): union(a, c)
                return ids[0]
            _, ref, pn, L = t
            p = [q for q in self.b['fps'][ref]['pads'] if q['n'] == pn][0]
            m = (np.abs(self.X - p['x']) <= p['sx'] / 2) & (np.abs(self.Y - p['y']) <= p['sy'] / 2) & self.mask[L]
            ids = idx[L][m]
            for a in ids[1:]: union(int(ids[0]), int(a))
            return int(ids[0])
        src = [term_nodes(t) for t in sources]
        snk = [term_nodes(t) for t in sinks]
        for a in src[1:]: union(src[0], a)
        if mode == 'equipotential':
            for a in snk[1:]: union(snk[0], a)
        for L in LAYERS:
            g = T[L] / RHO
            a = idx[L]
            m = (a[:, :-1] >= 0) & (a[:, 1:] >= 0)
            p, q2 = a[:, :-1][m], a[:, 1:][m]
            rows.extend([p, q2, p, q2]); cols.extend([p, q2, q2, p]); vals.extend([np.full(p.size, g), np.full(p.size, g), np.full(p.size, -g), np.full(p.size, -g)])
            m = (a[:-1, :] >= 0) & (a[1:, :] >= 0)
            p, q2 = a[:-1, :][m], a[1:, :][m]
            rows.extend([p, q2, p, q2]); cols.extend([p, q2, q2, p]); vals.extend([np.full(p.size, g), np.full(p.size, g), np.full(p.size, -g), np.full(p.size, -g)])
        rows = np.concatenate([np.atleast_1d(np.asarray(r, np.int64)) for r in rows]); cols = np.concatenate([np.atleast_1d(np.asarray(c, np.int64)) for c in cols])
        vals = np.concatenate([np.atleast_1d(np.asarray(v, float)) for v in vals])
        root = np.array([find(i) for i in range(n)])
        uniq, comp = np.unique(root, return_inverse=True)
        N = uniq.size
        G = sp.coo_matrix((vals, (comp[rows], comp[cols])), shape=(N, N)).tocsr()
        G.setdiag(G.diagonal())
        ncomp, lab = connected_components(G, directed=False)
        s = comp[find(src[0])]
        keep = np.where(lab == lab[s])[0]
        snk_c = [comp[find(a)] for a in snk]
        for a in snk_c:
            if lab[a] != lab[s]: raise RuntimeError('a sink is not connected to the source through this net')
        remap = -np.ones(N, np.int64); remap[keep] = np.arange(keep.size)
        Gk = G[keep][:, keep].tocsr()
        s_k = remap[s]; snk_k = [remap[a] for a in snk_c]
        rhs = np.zeros(keep.size)
        if mode == 'equipotential':
            rhs[snk_k[0]] -= I
        else:
            for a in snk_k: rhs[a] -= I / len(snk_k)
        free = np.ones(keep.size, bool); free[s_k] = False          # source at 0 V
        Gf = Gk[free][:, free].tocsc()
        v = np.zeros(keep.size); v[free] = spla.spsolve(Gf, rhs[free])
        vs = [-v[a] for a in snk_k]
        self.last = dict(v=v, remap=remap, comp=comp, idx=idx, find=find, bnode=bnode)
        if verbose: print('   unknowns', keep.size, 'components', ncomp)
        return (sum(vs) / len(vs)) / I, [x / I for x in vs]

    def node_v(self, name):
        L = self.last
        return -L['v'][L['remap'][L['comp'][L['find'](L['bnode'][name][0])]]]
