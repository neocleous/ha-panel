# rev F h3c (2026-11-11): step 3, block 3 - read-only: what every lead touches and how close it runs to everything else.
#   For each LEAD_* body of the present set and each other current body (keep-outs and the door included, other leads not) whose box
#   comes within RANGE: measureMinimumDistance on the model bodies, with both points (board frame u, v, w and world x_rel, y, z).
#   A distance of 0 is then measured as an overlap (mm3 and the overlap's box in the board frame) on temporary copies.
#   Results are cached per lead (name and volume) and body, and a call stops after BUDGET seconds: call until 'left' is 0.
#   ONLY (global) restricts the leads; CLR is the clearance below which a pair is listed.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_h_lib.py'), encoding='utf-8').read())
ONLY = globals().get('ONLY', None)
BUDGET = globals().get('BUDGET', 30.0)
RANGE = globals().get('RANGE', 4.0)
CLR = globals().get('CLR', 2.0)
SKIP = ('MAIN_PS1_tol',)


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
        res = cache().setdefault('h3c', {})
        leads = [b for b in current(X, leads=True) if b.name.startswith('LEAD_') and (ONLY is None or b.name in ONLY)]
        others = [b for b in current(X) if b.name not in SKIP]
        left = 0; out = {}
        for a in leads:
            ka = '%s|%.4f' % (a.name, a.volume * 1000.0)
            row = res.setdefault(ka, {})
            for b in others:
                if b.name in row:
                    continue
                if not near(a, b, RANGE):
                    row[b.name] = None; continue
                if time.time() - t0 > BUDGET:
                    left += 1; continue
                m = X.app.measureManager.measureMinimumDistance(a, b)
                d = m.value * 10.0
                if d > RANGE:
                    row[b.name] = None; continue
                q = m.positionOne
                e = [round(d, 2), [round(v, 1) for v in Bf(q)], [round(v, 1) for v in W(q)]]
                if d < 0.005:
                    t = X.cp(a)
                    try:
                        X.tbm.booleanOperation(t, tcopy(X, b.name), BT.IntersectionBooleanType); v = X.vol(t)
                    except Exception:
                        v = -1.0
                    e = [0.0, round(v, 2), bbb(t, 1) if v > 0.001 else []]
                row[b.name] = e
            out[a.name[5:]] = {k: v for k, v in row.items() if v and v[0] < CLR}
        st['left'] = left
        st['leads'] = out
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('h3c', st)


run(None)
