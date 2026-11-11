# rev F h1d (2026-11-11): step 3, block 1 - read-only: does the rev 3 board ride in on the display module?
#   The module (slab frame, LCD, carrier, ReSpeaker with its USB plug, main board) goes in from the front along the slab normal. Every
#   part of the board stands inside its outline, so the test body is the outline's prism: u +/-43.5, v +/-28.95, from the top of the
#   supply module at the top of its tolerance (w 28.5) to 60 mm out of place (depth -28.9 .. 61.2). Prism, and the prism grown by g
#   in u and v, against every body that is not part of the module (leads, keep-outs and the door left out: the door is off).
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_h_lib.py'), encoding='utf-8').read())
MODULE = ('SLAB_frame', 'LCD_', 'RESP_', 'MAIN_')
GROW = (0.0, 0.5, 0.9, 1.0, 1.1, 1.5, 2.0, 3.0)


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        fixed = [b for b in current(X, kos=False) if not b.name.startswith(MODULE) and b.name != 'HOUSING_F_door']
        st['fixed'] = len(fixed)
        res = {}
        for g in GROW:
            pr = X.dbox(U0 - 43.5 - g, U0 + 43.5 + g, -28.9, 61.2, V0 - 28.95 - g, V0 + 28.95 + g)
            row = {}
            for b in (fixed if g == 0.0 else [X.body('HOUSING_F_front')]):
                if not pr.boundingBox.intersects(b.boundingBox):
                    continue
                big = tcopy(X, b.name)
                t = X.cp(pr)
                try:
                    X.tbm.booleanOperation(t, big, BT.IntersectionBooleanType); v = X.vol(t)
                except Exception:
                    v = -1.0
                if abs(v) > 0.001:
                    row[b.name] = [round(v, 2)] + [bbb(t, 1)]
            res['grown %.1f' % g] = row
            st['res'] = res; st['t'] = round(time.time() - t0, 1); status3('h1d', st)
            if time.time() - t0 > 40.0:
                st['partial'] = True; break
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('h1d', st)


run(None)
