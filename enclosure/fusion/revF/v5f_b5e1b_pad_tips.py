# rev F block 5e-1b (2026-11-05): remove the eight tips of the R1 lip pads left in front of the B5e-1 removal box (y -53.4...-52.2;
# separate bodies 'HOUSING_F_front (1..8)', 25.8 mm3 in all) - they belonged to the removed pads, not to any kept feature.
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback

def run(_context):
    X = Ctx(); out = {'removed': [], 'kept': []}
    try:
        for b in list(X.comp.bRepBodies):
            if b.name.startswith('HOUSING_F_front ('):
                bb = wbb(X, b)
                v = b.volume * 1000
                if v < 20.0 and bb[2] > -53.5 and bb[3] < -52.0:
                    out['removed'].append([b.name, round(v, 2), [round(c, 1) for c in bb]])
                    b.deleteMe()
                else:
                    out['kept'].append([b.name, round(v, 2), [round(c, 1) for c in bb]])
        out['names'] = [b.name for b in X.comp.bRepBodies if b.name.startswith('HOUSING_F')]
        out['front_cm3'] = round(X.body('HOUSING_F_front').volume, 3)
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b5e1b_pad_tips', 'cleanup', out)
    print(json.dumps(out))
