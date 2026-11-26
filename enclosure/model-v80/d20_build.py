# Block 1 (as temporary bodies, for the plan) and block 2 (the build): the drivers' seat. Builds temporary bodies and keeps
# them in the library's cache k.c; NOTHING IS PUT INTO THE DOCUMENT here (d21_put.py does that).
#
# World mm: x + = viewer's left, y + toward the screen, z up. Side 'L' is the viewer's left (x > 0), 'R' its mirror.
# Figures and their sources:
#   the driver (Dayton DMA45-4) as Daniel measured it, D481 (architect log 2026-11-26-f section 1, the brief's table):
#     flange 46 a side (the data sheet's, not measured) and 3.8 thick; screw holes 3.3 across, 35.5 between centres;
#     counterbores 6.3 across and 2.0 deep on the front face; foam 2.0 thick on the flange's back, one closed frame;
#     a rubber ring 36 across, 2.0 proud of the flange's front; about 25 deep behind the flange's back; 37.5 across at 13
#     from the rear end; about 34.25 across within the last 10 over the spade connector; the magnet 32 across (the record's, D485)
#   assumed, not measured: the basket 40 across where it meets the flange (the model's and the record's driver); 37.5 across
#     from 13 to 10 before the rear end; the connector drawn as a block as wide as the magnet, reaching 34.25 - 16 = 18.25
#     from the axis on one side; the ring drawn as a full disc (its inner edge is not measured); the foam's inner edge taken
#     as the box's opening, 40.6 across
#   the plan (claude/note-enclosure-drivers-seat-plan-2026-11-26.md): flange front stays at y 0.0; flange back y -3.8; foam
#     squeezed 2.0 -> 1.2 between the stops and taken as 0.2 on a stop; box front face y -5.0 (bed 47.0) below z 52.2; stops
#     8.0 across at y -4.0 (bed 48.0), flared 45 deg to 10.0 at the face; front wall 2.0 (inner face y -7.0) below z 54.2;
#     insert holes 4.0 across, 6.7 deep from the stops' tops; columns to y -12.6; the clip block's pilot 2.4 further back
#     (y -9.45) and the block y -12.8 to -5.0; the left box's pocket corner as an arc wall 16.3 to 17.8 from the driver's axis;
#     the clips' screw line also 3.0 off the clip's mid-height (block 2, after the key's sweep was read on version 80: with
#     the line 2.4 back at z 38 the 101 key's tip meets the door opening's arch at 58 to 59.5 deg): z 35.0 on the left box,
#     z 41.0 on the right, so that the right clip is still the left one turned top for bottom about z 38
#     the shell: lower bar removed, a channel for the ring to y 1.8 (bed 5.0) 18.75 either side of the axis, two side bars
#     x 47.5..51.5 and 89.5..93.5, z 14.6..41.4, faces at y 0.0, cut back to the recess's wall where they would hang over it
#     (block 2, third put: the first build left a lip 1.0 deep over the recess on each bar, a face that looks at the bed)
# The boxes and the shell are built from version 79's state: from the hidden copy <name>_v79 where it exists (after the first
# put), else from the body itself (before it). So a second run on version 80 builds the same bodies as the first on version 79.
# Stages: spk, box, shell, clip (each for both sides), all. Run: runpy.run_path(D + 'd20_build.py')['main'](stage)  -> d20_<stage>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
L = runpy.run_path(D + 'v80_lib.py')
AX = 70.5; AZ = 28.0; HALF = 17.75                      # the driver's axis; half of 35.5
Y_FRONT = 0.0; Y_BACK = -3.8; Y_FACE = -5.0; Y_STOP = -4.0; Y_INNER = -7.0; Y_HOLE = -10.7; Y_COL = -12.6
Z_STEP = 52.2; Z_STEP_IN = 54.2
Y_REAR = Y_BACK - 25.0                                  # the driver's rear end, -28.8
CLIP_Y = -9.45; CLIP_Z = 38.0; CLIP_REAR = -12.8        # the clip's screw line (y), the clip's mid-height, the rear face of clip and block
CLIP_DZ = 3.0                                           # the screw line's offset from the mid-height: down on the left, up on the right
POCKET_R = 16.3; POCKET_W = 1.5
POCKET_END = 0.4                                        # the relief's floor behind the magnet's rear end: y -29.2, bed 22.8 (on the grid; 0.3 would lie at 22.9)
BAND = 18.75; Y_CHAN = 1.8


def clip_z(sx):
    return CLIP_Z - CLIP_DZ if sx > 0 else CLIP_Z + CLIP_DZ


def src(X, name):
    return X.body(name + '_v79') or X.body(name)


def screws(sx):
    return [(sx * (AX + a * HALF), AZ + b * HALF) for a in (-1, 1) for b in (-1, 1)]


def spk(k, X, sx, up=(0.0, 1.0)):
    """The driver as one solid: flange with holes and counterbores, ring, basket, magnet, connector toward 'up' (x, z)."""
    cx = sx * AX
    t = X.wbox(cx - 23.0, cx + 23.0, Y_BACK, Y_FRONT, AZ - 23.0, AZ + 23.0)
    for px, pz in screws(sx):
        X.dif(t, X.cyl((px, Y_BACK - 0.1, pz), (px, Y_FRONT + 0.1, pz), 1.65))
        X.dif(t, X.cyl((px, Y_FRONT - 2.0, pz), (px, Y_FRONT + 0.1, pz), 3.15))
    X.uni(t, X.cyl((cx, Y_FRONT - 0.05, AZ), (cx, Y_FRONT + 2.0, AZ), 18.0))                      # the ring, as a disc
    X.uni(t, X.cyl((cx, Y_BACK + 0.05, AZ), (cx, Y_REAR + 13.0, AZ), 20.0, 18.75))               # basket, 40 -> 37.5
    X.uni(t, X.cyl((cx, Y_REAR + 13.05, AZ), (cx, Y_REAR + 10.0, AZ), 18.75))                    # 37.5 to the last 10
    X.uni(t, X.cyl((cx, Y_REAR + 10.05, AZ), (cx, Y_REAR, AZ), 16.0))                            # magnet, 32
    u = k.unit((up[0], 0.0, up[1])); v = (u[2], 0.0, -u[0])
    X.uni(t, X.obox((cx + u[0] * 9.125, Y_REAR + 5.0, AZ + u[2] * 9.125), u, v, 18.25, 32.0, 10.0))   # connector's envelope
    return t


def foam(k, X, sx):
    cx = sx * AX
    t = X.wbox(cx - 23.0, cx + 23.0, Y_FACE, Y_BACK, AZ - 23.0, AZ + 23.0)
    X.dif(t, X.cyl((cx, Y_FACE - 0.1, AZ), (cx, Y_BACK + 0.1, AZ), 20.3))
    for px, pz in screws(sx):
        X.dif(t, X.cyl((px, Y_FACE, pz), (px, Y_STOP, pz), 5.0, 4.0))
        X.dif(t, X.cyl((px, Y_FACE - 0.1, pz), (px, Y_BACK + 0.1, pz), 1.65))
    return t


def heads(k, X):
    t = None
    for sx in (1, -1):
        for px, pz in screws(sx):
            h = X.cyl((px, Y_FRONT - 2.0, pz), (px, Y_FRONT - 0.35, pz), 2.85)
            t = h if t is None else X.uni(t, h)
    return t


def air(k, X, name, sx):
    """The chamber's air of a box as it stands in the model (the record's method, k4a chambers), and the box filled with it."""
    x0, x1 = sorted((sx * 40.0, sx * 101.0))
    A = X.wbox(x0, x1, -60.0, 3.0, 1.0, 92.0)
    X.dif(A, X.cp(src(X, name)))
    X.dif(A, X.wbox(x0, x1, -3.7, -3.0, 1.0, 92.0))
    X.dif(A, X.cyl((sx * 62.0, -53.5, 30.0), (sx * 62.0, -49.0, 30.0), 2.2))
    pc = k.Wp(sx * AX, -30.0, 62.0)
    for lump in A.lumps:
        if lump.pointContainment(pc) == adsk.fusion.PointContainment.PointInsidePointContainment:
            return X.cp(lump)
    raise RuntimeError('no chamber lump in ' + name)


def box(k, X, sx):
    side = 'L' if sx > 0 else 'R'; name = 'SPKBOX_' + side
    cx = sx * AX
    x0, x1 = sorted((sx * 38.0, sx * 102.0))
    t = X.cp(src(X, name))
    a = air(k, X, name, sx)
    hull = X.cp(src(X, name)); X.uni(hull, X.cp(a))                                              # the box with its chamber filled
    # 1. the front face set back to y -5.0 below z 52.2
    X.dif(t, X.wbox(x0, x1, Y_FACE, 2.0, 0.0, Z_STEP))
    # 2. the front wall 2.0 again: the chamber's air between y -7.0 and the old inner face filled, below z 54.2
    s = X.wbox(x0, x1, Y_INNER, -5.5, 0.0, Z_STEP_IN); X.sec(s, X.cp(a)); X.uni(t, s)
    # 4. the clip block: solid from y -12.8 to the face, x 43.5..50.5, z 30..46 (the old pilot filled)
    xa, xb = sorted((sx * 43.5, sx * 50.5))
    X.uni(t, X.wbox(xa, xb, CLIP_REAR, Y_FACE, 30.0, 46.0))
    # 5. columns: 8.0 across from the wall's inner face to y -12.6 (the inner lower one is the long sleeve)
    for px, pz in screws(sx):
        if abs(abs(px) - (AX - HALF)) < 0.01 and pz < AZ:
            continue
        X.uni(t, X.cyl((px, Y_COL, pz), (px, Y_INNER + 0.1, pz), 4.0))
    # 6. the four stops: 8.0 across at y -4.0, flared 45 deg to 10.0 at the face, kept inside the box's own outline
    for px, pz in screws(sx):
        c = X.cyl((px, Y_FACE - 0.2, pz), (px, Y_STOP, pz), 5.2, 4.0); X.sec(c, X.cp(hull)); X.uni(t, c)
    # 3. the opening, 40.6 across, through the wall only (as before), cut after the stops so that a stop's flare ends at its edge
    X.dif(t, X.cyl((cx, Y_INNER, AZ), (cx, Y_STOP + 0.5, AZ), 20.3))
    c = X.cyl((cx, CLIP_REAR - 0.1, AZ), (cx, Y_INNER, AZ), 20.3)                                 # the clip block's lower corner kept out of the opening's line
    X.sec(c, X.wbox(*sorted((sx * 49.5, sx * 51.0)), CLIP_REAR - 0.2, Y_INNER + 0.1, 29.9, 32.0)); X.dif(t, c)
    # 7. the insert holes 4.0 across, 6.7 deep from the stops' tops; behind the outer pair a 2.5 hole 0.8 deep, as before
    for px, pz in screws(sx):
        X.dif(t, X.cyl((px, Y_HOLE, pz), (px, Y_STOP + 0.2, pz), 2.0))
        if abs(abs(px) - (AX + HALF)) < 0.01:
            X.dif(t, X.cyl((px, Y_HOLE - 0.8, pz), (px, Y_HOLE + 0.1, pz), 1.25))
    # 8. the clip's pilot, 2.7 across, along x, 5.75 deep as before
    X.dif(t, X.cyl((sx * 43.4, CLIP_Y, clip_z(sx)), (sx * 49.25, CLIP_Y, clip_z(sx)), 1.35))
    # 9. the left box's plug pocket: its corner toward the driver as an arc wall, 16.3 to 17.8 from the axis, over the magnet's length
    if sx > 0:
        ya = Y_REAR - POCKET_END; yb = -19.3
        c = X.cyl((cx, ya, AZ), (cx, -19.45, AZ), POCKET_R + POCKET_W); X.sec(c, X.wbox(53.0, 57.15, ya - 1, -19.0, 17.0, 22.2)); X.uni(t, c)
        r0 = math.hypot(AX - 55.65, AZ - 20.7)                                                   # the pocket's inner corner, 16.547 from the axis
        c = X.cyl((cx, ya - 2.6, AZ), (cx, ya, AZ), r0, POCKET_R + POCKET_W); X.sec(c, X.wbox(53.0, 55.65, ya - 3, ya + 0.1, 17.0, 20.7)); X.uni(t, c)   # the lead-in below it
        X.dif(t, X.cyl((cx, ya, AZ), (cx, yb, AZ), POCKET_R))
    return t


def shell(k, X):
    t = X.cp(src(X, 'HOUSING_F_front'))
    for sx in (1, -1):
        cx = sx * AX
        X.dif(t, X.wbox(cx - BAND, cx + BAND, -1.0, Y_CHAN, 2.0, AZ))                             # the ring's channel, with the lower bar
        for a, b in ((-23.0, -19.0), (19.0, 23.0)):                                               # the two side bars
            bar = X.wbox(cx + a, cx + b, 0.0, 1.4, 14.6, 41.4)
            X.dif(bar, X.cyl((cx, -0.2, AZ), (cx, 1.6, AZ), 20.0))                                # not over the recess (40 across): no lip hangs over it in the print
            X.uni(t, bar)
    return t


def clip(k, X, sx):
    xs = lambda a, b: sorted((sx * a, sx * b))
    t = X.wbox(*xs(40.5, 43.5), CLIP_REAR, -0.5, 30.0, 46.0)
    X.uni(t, X.wbox(*xs(43.4, 45.0), Y_FACE + 0.4, -0.5, 30.0, 46.0))
    X.uni(t, X.wbox(*xs(43.6, 45.0), -0.6, 2.8, 30.0, 46.0))
    cz = clip_z(sx)
    for dy in (-0.4, 0.4):
        X.dif(t, X.cyl((sx * 40.4, CLIP_Y + dy, cz), (sx * 43.6, CLIP_Y + dy, cz), 1.7))
    X.dif(t, X.wbox(*xs(40.4, 43.6), CLIP_Y - 0.4, CLIP_Y + 0.4, cz - 1.7, cz + 1.7))
    return t


def say(k, X, key, t, ref=None):
    k.c[key] = t
    r = X.body(ref) if ref else None
    print('%-12s %12.3f mm3, lumps %d, faces %d%s' % (key, X.vol(t), t.lumps.count, t.faces.count,
          (' | %s in the model %.3f, lumps %d, faces %d' % (ref, r.volume * 1000, r.lumps.count, r.faces.count)) if r else ''))


def _main(stage):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    if stage in ('spk', 'all'):
        for sx, s in ((1, 'L'), (-1, 'R')):
            say(k, X, 'ds_spk_' + s, spk(k, X, sx), 'SPK_' + s)
            say(k, X, 'ds_foam_' + s, foam(k, X, sx))
        say(k, X, 'ds_heads', heads(k, X), 'DRV_screw_heads_env')
    if stage in ('box', 'all'):
        for sx, s in ((1, 'L'), (-1, 'R')):
            say(k, X, 'ds_box_' + s, box(k, X, sx), 'SPKBOX_' + s)
    if stage in ('clip', 'all'):
        for sx, s in ((1, 'L'), (-1, 'R')):
            say(k, X, 'ds_clip_' + s, clip(k, X, sx), 'TOUCH_CLIP_' + s)
    if stage in ('shell', 'all'):
        say(k, X, 'ds_shell', shell(k, X), 'HOUSING_F_front')
    print(L['stamp'](), 'after', X.state())


def main(stage='all'):
    L['out']('d20_%s.txt' % stage, _main, stage)
# END
