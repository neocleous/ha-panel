# rev F block 6a (2026-11-05), read-only: full interference matrix (brief block 6.1).
#   Parts = every current body (the B5j-1 filter: no housings of earlier revisions, references, tools, stale rev D bodies,
#   superseded copies, V11 option envelopes) + HOUSING_F_front, HOUSING_F_door, GROMMET_usbc_F = 76 bodies.
#   Every pair whose design bounding boxes overlap: both bodies cropped to the boxes' intersection (+0.1 mm), intersected,
#   volume in mm³; non-zero pairs (> 0.005 mm³) with the overlap's tight world box. Progress logged every 40 pairs.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
SKIP_PREFIX = ('HOUSING_F', 'HOUSING_E', 'REF_', 'INNER_', 'TOOL_', 'V11', 'RENDER_', 'sk_')
SKIP_SUFFIX = ('_b4n', '_b4d', '_b1', '_b2', '_revE', '_revD', '_tmp', '_wip', '_r2')
STALE = ('HOUSING_shell', 'DOOR_tray', 'REF_outer_hidden', 'DOOR_plate', 'DOOR_F', 'GROMMET_usbc', 'TOUCH_pcb', 'LD2410C_env',
         'SENSOR_strip_L', 'SENSOR_strip_R', 'SPK_driver_D40', 'PD_trigger_env_20V')


def current_parts(X):
    parts = []
    for b in X.comp.bRepBodies:
        n = b.name
        if n.startswith(SKIP_PREFIX) or n.endswith(SKIP_SUFFIX) or n in STALE or n.startswith(('VOICEPE_', 'BUCK_', 'AMP_', 'SPK_driver', 'SENSOR_strip')) \
                or n == 'GROMMET_usbc_F' or (n.startswith('PI5_') and n not in ('PI5_F', 'PI5_F_cooler')) \
                or (n.startswith('TOUCH_') and n != 'TOUCH_PCB'):
            continue
        parts.append(b)
    return parts + [X.body(n) for n in ('HOUSING_F_front', 'HOUSING_F_door', 'GROMMET_usbc_F')]


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        parts = current_parts(X)
        out['n_parts'] = len(parts)
        bbs = [p.boundingBox for p in parts]
        hits = {}; fails = {}; n_pairs = 0
        for i in range(len(parts)):
            for j in range(i + 1, len(parts)):
                a = bbs[i]; b = bbs[j]
                lo = [max(a.minPoint.x, b.minPoint.x), max(a.minPoint.y, b.minPoint.y), max(a.minPoint.z, b.minPoint.z)]
                hi = [min(a.maxPoint.x, b.maxPoint.x), min(a.maxPoint.y, b.maxPoint.y), min(a.maxPoint.z, b.maxPoint.z)]
                if any(hi[k] < lo[k] for k in range(3)):
                    continue
                n_pairs += 1
                try:
                    v = pair_vol(X, parts[i], parts[j], lo, hi, hits)
                except Exception as e:
                    fails['%s | %s' % (parts[i].name, parts[j].name)] = str(e)[:80]
                if n_pairs % 40 == 0:
                    log('v5f_b6a_matrix', 'progress', {'pairs': n_pairs, 't_s': round(time.time() - t0, 1), 'hits': len(hits)})
        out['n_pairs_bbox'] = n_pairs
        out['n_nonzero'] = len(hits)
        out['nonzero_mm3'] = hits
        out['fails'] = fails
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b6a_matrix', 'matrix', out)
    print(json.dumps({k: out[k] for k in out if k != 'nonzero_mm3'}))


def pair_vol(X, pa, pb, lo, hi, hits):     # both bodies cropped to the bbox intersection (+0.1 mm), then intersected
    box = X.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(
        P3((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2, (lo[2] + hi[2]) / 2), V3(1, 0, 0), V3(0, 1, 0),
        hi[0] - lo[0] + 0.02, hi[1] - lo[1] + 0.02, hi[2] - lo[2] + 0.02))
    qa = X.tbm.copy(pa); inter(X, qa, box)
    if qa.volume <= 0:
        return 0.0
    qb = X.tbm.copy(pb); inter(X, qb, X.tbm.copy(box))
    if qb.volume <= 0:
        return 0.0
    inter(X, qa, qb)
    v = qa.volume * 1000
    if v > 0.005:
        hits['%s | %s' % (pa.name, pb.name)] = [round(v, 2), [round(c, 1) for c in wbb(X, qa)]]
    return v
