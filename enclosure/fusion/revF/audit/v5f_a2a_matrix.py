# HA panel model audit (2026-11-05) block 2a: full interference matrix on the c2 state (M.1), read-only.
#   Part filter = B6w3's current_parts() (v5f_b6w3_checks.py) + HOUSING_F_cap, with the c0/c1/c2 copies and the other
#   superseded suffixes skipped as well. Pairs = every pair whose DESIGN bounding boxes overlap (as B6m / B6w3); each pair:
#   both bodies cropped to the boxes' intersection + 0.1 mm, intersected (TemporaryBRep), non-zero if > 0.005 mm³, with the
#   overlap's tight world box. Chunked: MODE 'list' writes the part list, the pair list and B6w3's matrix (from the design
#   log, read only) to ~/Documents/audit/data/; MODE 'run' does pairs I0 … I1 (time-boxed at 45 s) -> data/a2a_hits_<I0>.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
exec(open(os.path.expanduser('~/Documents/audit/scripts/v5f_audit_common.py')).read())
SKIP_PREFIX = ('HOUSING_F', 'HOUSING_E', 'REF_', 'INNER_', 'TOOL_', 'V11', 'RENDER_', 'sk_', 'PROBE_', 'B6W2', 'AUDIT_')
SKIP_SUFFIX = ('_b4n', '_b4d', '_b1', '_b2', '_b5', '_b6v1', '_b6s3', '_b6w', '_revE', '_revD', '_tmp', '_wip', '_r2', '_r3',
               '_fail1', '_fail3', '_fail3b', '_fail', '_c0', '_c1', '_c1v1', '_c2a', '_v1')
STALE = ('HOUSING_shell', 'DOOR_tray', 'REF_outer_hidden', 'DOOR_plate', 'DOOR_F', 'GROMMET_usbc', 'TOUCH_pcb', 'LD2410C_env',
         'SENSOR_strip_L', 'SENSOR_strip_R', 'SPK_driver_D40', 'PD_trigger_env_20V')
DATA = os.path.join(AUD, 'data')


def audit_parts(X):
    parts = []
    for b in X.comp.bRepBodies:
        n = b.name
        base = re.sub(r' \(\d+\)$', '', n)
        if n.startswith(SKIP_PREFIX) or base.endswith(SKIP_SUFFIX) or base in STALE or \
                n.startswith(('VOICEPE_', 'BUCK_', 'AMP_', 'SPK_driver', 'SENSOR_strip')) or 'fail' in n or \
                n == 'GROMMET_usbc_F' or (n.startswith('PI5_') and n not in ('PI5_F', 'PI5_F_cooler')) or \
                (n.startswith('TOUCH_') and n != 'TOUCH_PCB'):
            continue
        parts.append(b)
    return parts + [X.body(n) for n in ('HOUSING_F_front', 'HOUSING_F_cap', 'HOUSING_F_door', 'GROMMET_usbc_F')]


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
    X = Ctx(); guard(X); out = {}; t0 = time.time()
    mode = globals().get('MODE', 'list')
    try:
        os.makedirs(DATA, exist_ok=True)
        parts = audit_parts(X); prs = pairs_of(parts)
        out['n_parts'] = len(parts); out['n_pairs'] = len(prs)
        if mode == 'list':
            json.dump([p.name for p in parts], open(os.path.join(DATA, 'a2a_parts.json'), 'w'))
            json.dump([[i, j] for (i, j, lo, hi) in prs], open(os.path.join(DATA, 'a2a_pairs.json'), 'w'))
            dl = json.load(open(os.path.expanduser('~/Documents/v5f_log.json')))
            m = [e for e in dl if e.get('script') == 'v5f_b6w3_checks' and e.get('step') == 'matrix']
            if m:
                json.dump({'t': m[-1]['t'], 'n_parts': m[-1]['data'].get('n_parts'), 'nonzero_mm3': m[-1]['data'].get('nonzero_mm3')},
                          open(os.path.join(DATA, 'b6w3_matrix.json'), 'w'))
            out['b6w3_rows'] = len(m)
        else:
            i0 = globals().get('I0', 0); i1 = min(globals().get('I1', len(prs)), len(prs))
            hits = {}; zero = 0; fails = {}; k = i0
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
            else:
                out['stopped_at'] = i1
            out['range'] = [i0, out['stopped_at']]; out['hits'] = hits; out['zero'] = zero; out['fails'] = fails
            json.dump(out, open(os.path.join(DATA, 'a2a_hits_%d.json' % i0), 'w'))
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_a2a_matrix', mode, {k: v for k, v in out.items() if k != 'hits'})
    print(json.dumps({k: (len(v) if k == 'hits' else v) for k, v in out.items()}))
