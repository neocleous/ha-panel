# recheck (block 2): where support goes and what it touches, from a parsed G-code (gparse.py npz).
#   Usage: python3 gsupport.py <job.npz> <M_world_to_bed as JSON 4x4 or orient json path> <out.json> [cell=1.0]
#   Rasterises extrusion per layer on a cell grid (bed XY). Contact cells: support (incl. interface) in layer L whose cell holds
#   object extrusion (any non-support feature) in one of the next 3 layers. Contacts are grouped in 3-D (26-connectivity over
#   cells x layers) and reported in world coordinates with their area (cells x cell^2), z range, the features they touch and
#   whether the touched extrusion is an outer wall / overhang wall / bridge / bottom surface.
import sys, json, math
import numpy as np
from scipy import ndimage

A = math.pi * 0.875 ** 2


def load(p):
    d = np.load(p, allow_pickle=False)
    return d['seg'], d['feat'], [str(s) for s in d['names']], d['layers']


def raster(seg, cell, x0, y0, nx, ny):
    # sample each segment every cell/2 and mark cells
    out = []
    for s in seg:
        L = math.hypot(s[2] - s[0], s[3] - s[1]); n = max(2, int(L / (cell * 0.5)) + 1)
        t = np.linspace(0, 1, n)
        xs = s[0] + (s[2] - s[0]) * t; ys = s[1] + (s[3] - s[1]) * t
        ix = ((xs - x0) / cell).astype(int); iy = ((ys - y0) / cell).astype(int)
        out.append(np.stack([ix, iy], 1))
    return np.unique(np.concatenate(out), axis=0) if out else np.zeros((0, 2), int)


def main():
    seg, feat, names, layers = load(sys.argv[1])
    mj = sys.argv[2]
    M = np.array(json.load(open(mj))['M_world_to_bed'] if mj.endswith('.json') else json.loads(mj), float)
    Minv = np.linalg.inv(M)
    cell = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
    sup_ids = [i for i, n in enumerate(names) if n.startswith('Support')]
    obj_ids = [i for i, n in enumerate(names) if not n.startswith('Support') and n not in ('Brim', 'Custom', 'Skirt', 'Prime tower')]
    issup = np.isin(feat, sup_ids); isobj = np.isin(feat, obj_ids)
    if not issup.any():
        json.dump({'support': None}, open(sys.argv[3], 'w')); print('no support'); return
    x0 = float(min(seg[:, 0].min(), seg[:, 2].min())) - 2; y0 = float(min(seg[:, 1].min(), seg[:, 3].min())) - 2
    nx = int((max(seg[:, 0].max(), seg[:, 2].max()) - x0) / cell) + 4; ny = int((max(seg[:, 1].max(), seg[:, 3].max()) - y0) / cell) + 4
    nL = len(layers)
    li = seg[:, 7].astype(int)
    S = np.zeros((nL, nx, ny), bool); O = np.zeros((nL, nx, ny), np.uint8)   # O: 0 none, else feature id + 1 of last writer
    for L in np.unique(li[issup]):
        c = raster(seg[(li == L) & issup], cell, x0, y0, nx, ny)
        S[L, c[:, 0], c[:, 1]] = True
    # object features per layer with a priority so that the most telling feature wins in a cell
    pri = {n: k for k, n in enumerate(['Sparse infill', 'Internal solid infill', 'Gap infill', 'Inner wall', 'Floating vertical shell',
                                        'Top surface', 'Outer wall', 'Bottom surface', 'Overhang wall', 'Bridge'])}
    order = sorted(obj_ids, key=lambda i: pri.get(names[i], -1))
    Lsup = np.unique(li[issup]); need = set()
    for L in Lsup:
        for k in (1, 2, 3):
            if L + k < nL:
                need.add(L + k)
    for L in sorted(need):
        m = li == L
        for i in order:
            mm = m & (feat == i)
            if mm.any():
                c = raster(seg[mm], cell, x0, y0, nx, ny)
                O[L, c[:, 0], c[:, 1]] = i + 1
    C = np.zeros_like(S); T = np.zeros((nL, nx, ny), np.uint8)
    for L in Lsup:
        for k in (1, 2, 3):
            if L + k < nL:
                hit = S[L] & (O[L + k] > 0) & ~C[L]
                T[L][hit] = O[L + k][hit]; C[L] |= hit
    lab, n = ndimage.label(C, structure=np.ones((3, 3, 3)))
    cl = []
    objs = ndimage.find_objects(lab)
    for k, sl in enumerate(objs):
        m = lab[sl] == (k + 1)
        Ls, ix, iy = np.nonzero(m)
        Ls = Ls + sl[0].start; ix = ix + sl[1].start; iy = iy + sl[2].start
        bx = x0 + (ix + 0.5) * cell; by = y0 + (iy + 0.5) * cell; bz = layers[Ls] + 0.2
        P = np.stack([bx, by, bz, np.ones_like(bx)], 1) @ Minv.T
        tf = T[Ls, ix, iy]
        tcount = {}
        for v in tf:
            nm = names[int(v) - 1]; tcount[nm] = tcount.get(nm, 0) + 1
        cl.append({'n_cells': int(len(ix)), 'area_mm2': round(len(ix) * cell * cell, 1),
                   'bed_z': [round(float(bz.min()), 2), round(float(bz.max()), 2)],
                   'world': [round(float(P[:, j].min()), 1) for j in range(3)] + [round(float(P[:, j].max()), 1) for j in range(3)],
                   'touches': dict(sorted(tcount.items(), key=lambda kv: -kv[1]))})
    cl.sort(key=lambda c: -c['n_cells'])
    # support volume by z band (bed z) and footprint
    sv = seg[issup]; vz = {}
    for s, e in zip(sv[:, 4], sv[:, 5]):
        b = int(s // 10) * 10; vz[b] = vz.get(b, 0.0) + float(e) * A
    out = {'cell': cell, 'support_mm3': round(float(seg[issup, 5].sum() * A), 1),
           'support_layers': [round(float(layers[Lsup.min()]), 2), round(float(layers[Lsup.max()]), 2)],
           'support_vol_by_bed_z10': {int(k): round(v, 1) for k, v in sorted(vz.items())},
           'n_contact_clusters': len(cl), 'clusters': cl}
    json.dump(out, open(sys.argv[3], 'w'), indent=0)
    print(json.dumps({k: out[k] for k in ('support_mm3', 'support_layers', 'support_vol_by_bed_z10', 'n_contact_clusters')}))
    for c in cl[:40]:
        print(json.dumps(c))


if __name__ == '__main__':
    main()
