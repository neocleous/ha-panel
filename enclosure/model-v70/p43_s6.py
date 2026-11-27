# Block 4, its first part: the architect log 2026-11-24-d, section 6, points 1 to 3, built on temporary bodies.
# CHANGES NOTHING IN THE DOCUMENT except a hidden temporary body 'TMP_door' (Offset Face on the four boss tops), deleted again.
# Results kept in k.c['b4_plate'], ['b4_door'], ['b4_grommet'] (p46 puts them in).
#   1. D419: the base plate's eight counterbore roofs back to version 69's plain flat roofs at z 1.0: block 3's slot (z 1.0-1.2)
#      and square (1.2-1.4) filled with version 69's own material (FLOOR_PLATE_v69 cropped round each counterbore).
#   2. The door's four insert bosses: tops 10.6 -> 10.8 (door grid 2.8 + 0.2 k), so the roof over each insert hole (top 10.0)
#      is 0.8 (rule point 8). Offset Face +0.2 on the four top faces, as block 3 raised them by 0.1.
#   3. The cradle's +x leg boss on the base plate (axis (6.5, -72.5); r 4.0 above z 8.5, a 14 deg root flare below, joined to
#      the -x boss by a block whose face is y -76.5): 0.6 or more to the grommet and to the door's +x seat, by trimming them,
#      so that the boss keeps its 2.0 round the insert. The cutters are the boss's own surfaces offset by 0.6, exactly:
#        a cylinder r 4.6; the flare's cone offset 0.6 along its normal (r 5.368 at z 5.5, same 14 deg); the block's face y -76.5
#        offset to -77.1 for x <= 6.5.
#      The grommet loses only what lies within r 4.6 of the axis (its +x ear and the tab's back edge beside it); the door's seat
#      loses only what lies within the three cutters, inside the seat's own box.
# Run: runpy.run_path(D + 'p43_s6.py')['main']()  -> p43_s6.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
CB = [(-19.0, -77.0), (19.0, -74.5), (50.0, -67.0), (-50.0, -67.0), (64.0, -45.0), (-72.0, -38.0), (51.0, -14.0), (-51.0, -14.0)]
BOSS = [(-19.0, -77.0), (19.0, -74.5), (50.0, -67.0), (-50.0, -67.0)]
AX = (6.5, -72.5)
GAP = 0.62       # 0.6 asked; 0.02 over it so that a body-to-body reading of the faceted cone does not come out at 0.599
T14 = math.tan(math.radians(14.0))
R_CONE55 = 4.75 + GAP / math.cos(math.radians(14.0))       # the flare's cone offset along its normal, radius at z 5.5
SEAT_BOX = (4.4, 12.4, -81.8, -76.5, 3.65, 10.05)


def rcone(z):
    return R_CONE55 + (5.5 - z) * T14


def cutters(X):
    out = [X.cyl((AX[0], AX[1], 8.0), (AX[0], AX[1], 14.5), 4.0 + GAP)]
    z0, z1 = 1.9, 9.2
    out.append(X.cyl((AX[0], AX[1], z0), (AX[0], AX[1], z1), rcone(z0), rcone(z1)))
    out.append(X.wbox(-1.5 - GAP, AX[0], -76.5 - GAP, AX[1], 1.9, 13.1))
    return out


def _main():
    k = L['load'](); X = k.K(); k.budget(75)
    print(L['stamp'](), 'before', X.state())
    # 1. the base plate
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
    k.c['b4_plate'] = p
    print('plate: %.3f -> %.3f (%+.3f; block 3 took %.3f for the bridges); lumps %d, solid %s' % (v0, X.vol(p), X.vol(p) - v0, 32539.830 - 32516.714,
                                                                                               p.lumps.count, p.isSolid))
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
    # 3. the door's +x seat
    sb = X.wbox(*SEAT_BOX)
    cut = None
    for c in cutters(X):
        t = X.tbm.copy(c); X.sec(t, X.tbm.copy(sb))
        if cut is None:
            cut = t
        else:
            X.uni(cut, t)
    vx = X.xv(cut, d)
    X.dif(d, cut)
    vd2 = X.vol(d)
    print('door: +x seat trimmed 0.6 off the boss: removed %.4f (%.3f -> %.3f); lumps %d, solid %s' % (vx, vd1, vd2, d.lumps.count, d.isSolid))
    k.c['b4_door'] = d
    # 3. the grommet
    g = X.tbm.copy(X.body('GROMMET_usbc_F'))
    vg0 = X.vol(g)
    # the boss's cylinder and the joining block's face (y -76.5, x -1.5..6.5), each offset by GAP: the block stands 0.45 from
    # the tab's back edge (y -76.95) over x -1.5..6.5
    # and the -x boss (axis (-1.5, -72.5), r 4.0), which the block joins: the tab's back passes it at 0.45 too
    cg = X.cyl((AX[0], AX[1], 8.0), (AX[0], AX[1], 14.5), 4.0 + GAP)
    X.uni(cg, X.cyl((-1.5, AX[1], 8.0), (-1.5, AX[1], 14.5), 4.0 + GAP))
    X.uni(cg, X.wbox(-1.5, AX[0], -76.5 - GAP, AX[1], 8.0, 14.5))
    rem = X.tbm.copy(cg); X.sec(rem, X.tbm.copy(g))
    print('grommet: within %.2f of the boss and the block: %.4f mm3, %d lump(s): %s' % (GAP, X.vol(rem), rem.lumps.count, X.lumps(rem)))
    X.dif(g, cg)
    k.c['b4_grommet'] = g
    print('grommet: %.3f -> %.3f (%+.4f); lumps %d, solid %s' % (vg0, X.vol(g), X.vol(g) - vg0, g.lumps.count, g.isSolid))
    for b in [b for b in X.root.bRepBodies if b.name.startswith('TMP_')]:
        b.deleteMe()
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p43_s6.txt', _main)
