# rev F h1c (2026-11-11): step 3, block 1 - read-only: smallest distance between each body of the placed main board (rev 3) and every
#   other current body whose box comes within RANGE of it (leads and the old carrier left out; they are rebuilt in blocks 2 and 3).
#   measureMinimumDistance on the model bodies. Results are kept in the cache and a call stops after BUDGET seconds, so the script is
#   called until 'left' is 0. ONLY / SKIP (globals) restrict the other bodies: the shell and the door are slow and get their own calls.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_h_lib.py'), encoding='utf-8').read())
NEW = ['MAIN_pcb', 'MAIN_PS1', 'MAIN_PS1_tol', 'MAIN_conn', 'MAIN_tall', 'MAIN_low', 'MAIN_plug_env', 'MAIN_J2_plug_env']
RANGE = 12.0
BUDGET = globals().get('BUDGET', 30.0)
ONLY = globals().get('ONLY', None)
SKIP = globals().get('SKIP', ('HOUSING_F_front', 'HOUSING_F_door', 'RESP_CARRIER'))
NEWSET = globals().get('NEWSET', NEW)


def near(a, b, r):
    p, q = a.boundingBox, b.boundingBox
    r = r / 10.0
    return not (p.minPoint.x - r > q.maxPoint.x or q.minPoint.x - r > p.maxPoint.x or p.minPoint.y - r > q.maxPoint.y or q.minPoint.y - r > p.maxPoint.y
                or p.minPoint.z - r > q.maxPoint.z or q.minPoint.z - r > p.maxPoint.z)


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        res = cache().setdefault('h1c', {})
        others = [b for b in current(X) if b.name not in NEW and (b.name in ONLY if ONLY else b.name not in SKIP)]
        left = 0; slow = []
        for n in NEWSET:
            a = X.body(n)
            for b in others:
                k = n[5:] + '~' + b.name
                if k in res or not near(a, b, RANGE):
                    continue
                if time.time() - t0 > BUDGET:
                    left += 1; continue
                t1 = time.time()
                res[k] = round(dist(X, a, b), 2)
                if time.time() - t1 > 3.0:
                    slow.append([k, round(time.time() - t1, 1)])
        st['left'] = left; st['slow'] = slow
        st['dist'] = {k: v for k, v in sorted(res.items(), key=lambda kv: kv[1]) if v <= RANGE}
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('h1c', st)


run(None)
