import json, numpy as np, trimesh
E = '/mnt/user-data/uploads/print_audit_recheck/exports/'
m = trimesh.load(E + 'front.stl')
# crop to the region near the bosses for speed
for c, a in (([58.55, -0.78, 80.0], [0.174, 0.985, 0.0]), ([-58.61, -0.43, 80.0], [-0.174, 0.985, 0.0])):
    c = np.array(c); a = np.array(a); a = a / np.linalg.norm(a)
    sub = m.slice_plane([0, 0, 70], [0, 0, 1]).slice_plane([0, 0, 90], [0, 0, -1])
    u = np.array([0, 0, 1.0]); v = np.cross(a, u)
    print('hole at', c, 'axis', a)
    for t in np.arange(-3.4, 3.6, 0.5):
        row = []
        for k in range(16):
            th = 2 * np.pi * k / 16; d = np.cos(th) * u + np.sin(th) * v
            o = c + a * t + d * 2.02
            loc, ir, _ = sub.ray.intersects_location([o], [d], multiple_hits=False)
            row.append(round(float(np.linalg.norm(loc[0] - o)) + 0.02, 2) if len(loc) else None)
        print('  t %+.1f' % t, row)
