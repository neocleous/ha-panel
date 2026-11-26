# Block 4, its first part, as built: the architect log 2026-11-24-d, section 6, points 1 to 3, on temporary bodies.
# Replaces p43_s6.py (a first try, kept with its output: it trimmed the grommet's +x ear for the boss, which takes the wall
# behind the screw head's rim from 0.64 to 0.43, p44c_measure.txt).
# CHANGES NOTHING IN THE DOCUMENT except a hidden temporary body 'TMP_door' (Offset Face on the four boss tops), deleted again.
# Results kept in k.c['b4_plate'], ['b4_door'], ['b4_grommet'] (p46 puts them in).
#   1. D419: the base plate's eight counterbore roofs back to version 69's plain flat roofs at z 1.0: block 3's slot (z 1.0-1.2)
#      and square (1.2-1.4) filled with version 69's own material (FLOOR_PLATE_v69 cropped round each counterbore).
#   2. The door's four insert bosses: tops 10.6 -> 10.8 (door grid 2.8 + 0.2 k): roof 0.8 over each insert hole (top 10.0).
#      Offset Face +0.2 on the four top faces, as block 3 raised them by 0.1.
#      And the two pilots' entry chamfers (block 3's cone r 1.4 at 0.3 along the 18 deg axis to r 0.8 at -0.3) cut on to 0.7
#      (r 1.8): the cone ended under the level seat top on the +y side and left a sliver 0.15 thick over it (p44b, p44c).
#   3. The cradle's legs' bosses on the base plate (axes (6.5, -72.5) and (-1.5, -72.5), r 4.0 above z 8.5 round Ø4.0 insert
#      holes, a 14 deg root flare below, joined by a block whose face is y -76.5): GAP (0.62) or more to the grommet and to the
#      door's +x seat. Each by what keeps the walls of the screws and the inserts:
#        - the door's +x seat (no hole near): trimmed by the boss's surfaces offset by GAP: cylinder r 4.62, the flare's cone
#          offset along its normal, the block's face to y -77.12;
#        - the grommet's tab back (y -76.95, no hole near): trimmed by the block's face offset and both bosses' cylinders r 4.62,
#          but not inside its +x ear (r 2.35 round (9.0, -78.72)): there the ear's wall round the countersink is the screw's;
#        - the +x ear: the boss is relieved instead, by a cylinder r 2.35 + GAP round the ear's axis from z 9.4 (grid) to 11.92,
#          then a 45 deg cone to r 2.70 at 12.19 (no hanging face). The insert's wall there: 6.70 - 2.97 - 2.0 = 1.73 (rule point
#          1: 1.6 to 2.0, listed; Ruthex's 1.6).
# Run: runpy.run_path(D + 'p43b_s6.py')['main']()  -> p43b_s6.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
CB = [(-19.0, -77.0), (19.0, -74.5), (50.0, -67.0), (-50.0, -67.0), (64.0, -45.0), (-72.0, -38.0), (51.0, -14.0), (-51.0, -14.0)]
BOSS = [(-19.0, -77.0), (19.0, -74.5), (50.0, -67.0), (-50.0, -67.0)]
U = (0.0, math.sin(math.radians(18.0)), math.cos(math.radians(18.0)))
SCREWS = [(9.0, -79.3, 10.0), (-9.0, -79.3, 10.0)]
AX = (6.5, -72.5)
AXM = (-1.5, -72.5)
EAR = (9.0, -78.72, 2.35)
GAP = 0.62       # 0.6 asked; 0.02 over it so that a body-to-body reading of a faceted cone does not come out at 0.599
T14 = math.tan(math.radians(14.0))
R_CONE55 = 4.75 + GAP / math.cos(math.radians(14.0))       # the flare's cone offset along its normal, radius at z 5.5
SEAT_BOX = (4.4, 12.4, -81.8, -76.5, 3.65, 10.05)


def along(P, t):
    return tuple(P[i] + U[i] * t for i in range(3))


def rcone(z):
    return R_CONE55 + (5.5 - z) * T14


def _main():
    k = L['load'](); X = k.K(); k.budget(75)
    print(L['stamp'](), 'before', X.state())
    # 1. the base plate's counterbores
    p = X.tbm.copy(X.body('FLOOR_PLATE'))
    old = X.body('FLOOR_PLATE_v69')
    v0 = X.vol(p)
    for (x, y) in CB:
        bx = X.wbox(x - 3.5, x + 3.5, y - 3.5, y + 3.5, 0.95, 1.45)
        piece = X.tbm.copy(bx); X.sec(piece, X.tbm.copy(old))
        X.uni(p, piece)
        a = X.tbm.copy(bx); X.sec(a, X.tbm.copy(p))
        b = X.tbm.copy(bx); X.sec(b, X.tbm.copy(old))
        print('  counterbore (%+.1f, %+.1f): plate in the box %.4f, version 69 in the box %.4f, diff %+.5f' % (x, y, X.vol(a), X.vol(b), X.vol(a) - X.vol(b)))
    v1 = X.vol(p)
    print('plate: counterbore roofs back: %.3f -> %.3f (%+.3f; block 3 took %.3f for the bridges)' % (v0, v1, v1 - v0, 32539.830 - 32516.714))
    # 3. the +x boss relieved round the grommet's ear
    ex, ey, er = EAR
    rr = er + GAP
    rel = X.cyl((ex, ey, 9.4), (ex, ey, 11.92), rr)
    X.uni(rel, X.cyl((ex, ey, 11.92), (ex, ey, 11.92 + (rr - 2.70)), rr, 2.70))
    vr = X.xv(rel, p)
    X.dif(p, rel)
    k.c['b4_plate'] = p
    print('plate: the +x cradle boss relieved round the grommet ear (r %.2f, z 9.4-11.92, 45 deg to r 2.70): removed %.4f; plate %.3f, lumps %d, solid %s' % (
        rr, vr, X.vol(p), p.lumps.count, p.isSolid))
    # 2. the door's boss tops
    door = X.body('HOUSING_F_door')
    tb = X.add(X.tbm.copy(door), 'TMP_door', show=False)
    tops = []
    for f in tb.faces:
        if f.geometry.surfaceType != adsk.core.SurfaceTypes.PlaneSurfaceType:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
        n = k.wv(nv); q = k.W(f.pointOnFace)
        if n[2] > 0.999 and abs(q[2] - 10.6) < 0.01 and any(abs(q[0] - bx) < 7.0 and abs(q[1] - by) < 9.0 for (bx, by) in BOSS):
            tops.append(f)
    print('door boss tops found at 10.6: %d, areas %s' % (len(tops), [round(f.area * 100, 2) for f in tops]))
    if len(tops) != 4:
        tb.deleteMe()
        raise RuntimeError('boss tops: %d' % len(tops))
    inp = X.root.features.offsetFacesFeatures.createInput(tops, adsk.core.ValueInput.createByReal(0.02))
    X.root.features.offsetFacesFeatures.add(inp)
    tb = X.body('TMP_door')
    d = X.tbm.copy(tb)
    tb.deleteMe()
    vd0 = X.vol(X.tbm.copy(door)); vd1 = X.vol(d)
    print('door: boss tops +0.2: %.3f -> %.3f (%+.3f)' % (vd0, vd1, vd1 - vd0))
    for P in SCREWS:
        X.dif(d, X.cyl(along(P, 0.3), along(P, 0.7), 1.4, 1.8))
    vd2 = X.vol(d)
    print('door: the two pilots\' chamfers run out through the seat top: removed %.4f' % (vd1 - vd2))
    # 3. the door's +x seat
    sb = X.wbox(*SEAT_BOX)
    cut = None
    for c in (X.cyl((AX[0], AX[1], 8.0), (AX[0], AX[1], 14.5), 4.0 + GAP),
              X.cyl((AX[0], AX[1], 1.9), (AX[0], AX[1], 9.2), rcone(1.9), rcone(9.2)),
              X.wbox(AXM[0] - GAP, AX[0], -76.5 - GAP, AX[1], 1.9, 13.1)):
        t = X.tbm.copy(c); X.sec(t, X.tbm.copy(sb))
        cut = t if cut is None else X.uni(cut, t)
    vx = X.xv(cut, d)
    X.dif(d, cut)
    k.c['b4_door'] = d
    print('door: +x seat trimmed %.2f off the boss: removed %.4f; door %.3f, lumps %d, solid %s' % (GAP, vx, X.vol(d), d.lumps.count, d.isSolid))
    # 3. the grommet's tab back
    g = X.tbm.copy(X.body('GROMMET_usbc_F'))
    vg0 = X.vol(g)
    cg = X.cyl((AX[0], AX[1], 8.0), (AX[0], AX[1], 14.5), 4.0 + GAP)
    X.uni(cg, X.cyl((AXM[0], AXM[1], 8.0), (AXM[0], AXM[1], 14.5), 4.0 + GAP))
    X.uni(cg, X.wbox(AXM[0], AX[0], -76.5 - GAP, AX[1], 8.0, 14.5))
    X.dif(cg, X.cyl((ex, ey, 8.0), (ex, ey, 14.5), er + 0.001))
    rem = X.tbm.copy(cg); X.sec(rem, X.tbm.copy(g))
    print('grommet: tab back within %.2f of the bosses and the block, the ear kept: %.4f mm3, %d lump(s): %s' % (GAP, X.vol(rem), rem.lumps.count, X.lumps(rem)))
    X.dif(g, cg)
    k.c['b4_grommet'] = g
    print('grommet: %.3f -> %.3f (%+.4f); lumps %d, solid %s' % (vg0, X.vol(g), X.vol(g) - vg0, g.lumps.count, g.isSolid))
    for b in [b for b in X.root.bRepBodies if b.name.startswith('TMP_')]:
        b.deleteMe()
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p43b_s6.txt', _main)
