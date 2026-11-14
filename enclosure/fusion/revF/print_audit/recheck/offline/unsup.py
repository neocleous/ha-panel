# recheck: which unsupported-overhang regions of the layer analysis (60°) got no support in the slice.
#   Usage: python3 unsup.py <tag> <job.npz> [amin]
import sys, json, numpy as np
sys.path.insert(0, '/home/claude/pa')
from pa_summ import wbox
tag = sys.argv[1]; job = sys.argv[2]; amin = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
d = json.load(open('/home/claude/pa/data/L_%s_plan.json' % tag)); Mp = d['M']
Mo = np.array(json.load(open('/mnt/user-data/outputs/rc/orient/%s_plan.json' % tag))['M_world_to_bed'])
g = np.load(job); seg = g['seg']; feat = g['feat']; names = [str(s) for s in g['names']]
sup = np.isin(feat, [i for i, n in enumerate(names) if n.startswith('Support')])
S = seg[sup]
for r in d['regions']:
    if r['area'] < amin:
        continue
    w = wbox(Mp, r['bbox'], r['z'], r['z'] + 0.2)
    P = np.array([[x, y, z, 1] for x in w[0:2] for y in w[2:4] for z in w[4:6]]) @ Mo.T
    bx0, by0, bz0 = P[:, 0].min(), P[:, 1].min(), P[:, 2].min(); bx1, by1, bz1 = P[:, 0].max(), P[:, 1].max(), P[:, 2].max()
    m = (S[:, 4] <= bz0 + 0.05) & (S[:, 4] >= bz0 - 1.2) & (np.maximum(S[:, 0], S[:, 2]) >= bx0 - 0.5) & (np.minimum(S[:, 0], S[:, 2]) <= bx1 + 0.5) & \
        (np.maximum(S[:, 1], S[:, 3]) >= by0 - 0.5) & (np.minimum(S[:, 1], S[:, 3]) <= by1 + 0.5)
    print('%s A %6.1f %-10s z(build) %5.1f dmax %s width %s bed_frac %.2f  world %s  support_below %d' % (
        'OK ' if m.sum() else 'NO ', r['area'], r['kind'], r['z'], r['dmax'], r['width'], r['bed_frac'], w, int(m.sum())))
