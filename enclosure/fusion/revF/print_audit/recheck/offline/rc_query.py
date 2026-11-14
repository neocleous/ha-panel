# recheck: list raw unsupported regions (60 deg) and islands of L_<tag>_<orient>.json inside a world box.
# Usage: python3 rc_query.py <tag> <orient> x0 x1 y0 y1 z0 z1 [amin]
import sys, json, numpy as np
sys.path.insert(0, '/home/claude/pa')
from pa_summ import wbox
tag, okey = sys.argv[1], sys.argv[2]; B = [float(v) for v in sys.argv[3:9]]; amin = float(sys.argv[9]) if len(sys.argv) > 9 else 0.2
d = json.load(open('/home/claude/pa/data/L_%s_%s.json' % (tag, okey))); M = d['M']
def hit(w):
    return w[0] <= B[1] and w[1] >= B[0] and w[2] <= B[3] and w[3] >= B[2] and w[4] <= B[5] and w[5] >= B[4]
for r in d['regions']:
    w = wbox(M, r['bbox'], r['z'], r['z'] + 0.2)
    if hit(w) and r['area'] >= amin:
        print('REG k%d zb %.1f A %.2f %s anc %d dmax %s width %s land %.1f-%.1f bed %.2f W %s' % (r['k'], r['z'], r['area'], r['kind'], r['n_anchor'], r['dmax'], r['width'], r['land_min'], r['land_max'], r['bed_frac'], w))
for i in d['islands']:
    w = wbox(M, i['bbox'], i['z0'], i['z0'] + 0.2)
    if hit(w):
        print('ISL zb %.1f A %.3f weak %s land %s W %s' % (i['z0'], i['area'], i['weak'], [i['land_min'], i['land_max']], w))
