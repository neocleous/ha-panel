# HA panel model audit (2026-11-05) block 2c: tight world bounding boxes (x_rel, y, z) and volumes for named bodies, read-only.
#   SEL (set by the loader) = body names; '*' prefix patterns allowed (e.g. 'LEAD_*'). Printed and written to
#   ~/Documents/audit/data/bbox_<TAG>.json.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
exec(open(os.path.expanduser('~/Documents/audit/scripts/v5f_audit_common.py')).read())


def run(_context):
    X = Ctx(); guard(X); out = {}; t0 = time.time()
    try:
        sel = globals().get('SEL', [])
        for b in X.comp.bRepBodies:
            if any(b.name == s or (s.endswith('*') and b.name.startswith(s[:-1])) for s in sel):
                out[b.name] = {'bb': [round(v, 2) for v in wbb(X, b)], 'cm3': round(b.volume, 4), 'vis': b.isLightBulbOn}
        os.makedirs(os.path.join(AUD, 'data'), exist_ok=True)
        json.dump(out, open(os.path.join(AUD, 'data', 'bbox_%s.json' % globals().get('TAG', 'x')), 'w'))
        out['t_s'] = round(time.time() - t0, 1)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_a2c_bbox', globals().get('TAG', 'x'), {'n': len(out)})
    for k, v in out.items():
        print(k, json.dumps(v))
