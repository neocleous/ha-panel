# Block 3: the base plate (FLOOR_PLATE), built on a temporary body. CHANGES NOTHING IN THE DOCUMENT: the result is kept in
# k.c['b3_plate'] (p36 puts it in). World mm; the plate prints underside down at 0.20 from z 0.
#   D408 (Daniel's 2a): two finger scallops in the rear border, chord 18 along the door's outer face, 4.2 deep, through the plate
#     (z -1 to 2.62), at x +-61.5 (block 2's placing: scallop_place.json).
#   AA-C5: the eight counterbore roofs (z 1.0) as two-step bridges: a slot 3.4 wide across the counterbore at z 1.0-1.2, a square
#     3.4 at z 1.2-1.4, then the round hole.
#   AA-A11: the four foot recesses r 6.5 -> 6.8 (Ø13.6), depth 0.5 as now.
#   AA-A24 / AA-C12: the right rear land (at -19, -77) ends 0.5 inside the band's edge, with the plate's top (z 2.5, 0.30 under
#     the door's foot) between, as at the left land; its stair at z 2.6 / 2.7 goes.
# Run: runpy.run_path(D + 'p35_plate.py')['main']()  -> p35_plate.txt
import runpy, math

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')

SCAL = [(61.5, -71.034, 0.4962, -0.8682), (-61.5, -71.043, -0.4863, -0.8738)]   # point on the door's outer face, outward normal
CHORD, DEPTH = 18.0, 4.2
CB = [(-19.0, -77.0), (19.0, -74.5), (50.0, -67.0), (-50.0, -67.0), (64.0, -45.0), (-72.0, -38.0), (51.0, -14.0), (-51.0, -14.0)]
FEET = [(80.0, -5.5), (-80.0, -5.5), (30.0, -70.6), (-30.0, -70.6)]
R_FOOT = 6.8
# the band's edge (its riser) beside the right land, measured on the mesh of version 70 at z 1.9 to 2.75:
# x -21: y -80.045; x -19: -80.21; x -17: -80.36  ->  y = -80.21 - 0.0788 (x + 19)
RISER = (-19.0, -80.21, -0.0788)
SHELF = 0.5


def _main():
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    p = X.tbm.copy(X.body('FLOOR_PLATE'))
    v0 = X.vol(p)
    print('plate: volume %.3f faces %d' % (v0, p.faces.count))
    # 1. scallops
    R = (CHORD ** 2 / 4.0 + DEPTH ** 2) / (2.0 * DEPTH)
    for (px, py, nx, ny) in SCAL:
        n = math.hypot(nx, ny); nx, ny = nx / n, ny / n
        cx, cy = px + nx * (R - DEPTH), py + ny * (R - DEPTH)
        vb = X.vol(p)
        X.dif(p, X.cyl((cx, cy, -1.0), (cx, cy, 2.62), R))
        print('  scallop centre (%.3f, %.3f) R %.3f: removed %.3f' % (cx, cy, R, vb - X.vol(p)))
    v1 = X.vol(p)
    # 2. two-step bridges
    for (x, y) in CB:
        slot = X.wbox(x - 3.4, x + 3.4, y - 1.7, y + 1.7, 1.0, 1.2)
        X.sec(slot, X.cyl((x, y, 0.9), (x, y, 1.3), 3.25))
        X.dif(p, slot)
        X.dif(p, X.wbox(x - 1.7, x + 1.7, y - 1.7, y + 1.7, 1.2, 1.4))
    v2 = X.vol(p)
    # 3. foot recesses
    for (x, y) in FEET:
        X.dif(p, X.cyl((x, y, -1.0), (x, y, 0.5), R_FOOT))
    v3 = X.vol(p)
    # 4. the right rear land: off above the plate's top within SHELF of the band's edge
    x0, y0, s = RISER
    ax = (1.0, s, 0.0); m = math.hypot(1.0, s); ax = (ax[0] / m, ax[1] / m, 0.0)
    ay = (-ax[1], ax[0], 0.0)                                   # in plan, toward +y (into the plate)
    yc = y0 + SHELF                                             # the new edge at x0
    Wd = 4.0
    cen = (x0 - ay[0] * Wd / 2.0, yc - ay[1] * Wd / 2.0, 2.75)
    cut = X.obox(cen, ax, ay, 12.0, Wd, 0.5)
    X.sec(cut, X.wbox(-26.0, -12.0, -90.0, -70.0, 2.5, 3.0))
    X.dif(p, cut)
    v4 = X.vol(p)
    k.c['b3_plate'] = p
    print('volumes: start %.3f, scallops %.3f, bridges %.3f, recesses %.3f, land %.3f' % (v0, v1, v2, v3, v4))
    print('plate: volume %.3f faces %d lumps %d solid %s' % (X.vol(p), p.faces.count, p.lumps.count, p.isSolid))
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p35_plate.txt', _main)
