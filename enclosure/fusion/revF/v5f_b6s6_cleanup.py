# rev F block 6 (2026-11-05): cleanup – B6s-4's door combines left a degenerate extra body 'HOUSING_F_door (1)' (0.0000 cm³,
#   bbox ≈ 0.1 × 0.1 × 0 mm at x_rel −63.8, y −58.0, z 96.8, beside the old −x z 95 pocket). It is an artefact, not a part, a
#   tool or an old body → deleted (bodies named 'HOUSING_F_* (n)' with volume < 0.001 cm³ only).
import os
exec(open(os.path.expanduser('~/Documents/v5f_common.py')).read())
exec(open(os.path.expanduser('~/Documents/v5f_b5_common.py')).read())
import traceback


def run(_context):
    X = Ctx(); out = {'deleted': []}
    try:
        cands = [b for b in X.comp.bRepBodies if b.name.startswith('HOUSING_F_') and '(' in b.name]
        out['candidates'] = [[b.name, b.volume, b.lumps.count, b.faces.count, b.edges.count] for b in cands]
        for b in cands:
            if b.volume < 0.001:
                nm = b.name; b.deleteMe(); out['deleted'].append(nm)
        fb = X.body('HOUSING_F_front'); db = X.body('HOUSING_F_door')
        out['after'] = {'front': [round(fb.volume, 4), fb.lumps.count], 'door': [round(db.volume, 4), db.lumps.count],
                        'n_bodies': X.comp.bRepBodies.count,
                        'others': [b.name for b in X.comp.bRepBodies if '(' in b.name and b.isLightBulbOn]}
    except Exception:
        out['FAIL'] = traceback.format_exc().splitlines()[-3:]
    log('v5f_b6s6_cleanup', 'cleanup', out)
    print(json.dumps(out))
