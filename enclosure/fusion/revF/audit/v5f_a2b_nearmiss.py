# HA panel model audit (2026-11-05) block 2b: near misses (M.2), read-only.
#   Same part list as v5f_a2a_matrix.py. Candidates: every pair whose design bounding boxes come within 1.0 mm (boxes grown
#   0.5 mm each) and that is not a non-zero pair of a2a (data/a2a_hits_0.json). Each candidate: measureMinimumDistance on the
#   two real bodies -> d (mm) and the point pair (world mm, x_rel). Pairs with d < 1.0 are kept. Chunked by I0 / I1,
#   time-boxed at 45 s -> data/a2b_near_<I0>.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
exec(open(os.path.expanduser('~/Documents/audit/scripts/v5f_audit_common.py')).read())
MODE = 'list'
exec(open(os.path.expanduser('~/Documents/audit/scripts/v5f_a2a_matrix.py')).read().split('def run(_context):')[0])
G = 0.05   # cm grown on each box side


def cands(parts):
    bbs = [p.boundingBox for p in parts]; out = []
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            a = bbs[i]; b = bbs[j]
            if (a.maxPoint.x + G < b.minPoint.x - G or b.maxPoint.x + G < a.minPoint.x - G or a.maxPoint.y + G < b.minPoint.y - G or
                    b.maxPoint.y + G < a.minPoint.y - G or a.maxPoint.z + G < b.minPoint.z - G or b.maxPoint.z + G < a.minPoint.z - G):
                continue
            out.append([i, j])
    return out


def run(_context):
    X = Ctx(); guard(X); out = {}; t0 = time.time()
    try:
        parts = audit_parts(X)
        hits = json.load(open(os.path.join(DATA, 'a2a_hits_0.json')))['hits']
        nz = set(' | '.join(sorted(k.split(' | '))) for k in hits)
        cs = [c for c in cands(parts) if ' | '.join(sorted((parts[c[0]].name, parts[c[1]].name))) not in nz]
        out['n_cands'] = len(cs)
        i0 = globals().get('I0', 0); i1 = min(globals().get('I1', len(cs)), len(cs))
        near = {}; far = 0; fails = {}; stop = i1
        for k in range(i0, i1):
            if time.time() - t0 > 45:
                stop = k; break
            a, b = parts[cs[k][0]], parts[cs[k][1]]
            try:
                d, pa, pb = mindist(X, a, b)
                if d < 1.0:
                    near['%s | %s' % (a.name, b.name)] = [d, pa, pb]
                else:
                    far += 1
            except Exception as e:
                fails['%s | %s' % (a.name, b.name)] = str(e)[:80]
        out['range'] = [i0, stop]; out['near'] = near; out['far'] = far; out['fails'] = fails
        json.dump(out, open(os.path.join(DATA, 'a2b_near_%d.json' % i0), 'w'))
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_a2b_nearmiss', 'run', {k: v for k, v in out.items() if k != 'near'})
    print(json.dumps({k: (len(v) if k == 'near' else v) for k, v in out.items()}))
