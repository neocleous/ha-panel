"""The main board's site behind the display, as numbers (claude/main-board-site-2026-11-10.md, issue 2,
with the enclosure's findings of 2026-11-11 for the right-hand top post and the display's power lead): rev 3.1.
Board frame: u to the right seen from the door (toward the left speaker), v up the slab, w out of the door-side face.
KiCad: X = u + 43.5, Y = 28.95 - v, front copper = door side (site document section 0)."""
import math

U0, V0 = 43.5, 28.95                    # half outline: 87.0 x 57.9 (section 1)
RESPEAKER = (-40.1, -20.55, 41.9, 13.46)        # u0, v0, u1, v1 behind the board (section 1)

# Allowed part height on the door-side face: depth to the door or shell minus 2.0, grid +/- 1 (section 1)
HU = [-42.5, -32.5, -22.5, -12.5, -2.5, 7.5, 17.5, 27.5, 37.5, 42.5]
HV = [27.4, 22.4, 17.4, 12.4, 7.4, 2.4, -2.6, -7.6, -12.6, -17.6, -22.6, -27.6]
HT = [[23, 26, 28, 30, 31, 29, 28, 25, 23, 20],
      [24, 28, 32, 33, 33, 33, 32, 28, 24, 23],
      [28, 33, 35, 36, 36, 36, 35, 33, 28, 26],
      [31, 35, 37, 38, 38, 38, 37, 35, 30, 28],
      [35, 38, 39, 40, 40, 40, 39, 37, 35, 31],
      [37, 40, 42, 43, 43, 43, 42, 39, 37, 33],
      [40, 42, 44, 45, 45, 45, 44, 41, 39, 37],
      [42, 45, 46, 47, 47, 47, 46, 44, 42, 40],
      [44, 47, 49, 49, 49, 49, 48, 46, 44, 42],
      [46, 49, 51, 51, 51, 51, 50, 48, 46, 44],
      [48, 51, 53, 53, 53, 53, 52, 50, 48, 46],
      [50, 53, 54, 55, 55, 55, 54, 52, 50, 48]]


def _bracket(xs, x, descending=False):
    """Indices of the grid nodes on both sides of x (clamped)."""
    n = len(xs)
    if descending:
        if x >= xs[0]:
            return 0, 0
        if x <= xs[-1]:
            return n - 1, n - 1
        for i in range(n - 1):
            if xs[i] >= x >= xs[i + 1]:
                return i, i + 1
    else:
        if x <= xs[0]:
            return 0, 0
        if x >= xs[-1]:
            return n - 1, n - 1
        for i in range(n - 1):
            if xs[i] <= x <= xs[i + 1]:
                return i, i + 1
    return 0, 0


def door_grid(u, v):
    """Lowest of the four grid nodes round (u, v): a conservative reading of the table."""
    i0, i1 = _bracket(HV, v, True)
    j0, j1 = _bracket(HU, u)
    return min(HT[i][j] for i in (i0, i1) for j in (j0, j1))


def in_cap_back_strip(u):
    return 18.0 <= u <= 25.5 or -30.5 <= u <= -23.0          # section 3, run down from the top edge


def cap_side_centre(v, side):
    return 29.2 + 0.196 * (v + 2.95) if side > 0 else -34.2 - 0.196 * (v + 2.95)


def in_cap_side_strip(u, v):
    return abs(u - cap_side_centre(v, 1)) <= 3.5 or abs(u - cap_side_centre(v, -1)) <= 3.5


def door_allowed(u, v):
    """Allowed height w at a point of the door-side face, with the key-path limits of section 3."""
    h = door_grid(u, v)
    why = 'door'
    if in_cap_back_strip(u):
        k = 38.2 - 0.74 * v
        if k < h:
            h, why = k, 'cap back-screw key path'
    if in_cap_side_strip(u, v):
        k = 35.2 - 0.79 * v
        if k < h:
            h, why = k, 'cap side-screw key path'
    return h, why


def door_allowed_rect(r):
    """Lowest allowed height over a rectangle (u0, v0, u1, v1), sampled every 0.5 mm."""
    u0, v0, u1, v1 = r
    best = (1e9, '')
    nu = max(1, int(math.ceil((u1 - u0) / 0.5)))
    nv = max(1, int(math.ceil((v1 - v0) / 0.5)))
    for i in range(nu + 1):
        for j in range(nv + 1):
            h = door_allowed(u0 + (u1 - u0) * i / nu, v0 + (v1 - v0) * j / nv)
            if h[0] < best[0]:
                best = h
    return best


# Allowed part height on the back face, 1.0 clear already taken off (section 1)
BACK_ZONES = [   # (name, u0, v0, u1, v1, allowed)
    ("ReSpeaker's header (bare board)", 33.8, -7.5, 40.8, 0.4, 0.0),
    ("ReSpeaker's audio jack", 28.9, -18.4, 43.5, -9.7, 0.9),
    ("ReSpeaker's USB socket", 35.4, 2.7, 42.8, 11.7, 3.0),
    ("beside the ReSpeaker's USB plug", 42.8, 1.0, 43.5, 13.4, 1.4),
]


def back_allowed(u, v):
    best = None
    for name, a, b, c, d, h in BACK_ZONES:
        if a <= u <= c and b <= v <= d and (best is None or h < best[0]):
            best = (h, name)
    if best:
        return best
    if v < -20.6:
        return 12.0, 'bottom band'
    if v > 13.5:
        return 5.0, 'top band'
    return 4.0, 'over the ReSpeaker'


def back_allowed_rect(r):
    u0, v0, u1, v1 = r
    best = (1e9, '')
    for u in (u0, (u0 + u1) / 2, u1):
        for v in (v0, (v0 + v1) / 2, v1):
            h = back_allowed(u, v)
            if h[0] < best[0]:
                best = h
    return best


# Mounting (section 2, issue 2)
HOLE_D = 3.2
POST_ZONE_BACK = 9.0          # clear diameter on the back face (post dia 8)
HEAD_ZONE_FRONT = 7.0         # clear diameter on the door side (screw head dia 5.7)
LCD_POINTS = [(-18.95, -24.48), (39.05, -24.48), (-18.95, 24.52), (39.05, 24.52)]      # display's Pi mounting points


def post_zone_ok(u, v):
    """Where post centres may stand: section 2 of the site document, with the zone for the right-hand top post
    replaced by the enclosure's findings of 2026-11-11 (claude/main-board-rev3-enclosure-findings-2026-11-11.md,
    section 2): the old band left out the plug on the display's own power header."""
    if abs(v + 25.25) <= 0.2:
        return (-38.5 <= u <= -26.0) or (-12.0 <= u <= 32.0), 'bottom band v -25.25 +/- 0.2'
    if u > -20.0:                                   # the right-hand top post
        return (-12.0 <= u <= 22.7 and 21.6 <= v <= 25.5), 'new zone u -12.0...+22.7, v +21.6...+25.5'
    if abs(v - 18.0) < 1e-6:
        return (-38.5 <= u <= -21.5), 'top band at v +18.0'
    if 18.0 <= v <= 25.5:
        return (-38.5 <= u <= -26.0), 'top band v +18.0...+25.5'
    return False, 'outside the zones'


# The display's power lead behind the board (findings, section 5): pin ends 4.0 or less in these strips (u0, v0, u1, v1)
LEAD_STRIPS = [(-42.1, 14.0, 30.0, 17.1), (-43.6, -28.95, -40.6, 17.1)]
LEAD_PIN_LIMIT = 4.0


# Keep-outs drawn in the picture (section 3)
DISPLAY_SCREW_STRIPS = [(44.0, 51.0), (-51.0, -44.0)]          # u ranges, outside the outline
DISPLAY_SCREW_V = [(-31.2, -22.7), (22.8, 31.3)]               # where they cross the board plane
MIC_LEADS = [(34.5, 36.5), (-34.5, -30.5)]                      # u ranges behind the back face
XIAO_ROWS = [(-37.17, -21.93, -11.16), (-37.17, -21.93, 4.08)]  # ReSpeaker's empty XIAO footprint (u0, u1, v), from
#   hardware/envelopes/revF-envelopes.md (X 2.93-18.17, Y 9.39 / 24.63) and the ReSpeaker's corner at u -40.1, v -20.55

# Connector zones and reach (section 5): (name, u0, v0, u1, v1, fingertip, pinch)
ZONES = [
    ('A', -14.0, -28.95, 14.0, -20.0, '6 of 6', '5 of 6'),
    ('B', -43.5, -28.95, -18.0, -20.0, '5 of 6', 'no'),
    ('C', 18.0, -28.95, 43.5, -20.0, '4 of 6', 'no'),
    ('D', -43.5, -18.0, -33.5, -2.0, '3 of 6', 'no'),
    ('E', -10.0, -6.0, 10.0, 6.0, '6 of 6', '6 of 6'),     # box as drawn; probed at u -0.5, v -0.5
]
TOP_THIRD_V = V0 - 2 * V0 / 3            # +9.65: nothing that is plugged in place above this line
NID_UPRIGHT_MAX_V = 8.0                  # section 4
PLUG20_MAX_V = 18.0                      # section 4: 20 mm plug-plus-bend anywhere below v +18
CORNER_PLUG_LIMIT_U = 47.0               # section 3: plugs and leads at the lower corners stay inside u +/- 47
