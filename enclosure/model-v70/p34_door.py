# Block 3: the door (HOUSING_F_door), built on temporary bodies. CHANGES NOTHING IN THE DOCUMENT except a temporary body
# 'TMP_door' in stage 2 (Offset Face on the four boss tops), deleted again. The result is kept in k.c['b3_door'] (p36 puts it in).
# World mm; the door prints bottom edge down at 0.20 from its bed at z 2.8: level faces at 2.8 + 0.2 k.
#   stage 1 (TBM): the old pilots and the two peg holes filled with the door's own material (the door's crop shifted clear of
#     the hole, both ways, intersected); the cut-out x +-12.7, z 12.0-30.8; the two new level seats (top 10.0) with a 45 deg
#     underside beyond the foot, kept 0.4 off the base plate; room for the grommet's leg and tab and their drop; the two new
#     pilots at 18 deg; the baffle behind the strip over the port.
#   stage 2: the ten magnet pockets' teardrop tops (AA-C2), from each pocket's floor (the skin, +y side) out through its mouth; the four boss tops +0.1 (Offset Face) and the insert holes to z 10.0
#     (AA-B2: roof 0.6).
# Run: runpy.run_path(D + 'p34_door.py')['main'](1), then (2)  -> p34_door_1.txt, p34_door_2.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')

U = (0.0, math.sin(math.radians(18.0)), math.cos(math.radians(18.0)))
# the cut-out (door grid: 12.0 = bed + 9.2, 30.8 = bed + 28.0)
CUT = (-12.7, 12.7, -90.0, -79.5, 12.0, 30.8)
# the seats (top 10.0 = bed + 7.2): from the wall (inside it, -81.75) to y -76.9; flat on the foot's top (3.65) to y -79.0,
# then 45 deg up to the front end
SEAT_X = (4.5, 12.3)
SEAT_Y = (-81.75, -76.9)
SEAT_Z = (3.65, 10.0)
WEDGE_Y0 = -79.0
CLR_PLATE = 0.4
# room for the grommet's leg, tab and ears, seated and on the way down (lifted 2.3)
ROOM = (-12.1, 12.1, -81.7, -76.0, 10.0, 17.0)
# the new pilots: M2 x 6 thread-forming, as version 69 (r 0.8), 4.6 deep from the seat, 0.3 entry chamfer
PIL = [(9.0, -79.3, 10.0), (-9.0, -79.3, 10.0)]
# the baffle (bottom 28.2 = bed + 25.4, top 31.4 = bed + 28.6)
BAF = (-13.6, 13.6, -81.05, -79.85, 28.2, 31.4)
# old features to fill
OLD_PIL = [((7.5, -81.97, 7.64), (7.5, -80.69, 11.59)), ((-7.5, -81.97, 7.64), (-7.5, -80.69, 11.59))]
PEGS = [(13.85, 20.6), (-13.85, 20.6)]
# bosses and insert holes
BOSS = [(-19.0, -77.0), (19.0, -74.5), (50.0, -67.0), (-50.0, -67.0)]
HOLE_TOP = 10.0           # bed + 7.2
GRID0, GRID = 2.8, 0.2


def along(p, t):
    return (p[0] + U[0] * t, p[1] + U[1] * t, p[2] + U[2] * t)


def unit(v):
    n = math.sqrt(sum(w * w for w in v)); return tuple(w / n for w in v)


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def plug(X, crop, tool, shifts):
    """tool intersected with the crop shifted each way: the door's own material where the hole is"""
    t = X.tbm.copy(tool)
    for s in shifts:
        c = X.tbm.copy(crop); X.move(c, *s); X.sec(t, c)
    return t


def stage1(k, X):
    door = X.body('HOUSING_F_door')
    d = X.tbm.copy(door)
    v0 = X.vol(d)
    print('door: volume %.3f faces %d' % (v0, d.faces.count))
    # 1. fill the old pilots (they reach 1.0 into the wall) and the peg holes
    for (A, B) in OLD_PIL:
        sx = 1 if A[0] > 0 else -1
        crop = X.wbox(sx * 3.0, sx * 12.5, -85.5, -76.0, 4.0, 14.5); X.sec(crop, X.tbm.copy(door))
        a = (A[0], A[1] - U[1] * 0.3, A[2] - U[2] * 0.3); b = (B[0], B[1] + U[1] * 0.3, B[2] + U[2] * 0.3)
        p = plug(X, crop, X.cyl(a, b, 0.95), [(1.7, 0, 0), (-1.7, 0, 0)])
        print('  old pilot at x %+.1f: plug %.3f' % (A[0], X.vol(p)))
        X.uni(d, p)
    for (x, z) in PEGS:
        sx = 1 if x > 0 else -1
        crop = X.wbox(sx * 12.0, sx * 16.5, -86.0, -79.5, z - 5.0, z + 5.0); X.sec(crop, X.tbm.copy(door))
        p = plug(X, crop, X.cyl((x, -84.8, z), (x, -80.2, z), 1.0), [(0, 0, 2.0), (0, 0, -2.0)])
        print('  peg hole at x %+.2f: plug %.3f' % (x, X.vol(p)))
        X.uni(d, p)
    v1 = X.vol(d)
    # 2. the cut-out
    X.dif(d, X.wbox(*CUT))
    v2 = X.vol(d)
    # 3. the seats
    plate = {}
    for sx in (1, -1):
        x0, x1 = sorted((sx * SEAT_X[0], sx * SEAT_X[1]))
        s = X.wbox(x0, x1, SEAT_Y[0], SEAT_Y[1], SEAT_Z[0], SEAT_Z[1])
        # the 45 deg underside: off everything under the plane z - y = 3.65 - WEDGE_Y0, beyond y WEDGE_Y0
        n = (0.0, -math.sqrt(0.5), math.sqrt(0.5)); P0 = ((x0 + x1) / 2.0, WEDGE_Y0 + 1.5, SEAT_Z[0] + 1.5)
        cen = tuple(P0[i] - n[i] * 4.0 for i in range(3))
        X.dif(s, X.obox(cen, (1, 0, 0), (0, math.sqrt(0.5), math.sqrt(0.5)), 12.0, 14.0, 8.0))
        vs = X.vol(s)
        # 0.4 off the base plate
        pcs = k.region(X, 'FLOOR_PLATE', 'b3_seat_%d' % sx, (x0 - 3.0, x1 + 3.0, -85.0, -70.0, 0.0, 14.0))
        g = CLR_PLATE; h = g * math.sqrt(0.5)
        offs = [(0, 0, 0), (g, 0, 0), (-g, 0, 0), (0, g, 0), (0, -g, 0), (0, 0, g), (0, 0, -g),
                (0, h, h), (0, -h, h), (h, 0, h), (-h, 0, h), (h, h, 0), (-h, h, 0), (h, -h, 0), (-h, -h, 0)]
        for pc in pcs:
            for o in offs:
                t = X.tbm.copy(pc); X.move(t, *o); X.dif(s, t)
        plate[sx] = (round(vs, 3), round(X.vol(s), 3), s.lumps.count)
        print('  seat x %+.1f..%+.1f: prism %.3f, after the plate clearance %.3f (lumps %d)' % (x0, x1, vs, X.vol(s), s.lumps.count))
        X.uni(d, s)
    v3 = X.vol(d)
    # 4. room for the grommet's leg and tab, seated and dropping
    X.dif(d, X.wbox(*ROOM))
    v4 = X.vol(d)
    # 5. the new pilots
    for P in PIL:
        X.dif(d, X.cyl(along(P, 0.5), along(P, -4.6), 0.8))
        X.dif(d, X.cyl(along(P, 0.3), along(P, -0.3), 1.4, 0.8))
    v5 = X.vol(d)
    # 6. the baffle behind the strip over the port
    X.uni(d, X.wbox(*BAF))
    v6 = X.vol(d)
    k.c['b3_door1'] = d
    print('volumes: start %.3f, plugs %.3f, cut-out %.3f, seats %.3f, room %.3f, pilots %.3f, baffle %.3f' % (v0, v1, v2, v3, v4, v5, v6))
    print('door after stage 1: volume %.3f faces %d lumps %d solid %s' % (X.vol(d), d.faces.count, d.lumps.count, d.isSolid))


def pocket_tops(k, X, d):
    door = X.body('HOUSING_F_door_v69')      # the pockets as at version 70 (g25): block 0's copy
    pk = [h for h in k.holes_of(door, 4.0, 4.3) if h['k'] == 'h']
    rows = []
    for h in pk:
        A, B = h['A'], h['B']
        # A is the floor: the pocket opens toward -y (into the door, where the magnet goes in) and its floor is the skin on
        # the +y side, facing the front shell's lip (sections b3_raster_pockets.png). So A is the end with the larger y, and
        # the prism runs from the floor out through the mouth.
        if A[1] < B[1]:
            A, B = B, A
        a = unit(tuple(B[i] - A[i] for i in range(3)))
        r = h['r']
        up = unit((-a[2] * a[0], -a[2] * a[1], 1.0 - a[2] * a[2]))
        side = cross(a, up)
        top = max(A[2], B[2]) + r * up[2]
        kk = math.ceil((top + 0.2 - GRID0) / GRID - 1e-6)
        flat = round(GRID0 + GRID * kk, 3)
        Lp = math.sqrt(sum((B[i] - A[i]) ** 2 for i in range(3))) + 3.0
        mid = tuple(A[i] + a[i] * Lp / 2.0 for i in range(3))
        dia = X.obox(mid, a, unit(tuple(up[i] + side[i] for i in range(3))), Lp, 2 * r, 2 * r)
        h0 = r * math.sqrt(0.5)
        X.sec(dia, X.obox(tuple(mid[i] + up[i] * (h0 + 4.0) for i in range(3)), a, tuple(-w for w in side), Lp, 30.0, 8.0))
        X.sec(dia, X.wbox(A[0] - 20, A[0] + 20, A[1] - 20, A[1] + 20, flat - 20.0, flat))
        rows.append((A, B, r, top, flat, dia))
    return rows


def stage2(k, X):
    d = X.tbm.copy(k.c['b3_door1'])
    v0 = X.vol(d)
    # 7. the pockets' teardrop tops
    for (A, B, r, top, flat, dia) in pocket_tops(k, X, d):
        vt = X.vol(dia)
        vx = X.xv(dia, d)
        X.dif(d, dia)
        print('  pocket floor %s mouth %s: circle top %.3f, flat %.2f (+%.2f), teardrop prism %.3f mm3, of it in the door %.3f' % (
            [round(w, 2) for w in A], [round(w, 2) for w in B], top, flat, flat - top, vt, vx))
    v7 = X.vol(d)
    # 8. the four boss tops +0.1 (Offset Face on a temporary body), then the insert holes to z 10.0
    b = X.add(X.tbm.copy(d), 'TMP_door', show=False)
    tops = []
    for f in b.faces:
        if f.geometry.surfaceType != adsk.core.SurfaceTypes.PlaneSurfaceType:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
        n = k.wv(nv); p = k.W(f.pointOnFace)
        if n[2] > 0.999 and abs(p[2] - 10.5) < 0.01 and any(abs(p[0] - bx) < 6.5 and abs(p[1] - by) < 8.0 for (bx, by) in BOSS):
            tops.append(f)
    print('  boss tops found: %d, areas %s' % (len(tops), [round(f.area * 100, 2) for f in tops]))
    if len(tops) != 4:
        b.deleteMe()
        raise RuntimeError('boss tops: %d' % len(tops))
    inp = X.root.features.offsetFacesFeatures.createInput(tops, adsk.core.ValueInput.createByReal(0.01))
    X.root.features.offsetFacesFeatures.add(inp)
    b = X.body('TMP_door')
    d = X.tbm.copy(b)
    b.deleteMe()
    v8 = X.vol(d)
    for (bx, by) in BOSS:
        X.dif(d, X.cyl((bx, by, 9.0), (bx, by, HOLE_TOP), 2.0))
    v9 = X.vol(d)
    k.c['b3_door'] = d
    print('volumes: start %.3f, teardrops %.3f, boss tops %.3f, holes %.3f' % (v0, v7, v8, v9))
    print('door after stage 2: volume %.3f faces %d lumps %d solid %s' % (X.vol(d), d.faces.count, d.lumps.count, d.isSolid))
    print('lumps:', X.lumps(d, maxv=200)[:3])


def _main(stage):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    stage1(k, X) if stage == 1 else stage2(k, X)
    for b in [b for b in X.root.bRepBodies if b.name.startswith('TMP_')]:
        b.deleteMe()
    print(L['stamp'](), 'after', X.state())


def main(stage):
    L['out']('p34_door_%d.txt' % stage, _main, stage)
