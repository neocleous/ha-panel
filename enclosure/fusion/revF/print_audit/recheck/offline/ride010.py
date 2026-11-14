# recheck point 5: where the ride-in's nearest pair (lead parts vs shell, 0.08 at 10 out) lies.
#   Lead parts = lead body inside the board-frame box LOW (u -60..60, v -32.9..36, w -14..-1; aud4_lib LEADPART), moved
#   along the slab normal (0, cos12, sin12) by s; nearest shell point by trimesh closest-point queries on dense samples.
import numpy as np, trimesh, json
E = '/mnt/user-data/uploads/print_audit_recheck/exports/'
C, S, H = np.cos(np.radians(12)), np.sin(np.radians(12)), 143.3
def board(P):
    Y = P[:, 1] * C + (P[:, 2] - H) * S; Z = -P[:, 1] * S + (P[:, 2] - H) * C
    return np.stack([P[:, 0] - 2.5, Z + 27.45, -Y - 32.7], 1)
front = trimesh.load(E + 'front.stl')
# crop the shell to the LCD opening's neighbourhood
c = front.triangles_center
k = (np.abs(c[:, 0]) < 70) & (c[:, 1] > -40) & (c[:, 1] < 15) & (c[:, 2] > 60) & (c[:, 2] < 170)
sh = front.submesh([np.nonzero(k)[0]], append=True)
pq = trimesh.proximity.ProximityQuery(sh)
nrm = np.array([0, C, S])
res = {}
for n in ['LEAD_GPIO_A1', 'LEAD_GPIO_A2', 'LEAD_GPIO_B', 'LEAD_LCD_5V']:
    m = trimesh.load(E + 'comp/' + n + '.stl')
    P, _ = trimesh.sample.sample_surface_even(m, 60000)
    B = board(P)
    keep = (B[:, 0] >= -60) & (B[:, 0] <= 60) & (B[:, 1] >= -32.9) & (B[:, 1] <= 36) & (B[:, 2] >= -14) & (B[:, 2] <= -1)
    Q = P[keep]
    best = []
    for s in (0.5, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 26, 30):
        T = Q + nrm * s
        cp, dist, tri = pq.on_surface(T)
        # inside test (sign): point inside the shell material?
        i = int(np.argmin(dist))
        best.append((s, round(float(dist[i]), 3), np.round(T[i], 2).tolist(), np.round(cp[i], 2).tolist(), np.round(board(T[i:i+1])[0], 2).tolist()))
    res[n] = {'n_part_pts': int(keep.sum()), 'by_s': best}
    print(n, keep.sum())
    for b in best:
        print('   s %4.1f  d %.3f  lead pt %s  shell pt %s  lead (u,v,w) %s' % b)
json.dump(res, open('g/ride010.json', 'w'), indent=1)
