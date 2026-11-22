# Version 67 -> 68: the ReSpeaker's USB cable, fold 1.
# The fold lay against the lip over the door opening. It is made nearer the plug (SHORTER mm less
# cable between the plug's sleeve and the fold), which takes it off the lip. Below the fold the cable
# leans back to its old line by the time it reaches the roll behind the left speaker box.
import sys, math

v = sys.modules['v68']; k = v.k; G = v.G

S1 = k.unit((0.0, -0.978, -0.208))     # the cable's run from the plug to the fold
P1 = (47.0, -46.0, 113.0)              # a point on that run, before the fold
SHORTER = 1.2
Z_FOLD, Z_ROLL = 104.0, 62.0           # the cable is redrawn between these two levels
RUN = (44.54, -55.265)                 # middle of the cable's run down (x, y); its section is 1.44 x 5.25


def half(X, p, n):
    """The half space behind the plane through p (n points out of it)."""
    c = tuple(p[i] - 100.0 * n[i] for i in range(3))
    return X.obox(c, n, (1.0, 0.0, 0.0), 200.0, 300.0, 300.0)


def cable(X, shorter=SHORTER):
    old = X.body('LEAD_USB_RESP')
    d = tuple(-shorter * q for q in S1)                       # how far the fold moves
    a = X.tbm.copy(old)
    X.sec(a, half(X, P1, S1))                                 # from the plug to the cut
    p2 = tuple(P1[i] + shorter * S1[i] for i in range(3))
    b = X.tbm.copy(old)
    X.dif(b, half(X, p2, S1))
    X.sec(b, X.wbox(30.0, 80.0, -70.0, -30.0, Z_FOLD, 130.0))  # the fold and the first of the run down
    X.move(b, d[0], d[1], d[2])
    c = X.tbm.copy(old)
    X.sec(c, X.wbox(30.0, 80.0, -70.0, -30.0, 0.0, Z_ROLL))    # the roll and the far end, as they were
    lo = (RUN[0], RUN[1], Z_ROLL); hi = (RUN[0], RUN[1] + d[1], Z_FOLD + d[2])
    ax = k.unit(tuple(hi[i] - lo[i] for i in range(3)))
    length = math.sqrt(sum((hi[i] - lo[i]) ** 2 for i in range(3)))
    mid = tuple((hi[i] + lo[i]) / 2.0 for i in range(3))
    run = X.obox(mid, ax, (1.0, 0.0, 0.0), length + 0.6, 1.44, 5.25)   # the run down between them, leaning by the fold's shift
    for q in (b, c, run):
        X.uni(a, q)
    G['LEAD_USB_RESP'] = a
    return a


def commit(X):
    X.swap('LEAD_USB_RESP', G['LEAD_USB_RESP'], v.BACKUP)
    return X.state()
