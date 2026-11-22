# Version 67 -> 68: the top cap.
# The two microphone strips and the light-sensor board were held by pins of the cap, melted over.
# Now one printed clamp on each side holds a strip and one edge of the sensor board, with one
# M2 x 6 flat-head screw for plastic into a boss of the cap. The cap's pins stay as locating pegs.
# The light opening moves so that it sits over the sensor of the board as measured.
#
# Dimensions are for the left-hand side (x > 0); sx = -1 gives the right-hand mirror image.
import sys

v = sys.modules['v68']; k = v.k; G = v.G

Z0 = 172.6                  # the cap's lowest plane = the clamps' underside
ZR = 177.5                  # underside of the cap's roof = the clamps' seat
SCREW = (15.5, -35.2)       # clamp screw
PEG = (32.75, -33.25)       # peg that stops the clamp turning with the screw
STRIP_PINS = ((11.5, -26.5), (30.0, -26.5))
SENSOR_PIN = (5.5, -28.23)
PORT_OLD = (0.0, -33.7)
PORT_NEW = (0.0, -31.73)    # 3.5 behind the sensor board's holes: where the measured board has its sensor
BOARD_Z = (175.76, 177.3)   # the sensor board, 1.54 thick, its front face on the cap's seats


def cap(X):
    """The cap with a screw boss and a peg per side, shorter pins, and the light opening moved."""
    t = v.start(X, 'HOUSING_F_cap')
    for sx in (1.0, -1.0):
        # boss, 6 across, standing down from the roof to z 174.6, with a 45 degree flare 1.0 at its root
        x, y = SCREW
        v.add(X, t, v.cyl(X, sx, x, y, 174.6, ZR + 0.1, 3.0), v.cyl(X, sx, x, y, 176.5, ZR + 0.1, 3.0, 4.1))
        # peg, 3 across, down to z 175.3, flared the same way
        x, y = PEG
        v.add(X, t, v.cyl(X, sx, x, y, 175.3, ZR + 0.1, 1.5), v.cyl(X, sx, x, y, 176.5, ZR + 0.1, 1.5, 2.6))
    for sx in (1.0, -1.0):
        # pilot for the self-tapper: 1.6 across up to z 179.0 (1.0 of roof stays over it), 0.3 x 45 degree entry
        x, y = SCREW
        v.cut(X, t, v.cyl(X, sx, x, y, 174.5, 179.0, 0.8), v.cyl(X, sx, x, y, 174.5, 174.9, 1.2, 0.8))
        # the strips' pins end inside the strip (z 177.0), so that a clamp toe can lie over each hole
        for x, y in STRIP_PINS:
            v.cut(X, t, v.cyl(X, sx, x, y, 174.7, 177.0, 1.0))
        # the sensor board's pins end 0.76 beyond the board's back
        x, y = SENSOR_PIN
        v.cut(X, t, v.cyl(X, sx, x, y, 173.6, 175.0, 1.0))
    # light opening: the old one filled; the new one 2.0 across, its inside end widened to 3.4
    v.add(X, t, v.cyl(X, 1.0, PORT_OLD[0], PORT_OLD[1], 178.3, 180.0, 1.02))
    x, y = PORT_NEW
    v.cut(X, t, v.cyl(X, 1.0, x, y, 178.2, 180.1, 1.0), v.cyl(X, 1.0, x, y, 178.2, 179.0, 1.8, 1.0))
    G['HOUSING_F_cap'] = t
    return t


def clamp(X, sx, lug_top=176.5, press=0.2):
    """One clamp. press = how far the sensor board bends the tip of the spring finger."""
    def b(*a):
        return v.box(X, sx, *a)
    t = b(9.8, 31.0, -31.6, -29.9, Z0, ZR)                        # rail, seated on the roof
    v.add(X, t,
          b(10.8, 20.2, -39.9, -31.5, Z0, ZR),                    # block round the cap's boss
          b(11.8, 29.0, -29.95, -27.0, Z0, 175.0),                # bar under the strip's rear half
          b(9.8, 11.8, -29.95, -24.5, Z0, 176.4),                 # inner finger
          b(29.0, 31.0, -29.95, -24.5, Z0, 176.4),                # outer finger
          b(9.8, 11.8, -28.5, -24.5, 176.3, 176.8),               # toes, 2 x 4, 0.7 below the seat
          b(29.0, 31.0, -28.5, -24.5, 176.3, 176.8),
          b(30.9, 36.2, -36.2, -29.9, 173.2, lug_top))            # lug round the cap's peg
    # the sensor board's spring: an arm from the inner finger, a flat finger 1.0 thick, a post at its tip
    v.add(X, t,
          b(6.6, 9.9, -26.3, -24.5, Z0, 175.0),
          b(6.6, 8.4, -38.4, -26.2, Z0, Z0 + 1.0),
          b(6.6, 8.4, -38.4, -36.6, Z0 + 0.9, BOARD_Z[0] + press))
    x, y = SCREW
    v.cut(X, t,
          v.cyl(X, sx, x, y, 174.45, ZR + 0.2, 3.4),              # pocket for the boss, 0.4 clear all round
          v.cyl(X, sx, x, y, 176.4, ZR + 0.1, 3.4, 4.6),          # widened for the boss's flare
          v.cyl(X, sx, x, y, Z0 - 0.1, 174.5, 1.1),               # screw clearance, 2.2 across
          v.cyl(X, sx, x, y, Z0 - 0.1, 173.7, 2.3, 1.1),          # countersink: head 3.8 x 1.2, flush
          b(30.8, 34.9, -34.9, -31.6, 175.0, lug_top + 0.1))      # slot for the peg, 3.3 wide
    # 1.0 x 45 degree chamfer on the block's lower edge beside the shell's shelf
    v.cut(X, t, X.obox((sx * 20.2, -35.95, Z0), (sx, 0.0, 1.0), (0.0, 1.0, 0.0), 1.41421, 8.7, 1.41421))
    return t


def sensor_board(X):
    """The light-sensor board as measured: 15.25 x 15.2 x 1.54; two holes 2.1 across, 11 apart and 2.0
    from one edge; the sensor 5.5 from that edge; the wires at the far edge."""
    z0, z1 = BOARD_Z
    yh = SENSOR_PIN[1]; y0 = yh + 2.0                             # y0 = the edge with the holes
    t = X.wbox(-7.625, 7.625, y0 - 15.2, y0, z0, z1)
    for sx in (1.0, -1.0):
        v.cut(X, t, v.cyl(X, sx, SENSOR_PIN[0], yh, z0 - 0.1, z1 + 0.1, 1.05))
    v.add(X, t,
          X.wbox(-1.0, 1.0, y0 - 6.5, y0 - 4.5, z1 - 0.1, z1 + 0.85),       # the sensor
          X.wbox(-5.9, 5.9, y0 - 15.2, y0 - 11.2, 173.1, z0 + 0.1))         # the wires under the pad row
    G['VEML_env'] = t
    return t


def mic_lead(X, sx):
    """A microphone lead, drawn on from where its body ended under the cap up to the strip's pads:
    in front of the clamp's bar and between its toes."""
    name = 'LEAD_MIC_L' if sx > 0 else 'LEAD_MIC_R'
    t = v.start(X, name)
    a = (sx * 21.0, -26.05, 171.7); e = (sx * 17.0, -24.8, 177.0)
    v.add(X, t, X.cyl(a, e, 1.0), X.sph(a, 1.0))
    G[name] = t
    return t


def build(X):
    cap(X)
    G['MIC_CLAMP_L'] = clamp(X, 1.0)
    G['MIC_CLAMP_R'] = clamp(X, -1.0)
    sensor_board(X)
    mic_lead(X, 1.0)
    mic_lead(X, -1.0)
    return ['HOUSING_F_cap', 'MIC_CLAMP_L', 'MIC_CLAMP_R', 'VEML_env', 'LEAD_MIC_L', 'LEAD_MIC_R']
