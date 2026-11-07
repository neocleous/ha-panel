# HA panel print audit (2026-11-07): per-layer analysis of one print in one orientation (P2 islands, P3 overhangs and
#   bridges, P4 support landing, P7 first layer). Usage: python3 pa_layers.py <tag> <orient-key> <px_mm> [spin_deg]
#   Writes /home/claude/pa/data/L_<tag>_<orient>.json and the packed layer stack /home/claude/pa/work/M_<tag>_<orient>.npz.
import sys, json, time, math, numpy as np
sys.path.insert(0, '/home/claude/pa')
from pa_geom import *
from scipy import ndimage as ndi

TAN = {45: math.tan(math.radians(45)), 60: math.tan(math.radians(60)), 70: math.tan(math.radians(70))}
AMIN = 0.05            # mm2, smallest unsupported region kept
S8 = np.ones((3, 3), bool)


def comp_stats(lab, idx, sl_, px, x0, y0):
    """bbox (build mm) and centroid of label idx inside slice sl_."""
    sub = lab[sl_] == idx
    jj, ii = np.nonzero(sub)
    jj = jj + sl_[0].start; ii = ii + sl_[1].start
    xb, yb = px2b(jj, ii, x0, y0, px)
    return [float(xb.min()), float(xb.max()), float(yb.min()), float(yb.max())], [float(xb.mean()), float(yb.mean())], len(jj)


def run(tag, okey, px, spin=0.0, U=None):
    t0 = time.time()
    mw = load_world(tag)
    if U is None:
        U = ORIENT[tag][okey]
    mb, M = to_build(mw, U, spin)
    sl = Slicer(mb); x0, y0, W, Hh = grid_for(mb, px)
    zs = layer_mids(mb.extents[2])
    out = {'tag': tag, 'orient': okey, 'U': [float(u) for u in U], 'spin': spin, 'px': px, 'M': M.tolist(),
           'grid': [x0, y0, W, Hh], 'n_layers': len(zs), 'height': float(mb.extents[2]),
           'overhang_normals': overhang_stats(mb), 'footprint': footprint(mb)}
    prev = None
    hm = np.zeros((Hh, W), np.float32)        # top z of the last material at each pixel (0 = bed)
    ever = np.zeros((Hh, W), bool)
    packed = []; layers = []; islands = []; regions = []
    pa = px * px
    for k, z in enumerate(zs):
        m = raster(sl.segments(z + EPS), x0, y0, px, W, Hh)
        packed.append(np.packbits(m))
        L = {'k': k, 'z': round(float(z), 3), 'area': round(float(m.sum() * pa), 3)}
        if k == 0:
            out['first_layer_area'] = L['area']
        elif m.any():
            dprev = ndi.distance_transform_edt(~prev) * px if prev.any() else np.full(m.shape, 1e9)
            for a in (45, 60, 70):
                L['u%d' % a] = round(float((m & (dprev > LAYER_H * TAN[a])).sum() * pa), 3)
            lab, n = ndi.label(m, S8)
            if n:
                ov = ndi.sum(prev, lab, index=np.arange(1, n + 1))
                ar = ndi.sum(np.ones_like(m), lab, index=np.arange(1, n + 1))
                objs = ndi.find_objects(lab)
                for i in range(n):
                    if ar[i] * pa < 0.01:
                        continue
                    weak = ov[i] > 0 and (ov[i] * pa < 0.05 or ov[i] / ar[i] < 0.02)
                    if ov[i] == 0 or weak:
                        bb, cen, npx = comp_stats(lab, i + 1, objs[i], px, x0, y0)
                        sub = lab[objs[i]] == i + 1
                        land = hm[objs[i]][sub]; onbed = ~ever[objs[i]][sub]
                        islands.append({'k': k, 'z0': round(layer_top(k) - (FIRST_H if k == 0 else LAYER_H), 3),
                                        'area': round(float(ar[i] * pa), 3), 'overlap_mm2': round(float(ov[i] * pa), 3),
                                        'weak': bool(weak), 'bbox': [round(v, 2) for v in bb], 'c': [round(v, 2) for v in cen],
                                        'land_max': round(float(land.max()), 2), 'land_min': round(float(land.min()), 2),
                                        'bed_frac': round(float(onbed.mean()), 3)})
            u = m & (dprev > LAYER_H * TAN[60])
            if u.any():
                ulab, un = ndi.label(u, S8)
                uobjs = ndi.find_objects(ulab)
                sup = m & ~u
                for i in range(un):
                    s_ = uobjs[i]
                    # pad the crop by 3 px for anchor tests
                    j0, j1 = max(s_[0].start - 3, 0), min(s_[0].stop + 3, Hh)
                    i0, i1 = max(s_[1].start - 3, 0), min(s_[1].stop + 3, W)
                    R = ulab[j0:j1, i0:i1] == i + 1
                    a_ = R.sum() * pa
                    if a_ < AMIN:
                        continue
                    S = sup[j0:j1, i0:i1]
                    anc = R & ndi.binary_dilation(S, S8)
                    if anc.any():
                        alab, an = ndi.label(ndi.binary_dilation(anc, S8, iterations=2) & R, S8)
                        d = ndi.distance_transform_edt(~anc) * px
                        dmax = float(d[R].max())
                    else:
                        an, dmax = 0, None
                    bnd = R & ~ndi.binary_erosion(R, S8)
                    afrac = float(anc.sum() / max(bnd.sum(), 1))
                    win = float(ndi.distance_transform_edt(R).max() * px * 2)
                    if an == 0:
                        kind = 'island'
                    elif an >= 2 or afrac >= 0.6:
                        kind = 'bridge'
                    else:
                        kind = 'cantilever'
                    jj, ii = np.nonzero(R); jj = jj + j0; ii = ii + i0
                    xb, yb = px2b(jj, ii, x0, y0, px)
                    land = hm[jj, ii]; onbed = ~ever[jj, ii]
                    regions.append({'k': k, 'z': round(float(layer_top(k) - LAYER_H), 3), 'area': round(float(a_), 3), 'kind': kind,
                                    'n_anchor': int(an), 'anchor_frac': round(afrac, 2), 'dmax': None if dmax is None else round(dmax, 2),
                                    'width': round(win, 2),
                                    'bbox': [round(float(xb.min()), 2), round(float(xb.max()), 2), round(float(yb.min()), 2), round(float(yb.max()), 2)],
                                    'c': [round(float(xb.mean()), 2), round(float(yb.mean()), 2)],
                                    'land_max': round(float(land.max()), 2), 'land_min': round(float(land.min()), 2),
                                    'land_med': round(float(np.median(land)), 2), 'bed_frac': round(float(onbed.mean()), 3)})
        hm[m] = layer_top(k); ever |= m
        layers.append(L)
        prev = m
    out['layers'] = layers; out['islands'] = islands; out['regions'] = regions
    out['t_s'] = round(time.time() - t0, 1)
    sfx = '%s_%s' % (tag, okey) + ('' if not spin else '_s%d' % spin)
    json.dump(out, open('/home/claude/pa/data/L_%s.json' % sfx, 'w'))
    np.savez_compressed('/home/claude/pa/work/M_%s.npz' % sfx, packed=np.array(packed), shape=np.array([Hh, W]),
                        grid=np.array([x0, y0, px]), zs=zs, M=M)
    print(tag, okey, 'layers', len(zs), 'islands', len(islands), 'regions', len(regions), 't', out['t_s'], flush=True)
    return out


if __name__ == '__main__':
    tag, okey, px = sys.argv[1], sys.argv[2], float(sys.argv[3])
    spin = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
    run(tag, okey, px, spin)
