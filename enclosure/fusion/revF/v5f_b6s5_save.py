# rev F block 6 (2026-11-05): intermediate named version after V11 option 1 (B6V-1..3) and the seam re-cut (B6s-1..4).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
VERSION = 'rev F WIP 2026-11-05 b6a: V11 option 1 (5807 +6.5, cradle bosses, RR boss y -77) + joint faces normal to the wall, magnets moved (Claude)'
EXPECT = {'HOUSING_F_front': 239.797, 'HOUSING_F_door': 50.601}


def run(_context):
    X = Ctx(); out = {}
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.002:
                raise RuntimeError('guard: %s volume %s, expected %s' % (k, None if b is None else round(b.volume, 3), v))
        out['n_bodies'] = X.comp.bRepBodies.count
        out['tmp'] = [b.name for b in X.comp.bRepBodies if b.name.endswith('_tmp') or b.name.startswith(('RENDER_tmp', 'PROBE_tmp'))]
        out['saved'] = X.doc.save(VERSION)
        out['version'] = VERSION
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b6s5_save', 'save', out)
    print(json.dumps(out))
