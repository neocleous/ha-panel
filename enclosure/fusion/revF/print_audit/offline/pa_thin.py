# HA panel print audit: P5 thin features and narrow gaps on the stored layer stacks (M_<tag>_<orient>.npz).
#   thin(w) = layer - opening(layer, w/2), w = 0.84 (two 0.42 lines); each thin region's width = 2 x max inscribed distance,
#   refined on a 0.01 mm raster of the same section (re-sliced) for regions under 0.84. Gaps = closing(layer, 0.2) - layer
#   (in-layer slits under 0.4). Usage: python3 pa_thin.py <tag> <orient> [step]
import sys, json, math, numpy as np
sys.path.insert(0, '/home/claude/pa')
from pa_geom import *
from pa_summ import wbox
from scipy import ndimage as ndi
S8 = np.ones((3, 3), bool)


def run(tag, okey, step=None):
    z = np.load('/home/claude/pa/work/M_%s_%s.npz' % (tag, okey))
    Hh, W = [int(v) for v in z['shape']]; x0, y0, px = [float(v) for v in z['grid']]; zs = z['zs']; M = z['M']
    packed = z['packed']
    n = len(zs)
    if step is None:
        step = 1 if n <= 150 else (2 if n <= 450 else 4)
    mw = load_world(tag); U = ORIENT[tag][okey]
    mb, M2 = to_build(mw, U); sl = Slicer(mb)
    thin = []; gaps = []
    for k in range(0, n, step):
        m = np.unpackbits(packed[k])[:Hh * W].reshape(Hh, W).astype(bool)
        if not m.any():
            continue
        ein = ndi.distance_transform_edt(m) * px
        er = ein > 0.42
        opened = (ndi.distance_transform_edt(~er) * px <= 0.42) if er.any() else np.zeros_like(m)
        th = m & ~opened
        lab, nl = ndi.label(th, S8)
        if nl:
            objs = ndi.find_objects(lab)
            for i in range(nl):
                s_ = objs[i]; R = lab[s_] == i + 1
                a = R.sum() * px * px
                if a < max(0.05, 4 * px * px):
                    continue
                w_est = 2 * float(ein[s_][R].max())
                jj, ii = np.nonzero(R); jj = jj + s_[0].start; ii = ii + s_[1].start
                xb, yb = px2b(jj, ii, x0, y0, px)
                thin.append({'k': k, 'z': round(float(zs[k]), 2), 'area': round(float(a), 3), 'w_est': round(w_est, 3),
                             'bbox': [round(float(xb.min()), 2), round(float(xb.max()), 2), round(float(yb.min()), 2), round(float(yb.max()), 2)]})
        # narrow gaps (< 0.4) inside the layer
        dil = ndi.distance_transform_edt(~m) * px <= 0.2
        closed = ndi.distance_transform_edt(dil) * px > 0.2
        gp = closed & ~m
        glab, ng = ndi.label(gp, S8)
        if ng:
            gobjs = ndi.find_objects(glab)
            for i in range(ng):
                s_ = gobjs[i]; R = glab[s_] == i + 1
                a = R.sum() * px * px
                if a < max(0.05, 4 * px * px):
                    continue
                jj, ii = np.nonzero(R); jj = jj + s_[0].start; ii = ii + s_[1].start
                xb, yb = px2b(jj, ii, x0, y0, px)
                gaps.append({'k': k, 'z': round(float(zs[k]), 2), 'area': round(float(a), 3),
                             'bbox': [round(float(xb.min()), 2), round(float(xb.max()), 2), round(float(yb.min()), 2), round(float(yb.max()), 2)]})
    # refine widths on a 0.01 mm raster for regions with w_est < 0.84 (one section per region)
    for t in thin:
        if t['w_est'] >= 0.84:
            continue
        b = t['bbox']; fx0, fy0 = b[0] - 0.6, b[2] - 0.6
        fW = int(math.ceil((b[1] - b[0] + 1.2) / 0.01)); fH = int(math.ceil((b[3] - b[2] + 1.2) / 0.01))
        if fW * fH > 4e7:
            continue
        seg = sl.segments(float(zs[t['k']]) + EPS)
        sel = ((seg[:, :, 0].max(1) >= fx0 - 1) & (seg[:, :, 0].min(1) <= fx0 + fW * 0.01 + 1))
        fm = raster(seg[sel], fx0, fy0, 0.01, fW, fH) if sel.any() else None
        if fm is None or not fm.any():
            continue
        fe = ndi.distance_transform_edt(fm) * 0.01
        er = fe > 0.42
        op = (ndi.distance_transform_edt(~er) * 0.01 <= 0.42) if er.any() else np.zeros_like(fm)
        th = fm & ~op
        # ignore the 0.6 mm border band of the crop (neighbouring geometry cut by the crop edge)
        th[:60, :] = False; th[-60:, :] = False; th[:, :60] = False; th[:, -60:] = False
        if th.any():
            t['w_fine'] = round(2 * float(fe[th].max()), 3)
            t['w_fine_p10'] = round(2 * float(np.percentile(fe[th], 90)), 3)
    out = {'tag': tag, 'orient': okey, 'step': step, 'px': px, 'thin': thin, 'gaps': gaps}
    # clusters across sampled layers
    from pa_summ import clusters
    for key in ('thin', 'gaps'):
        rr = [dict(r, k=r['k'] // step) for r in out[key]]
        cl = []
        for c in clusters(rr, slack=0.2):
            A = sum(r['area'] for r in c)
            z0 = min(r['z'] for r in c); z1 = max(r['z'] for r in c)
            bb = [min(r['bbox'][0] for r in c), max(r['bbox'][1] for r in c), min(r['bbox'][2] for r in c), max(r['bbox'][3] for r in c)]
            e = {'z': [round(z0 - 0.1, 2), round(z1 + 0.1, 2)], 'n': len(c), 'area_sum': round(A, 2), 'world': wbox(M, bb, z0 - 0.1, z1 + 0.1)}
            if key == 'thin':
                e['w_est_min'] = min(r['w_est'] for r in c)
                wf = [r['w_fine'] for r in c if 'w_fine' in r]
                e['w_fine_min'] = min(wf) if wf else None
                e['w_fine_max'] = max(wf) if wf else None
            cl.append(e)
        cl.sort(key=lambda e: (e.get('w_fine_min') if e.get('w_fine_min') is not None else 9, -e['area_sum']))
        out[key + '_clusters'] = cl
    json.dump(out, open('/home/claude/pa/data/T_%s_%s.json' % (tag, okey), 'w'))
    print('==', tag, okey, 'step', step, 'thin clusters', len(out['thin_clusters']), 'gap clusters', len(out['gaps_clusters']))
    for e in out['thin_clusters'][:25]:
        print('  THIN', e)
    for e in out['gaps_clusters'][:12]:
        print('  GAP ', e)
    return out


if __name__ == '__main__':
    tag, okey = sys.argv[1], sys.argv[2]
    step = int(sys.argv[3]) if len(sys.argv) > 3 else None
    run(tag, okey, step)
