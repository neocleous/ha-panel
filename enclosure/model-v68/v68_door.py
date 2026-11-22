# Version 67 -> 68: the USB-C grommet and the rear door.
# The grommet was held by two pins melted over inside the door. Now its sleeve has two lugs that
# reach in under the door's cutout, each held by one M2 x 6 flat-head screw for plastic into a boss
# on the door's inside. None of it can be seen from outside: the lowered edge of the cutout lies
# behind the grommet's flange. The two pins stay as plain locating pegs.
#
# The screws lean 18 degrees away from the door, so that the driver clears the door when the door
# lies on the bench. The shapes are worked out in the y-z plane and are the same at x = +7.5 and -7.5.
import sys, math

v = sys.modules['v68']; k = v.k; G = v.G

LEAN = 18.0
X_SCREW = 7.5
HALF = 3.0                 # half the width of a lug and of its boss
A = (-82.1, 14.2)          # where a lug's sloped top face begins (y, z): 0.5 inside the door's wall
T = 1.75                   # thickness of the lug under the screw head
SINK = 0.95                # depth of the countersink; the head stands 0.15 proud of the sloped face
S_HEAD = 2.15              # the screw, measured down the slope from A
S_END = 4.8                # the end of the lug, measured the same way
DEEP = 4.45                # depth of the pilot below the boss's top face


def frame():
    b = math.radians(LEAN)
    u = (0.0, math.sin(b), math.cos(b))        # from the screw's tip to its head: the driver's line
    e = (0.0, math.cos(b), -math.sin(b))       # down the slope, into the unit
    return u, e


def pt(x, s, depth):
    """A world point: s down the slope from A, depth below the lug's top face along the screw."""
    u, e = frame()
    return (x, A[0] + s * e[1] - depth * u[1], A[1] + s * e[2] - depth * u[2])


def slab(X, x, s0, s1, d0, d1, half=HALF):
    """A box lying along the slope: from s0 to s1, from depth d0 to d1, 2 x half wide."""
    u, e = frame()
    return X.obox(pt(x, (s0 + s1) / 2.0, (d0 + d1) / 2.0), e, (1.0, 0.0, 0.0), s1 - s0, 2.0 * half, d1 - d0)


def head(x):
    """Centre of the screw head's top face, and the driver's direction."""
    return pt(x, S_HEAD, SINK - 1.1), frame()[0]


def grommet(X):
    t = v.start(X, 'GROMMET_usbc_F')
    # the sleeve's bottom wall, 0.8 thick, made 1.8 thick downward where it passes through the door
    v.add(X, t, X.wbox(-10.5, 10.5, -85.0, -81.9, 12.4, 14.2))
    for sx in (1.0, -1.0):
        x = sx * X_SCREW
        lug = slab(X, x, -0.7, S_END, 0.0, T)
        v.cut(X, lug, X.wbox(x - 5.0, x + 5.0, -86.0, -70.0, 14.2, 17.0))    # nothing above the sleeve's own top face
        v.add(X, t, lug)
    for sx in (1.0, -1.0):
        x = sx * X_SCREW
        v.cut(X, t,
              X.cyl(pt(x, S_HEAD, -3.0), pt(x, S_HEAD, T + 1.0), 1.1),                       # screw clearance, 2.2 across
              X.cyl(pt(x, S_HEAD, -0.3), pt(x, S_HEAD, SINK), 1.4 + SINK, 1.1))             # countersink
    G['GROMMET_usbc_F'] = t
    return t


def door(X):
    t = v.start(X, 'HOUSING_F_door')
    # the cutout's bottom edge lowered from z 13.3 to 12.0 across the sleeve: behind the grommet's flange
    v.cut(X, t, X.wbox(-10.7, 10.7, -85.0, -81.0, 12.0, 13.4))
    q = math.sqrt(0.5)
    for sx in (1.0, -1.0):
        x = sx * X_SCREW
        # block under the lug: its top face is the lug's seat; 2.0 of wall round the pilot
        boss = slab(X, x, -1.5, S_HEAD + 2.8, T, T + 5.0)
        # a 45 degree gusset under the block, so that it prints without support
        p0 = pt(x, S_HEAD + 2.8, T + 5.0)
        wedge = X.obox((x, p0[1] - 5.0 * q, p0[2] + 5.0 * q), (0.0, q, q), (1.0, 0.0, 0.0), 20.0, 2.0 * HALF, 10.0)
        X.sec(wedge, X.wbox(x - HALF, x + HALF, -82.5, p0[1] + 0.1, p0[2] - 3.5, p0[2] + 1.0))
        v.add(X, boss, wedge)
        X.sec(boss, X.wbox(x - HALF, x + HALF, -82.5, -70.0, 2.0, 20.0))       # none of it beyond the middle of the door's wall
        v.cut(X, boss, X.wbox(x - 4.0, x + 4.0, -83.0, -81.9, 12.2, 15.0))     # clear of the sleeve's thickened wall
        v.add(X, t, boss)
    for sx in (1.0, -1.0):
        x = sx * X_SCREW
        v.cut(X, t,
              X.cyl(pt(x, S_HEAD, T - 0.5), pt(x, S_HEAD, T + DEEP), 0.8),                   # pilot, 1.6 across
              X.cyl(pt(x, S_HEAD, T - 0.1), pt(x, S_HEAD, T + 0.3), 1.2, 0.8))               # 0.3 x 45 degree entry
    G['HOUSING_F_door'] = t
    return t


def build(X):
    grommet(X)
    door(X)
    return ['GROMMET_usbc_F', 'HOUSING_F_door']
