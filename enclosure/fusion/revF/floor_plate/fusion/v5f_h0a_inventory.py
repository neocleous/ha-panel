# rev F h0a (2026-11-11): step 3, block 0 - read-only inventory of the bodies that make up the unit today (leads and keep-outs
# included): name, visible, mm3, lumps and the box in the main board's frame (u0, u1, v0, v1, w0, w1). Writes fp/step3/h0a_status.json.
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_h_lib.py'), encoding='utf-8').read())


def run(_context):
    st = {}
    t0 = time.time()
    X = K()
    rows = []
    for b in current(X, leads=True):
        rows.append([b.name, int(b.isLightBulbOn), round(b.volume * 1000.0, 1), b.lumps.count] + bbb(b, 1))
    st['n_all'] = X.root.bRepBodies.count
    st['n_current'] = len(rows)
    st['rows'] = rows
    st['t'] = round(time.time() - t0, 1)
    status3('h0a', st)


run(None)
