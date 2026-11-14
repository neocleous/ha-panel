import json, numpy as np, collections
R = json.load(open('/mnt/user-data/uploads/print_audit_recheck/data/rc2_holes.json'))['rows']
UP = {}
for t in ['spkbox_L', 'spkbox_R', 'carrier', 'cradle', 'door', 'plate', 'front']:
    d = json.load(open('/mnt/user-data/outputs/rc/orient/%s_plan.json' % t)); M = np.array(d['M_world_to_bed'])
    UP[t] = np.linalg.inv(M[:3, :3]) @ np.array([0, 0, 1.0])
def merge(g):
    holes = []
    for r in g:
        a = np.array(r[4]); c = np.array(r[5])
        for h in holes:
            if abs(abs(np.dot(a, h['a'])) - 1) < 1e-3:
                d = c - h['c']; perp = d - np.dot(d, h['a']) * h['a']
                if np.linalg.norm(perp) < 0.3:
                    h['L'] += r[6]; h['seg'].append(r); h['t'] += [np.dot(c - h['c0'], h['a']) - r[6]/2, np.dot(c - h['c0'], h['a']) + r[6]/2]; break
        else:
            holes.append({'a': a, 'c': c, 'c0': c, 'L': r[6], 'seg': [r], 't': [-r[6]/2, r[6]/2]})
    return holes
res = {}
for tag in ['front', 'plate', 'spkbox_L', 'spkbox_R', 'carrier', 'cradle', 'door']:
    rows = [r for r in R if r[0] == tag and r[1] == 'cyl' and r[3] == 'hole' and r[2] <= 4.6]
    groups = collections.defaultdict(list)
    for r in rows:
        groups[r[2]].append(r)
    print('==', tag)
    for dia in sorted(groups):
        hs = merge(groups[dia]); cnt = collections.Counter()
        for h in hs:
            cs = abs(float(np.dot(h['a'], UP[tag])))
            h['o'] = 'vert' if cs > 0.97 else ('side' if cs < 0.26 else 'obl%.0f' % np.degrees(np.arccos(cs)))
            cnt[h['o']] += 1
        line = '  Ø%.2f: %d holes %s' % (dia, len(hs), dict(cnt))
        if dia in (1.6, 1.7, 2.0, 2.1, 2.2, 2.5, 2.7, 2.9, 3.2, 3.3, 3.4, 3.6, 4.0, 4.2, 4.4, 4.6) and len(hs) <= 16:
            print(line)
            for h in hs:
                span = max(h['t']) - min(h['t'])
                print('     L %.2f (span %.2f) axis %s at %s %s' % (h['L'], span, np.round(h['a'], 3).tolist(), np.round(h['c'], 2).tolist(), h['o']))
        else:
            print(line)
