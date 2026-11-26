# Block 3 (D458, D471): the level faces that carry or face a fit, onto their print's layer grid. Builds temporary bodies and
# keeps them in the library's cache k.c; NOTHING IS PUT INTO THE DOCUMENT here (d21_put.py does that).
#
# Built from the model as block 2 left it (version 82). World mm: x + = viewer's left, y + toward the screen, z up.
#   FLOOR_PLATE (prints underside down, height = z)                                              key b3_plate
#     E  its top, z 2.5 -> 2.4. Everything that stands on the top keeps its own height: under each riser its first 0.1 is
#        repeated downward, and the eight tapered roots (the Pi posts', the cradle posts') are carried on down as cones
#     C  the six box seats, z 3.7 -> 3.8 (the pads 0.1 taller; the boxes' bottoms follow, below)
#     D  the four foot recess floors, z 0.5 -> 0.4 (PR41)
#     F  the two noses' undersides, z 4.35 -> 4.4
#     G  the four shoulders round the Pi's seats, z 7.5 -> 7.4, and the web between the cradle posts, z 12.5 -> 12.4.
#        Nothing stands on them: the Pi sits on four collars at z 8.0 and the cradle on its posts at z 13.0 (d30 front)
#   SPKBOX_L, SPKBOX_R (print rear face down, bed y -52)                                         keys b3_box_L, b3_box_R
#     C  the bottom face, z 3.7 -> 3.8, so that each box stays where it is (floor 1.5 -> 1.4; floor insert holes 6.4 deep)
#     I  the tab's top face, y -0.78 -> -0.80 (bed 51.2)
#     left box only: the plug pocket's end wall, its face toward the USB-A plug, y -20.95 -> -20.80 (bed 31.2): a face that
#        looks at the bed and faces the plug at 0.49; not on D458's list (this pass's choice, reported)
#   HOUSING_F_front (prints chin down, bed y 6.7992)                                             key b3_shell
#     H  the lip's face under the cap's seam, y -23.3 -> -23.2 (bed 30.0); the tip of the door frame's left lower end,
#        y -63.5 -> -63.4 (bed 70.2)
#   FOOT_FL, FOOT_FR, FOOT_RL, FOOT_RR (bought)                                                  keys b3_foot_FL ...
#     D  0.1 down with their recess floors
# Stages: plate, boxes, shell, feet, all; diff(names) compares what is built with the model's bodies.
# Run: runpy.run_path(D + 'd31_build3.py')['main'](stage)  -> d31_<stage>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/drivers_seat_v80/'
L = runpy.run_path(D + 'v80_lib.py')
PLN = adsk.core.SurfaceTypes.PlaneSurfaceType
CON = adsk.core.SurfaceTypes.ConeSurfaceType
TOP0 = 2.5; TOP1 = 2.4
SEATS = [(-82.0, -30.0), (-72.0, -38.0), (-51.0, -14.0), (51.0, -14.0), (64.0, -45.0), (82.0, -30.0)]
SEAT0 = 3.7; SEAT1 = 3.8
RECESS = [(80.0, -5.5), (-80.0, -5.5), (30.0, -70.6), (-30.0, -70.6)]
PI = [(-39.65, -54.5), (-39.65, -5.5), (18.35, -54.5), (18.35, -5.5)]
CRADLE = [(-1.5, -72.5), (6.5, -72.5)]
KEYS = {'FLOOR_PLATE': 'b3_plate', 'SPKBOX_L': 'b3_box_L', 'SPKBOX_R': 'b3_box_R', 'HOUSING_F_front': 'b3_shell',
        'FOOT_FL': 'b3_foot_FL', 'FOOT_FR': 'b3_foot_FR', 'FOOT_RL': 'b3_foot_RL', 'FOOT_RR': 'b3_foot_RR'}
BIGX = (-120.0, 120.0); BIGY = (-110.0, 30.0)


def slab(X, z0, z1):
    return X.wbox(BIGX[0], BIGX[1], BIGY[0], BIGY[1], z0, z1)


def cones_on_top(k, b):
    """The cone faces that rise from the plate's top face: axis place, radius at z 2.5, radius gained per unit of height
    (negative: it narrows upward), read from the face's own edges."""
    top = None
    for f in b.faces:
        if f.geometry.surfaceType != PLN or f.area * 100 < 5000:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
        if k.wv(nv)[2] > 0.999 and abs(k.W(f.pointOnFace)[2] - TOP0) < 0.003:
            top = f
    if top is None:
        raise RuntimeError('no top face at z %.2f' % TOP0)
    out = []; seen = {}
    for e in top.edges:
        for g in e.faces:
            if g.tempId in seen or g.geometry.surfaceType != CON:
                continue
            seen[g.tempId] = 1
            o = k.W(g.geometry.origin)
            pts = []
            for ee in g.edges:
                ev = ee.evaluator; ok, t0, t1 = ev.getParameterExtents(); ok, sp = ev.getStrokes(t0, t1, 0.005)
                pts += [k.W(q) for q in sp]
            lo = [q for q in pts if abs(q[2] - TOP0) < 0.002]
            zt = max(q[2] for q in pts); hi = [q for q in pts if abs(q[2] - zt) < 0.002]
            r0 = sum(math.hypot(q[0] - o[0], q[1] - o[1]) for q in lo) / len(lo)
            r1 = sum(math.hypot(q[0] - o[0], q[1] - o[1]) for q in hi) / len(hi)
            out.append((round(o[0], 3), round(o[1], 3), r0, (r1 - r0) / (zt - TOP0), zt))
    return out


def plate(k, X):
    src = X.body('FLOOR_PLATE')
    t = X.cp(src)
    v0 = X.vol(t)
    # E. the top to 2.4
    A = slab(X, TOP0, TOP0 + 0.1); X.sec(A, X.cp(src))                     # the risers' first 0.1
    keep = X.move(X.cp(A), 0.0, 0.0, -(TOP0 - TOP1))
    cs = cones_on_top(k, src)
    for (cx, cy, r0, slope, zt) in cs:
        rb = r0 - slope * (TOP0 - TOP1)                                      # the cone carried on down to the new top
        fr = X.cyl((cx, cy, TOP1), (cx, cy, TOP0), rb, r0)
        how = 'whole'
        if any(abs(cx - q[0]) < 0.01 and abs(cy - q[1]) < 0.01 for q in CRADLE) and zt > 5.0:
            # the cradle posts' buttress cones (14 deg, to z 8.5) stand on the rear side of their post only (y below the
            # post's axis) and end at the flats x -5.5 and x 10.5 (d30 cones): carried down inside the same bounds
            a, b = (cx - 20.0, 10.5) if cx > 0 else (-5.5, cx + 20.0)
            X.sec(fr, X.wbox(a, b, cy - 20.0, cy, TOP1 - 0.1, TOP0 + 0.1))
            how = 'x %.1f to %.1f, y below %.1f' % (a, b, cy)
        X.uni(keep, fr)
        print('   tapered root at (%.2f, %.2f): %.4f across at z %.1f, %.4f at z %.1f (it narrows %.4f a mm, to z %.3f); carried down %s' % (
            cx, cy, 2 * r0, TOP0, 2 * rb, TOP1, -slope, zt, how))
    cut = slab(X, TOP1, TOP0); X.dif(cut, keep)
    X.dif(t, cut)
    v1 = X.vol(t); print('E  top %.1f -> %.1f: %.3f removed' % (TOP0, TOP1, v0 - v1))
    # C. the six seats to 3.8
    for (cx, cy) in SEATS:
        s = X.cyl((cx, cy, SEAT0 - 0.1), (cx, cy, SEAT0), 4.3); X.sec(s, X.cp(t))
        X.uni(t, X.move(s, 0.0, 0.0, SEAT1 - SEAT0))
    v2 = X.vol(t); print('C  six seats %.1f -> %.1f: %.3f added' % (SEAT0, SEAT1, v2 - v1))
    # D. the four recess floors to 0.4 deep
    for (cx, cy) in RECESS:
        X.uni(t, X.wbox(cx - 7.2, cx + 7.2, cy - 7.2, cy + 7.2, 0.4, 0.5))
    v3 = X.vol(t); print('D  four recess floors 0.5 -> 0.4: %.3f added' % (v3 - v2))
    # F. the noses' undersides to 4.4
    for sx in (1, -1):
        a, b = sorted((sx * 24.5, sx * 35.5))
        X.dif(t, X.wbox(a, b, 1.15, 2.05, 4.3, 4.4))
    v4 = X.vol(t); print('F  two noses\' undersides 4.35 -> 4.4: %.3f removed' % (v3 - v4))
    # G. the shoulders round the Pi's seats to 7.4; the web between the cradle posts to 12.4
    for (cx, cy) in PI:
        r = X.cyl((cx, cy, 7.4), (cx, cy, 7.55), 3.95); X.dif(r, X.cyl((cx, cy, 7.3), (cx, cy, 7.6), 3.4)); X.dif(t, r)
    w = X.wbox(-1.5, 6.5, -76.5, -72.5, 12.4, 12.55)
    for (cx, cy) in CRADLE:
        X.dif(w, X.cyl((cx, cy, 12.3), (cx, cy, 12.6), 4.0))
    X.dif(t, w)
    v5 = X.vol(t); print('G  four shoulders 7.5 -> 7.4 and the web 12.5 -> 12.4: %.3f removed' % (v4 - v5))
    return t


def box(k, X, sx):
    side = 'L' if sx > 0 else 'R'; name = 'SPKBOX_' + side
    src = X.body(name); t = X.cp(src); v0 = X.vol(t)
    X.dif(t, slab(X, SEAT0 - 0.2, SEAT1))                                   # C. the bottom to 3.8
    v1 = X.vol(t); print('%s C  bottom %.1f -> %.1f: %.3f removed' % (name, SEAT0, SEAT1, v0 - v1))
    a, b = sorted((sx * 54.0, sx * 63.1))
    X.dif(t, X.wbox(a, b, -0.80, -0.5, 75.5, 84.5))                          # I. the tab's top to y -0.80
    v2 = X.vol(t); print('%s I  tab top -0.78 -> -0.80: %.4f removed' % (name, v1 - v2))
    if sx > 0:
        # the pocket's end wall, its face toward the plug: the pocket's own air just below it, carried 0.15 up into the wall
        air = X.wbox(40.0, 60.0, -21.10, -20.95, 4.0, 24.0); X.dif(air, X.cp(t))
        best = None
        pin = k.Wp(50.92, -21.02, 12.75)                                    # under the plug's nearest point on the wall (d27 near)
        for lump in air.lumps:
            if lump.pointContainment(pin) == adsk.fusion.PointContainment.PointInsidePointContainment:
                best = X.cp(lump)
        if best is None:
            raise RuntimeError('the pocket\'s air under its end wall was not found')
        print('%s    the pocket\'s section under its end wall: %.2f mm2, box %s' % (name, X.vol(best) / 0.15, k.r2(k.wbb(X, best), 3)))
        X.dif(t, X.move(best, 0.0, 0.15, 0.0))
        v3 = X.vol(t); print('%s    pocket end wall\'s face -20.95 -> -20.80: %.3f removed' % (name, v2 - v3))
    return t


def shell(k, X):
    src = X.body('HOUSING_F_front'); t = X.cp(src); v0 = X.vol(t)
    X.dif(t, X.wbox(-60.0, 60.0, -23.35, -23.2, 176.5, 177.45))
    v1 = X.vol(t); print('HOUSING_F_front H  lip\'s face -23.3 -> -23.2: %.3f removed' % (v0 - v1))
    X.dif(t, X.wbox(65.6, 69.3, -63.55, -63.4, 6.45, 7.7))
    v2 = X.vol(t); print('HOUSING_F_front H  frame end\'s tip -63.5 -> -63.4: %.4f removed' % (v1 - v2))
    return t


def say(k, X, key, t, ref):
    k.c[key] = t
    r = X.body(ref)
    print('%-12s %12.3f mm3, lumps %d, faces %d | %s in the model %.3f, lumps %d, faces %d' % (key, X.vol(t), t.lumps.count, t.faces.count, ref, r.volume * 1000, r.lumps.count, r.faces.count))


def _main(stage):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    if stage in ('plate', 'all'):
        say(k, X, 'b3_plate', plate(k, X), 'FLOOR_PLATE')
    if stage in ('boxes', 'all'):
        for sx, s in ((1, 'L'), (-1, 'R')):
            say(k, X, 'b3_box_' + s, box(k, X, sx), 'SPKBOX_' + s)
    if stage in ('shell', 'all'):
        say(k, X, 'b3_shell', shell(k, X), 'HOUSING_F_front')
    if stage in ('feet', 'all'):
        for n in ('FL', 'FR', 'RL', 'RR'):
            say(k, X, 'b3_foot_' + n, X.move(X.cp(X.body('FOOT_' + n)), 0.0, 0.0, -0.1), 'FOOT_' + n)
    print(L['stamp'](), 'after', X.state())


def main(stage='all'):
    L['out']('d31_%s.txt' % stage, _main, stage)


def _diff(names):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'what is built against the model\'s bodies as they stand')
    for n in names:
        if k.c.get(KEYS[n]) is None:
            print('%-18s not built in this session' % n); continue
        a = X.tbm.copy(k.c[KEYS[n]]); b = X.tbm.copy(X.body(n))
        add = X.tbm.copy(a); X.dif(add, X.tbm.copy(b))
        rem = X.tbm.copy(b); X.dif(rem, X.tbm.copy(a))
        la = X.lumps(add) if add.faces.count else []; lr = X.lumps(rem) if rem.faces.count else []
        print('%-18s new %.3f, old %.3f; added %.3f in %d lumps, removed %.3f in %d lumps' % (n, X.vol(a), X.vol(b), sum(q[0] or 0 for q in la), len(la), sum(q[0] or 0 for q in lr), len(lr)))
        for tag, ls in (('+', la), ('-', lr)):
            ls = sorted(ls, key=lambda q: -(q[0] or 0))
            for v, bb in ls[:12]:
                print('      %s %9.3f  %s' % (tag, v, bb))
            if len(ls) > 12:
                print('      %s ... %d more, the largest of them %.3f, %.3f in all' % (tag, len(ls) - 12, ls[12][0], sum(q[0] or 0 for q in ls[12:])))


def diff(names, tag=''):
    L['out']('d31_diff%s.txt' % (('_' + tag) if tag else ''), _diff, names)
# END
