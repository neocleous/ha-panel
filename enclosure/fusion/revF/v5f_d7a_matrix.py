# rev F audit-response d7a (2026-11-06), read-only: full interference matrix after the d-round, the audit's a2a method
#   (v5f_a2a_matrix.py: pairs whose DESIGN boxes overlap, both bodies cropped to the boxes' intersection + 0.1 mm, intersected,
#   non-zero if > 0.005 mm³) on the audit's own part list (~/Documents/audit/data/a2a_parts.json, 83 names) + the new
#   TOUCH_CLIP_L / R. Modes (set by the loader): 'copy' copies the audit's a2a data into d_data/data/audit/; 'list' writes the part
#   and pair lists; 'run' does pairs I0…I1 (time-boxed 45 s) -> d_data/data/d7_hits_<I0>.json.
import os, shutil, glob
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
DATA = os.path.expanduser('~/Documents/HA_panel_renders/d_data/data')
AUDD = os.path.expanduser('~/Documents/audit/data')
GUARD = {'HOUSING_F_door': 47.2694, 'GROMMET_usbc_F': 0.5062, 'CRADLE_5807': 2.1775, 'HOUSING_F_front': 233.5514,
         'SPKBOX_L': 25.6082, 'SPKBOX_R': 25.6435, 'MAIN_BRACKET': 5.3431, 'TOUCH_CLIP_L': 0.4896, 'TOUCH_CLIP_R': 0.4896,
         'HOUSING_F_cap': 9.9227, 'SLAB_frame': 62.9324, 'RESP_CARRIER': 10.0716}
NEW = ['TOUCH_CLIP_L', 'TOUCH_CLIP_R']


def parts_of(X):
    names = json.load(open(os.path.join(AUDD, 'a2a_parts.json'))) + NEW
    parts = []; missing = []
    for n in names:
        b = X.body(n)
        (parts if b is not None else missing).append(b if b is not None else n)
    return parts, missing


def pairs_of(parts):
    bbs = [p.boundingBox for p in parts]; out = []
    for i in range(len(parts)):
        for j in range(i + 1, len(parts)):
            a = bbs[i]; b = bbs[j]
            lo = [max(a.minPoint.x, b.minPoint.x), max(a.minPoint.y, b.minPoint.y), max(a.minPoint.z, b.minPoint.z)]
            hi = [min(a.maxPoint.x, b.maxPoint.x), min(a.maxPoint.y, b.maxPoint.y), min(a.maxPoint.z, b.maxPoint.z)]
            if any(hi[k] < lo[k] for k in range(3)):
                continue
            out.append([i, j, lo, hi])
    return out


def pair_vol(X, pa, pb, lo, hi):
    box = X.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(
        P3((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2), V3(1, 0, 0), V3(0, 1, 0),
        hi[0] - lo[0] + 0.02, hi[1] - lo[1] + 0.02, hi[2] - lo[2] + 0.02))
    qa = X.tbm.copy(pa); inter(X, qa, box)
    if qa.volume <= 0:
        return 0.0, None
    qb = X.tbm.copy(pb); inter(X, qb, X.tbm.copy(box))
    if qb.volume <= 0:
        return 0.0, None
    inter(X, qa, qb)
    v = qa.volume * 1000
    return v, ([round(c, 1) for c in wbb(X, qa)] if v > 0.005 else None)


def run(_context):
    X = Ctx(); out = {}; t0 = time.time()
    mode = globals().get('MODE', 'list')
    try:
        bad = {k: (None if X.body(k) is None else round(X.body(k).volume, 4)) for k, v in GUARD.items()
               if X.body(k) is None or abs(X.body(k).volume - v) > 0.0005}
        if bad:
            raise RuntimeError('guard: %s' % bad)
        os.makedirs(DATA, exist_ok=True)
        if mode == 'copy':
            dst = os.path.join(DATA, 'audit'); os.makedirs(dst, exist_ok=True)
            fs = glob.glob(os.path.join(AUDD, 'a2a_*.json')) + glob.glob(os.path.join(AUDD, 'sweep_*.json')) + \
                glob.glob(os.path.join(AUDD, 'tools_*.json')) + glob.glob(os.path.join(AUDD, 'a3*.json'))
            for f in fs:
                shutil.copy(f, dst)
            out['copied'] = sorted(os.path.basename(f) for f in fs)
        else:
            parts, missing = parts_of(X); prs = pairs_of(parts)
            out['n_parts'] = len(parts); out['n_pairs'] = len(prs); out['missing'] = missing
            if mode == 'list':
                json.dump([p.name for p in parts], open(os.path.join(DATA, 'd7_parts.json'), 'w'))
                json.dump([[i, j] for (i, j, lo, hi) in prs], open(os.path.join(DATA, 'd7_pairs.json'), 'w'))
            else:
                i0 = globals().get('I0', 0); i1 = min(globals().get('I1', len(prs)), len(prs))
                hits = {}; zero = 0; fails = {}
                out['stopped_at'] = i1
                for k in range(i0, i1):
                    if time.time() - t0 > 45:
                        out['stopped_at'] = k; break
                    i, j, lo, hi = prs[k]
                    try:
                        v, bb = pair_vol(X, parts[i], parts[j], lo, hi)
                        if bb is not None:
                            hits['%s | %s' % (parts[i].name, parts[j].name)] = [round(v, 3), bb]
                        else:
                            zero += 1
                    except Exception as e:
                        fails['%s | %s' % (parts[i].name, parts[j].name)] = str(e)[:80]
                out['range'] = [i0, out['stopped_at']]; out['hits'] = hits; out['zero'] = zero; out['fails'] = fails
                json.dump(out, open(os.path.join(DATA, 'd7_hits_%d.json' % i0), 'w'))
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d7a_matrix', mode, {k: v for k, v in out.items() if k != 'hits'})
    print(json.dumps({k: (len(v) if k == 'hits' else v) for k, v in out.items()}, separators=(',', ':')))
