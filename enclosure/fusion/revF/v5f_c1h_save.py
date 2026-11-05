# rev F cap block c1h (2026-11-05): named WIP version after step 1 (checkpoint), guards on the three parts.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
EXPECT = {'HOUSING_F_front': 235.6548, 'HOUSING_F_cap': 8.9419, 'HOUSING_F_door': 51.101}
VERSION = ('rev F WIP 2026-11-05 c1 step 1: top cap split at y -22.5 / z 175.3, clamp ledge + spline groove 2.8 x 2.5, '
           'lip, 4 posts + M3 countersunk, exhaust row moved to z 162.5-165.5 (Claude)')


def run(_context):
    X = Ctx(); out = {}
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.001:
                raise RuntimeError('guard: %s %s (expected %s)' % (k, None if b is None else round(b.volume, 4), v))
        out['bodies'] = X.comp.bRepBodies.count
        out['saved'] = X.doc.save(VERSION); out['version'] = VERSION
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_c1h_save', 'save', out)
    print(json.dumps(out))
