# rev F audit-response d6c (2026-11-06): named version after the LD2410C ribs (d5g), root fillets (d5h) and cap fixes (d6b).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
GUARD = {'HOUSING_F_door': 47.2694, 'GROMMET_usbc_F': 0.5062, 'CRADLE_5807': 2.1775, 'HOUSING_F_front': 233.5514,
         'SPKBOX_L': 25.6082, 'SPKBOX_R': 25.6435, 'MAIN_BRACKET': 5.3431, 'TOUCH_CLIP_L': 0.4896, 'TOUCH_CLIP_R': 0.4896,
         'HOUSING_F_cap': 9.9227, 'SLAB_frame': 62.9324, 'RESP_CARRIER': 10.0716}
MSG = ('rev F WIP 2026-11-06 d6: LD2410C heat-stake ribs; root fillets R0.8 / R0.5 at the cradle bosses, Pi bosses, cradle legs '
       'and posts, bracket feet (door boss junctions not possible: cove); cap void filled, mic strip seat pads (gasket 1.0 -> 0.7) (Claude)')


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
    log('v5f_d6c_save', 'save', out)
    print(json.dumps(out, separators=(',', ':')))
