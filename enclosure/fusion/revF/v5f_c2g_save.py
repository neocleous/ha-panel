# rev F cap block c2g (2026-11-05): named WIP version after c2 (checkpoint), guards on the three parts.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
import traceback
EXPECT = {'HOUSING_F_front': 236.6852, 'HOUSING_F_cap': 9.9147, 'HOUSING_F_door': 51.101}
VERSION = ('rev F WIP 2026-11-05 c2: cap held by 4 hidden M3 x 8 from below (Ruthex in cap bosses, pads + ribs, key lanes '
           'KO_capkey_*), shelf under the cap front edge, vertical lip (cap fits straight down), VEML6030 to the centre, '
           'mic strips 29 long (Claude)')


def run(_context):
    X = Ctx(); out = {}
    try:
        for k, v in EXPECT.items():
            b = X.body(k)
            if b is None or abs(b.volume - v) > 0.001:
                raise RuntimeError('guard: %s %s (expected %s)' % (k, None if b is None else round(b.volume, 4), v))
        left = [b.name for b in X.comp.bRepBodies if b.name.startswith('RENDER_tmp_')]
        if left:
            raise RuntimeError('render leftovers %s' % left)
        out['bodies'] = X.comp.bRepBodies.count
        out['saved'] = X.doc.save(VERSION); out['version'] = VERSION
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_c2g_save', 'save', out)
    print(json.dumps(out))
