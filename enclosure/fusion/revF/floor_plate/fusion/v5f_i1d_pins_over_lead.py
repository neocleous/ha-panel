# rev F i1d (2026-11-11): step 3 repeated, block 1 - read-only: the back-face pin ends of main board rev 3.1 above the display's power
#   lead, and where that lead runs behind the board (board frame u, v; w 0 = door-side face, the back face is at w -1.6).
#   A  the lead behind the board (its part inside u +/-44.5, v -31..+29.5, w -14..-1.6): the box of each leg, read in windows
#      (the run along v ~ +15.5; the run down the -u edge; the rise to the display's header at u ~ +30; the exit below the bottom edge)
#   B  the lead's shadow on the board: the lead swept toward the board (copies moved 0.5 at a time over 9.0 along the normal).
#      Every piece of MAIN_conn / MAIN_tall / MAIN_PS1 behind the back face that lies in the shadow: its u, v and how far it stands out.
#   C  every piece behind the back face at all, by group: count and the largest protrusion (for the table of the reply, section 5)
import os
exec(open(os.path.join(os.path.expanduser('~/Documents/HA_panel_renders/fp/scripts'), 'v5f_i_lib.py'), encoding='utf-8').read())
WIN = {'run along v': (-30.0, 20.0, -31.0, 29.5), 'run down the -u edge': (-44.5, -38.0, -25.0, 5.0), 'rise to the header': (20.0, 44.5, 19.5, 23.5),
       'whole lead behind the board': (-44.5, 44.5, -28.95, 29.5), 'below the bottom edge': (-44.5, 44.5, -31.0, -28.95)}
PARTS = ('MAIN_conn', 'MAIN_tall', 'MAIN_PS1')


def run(_context):
    st = {}
    t0 = time.time()
    try:
        X = K()
        lead = X.cp(X.body('LEAD_LCD_5V'))
        X.sec(lead, bbox_b(X, -44.5, 44.5, -31.0, 29.5, -14.0, -1.6))
        A = {}
        for k, (u0, u1, v0, v1) in WIN.items():
            t = X.cp(lead); X.sec(t, bbox_b(X, u0, u1, v0, v1, -14.0, -1.6))
            A[k] = bbb(t) if X.vol(t) > 0.001 else None
        st['A'] = A
        sh = X.cp(lead)
        for i in range(1, 19):
            X.uni(sh, move_n(X, X.cp(lead), -0.5 * i))            # toward the board: depth grows
        st['shadow box'] = bbb(sh)
        back = bbox_b(X, -44.5, 44.5, -31.0, 29.5, -14.0, -1.605)
        B = []; Cc = {}
        for n in PARTS:
            beh = X.cp(X.body(n)); X.sec(beh, back)
            pcs = []
            for l in beh.lumps:
                bb = l.boundingBox; a = Bf(bb.minPoint); c = Bf(bb.maxPoint)
                pcs.append([round(a[0], 2), round(c[0], 2), round(a[1], 2), round(c[1], 2), round(-1.6 - c[2], 2)])
            Cc[n[5:]] = [len(pcs), max(p[4] for p in pcs) if pcs else 0.0]
            t = X.cp(beh); X.sec(t, sh)
            for l in t.lumps:
                bb = l.boundingBox; a = Bf(bb.minPoint); c = Bf(bb.maxPoint)
                B.append([n[5:], round(a[0], 2), round(c[0], 2), round(a[1], 2), round(c[1], 2), round(-1.6 - c[2], 2), round(l.volume * 1000.0, 3)])
        st['B'] = sorted(B, key=lambda r: r[1])
        st['C'] = Cc
    except Exception:
        st['FAIL'] = traceback.format_exc().splitlines()[-5:]
    st['t_end'] = round(time.time() - t0, 1)
    status3('i1d', st)


run(None)
