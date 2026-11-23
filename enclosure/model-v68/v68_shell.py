# Version 67 -> 68: the shell and the BME680 hood.
#
# Radar board (Hi-Link LD2410C, 22 x 16, no holes): it stood in its pocket behind two ribs that were
# to be melted over its edge. Now two M2 x 6 flat-head screws for plastic sit 1.0 outside its two long
# edges, low down (z 119, below the row of pins whichever edge carries it). Each head overlaps the
# board's edge and presses it onto its ledge; the screws are driven until the board is held.
# They lean 15 degrees, handle down, so that the driver passes under the lip over the door opening.
#
# BME680 hood: its two pins were glued. Now one M2 x 6 through a new ear of the hood into a new boss
# on the tray's end wall at the door end. Both pins stay as plain pegs.
import sys, math

v = sys.modules['v68']; k = v.k; G = v.G
Q = math.sqrt(0.5)


def unit(a):
    n = math.sqrt(sum(q * q for q in a))
    return tuple(q / n for q in a)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


# ---------- the radar pocket's own frame ----------
EW = (0.515, 0.857, 0.0)        # along the board's 16 width, toward the screen
NIN = (0.857, -0.515, 0.0)      # into the unit; d = 0 is the board's antenna face on its ledge
C0 = (-72.53, -22.05)           # the antenna face's centre line
R_E, R_D, R_Z = 9.0, 2.2, 119.0  # a screw's head: 1.0 outside the board's edge; its top face 2.2 behind the ledge for a board 1.0 thick
C15, S15 = math.cos(math.radians(15.0)), math.sin(math.radians(15.0))


def rp(e, d, z):
    return (C0[0] + e * EW[0] + d * NIN[0], C0[1] + e * EW[1] + d * NIN[1], z)


def rbox(X, e0, e1, d0, d1, z0, z1):
    e0, e1 = sorted((e0, e1))
    return X.obox(rp((e0 + e1) / 2.0, (d0 + d1) / 2.0, (z0 + z1) / 2.0), EW, NIN, e1 - e0, d1 - d0, z1 - z0)


def raxis(sg, t):
    """A point on a radar screw's line: t = 0 at the head's top face, t > 0 toward the tip."""
    return rp(sg * R_E, R_D - C15 * t, R_Z + S15 * t)


def radar_head(sg):
    """Centre of the head's top face, and the driver's direction."""
    return raxis(sg, 0.0), (NIN[0] * C15, NIN[1] * C15, -S15)


def radar_tools(X):
    add = None; cut = None
    for sg in (1.0, -1.0):
        dmin = -5.2 if sg > 0 else -6.6       # the screen plate lies close on the screen side; the other side is filled to the shell's wall
        dmid = (dmin + 2.0) / 2.0
        # block on the rib's outer side: 2.0 of wall outside the pilot, with a 45 degree underside
        a = rbox(X, sg * 10.1, sg * 11.8, dmin, 2.0, 116.0, 122.4)
        w = X.obox(rp(sg * (11.8 - 5.0 * Q), dmid, 116.0 + 5.0 * Q), (sg * Q * EW[0], sg * Q * EW[1], Q), NIN, 20.0, 2.0 - dmin, 10.0)
        X.sec(w, rbox(X, sg * 10.1, sg * 11.8, dmin, 2.0, 114.2, 116.05))
        X.uni(a, w)
        # strip in the corner of the opening in front of the board: brings the wall on that side of the pilot to 1.6
        X.uni(a, rbox(X, sg * 6.6, sg * 7.2, -5.2, -0.01, 117.3, 123.2))
        add = a if add is None else X.uni(add, a)
        c = X.cyl(raxis(sg, -6.0), raxis(sg, 0.3), 2.2)                       # room for the head and the driver through the rib's end
        X.uni(c, X.cyl(raxis(sg, 0.2), raxis(sg, 1.4), 2.3, 1.1))             # countersink; the head stops on the board, 0.3 before its seat
        X.uni(c, X.cyl(raxis(sg, 1.3), raxis(sg, 6.75), 0.8))                 # pilot, 1.6 across
        X.uni(c, rbox(X, sg * 8.1, sg * 9.0, 0.0, 0.95, 118.5, 120.45))       # beside the board's edge the pilot is open to the pocket
        X.uni(c, rbox(X, sg * 8.0, sg * 10.3, 4.0, 5.6, 124.4, 130.6))        # the rib that was to be melted goes
        cut = c if cut is None else X.uni(cut, c)
    return add, cut


# ---------- the tray's end wall at the door end, at z 100, and the hood's own frame ----------
T0 = (-59.82, -47.43)           # the corner of the wall's outer face and its end
LW = unit((0.65, -0.76, 0.0))   # out of the wall's outer face, toward the door
WW = (-LW[1], LW[0], 0.0)       # along the wall toward its end
HA = unit(cross(LW, (0.7516, 0.6429, -0.1503)))    # the hood's own up: square to its top plate
HN = cross(HA, LW)              # square to its side plate, toward the room
TOP = (95.83, 97.02)            # the top plate lies between these two planes (measured along HA)
SIDE = (-90.43, -89.23)         # the side plate lies between these two planes (measured along HN)
L_T0 = T0[0] * LW[0] + T0[1] * LW[1]
H_Z = 100.0
HU = (math.cos(math.radians(22.0)), -math.sin(math.radians(22.0)), 0.0)    # from the screw's tip to its head: the driver's line
HT = (-HU[1], HU[0], 0.0)       # level, square to the screw
HE = (T0[0] - 2.5 * WW[0], T0[1] - 2.5 * WW[1], H_Z)                       # where the screw enters the wall's face: 2.5 from the wall's end
H_BOSS = 2.9                    # the boss's length
H_EAR = 1.85                    # the ear's thickness
H_GAP = 0.1                     # between boss and ear before the screw is driven


def hp(t, side=0.0, dz=0.0):
    """A point on the hood screw's line: t from the wall's face toward the head; side along HT; dz up."""
    return (HE[0] + t * HU[0] + side * HT[0], HE[1] + t * HU[1] + side * HT[1], H_Z + dz)


def hood_head():
    return hp(H_BOSS + H_GAP + H_EAR), HU


def hood_slab(X, l0, l1, n0, n1, a0, a1):
    """A box in the hood's own frame: l out of the end wall's face, n along HN, a along HA."""
    l = (l0 + l1) / 2.0 + L_T0; n = (n0 + n1) / 2.0; a = (a0 + a1) / 2.0
    c = tuple(l * LW[i] + n * HN[i] + a * HA[i] for i in range(3))
    return X.obox(c, LW, HN, l1 - l0, n1 - n0, a1 - a0)


def hood_boss_tools(X):
    # boss 6 across round the screw's line, flat underneath, with a 45 degree gusset below it
    a = X.cyl(hp(-0.8), hp(H_BOSS), 3.0)
    X.uni(a, X.obox(hp((H_BOSS - 0.8) / 2.0, 0.0, -1.5), HU, HT, H_BOSS + 0.8, 6.0, 3.0))
    p0 = hp(H_BOSS, 0.0, -3.0)
    w = X.obox((p0[0] - 5.0 * Q * HU[0], p0[1] - 5.0 * Q * HU[1], p0[2] + 5.0 * Q), (Q * HU[0], Q * HU[1], Q), HT, 20.0, 6.0, 10.0)
    X.sec(w, X.obox(hp((H_BOSS - 1.0) / 2.0, 0.0, -4.7), HU, HT, H_BOSS + 1.0, 6.0, 3.6))
    X.uni(a, w)
    # none of it where the hood's side plate lies against the wall's end, nor within 0.4 of that plate's end face
    X.dif(a, hood_slab(X, -3.0, 0.4, SIDE[0] - 0.05, SIDE[0] + 4.0, 78.0, 94.0))
    c = X.cyl(hp(H_BOSS + 0.3), hp(H_BOSS + H_GAP + H_EAR - 6.4), 0.8)        # pilot, 0.4 beyond the screw's tip
    X.uni(c, X.cyl(hp(H_BOSS + 0.1), hp(H_BOSS - 0.3), 1.2, 0.8))             # 0.3 x 45 degree entry
    return a, c


def shell_tools(X):
    ra, rc = radar_tools(X)
    ha, hc = hood_boss_tools(X)
    k.c['v68_shell_add'] = X.uni(ra, ha)
    k.c['v68_shell_cut'] = X.uni(rc, hc)
    return k.c['v68_shell_add'], k.c['v68_shell_cut']


def shell_apply(X):
    t = v.start(X, 'HOUSING_F_front')
    X.uni(t, X.tbm.copy(k.c['v68_shell_add']))
    X.dif(t, X.tbm.copy(k.c['v68_shell_cut']))
    G['HOUSING_F_front'] = t
    return t


def hood(X):
    t = v.start(X, 'BME_HOOD')
    hd, u = hood_head()
    m = (hd[0] - 0.5 * H_EAR * HU[0], hd[1] - 0.5 * H_EAR * HU[1])
    up = (0.0, 0.0, 1.0)
    # the ear: a plate square to the screw in front of the boss, 6.1 wide round the screw (z 96.95 to 103.5) ...
    ear = X.obox((m[0], m[1], 100.225), HT, up, 6.1, 6.55, H_EAR)
    # ... hung from the top plate by its room-side part (the other part would meet the door opening's frame higher up)
    X.uni(ear, X.obox((m[0] + 1.225 * HT[0], m[1] + 1.225 * HT[1], 106.2), HT, up, 3.65, 5.6, H_EAR))
    # the top plate drawn out over the ear, and the side plate's end drawn out to it above the boss
    X.uni(ear, hood_slab(X, 0.9, 4.6, -93.4, -89.2, TOP[0], TOP[1]))
    X.uni(ear, hood_slab(X, -0.5, 2.2, SIDE[0], SIDE[1], 91.13, 95.78))
    # nothing of it beyond the ear's outer face, nor above the top plate
    X.dif(ear, X.obox((hd[0] + 5.0 * HU[0], hd[1] + 5.0 * HU[1], 103.0), HT, up, 40.0, 40.0, 10.0))
    top0 = tuple(L_T0 * LW[i] - 92.4 * HN[i] + (TOP[1] + 5.0) * HA[i] for i in range(3))
    X.dif(ear, X.obox(top0, LW, HN, 40.0, 40.0, 10.0))
    X.uni(t, ear)
    X.dif(t, X.cyl((hd[0] + 1.0 * u[0], hd[1] + 1.0 * u[1], hd[2]), (hd[0] - 3.0 * u[0], hd[1] - 3.0 * u[1], hd[2]), 1.1))        # screw clearance, 2.2 across
    X.dif(t, X.cyl((hd[0] + 0.1 * u[0], hd[1] + 0.1 * u[1], hd[2]), (hd[0] - 1.1 * u[0], hd[1] - 1.1 * u[1], hd[2]), 2.3, 1.1))   # countersink, head flush
    G['BME_HOOD'] = t
    return t


def build(X):
    shell_tools(X)
    shell_apply(X)
    hood(X)
    return ['HOUSING_F_front', 'BME_HOOD']
