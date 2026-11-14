# Print audit re-check, follow-up 2026-11-14: Daniel's split of the front shell into a screen plate and the rest of the shell.
# Read-only study on the exported mesh (front.stl, version 63, world mm). The split is approximated: everything in front of the
# screen wall's inner face (depth d 14.8 behind the glass plane) above z 47.5 is the plate; the rest is the shell.
# Support estimate: faces whose normal points toward the plate more than 45 deg from vertical and that sit more than 0.3 above
# it (not a slice). The cut faces themselves are not in the mesh, so 'on the plate' is 0 for pieces that lie on the cut.
import math, numpy as np, trimesh
C, S, H = math.cos(math.radians(12)), math.sin(math.radians(12)), 143.3
E = '/mnt/user-data/uploads/print_audit_recheck/exports/'
m = trimesh.load(E + 'front.stl')
n = np.array([0, C, S])                                  # the screen's normal (toward the viewer, 12 deg up)
gd = lambda d: H * S - d                                 # a plane at depth d behind the glass plane: y*C + z*S = gd(d)
depth = lambda y, z: H * S - (y * C + z * S)
gcut = gd(14.8)
cen = m.triangles_center; A = m.area_faces; N = m.face_normals; V = m.vertices
plate = ((cen @ n) > gcut) & (cen[:, 2] > 47.5)
rest = ~plate

print('1. The chin against the screen plane (section x = 0): front-most y and its depth behind the glass plane')
sec = m.section(plane_origin=[0, 0, 0], plane_normal=[1, 0, 0])
P = np.vstack([sec.vertices[e.points] for e in sec.entities])
for z0, z1 in ((2.8, 10), (10, 20), (20, 30), (30, 40), (40, 48), (48, 54), (60, 100), (100, 150), (150, 180)):
    k = (P[:, 2] >= z0) & (P[:, 2] < z1)
    if k.any():
        gg = P[k] @ n
        print('   z %5.1f-%5.1f: front-most y %6.2f, depth d %5.2f' % (z0, z1, P[k, 1].max(), H * S - gg.max()))

chin = rest & (N[:, 1] > 0.99) & (cen[:, 2] < 48.5) & (cen[:, 1] > 6.0)
print('2. Chin cloth face: %.0f mm2, y %.2f-%.2f, x %.1f..%.1f, z %.1f..%.1f' % (A[chin].sum(), cen[chin, 1].min(), cen[chin, 1].max(),
      cen[chin, 0].min(), cen[chin, 0].max(), cen[chin, 2].min(), cen[chin, 2].max()))


def study(label, U, mask):
    U = np.asarray(U, float); U /= np.linalg.norm(U)
    vv = V[np.unique(m.faces[mask].ravel())] @ U
    lo, hi = vv.min(), vv.max()
    hgt = cen @ U - lo
    bed = mask & (N @ U < -0.99) & (hgt < 0.05)
    need = mask & (N @ U < -math.sin(math.radians(45))) & (hgt > 0.3)
    inner = need & (N[:, 0] * np.sign(cen[:, 0]) < 0)
    print('   %-40s height %5.1f | on the plate %6.0f mm2 | needs support %6.0f mm2, >30 up %6.0f, facing the centre %6.0f' % (
        label, hi - lo, A[bed].sum(), A[need].sum(), A[need & (hgt > 30)].sum(), A[inner].sum()))


print('3. Orientations')
study('whole shell, bottom edge down (as now)', (0, 0, 1), np.ones(len(A), bool))
study('rest of shell, bottom edge down', (0, 0, 1), rest)
study('rest of shell, chin face down', (0, -1, 0), rest)
study('rest of shell, top down', (0, 0, -1), rest)
study('screen plate, inside face down', n, plate)

print('4. Box-top bosses: material along the insert axis line at z 80')
for xb in (58.55, -58.61):
    pts = np.array([[xb, y, 80.0] for y in np.arange(-12, 4, 0.25)])
    ys = pts[m.contains(pts), 1]
    print('   x %.2f: material y %.2f..%.2f; screen wall at z 80: inner face y %.2f, outer face y %.2f' % (
        xb, ys.min(), ys.max(), (gcut - 80 * S) / C, (gd(12.3) - 80 * S) / C))
for p in ((47.5, 0.3, 80.6), (47.5, -13.9, 147.1)):
    print('   LCD screw head (K5) at %s: depth d %.2f' % (p, depth(p[1], p[2])))
