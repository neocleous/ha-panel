# rev F e2b0 (2026-11-08): undo e2b's first run (unsaved): it built the three new main-board bodies without the XC offset
#   (design x = x_rel + XC), so they sat 2.55 mm toward +x_rel. Removes those three bodies (checked by volume and by their
#   design x-range +-45 mm) and gives the hidden originals back their names. Nothing else is touched.
import os, traceback
exec(open(os.path.expanduser('~/Documents/v5f_common.py'), encoding='utf-8').read())
OUT = os.path.expanduser('~/Documents/HA_panel_renders/board_zone/e2b0_status.json')
WRONG = {'MAIN_pcb': 7.9192, 'MAIN_front_env': 146.9829, 'MAIN_back_env': 14.2437}
ORIG = {'MAIN_pcb_e2': 7.2, 'MAIN_front_env_e2': 130.14, 'MAIN_back_env_e2': 15.75}


def run(_context):
    st = {'t0': time.strftime('%H:%M:%S')}
    try:
        X = Ctx()
        chk = []
        for k, v in WRONG.items():
            b = X.body(k)
            bb = b.boundingBox if b else None
            ok = b is not None and abs(b.volume - v) < 0.0005 and abs(bb.minPoint.x * 10 + 45) < 0.01 and abs(bb.maxPoint.x * 10 - 45) < 0.01
            chk.append([k, ok])
        for k, v in ORIG.items():
            b = X.body(k)
            chk.append([k, b is not None and abs(b.volume - v) < 0.0005])
        st['checks'] = chk
        if not all(c[1] for c in chk):
            raise RuntimeError('state not as expected: %s' % chk)
        for k in WRONG:
            X.body(k).deleteMe()
        for k in ORIG:
            X.body(k).name = k[:-3]
        st['after'] = {k: round(X.body(k).volume, 4) for k in WRONG}
        st['modified'] = X.doc.isModified
        log('v5f_e2b0_undo_shift', 'done', st)
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-3:]
    json.dump(st, open(OUT, 'w'), indent=1)
    print(json.dumps(st))


run(None)
