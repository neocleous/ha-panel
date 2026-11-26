# Block 4, its first part (architect log 2026-11-24-d, section 6, point 4), after p44/p44b.
# p44b found, at the +y side of each new pilot's mouth in the door's seats, a sliver under the seat's top (z 9.85 to 10.0): the
# entry chamfer's cutter (a cone r 1.4 at 0.3 along the 18 deg axis to r 0.8 at -0.3, block 3's p34) ends at a disc square to
# the axis, and on the +y side that disc lies 0.15 below the level seat top: a roof of 0.7 mm2 over the chamfer, a lamella
# under 0.45 (rule point 10). Stage 'fix' cuts the same cone on to 0.7 along the axis (r 1.8), on k.c['b4_door'], so the
# chamfer runs out through the top (it meets the top at 0.53 on the +y side). CHANGES NOTHING IN THE DOCUMENT.
# Stage 'measure' (READ-ONLY): level rays from the hole's axis in each print layer (both parts print with world z up):
#   door, each pilot: 72 directions, its wall in each layer (grid 2.8 + 0.2 k);
#   grommet, each screw: the leg beside the spot face: the ray toward -y from the axis, and at 0.6 either side of it, in each
#     layer (grid 10.0 + 0.20 + 0.12 k) above the countersink; the ear's wall round the hole and countersink toward the cradle's
#     boss (directions 90 to 180 deg from +x, every 5), in each layer of the tab (10.2 to 11.88);
#   and the true least distance from the spot face's bore faces to the leg's back face (y -81.6, bounded copies).
# Run: runpy.run_path(D + 'p44c_walls.py')['main']('fix') then ('measure')  -> p44c_<stage>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
U = (0.0, math.sin(math.radians(18.0)), math.cos(math.radians(18.0)))
SCREWS = [(9.0, -79.3, 10.0), (-9.0, -79.3, 10.0)]


def along(P, t):
    return tuple(P[i] + U[i] * t for i in range(3))


def axis_at(P, z):
    t = (z - P[2]) / U[2]
    return along(P, t), t


def fix(k, X):
    d = k.c['b4_door']
    v0 = X.vol(d)
    for P in SCREWS:
        X.dif(d, X.cyl(along(P, 0.3), along(P, 0.7), 1.4, 1.8))
    print('door: the two chamfers run out through the seat top: removed %.4f (%.3f -> %.3f); lumps %d solid %s' % (
        v0 - X.vol(d), v0, X.vol(d), d.lumps.count, d.isSolid))


def first(k, X, part, c, e, reach=6.0):
    s = k.needle_t(X, [part], c, tuple(c[i] + e[i] * reach for i in range(3)), 0.02)
    if not s or s[0][0] < 0.3:
        return None
    return round(s[0][1] - s[0][0], 3), tuple(round(c[i] + e[i] * s[0][1], 2) for i in range(3))


def measure(k, X):
    k.budget(78)
    g, d = k.c['b4_grommet'], k.c['b4_door']
    dz = [round(2.8 + 0.2 * i, 2) for i in range(14, 37)]
    gz_tab = [round(10.2 + 0.12 * i, 2) for i in range(0, 15)]           # 10.2 .. 11.88
    gz_leg = [round(10.2 + 0.12 * i, 2) for i in range(14, 32)]          # 11.88 .. 13.92
    for P in SCREWS:
        sx = 1 if P[0] > 0 else -1
        dc = X.wbox(sx * 2.0, sx * 15.0, -84.5, -75.5, 3.0, 11.0); X.sec(dc, X.tbm.copy(d))
        rows = []
        for z in dz:
            c, t = axis_at(P, z)
            if t < -4.55 or t > -0.02:
                continue
            best = None
            for j in range(72):
                a = 2 * math.pi * j / 72.0
                r = first(k, X, dc, c, (math.cos(a), math.sin(a), 0.0))
                if r and (best is None or r[0] < best[0]):
                    best = (r[0], j * 5, r[1])
            rows.append((z,) + best)
        print('screw at x %+.1f, door pilot, wall in each layer (z, least, direction, where it ends):' % P[0])
        for r in rows:
            print('   %s' % (r,))
        gc = X.wbox(sx * 3.0, sx * 15.0, -83.0, -75.0, 9.9, 16.0); X.sec(gc, X.tbm.copy(g))
        print('screw at x %+.1f, grommet leg beside the spot face, toward -y from the axis (z: at the axis, 0.6 to +x, 0.6 to -x):' % P[0])
        for z in gz_leg:
            c, t = axis_at(P, z)
            if t < 1.88:
                continue
            out = []
            for dx in (0.0, 0.6, -0.6):
                q = (c[0] + dx, c[1], c[2])
                out.append(first(k, X, gc, q, (0.0, -1.0, 0.0)))
            print('   z %.2f: %s' % (z, out))
        print('screw at x %+.1f, grommet ear toward the cradle boss (directions %s), wall in each layer of the tab:' % (P[0], '90..180' if sx > 0 else '0..90'))
        for z in gz_tab:
            c, t = axis_at(P, z)
            best = None
            for j in range(19):
                a = math.radians(90 + 5 * j) if sx > 0 else math.radians(5 * j)
                r = first(k, X, gc, c, (math.cos(a), math.sin(a), 0.0))
                if r and (best is None or r[0] < best[0]):
                    best = (r[0], round(math.degrees(a)), r[1])
            print('   z %.2f: %s' % (z, best))
        # true: the spot face's bore faces to the leg's back face, bounded copies
        gb = X.add(X.tbm.copy(gc), 'TMP_gc', show=False)
        bore, back = [], []
        for f in gb.faces:
            gm = f.geometry
            if gm.surfaceType == 1 and abs(gm.radius * 10 - 2.4) < 0.01:
                bore.append(f)
            if gm.surfaceType == 0:
                ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
                n = k.wv(nv); p = k.W(f.pointOnFace)
                if n[1] < -0.999 and abs(p[1] + 81.6) < 0.05:
                    back.append(f)
        tb = adsk.fusion.TemporaryBRepManager.get()
        best = None
        for a in bore:
            for b in back:
                r = X.mm.measureMinimumDistance(tb.copy(a), tb.copy(b))
                v = round(r.value * 10, 3)
                if best is None or v < best[0]:
                    best = (v, k.r2(k.W(r.positionOne)), k.r2(k.W(r.positionTwo)))
        print('   true, the bore (%d faces) to the leg\'s back face (%d faces): %s' % (len(bore), len(back), best))
        gb.deleteMe()


def _main(stage):
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    {'fix': fix, 'measure': measure}[stage](k, X)
    for b in [b for b in X.root.bRepBodies if b.name.startswith('TMP_')]:
        b.deleteMe()
    print(L['stamp'](), 'after', X.state())


def main(stage):
    L['out']('p44c_%s.txt' % stage, _main, stage)
