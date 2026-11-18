"""Block 1: in-plane thickness of every printed part, layer by layer, in its print orientation.
For each layer the material is split into classes by local thickness (lines of the 0.4 nozzle);
pieces of one class that overlap in consecutive layers are joined into features."""
import sys, time, json, pickle, numpy as np
from fdm_lib import *

def run(name):
    t0 = time.time()
    p = Part(name)
    L = p.slice()
    hs = [h for h, _ in L]
    lb = [plane_bands(g) for _, g in L]
    pickle.dump(lb, open(os.path.join(DATA, 'bands_%s.pkl' % name), 'wb'))
    rows = []
    for k in range(len(T_PLANE)):
        cl, items = cluster_band(lb, k, hs, p.lh)
        for c in cl:
            if c['vol'] < 0.15:
                continue
            # smallest local thickness on up to 5 layers across the feature
            lis = sorted(set(q[0] for q in c['keys']))
            pick = sorted(set(lis[int(round(f * (len(lis) - 1)))] for f in (0.0, 0.25, 0.5, 0.75, 1.0)))
            wmin = 9.9
            for li in pick:
                reg = unary_union([items[q][0] for q in c['keys'] if q[0] == li])
                wmin = min(wmin, local_min_width(L[li][1], reg, hi=T_PLANE[k] + 0.05))
            c2 = {kk: vv for kk, vv in c.items() if kk != 'keys'}
            c2['wmin'] = round(wmin, 2)
            # corners of the box in world coordinates
            cu = [(c['ubox'][0], c['vbox'][0], c['h'][0]), (c['ubox'][1], c['vbox'][1], c['h'][1])]
            w = p.uvh_to_world(cu)
            c2['world_min'] = [round(float(x), 2) for x in w.min(0)]
            c2['world_max'] = [round(float(x), 2) for x in w.max(0)]
            rows.append(c2)
    json.dump(rows, open(os.path.join(DATA, 'plane_%s.json' % name), 'w'), indent=0)
    by = {}
    for r in rows:
        by.setdefault(r['band'], []).append(r)
    msg = ' '.join('b%d:%d(%.0fmm3)' % (k, len(v), sum(x['vol'] for x in v)) for k, v in sorted(by.items()))
    print('%-16s %s  dt %.0fs' % (name, msg, time.time() - t0), flush=True)

if __name__ == '__main__':
    for n in sys.argv[1:]:
        run(n)
