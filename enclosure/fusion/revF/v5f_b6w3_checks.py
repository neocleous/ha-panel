# rev F block 6w-3 (2026-11-05), read-only: checks after the decision-1 (a) wall fill (B6w-2d).
#   1. Full interference matrix, B6m method (every pair whose design bounding boxes overlap, both bodies cropped to the boxes'
#      intersection + 0.1 mm, intersected; non-zero > 0.005 mm³ with the overlap's tight world box); filters extended by
#      B6w's names (*_b6w, *_fail, PROBE_*). Compared with the last B6m matrix: new pairs, gone pairs, |Δ| > 0.01 mm³.
#   2. Speaker-box insertion path (B5j3 method, IN 42): (a) +y travel at 42 inboard, lifted 6, dy −70…−40 at 1 mm;
#      (b) sideways 42 → 1 inboard at dy −1, lift 6; (c) lowering at 1 inboard, lift 6 → 0 at 0.5; (d) last 1 mm outboard on
#      the floor at 0.25; (e) push dy −1 → 0 at 0.25. Front shell cropped to each box's path region.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
SKIP_PREFIX = ('HOUSING_F', 'HOUSING_E', 'REF_', 'INNER_', 'TOOL_', 'V11', 'RENDER_', 'sk_', 'PROBE_', 'B6W2')
SKIP_SUFFIX = ('_b4n', '_b4d', '_b1', '_b2', '_b5', '_b6v1', '_b6s3', '_b6w', '_revE', '_revD', '_tmp', '_wip', '_r2', '_r3',
               '_fail1', '_fail3', '_fail3b', '_fail')
STALE = ('HOUSING_shell', 'DOOR_tray', 'REF_outer_hidden', 'DOOR_plate', 'DOOR_F', 'GROMMET_usbc', 'TOUCH_pcb', 'LD2410C_env',
         'SENSOR_strip_L', 'SENSOR_strip_R', 'SPK_driver_D40', 'PD_trigger_env_20V')
IN = 42.0


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


def pair_vol(X, pa, pb, lo, hi, hits):
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


def run(_context):
    X = Ctx(); out = {}
    t0 = time.time()
    try:
        fb = X.body('HOUSING_F_front'); db = X.body('HOUSING_F_door')
        out['cm3'] = {'front': round(fb.volume, 4), 'door': round(db.volume, 4)}
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
                    pair_vol(X, parts[i], parts[j], lo, hi, hits)
                except Exception as e:
                    fails['%s | %s' % (parts[i].name, parts[j].name)] = str(e)[:80]
                if n_pairs % 60 == 0:
                    log('v5f_b6w3_checks', 'progress', {'pairs': n_pairs, 't_s': round(time.time() - t0, 1), 'hits': len(hits)})
        out['n_pairs_bbox'] = n_pairs
        out['n_nonzero'] = len(hits)
        out['fails'] = fails
        prev = [e for e in json.load(open(LOG)) if e['script'] == 'v5f_b6m_matrix' and e['step'] == 'matrix'][-1]['data']['nonzero_mm3']
        key = lambda k: ' | '.join(sorted(k.split(' | ')))
        pk = {key(k): v for k, v in prev.items()}; nk = {key(k): v for k, v in hits.items()}
        out['vs_B6m'] = {'n_before': len(pk), 'new': {k: nk[k] for k in nk if k not in pk}, 'gone': {k: pk[k] for k in pk if k not in nk},
                         'changed_[before, after]': {k: [pk[k][0], nk[k][0]] for k in nk if k in pk and abs(nk[k][0] - pk[k][0]) > 0.01}}
        out['nonzero_mm3'] = hits
        out['t_matrix_s'] = round(time.time() - t0, 1)
        log('v5f_b6w3_checks', 'matrix', out)
        bp = {}
        for bn, s in (('SPKBOX_L', 1), ('SPKBOX_R', -1)):
            box = X.body(bn)
            bb = wbb(X, box)
            region = X.wbox(XC + min(bb[0], bb[0] - IN * s) - 3, XC + max(bb[1], bb[1] - IN * s) + 3, bb[2] - 75, bb[3] + 3, bb[4] - 3, bb[5] + 9)
            crop = X.tbm.copy(fb); inter(X, crop, region)
            res = {'a_in_y_42': {}, 'b_sideways_to_1': {}, 'c_lower_at_1': {}, 'd_last_1mm_floor': {}, 'e_push': {}}

            def at(dx, dy, dz):
                q = X.tbm.copy(box); mvw(X, q, dx, dy, dz)
                return vol_x(X, q, crop)
            for dy in range(-70, -39):
                v = at(-IN * s, float(dy), 6.0)
                if v > 0: res['a_in_y_42'][str(dy)] = v
            for k in range(1, 43):
                v = at(-float(k) * s, -1.0, 6.0)
                if v > 0: res['b_sideways_to_1'][str(k)] = v
            for i in range(0, 13):
                v = at(-1.0 * s, -1.0, 6.0 - 0.5 * i)
                if v > 0: res['c_lower_at_1'][str(6.0 - 0.5 * i)] = v
            for i in range(0, 5):
                v = at(-(1.0 - 0.25 * i) * s, -1.0, 0.0)
                if v > 0: res['d_last_1mm_floor'][str(1.0 - 0.25 * i)] = v
            for i in range(0, 5):
                v = at(0.0, -1.0 + 0.25 * i, 0.0)
                if v > 0: res['e_push'][str(-1.0 + 0.25 * i)] = v
            bp[bn] = {kk: (vv or 'all 0') for kk, vv in res.items()}
            bp[bn]['final_pose_mm3'] = vol_x(X, box, fb)
            bp[bn]['min_to_front_mm'] = round(X.app.measureManager.measureMinimumDistance(box, fb).value * 10, 3)
        out2 = {'box_paths': bp, 't_s': round(time.time() - t0, 1)}
        log('v5f_b6w3_checks', 'box_paths', out2)
        out.update(out2)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
        log('v5f_b6w3_checks', 'fail', out)
    print(json.dumps({k: out[k] for k in out if k not in ('nonzero_mm3',)}, separators=(',', ':'))[:6000])
