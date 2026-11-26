# Block 4, its first part: after p43b. p44c's rays round the grommet's two screws found, above the spot face's plane (square to
# the screw at 1.88 along its axis) and up to the tab's top (z 11.88), crescents 0.00 to 0.18 thick in the layer: the ears are
# upright cylinders r 2.35 round (+-9.0, -78.72), the spot face's bore is r 2.4 round the leaning axis, and the two nearly
# coincide, so a hairline of each ear's wall is left outside the bore (block 3's shape; rule point 10: no lamella under 0.45).
# This cuts each ear's own outline (r 2.351) above the spot face's plane, in the tab (y > -79.5, z 10.9 to 11.95), from
# k.c['b4_grommet']. CHANGES NOTHING IN THE DOCUMENT.
# Run: runpy.run_path(D + 'p43c_ears.py')['main']()  -> p43c_ears.txt
import runpy, math

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
U = (0.0, math.sin(math.radians(18.0)), math.cos(math.radians(18.0)))
SCREWS = [(9.0, -79.3, 10.0), (-9.0, -79.3, 10.0)]
EAR_Y, EAR_R = -78.72, 2.351
T_SF = 1.88


def _main():
    k = L['load'](); X = k.K()
    print(L['stamp'](), 'before', X.state())
    g = k.c['b4_grommet']
    v0 = X.vol(g)
    for P in SCREWS:
        c = X.cyl((P[0], EAR_Y, 10.9), (P[0], EAR_Y, 11.95), EAR_R)
        # above the spot face's plane: a box whose height axis is the screw's, from the plane up
        base = tuple(P[i] + U[i] * T_SF for i in range(3))
        cen = tuple(base[i] + U[i] * 3.0 for i in range(3))
        X.sec(c, X.obox(cen, (1.0, 0.0, 0.0), (0.0, U[2], -U[1]), 12.0, 12.0, 6.0))
        X.sec(c, X.wbox(P[0] - 3, P[0] + 3, -79.5, -75.0, 10.9, 11.95))
        piece = X.tbm.copy(c); X.sec(piece, X.tbm.copy(g))
        print('  ear at x %+.1f: removed %.5f mm3 in %d piece(s): %s' % (P[0], X.vol(piece), piece.lumps.count, X.lumps(piece)[:4]))
        X.dif(g, c)
    print('grommet: %.4f -> %.4f; lumps %d, solid %s' % (v0, X.vol(g), g.lumps.count, g.isSolid))
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p43c_ears.txt', _main)
