# recheck point 10: insert holes and pilots per scope-A part, with the axis in the planned print orientation.
import json, numpy as np, collections
R = json.load(open('/mnt/user-data/uploads/print_audit_recheck/data/rc2_holes.json'))['rows']
UP = {}
for t in ['spkbox_L', 'spkbox_R', 'carrier', 'cradle', 'door', 'plate', 'front']:
    d = json.load(open('/mnt/user-data/outputs/rc/orient/%s_plan.json' % t)); M = np.array(d['M_world_to_bed'])
    UP[t] = np.linalg.inv(M[:3, :3]) @ np.array([0, 0, 1.0])
out = collections.OrderedDict()
for tag in ['front', 'plate', 'spkbox_L', 'spkbox_R', 'carrier', 'cradle', 'door', 'cap', 'slab', 'grommet', 'clip_L', 'clip_R', 'bme_hood']:
    rows = [r for r in R if r[0] == tag and r[1] == 'cyl' and r[3] == 'hole' and 1.4 <= r[2] <= 4.2]
    groups = collections.defaultdict(list)
    for r in rows:
        groups[r[2]].append(r)
    print('==', tag)
    for dia in sorted(groups):
        g = groups[dia]
        # merge faces of the same hole: same axis line (centre within 0.6 of each other's line)
        holes = []
        for r in g:
            a = np.array(r[4]); c = np.array(r[5])
            for h in holes:
                if abs(abs(np.dot(a, h['a'])) - 1) < 1e-3:
                    d = c - h['c']; perp = d - np.dot(d, h['a']) * h['a']
                    if np.linalg.norm(perp) < 0.3:
                        h['L'] += r[6]; h['seg'].append(r); break
            else:
                holes.append({'a': a, 'c': c, 'L': r[6], 'seg': [r]})
        for h in holes:
            up = UP.get(tag)
            if up is not None:
                cs = abs(float(np.dot(h['a'], up)))
                orient = 'vertical' if cs > 0.97 else ('sideways' if cs < 0.26 else 'oblique %.0f°' % np.degrees(np.arccos(cs)))
            else:
                orient = '?'
            fulls = [s[8] for s in h['seg'] if s[8] is not None]
            print('  Ø%.2f  L %.2f  axis %s  at %s  %s  full %s  n%d' % (dia, h['L'], np.round(h['a'], 3).tolist(), np.round(h['c'], 2).tolist(), orient,
                  [round(f, 2) for f in fulls], len(h['seg'])))
