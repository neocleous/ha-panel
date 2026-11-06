# rev F audit-response d4h (2026-11-06): the rebuilt grommet takes the old one's appearance / material, then a named version.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback
GUARD = {'HOUSING_F_door': 51.1617, 'GROMMET_usbc_F': 0.5062, 'CRADLE_5807': 2.1709, 'HOUSING_F_front': 236.2249,
         'SPKBOX_L': 25.6082, 'SPKBOX_R': 25.6435, 'MAIN_BRACKET': 5.3418, 'TOUCH_CLIP_L': 0.4896, 'TOUCH_CLIP_R': 0.4896,
         'HOUSING_F_cap': 9.9147, 'SLAB_frame': 62.9324, 'RESP_CARRIER': 10.0716}
MSG = ('rev F WIP 2026-11-06 d4: door - old RR stub cut, bottom flange 0.85, pin holes Ø1.7 at x ±13.85 (web 0.8); 0.3 floor pads '
       'under the 4 door bosses; grommet rebuilt (pins Ø1.5, USB-C opening to z 30.1 with a cloth collar, flange to z 33.1); '
       'webs between the tangent cradle legs / floor bosses; cradle leftover hole filled (Claude)')


def run(_context):
    X = Ctx(); out = {}
    try:
        bad = {k: (None if X.body(k) is None else round(X.body(k).volume, 4)) for k, v in GUARD.items()
               if X.body(k) is None or abs(X.body(k).volume - v) > 0.0005}
        if bad:
            raise RuntimeError('guard: %s' % bad)
        g = X.body('GROMMET_usbc_F'); g0 = X.body('GROMMET_usbc_F_d0')
        out['before'] = [g.appearance.name if g.appearance else None, g.material.name if g.material else None]
        if g0.appearance:
            g.appearance = g0.appearance
        if g0.material:
            g.material = g0.material
        out['after'] = [g.appearance.name if g.appearance else None, g.material.name if g.material else None]
        d = X.body('HOUSING_F_door'); d0 = X.body('HOUSING_F_door_d4e')
        out['door_app'] = [d.appearance.name if d.appearance else None, d0.appearance.name if d0.appearance else None]
        out['visible'] = sorted(b.name for b in X.comp.bRepBodies if b.isLightBulbOn)
        out['n_bodies'] = X.comp.bRepBodies.count
        out['saved'] = X.doc.save(MSG)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_d4h_save', 'save', out)
    print(json.dumps(out, separators=(',', ':')))
