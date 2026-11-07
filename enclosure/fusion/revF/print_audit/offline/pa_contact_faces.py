# HA panel print audit (P4): which faces the slicer's support touches. Reads data/C_<gcode>.json cells is not stored, so
#   this re-runs the contact pass and, for every contact cell (world point), finds the nearest mesh face and its world
#   normal. Output: contact area grouped by normal direction (rounded to 0.1) with world boxes.
import sys, json, numpy as np
sys.path.insert(0, '/home/claude/pa')
import trimesh
gtag, otag, okey = sys.argv[1], sys.argv[2], sys.argv[3]
src = open('/home/claude/pa/pa_contacts.py').read().split("out = {'gcode'")[0]
sys.argv = ['x', gtag, otag, okey]
G2 = {}
exec(src, G2)
cells = G2['cells']; M = G2['M']; b2w = G2['b2w']; mw = G2['mw']
cells = np.array(cells)
w = b2w(M, np.c_[cells[:, 1], cells[:, 2], cells[:, 0] - 0.1])
# nearest face: k nearest triangle centroids, then exact point-triangle distance among them (memory-light on big meshes)
from scipy.spatial import cKDTree
cen = mw.triangles_center; kd = cKDTree(cen)
K = 16
_, cand = kd.query(w, k=K)
best = np.full(len(w), np.inf); tri = np.zeros(len(w), int)
for j in range(K):
    t = cand[:, j]
    cpj = trimesh.triangles.closest_point(mw.triangles[t], w)
    dj = np.linalg.norm(cpj - w, axis=1)
    better = dj < best
    best[better] = dj[better]; tri[better] = t[better]
dist = best
nrm = mw.face_normals[tri]
np.savez_compressed('/home/claude/pa/work/CF_%s.npz' % gtag, cells=cells, world=w, nrm=nrm, dist=dist)
key = [tuple(np.round(n, 1)) for n in nrm]
groups = {}
for k, p, d in zip(key, w, dist):
    g = groups.setdefault(k, {'n': 0, 'pts': []}); g['n'] += 1; g['pts'].append(p)
out = []
for k, g in sorted(groups.items(), key=lambda kv: -kv[1]['n']):
    P = np.array(g['pts'])
    out.append({'normal': [float(v) for v in k], 'area_mm2': round(g['n'] * 0.0625, 1),
                'world_min': [round(float(v), 1) for v in P.min(0)], 'world_max': [round(float(v), 1) for v in P.max(0)]})
json.dump({'gcode': gtag, 'groups': out, 'median_dist_mm': round(float(np.median(dist)), 2)}, open('/home/claude/pa/data/CF_%s.json' % gtag, 'w'), indent=1)
print(gtag, 'cells', len(cells), 'median dist to surface %.2f' % np.median(dist))
for o in out[:12]:
    print('  n %-18s a %6.1f  x %6.1f..%6.1f y %6.1f..%6.1f z %6.1f..%6.1f' % (o['normal'], o['area_mm2'], o['world_min'][0], o['world_max'][0], o['world_min'][1], o['world_max'][1], o['world_min'][2], o['world_max'][2]))
