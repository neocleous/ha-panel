"""F6 candidates (world mm, x_rel): web between each side pad's strip and the back pad's outboard rib, and a front rib from the
slab-boss plate's back face under the side pad's inboard-front edge (46 deg underside). Writes STLs (SR and SL mirrored)."""
import numpy as np, sys, json
from scipy.spatial import ConvexHull
TAN46 = np.tan(np.radians(46.0))
ZTOP = float(sys.argv[1]) if len(sys.argv) > 1 else 172.5      # pad top in the mesh (d19 STL 172.5; model 172.6)


def plate_y(z):                                               # slab-boss plate back face (n (0, -0.9781, -0.2079))
    return -22.232 + (176.708 - z) * 0.21255


def web_sr():
    P = lambda y: np.array([-38.165 + (-31.043 - y) * (4.855 / 13.957), y])      # SR strip inboard face
    Q = lambda y: np.array([-31.906 + (-32.845 - y) * (1.724 / 18.138), y])      # BR outboard rib, outboard face
    nP = np.array([-0.9445, -0.3286]); nQ = np.array([0.9955, 0.0946])
    pts2 = [P(-32.7) + 0.5 * nP, Q(-32.7) + 0.5 * nQ, Q(-44.6) + 0.5 * nQ, P(-44.6) + 0.5 * nP]
    return np.array([[p[0], p[1], z] for p in pts2 for z in (169.5, ZTOP)])


def frib_sr(x0=-40.0, x1=-38.2, yb=-33.0):
    d = (plate_y(169.5) - yb) * TAN46 / (1 - 0.21255 * TAN46)                 # underside meets the plate
    yl = yb + d / TAN46 + 0.5; zl = 169.5 - (yl - yb) * TAN46                     # 0.5 past the plate face
    yz = [(yb, 169.5), (yb, 170.0), (plate_y(170.0) + 0.5, 170.0), (yl, zl)]
    return np.array([[x, y, z] for x in (x0, x1) for (y, z) in yz]), round(169.5 - d, 2)


def stl(pts, path):
    h = ConvexHull(pts); c = pts.mean(0)
    with open(path, 'w') as f:
        f.write('solid s\n')
        for s in h.simplices:
            a, b, cc = pts[s]
            n = np.cross(b - a, cc - a)
            if np.dot(n, a - c) < 0:
                b, cc = cc, b; n = -n
            n = n / np.linalg.norm(n)
            f.write('facet normal %g %g %g\n outer loop\n' % tuple(n))
            for v in (a, b, cc):
                f.write('  vertex %.5f %.5f %.5f\n' % tuple(v))
            f.write(' endloop\nendfacet\n')
        f.write('endsolid s\n')
    return h.volume


mir = lambda p: p * np.array([-1.0, 1.0, 1.0])
W = web_sr(); R, zlow = frib_sr()
vol = {}
for tag, p in (('web_SR', W), ('web_SL', mir(W)), ('frib_SR', R), ('frib_SL', mir(R))):
    vol[tag] = round(stl(p, 'cand_%s.stl' % tag), 1)
print(json.dumps({'vol_mm3': vol, 'frib_z_low': zlow}))
