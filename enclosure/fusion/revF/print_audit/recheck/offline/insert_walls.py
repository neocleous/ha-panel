# recheck point 10: wall round each insert hole / pilot, measured on the exported mesh (independent of the documents).
#   From points on the hole's surface (radius r + 0.02) rays go radially outward; the first exit from the material gives the wall.
#   12 directions x up to 9 stations along the axis (stations within 0.6 of either end skipped). Min and median per hole.
import json, numpy as np, trimesh, sys
E = '/mnt/user-data/uploads/print_audit_recheck/exports/'
R = json.load(open('/mnt/user-data/uploads/print_audit_recheck/data/rc2_holes.json'))['rows']
want = {'front': [4.0], 'plate': [4.0], 'spkbox_L': [4.0, 2.5], 'spkbox_R': [4.0, 2.5], 'carrier': [4.0, 1.6], 'cradle': [1.6, 3.4], 'door': [4.0]}
out = {}
for tag, dias in want.items():
    m = trimesh.load(E + tag + '.stl')
    rows = [r for r in R if r[0] == tag and r[1] == 'cyl' and r[3] == 'hole' and r[2] in dias]
    # merge coaxial faces
    holes = []
    for r in rows:
        a = np.array(r[4]); c = np.array(r[5])
        for h in holes:
            if abs(abs(np.dot(a, h['a'])) - 1) < 1e-3 and h['d'] == r[2]:
                d = c - h['c']; perp = d - np.dot(d, h['a']) * h['a']
                if np.linalg.norm(perp) < 0.3:
                    t = np.dot(c - h['c'], h['a']); h['lo'] = min(h['lo'], t - r[6] / 2); h['hi'] = max(h['hi'], t + r[6] / 2); break
        else:
            holes.append({'a': a, 'c': c, 'd': r[2], 'lo': -r[6] / 2, 'hi': r[6] / 2})
    res = []
    for h in holes:
        a = h['a'] / np.linalg.norm(h['a']); r0 = h['d'] / 2
        u = np.cross(a, [1, 0, 0] if abs(a[0]) < 0.9 else [0, 1, 0]); u /= np.linalg.norm(u); v = np.cross(a, u)
        ts = np.linspace(h['lo'] + 0.6, h['hi'] - 0.6, 9) if h['hi'] - h['lo'] > 1.4 else [0.5 * (h['lo'] + h['hi'])]
        O = []; D = []
        for t in ts:
            for k in range(12):
                th = 2 * np.pi * k / 12; dvec = np.cos(th) * u + np.sin(th) * v
                O.append(h['c'] + a * t + dvec * (r0 + 0.02)); D.append(dvec)
        O = np.array(O); D = np.array(D)
        loc, idx_ray, _ = m.ray.intersects_location(O, D, multiple_hits=False)
        dist = np.full(len(O), np.nan)
        for p, i in zip(loc, idx_ray):
            dd = np.linalg.norm(p - O[i]) + 0.02
            if np.isnan(dist[i]) or dd < dist[i]:
                dist[i] = dd
        w = dist[~np.isnan(dist)]
        res.append({'d': h['d'], 'axis': np.round(a, 3).tolist(), 'c': np.round(h['c'], 2).tolist(), 'len': round(h['hi'] - h['lo'], 2),
                    'wall_min': round(float(w.min()), 2) if len(w) else None, 'wall_med': round(float(np.median(w)), 2) if len(w) else None,
                    'n_miss': int(np.isnan(dist).sum())})
    out[tag] = res
    for r in res:
        print(tag, r)
json.dump(out, open('g/insert_walls.json', 'w'), indent=1)
