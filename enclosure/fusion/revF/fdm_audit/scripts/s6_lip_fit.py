"""Block 6, after Daniel's answer 1a (lip 2.0, grown inward by 0.8): what stands in front of the lip's inner faces now.
1 sections through the lip and the left box (picture); 2 the gap along world y between each box's back and the shell behind it,
by height; 3 nearest printed part in front of an inner-facing face of the lip zone (point samples 0.4 apart, so +-0.3).
Printed bodies only: leads, boards and bought parts are not in the audit's meshes."""
import numpy as np, trimesh
from scipy.spatial import cKDTree
from shapely.geometry import LineString
from shapely.ops import unary_union
from sec import section_polys
from secm import panels
from fdm_lib import *

rng = np.random.default_rng(1)


def picture(out):
    P = ['HOUSING_F_front', 'SPKBOX_L', 'HOUSING_F_door', 'FLOOR_PLATE']
    panels(out, [dict(axis='z', value=z, win=(52, 96, -68, -46), parts=P, title='horizontal cut', grid=2.0) for z in (6.0, 15.0, 30.0, 60.0)] +
           [dict(axis='x', value=x, win=(-68, -46, 0, 22), parts=P, title='vertical cut', grid=2.0) for x in (79.4, 70.0)], ncol=3, size=5.2)


def y_gap(box_name, sign):
    xs = np.arange(53.0, 81.01, 0.25) * sign
    for z in (7.0, 10.0, 15.0, 22.0, 30.0, 45.0, 60.0, 75.0):
        S = unary_union(section_polys('HOUSING_F_front', 'z', z)); B = unary_union(section_polys(box_name, 'z', z))
        best = None
        for x in xs:
            ln = LineString([(x, -70), (x, -40)]); b = B.intersection(ln); s = S.intersection(ln)
            if b.is_empty or s.is_empty: continue
            yb = b.bounds[1]
            ys = [g.bounds[3] for g in (s.geoms if hasattr(s, 'geoms') else [s]) if g.bounds[3] <= yb + 1e-6]
            if ys and (best is None or yb - max(ys) < best[0]): best = (yb - max(ys), x, max(ys))
        print('  %s z %5.1f: smallest gap along y %.2f at x %.2f; the shell face there is at y %.2f' % (box_name, z, best[0], best[1], best[2]))


def samp(mw, fsel, spacing=0.4):
    tri = mw.triangles[fsel]; ar = mw.area_faces[fsel]; n = int(ar.sum() / spacing ** 2) + 1
    idx = rng.choice(len(tri), n, p=ar / ar.sum()); r1 = np.sqrt(rng.random(n)); r2 = rng.random(n)
    return (1 - r1)[:, None] * tri[idx, 0] + (r1 * (1 - r2))[:, None] * tri[idx, 1] + (r1 * r2)[:, None] * tri[idx, 2], idx


def nearest():
    sh = load_model_mesh('HOUSING_F_front'); shw = trimesh.Trimesh(vertices=to_world(sh.vertices), faces=sh.faces, process=False)
    cen = shw.triangles_center; nrm = shw.face_normals
    inner = np.where((cen[:, 1] < -53.6) & (cen[:, 1] > -63.7) & (nrm[:, 1] > 0.25))[0]
    L, li = samp(shw, inner); fn = nrm[inner][li]
    print('  inner-facing faces of the lip zone: %.0f mm2, %d samples' % (shw.area_faces[inner].sum(), len(L)))
    for name in ('SPKBOX_L', 'SPKBOX_R', 'FLOOR_PLATE', 'CRADLE_5807', 'HOUSING_F_cap', 'GROMMET_usbc_F', 'BME_HOOD'):
        m = load_model_mesh(name); mw = trimesh.Trimesh(vertices=to_world(m.vertices), faces=m.faces, process=False)
        fs = np.where(mw.triangles_center[:, 1] < -42)[0]
        P, _ = samp(mw, fs); d, j = cKDTree(P).query(L)
        ok = ((P[j] - L) * fn).sum(1) > 0.2
        k = np.where(ok)[0][np.argmin(d[ok])]
        print('  %-15s nearest %.2f: lip %s, part %s' % (name, d[k], L[k].round(1).tolist(), P[j[k]].round(1).tolist()))


if __name__ == '__main__':
    picture(os.path.join(os.path.dirname(DATA), 'img', 's_lip_boxes.png'))
    print('2 gap along y between the box backs and the shell'); y_gap('SPKBOX_L', 1); y_gap('SPKBOX_R', -1)
    print('3 nearest printed part in front of the lip\'s inner faces'); nearest()
