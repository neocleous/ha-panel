# rev F audit-response d5f (2026-11-06): named version after the front-shell small fixes, vents, posts and shelf land (d5b / d5e).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
GUARD = {'HOUSING_F_door': 47.2694, 'GROMMET_usbc_F': 0.5062, 'CRADLE_5807': 2.1709, 'HOUSING_F_front': 233.5171,
         'SPKBOX_L': 25.6082, 'SPKBOX_R': 25.6435, 'MAIN_BRACKET': 5.3418, 'TOUCH_CLIP_L': 0.4896, 'TOUCH_CLIP_R': 0.4896,
         'HOUSING_F_cap': 9.9147, 'SLAB_frame': 62.9324, 'RESP_CARRIER': 10.0716}
MSG = ('rev F WIP 2026-11-06 d5: front - speaker-bore voids filled, 10 magnet pocket floors +0.2 (skin 0.49), Pi seats Ø6.8 + rear '
       'hole skins 1.5, intake 100 -> 475 x Ø2 (1 492 mm2), exhaust bridge posts, shelf 0.4 land; door - 12 vertical vent '
       'slots 3.0 wide (1 504 mm2) (Claude)')


def run(_context):
    X = Ctx(); out = {}
    try:
        bad = {k: (None if X.body(k) is None else round(X.body(k).volume, 4)) for k, v in GUARD.items()
               if X.body(k) is None or abs(X.body(k).volume - v) > 0.0005}
        if bad:
            raise RuntimeError('guard: %s' % bad)
        out['visible'] = sorted(b.name for b in X.comp.bRepBodies if b.isLightBulbOn)
        out['n_bodies'] = X.comp.bRepBodies.count
        out['saved'] = X.doc.save(MSG)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d5f_save', 'save', out)
    print(json.dumps(out, separators=(',', ':')))
