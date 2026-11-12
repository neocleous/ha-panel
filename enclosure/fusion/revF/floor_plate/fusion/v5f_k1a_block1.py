# rev F k1a (2026-11-12): fix pass, block 1 - the build. Run through k.step(); the library is the global k.
#   Fix 1  front shell: the two holes for the box-top inserts at (+-58, z 79.5) are filled and cut again on a line through the mouth
#          (+-58, -3.9, 80.0) that leans DEG toward the middle (hole raised RAISE), dia 4.0, DEPTH deep along the line, blind.
#          speaker boxes: the tab gets a wedge on its back face (0.05 at its inner edge to 1.53 at its outer edge) so that the
#          screw head's seat is square to the line; the tab's hole dia 3.6 is filled and cut again on the line.
#   Fix 5  front shell: notches through the wall round the LCD opening (depth 9.0 to 14.8): two in the lower edge, one in the top edge.
#   Fix 6  carrier: top edge back to v +29.15, bottom edge back to v -28.95 (this also takes 0.3 off the two bottom posts' rims).
#   Everything is built on temporary bodies kept in k.c; small() and shell_stage() change nothing in the model; apply() swaps
#   (old body -> <name>_v55, hidden). The shell takes three connector calls (copy, union, difference): shell_stage() does one step a call.
import math
DEG = 10.0; RAISE = 0.5; DEPTH = 6.7
S10 = math.sin(math.radians(DEG)); C10 = math.cos(math.radians(DEG))
NOTCH = {'low1': (-28.0, -11.0, -32.98, -29.0), 'low2': (4.0, 10.0, -32.98, -29.0), 'top': (-32.0, -27.0, 29.0, 33.02)}   # board frame u0, u1, v0, v1
WALL_D = (8.5, 15.3)                 # the wall is 9.0 .. 14.8 behind the glass; the tools overshoot it by 0.5 at both faces
CARRIER_V = (-28.95, 29.15)
SUF = '_v55'


def mouth(sx): return (sx * 58.0, -3.9, 79.5 + RAISE)
def a_in(sx): return (sx * S10, C10, 0.0)            # along the line, into the shell
def a_back(sx): return (-sx * S10, -C10, 0.0)        # along the line, toward the door
def seat_q(sx): return (sx * 53.8, -6.65, 80.0)      # a point of the seat plane: the tab's inner edge, 0.05 behind its old back face


def seat_t(sx):                                      # distance along the line from the mouth to the seat plane
    m = mouth(sx); q = seat_q(sx); ab = a_back(sx)
    return sum((q[i] - m[i]) * ab[i] for i in range(3))


def shell_tools(X):
    add = None; cut = None
    for sx in (1, -1):
        p = X.cyl((sx * 58.0, -3.9, 79.5), (sx * 58.0, 2.4, 79.5), 2.1)          # plug: the old hole, 0.1 larger and deeper, flush with the mouth
        add = p if add is None else X.uni(add, p)
        m = mouth(sx); a = a_in(sx)
        h = X.cyl(k.along(m, a, -1.5), k.along(m, a, DEPTH), 2.0)
        cut = h if cut is None else X.uni(cut, h)
    for nm, (u0, u1, v0, v1) in NOTCH.items():
        cut = X.uni(cut, X.dbox(k.U0 + u0, k.U0 + u1, WALL_D[0], WALL_D[1], k.V0 + v0, k.V0 + v1))
    return add, cut


def shell_stage(X, tmax=30.0):                        # one step per call; returns the stage reached (3 = built)
    import time
    c = k.c; t0 = time.time(); s = c.get('k1_stage', 0)
    try:
        if s == 0:
            c['k1_shell'] = X.cp(k.tcopy(X, 'HOUSING_F_front')); s = 1
        elif s == 1:
            add, cut = shell_tools(X); X.uni(c['k1_shell'], add); s = 2
        elif s == 2:
            add, cut = shell_tools(X); X.dif(c['k1_shell'], cut); s = 3
    except Exception:
        c['k1_stage'] = 0; c.pop('k1_shell', None)
        raise
    c['k1_stage'] = s
    print('shell stage', s, 'in', round(time.time() - t0, 1), 's')
    if s == 3:
        old = X.body('HOUSING_F_front'); new = c['k1_shell']
        print('shell volume old / new / change', round(old.volume * 1000.0, 1), round(X.vol(new), 1), round(X.vol(new) - old.volume * 1000.0, 1), 'lumps', new.lumps.count)
    return s


def box_new(X, name):
    sx = 1 if name.endswith('_L') else -1
    new = X.cp(X.body(name))
    xi, xo = sorted((sx * 53.8, sx * 62.2))
    blk = X.wbox(xi, xo, -9.6, -3.9, 75.5, 84.0)                                 # the tab's own outline, 0.5 into the roof
    ab = a_back(sx)
    X.sec(blk, X.obox(k.along(seat_q(sx), ab, -20.0), ab, (0.0, 0.0, 1.0), 40.0, 40.0, 60.0))   # the half-space in front of the seat plane
    X.uni(new, blk)
    m = mouth(sx); a = a_in(sx)
    X.dif(new, X.cyl(k.along(m, a, 1.0), k.along(m, a, -5.2), 1.8))
    return new


def carrier_new(X):
    new = X.cp(X.body('RESP_CARRIER'))
    X.dif(new, X.bbox(-46.0, 46.0, CARRIER_V[1], 31.0, -19.0, 0.0))
    X.dif(new, X.bbox(-46.0, 46.0, -31.0, CARRIER_V[0], -19.0, 0.0))
    return new


def delta(X, name, new):                             # what went and what came: lumps [mm3, world box]
    old = X.cp(X.body(name))
    rem = X.cp(old); X.dif(rem, new)
    add = X.cp(new); X.dif(add, old)
    return X.lumps(rem), X.lumps(add)


def small(X):                                        # boxes and carrier on temporary bodies, with the report
    c = k.c; out = {}
    for name, fn in (('SPKBOX_L', lambda: box_new(X, 'SPKBOX_L')), ('SPKBOX_R', lambda: box_new(X, 'SPKBOX_R')), ('RESP_CARRIER', lambda: carrier_new(X))):
        new = fn(); old = X.body(name)
        rem, add = delta(X, name, new)
        c[('k1_new', name)] = new
        out[name] = {'vol old/new': [round(old.volume * 1000.0, 1), round(X.vol(new), 1)], 'lumps': new.lumps.count, 'faces old/new': [old.faces.count, new.faces.count],
                     'removed': rem, 'added': add}
        print(name, out[name])
    print('seat plane: distance from the mouth along the line', round(seat_t(1), 3), '-> an M3 x 8 reaches', round(8.0 - seat_t(1), 2), 'into the shell hole')
    return out


def apply(X, names):                                 # swap; returns the new model bodies
    c = k.c; out = {}
    for name in names:
        tb = c['k1_shell'] if name == 'HOUSING_F_front' else c[('k1_new', name)]
        nb = X.swap(name, tb, SUF)
        out[name] = [round(nb.volume * 1000.0, 1), nb.lumps.count, nb.isLightBulbOn]
    print('applied', out, 'dups', X.dups(), 'bodies', len(X.names()))
    return out
