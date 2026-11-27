# Block 4: the slab (SLAB_frame) and the screen plate (HOUSING_F_plate), built on temporary bodies. CHANGES NOTHING IN THE
# DOCUMENT. Results in k.c['b4_slab'], k.c['b4_screen'] (p47 puts them in).
# Slab frame: x = world x, d = depth behind the glass's front (the slab prints glass side down: d is its print height),
# Zd = design z (height along the screen). Faces read from the model in p42 (p42_slab.txt, p42_plate.txt).
#   AA-A23, the rims turned over:
#     upper rim: its inner face (Zd 35.071, d 9 to 12, x -99 to 99) brought down onto the plate's top edge (Zd 34.770): the gap
#       above the plate (0.301) filled with slab;
#     lower rim: its inner face (Zd -89.929, on the plate's bottom edge) taken down by LOW (0.20): the plate takes the slab
#       0.10 before the glass does (rebate 0.30 a side, unchanged).
#     The rims' faces stand in the slab's print (they lie along d): no level face is made, so the layer grid does not set them.
#   AA-C7, the lip along the slab's +x end: the R6 front roll (centre x 99.0, d 6.0) is cut by the rebate's wall at x 99.85, so
#     the roll's lowest edge there is 0.061 off the bed (the -x end has 4.25 of land on the bed). Seated: a land 0.5 wide on
#     the bed from the rebate's wall (to x 100.35), then a plane at 25.4 deg tangent to the roll (at x 101.57, d 0.578); round
#     the two +x corners of the rebate (r 2.3 round (97.55, -84.929) and (97.55, 30.071)) the same section turned about the
#     corner's axis (a cone). Material is only added under the roll, up to 0.154 at the land's edge; the rebate stays clear.
#   AA-A6: the screen plate's two top holes (x +-70, Zd 27.0) and the one at the slot (x -85, Zd -82.002) Ø3.4 -> Ø4.2. The
#     hole at the round pocket (x +85) stays Ø3.4.
# Run: runpy.run_path(D + 'p46_slab_plate.py')['main']()  -> p46_slab_plate.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
LOW = 0.20
X_WALL, X_C, D_C, R_ROLL = 99.85, 99.0, 6.0, 6.0          # rebate's +x wall; the +x roll's centre and radius
LAND = 0.5
CORNERS = [((97.55, -84.929), -1), ((97.55, 30.071), +1)]  # rebate's +x corners (centre in x, Zd) and which way Zd goes out
R_CORNER = 2.3
HOLES = [(70.0, 27.0, 13.3), (-70.0, 27.0, 13.3), (-85.0, -82.002, 11.5)]
R_HOLE = 2.1


def sbox(k, X, cen, ax, ay, Lx, Wy, Hz):
    """box in the slab frame: centre, two unit axes (x, d, Zd), sizes; its third axis is ax x ay"""
    return X.tbm.createBox(adsk.core.OrientedBoundingBox3D.create(k.Dp(*cen), k.V3(ax[0], -ax[1], ax[2]), k.V3(ay[0], -ay[1], ay[2]),
                                                                 Lx / 10.0, Wy / 10.0, Hz / 10.0))


def face_z(k, b, n_up, box):
    """Zd of the planar face square to Zd, facing up (+1) or down (-1), whose sample point lies in box (x0,x1,d0,d1,z0,z1)"""
    out = []
    for f in b.faces:
        if f.geometry.surfaceType != 0:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
        if abs(nv.z - n_up) > 1e-6:
            continue
        p = k.Sf(f.pointOnFace)
        if box[0] <= p[0] <= box[1] and box[2] <= p[1] <= box[3] and box[4] <= p[2] <= box[5]:
            out.append((p[2], f.area * 100.0))
    return out


def tangent():
    """the line from (X_WALL + LAND, 0) tangent to the roll: returns the tangent point (x, d) and the slope"""
    px = X_WALL + LAND
    cx, cd = X_C, D_C
    ux, ud = cx - px, cd - 0.0
    n = math.hypot(ux, ud); ux, ud = ux / n, ud / n
    qx, qd = X_C - px, 0.0 - 0.0                 # the bed's tangent point (99, 0) relative to P
    pr = qx * ux + qd * ud
    perp = (qx - pr * ux, qd - pr * ud)
    rx, rd = pr * ux - perp[0], pr * ud - perp[1]
    return (px + rx, rd), rd / rx


def _main():
    k = L['load'](); X = k.K(); k.budget(78)
    print(L['stamp'](), 'before', X.state())
    S = X.body('SLAB_frame'); P = X.body('HOUSING_F_plate')
    up = face_z(k, S, -1, (-100, 100, 9.0, 12.0, 30.0, 38.0))
    lo = face_z(k, S, +1, (-100, 100, 9.0, 12.0, -93.0, -88.0))
    ptop = face_z(k, P, +1, (-100, 100, 9.0, 12.8, 30.0, 38.0))
    pbot = face_z(k, P, -1, (-100, 100, 9.0, 12.8, -93.0, -88.0))
    print('slab upper rim inner face(s) %s; lower %s; plate top %s; bottom %s' % (up, lo, ptop, pbot))
    zu = max(a for a, b in up); zl = min(a for a, b in lo); zpt = max(a for a, b in ptop)
    s = X.tbm.copy(S)
    v0 = X.vol(s)
    # AA-A23
    X.uni(s, X.dbox(-99.0, 99.0, 9.0, 12.0, zpt, zu))
    v1 = X.vol(s)
    X.dif(s, X.dbox(-99.0, 99.0, 9.0, 12.0, zl - LOW, zl))
    v2 = X.vol(s)
    print('rims: upper face %.4f -> %.4f (onto the plate\'s top %.4f): +%.3f; lower face %.4f -> %.4f: -%.3f' % (zu, zpt, zpt, v1 - v0, zl, zl - LOW, v1 - v2))
    # AA-C7
    (tx, td), m = tangent()
    ang = math.atan(m)
    print('lip: land to x %.3f, then %.2f deg to the tangent point (%.3f, %.3f) on the roll' % (X_WALL + LAND, math.degrees(ang), tx, td))
    sw = tx - X_WALL                                 # the band's width from the rebate's wall
    above = sbox(k, X, (X_WALL + LAND - math.sin(ang) * 5.0, math.cos(ang) * 5.0, 0.0), (math.cos(ang), math.sin(ang), 0.0),
                 (-math.sin(ang), math.cos(ang), 0.0), 30.0, 10.0, 400.0)      # the half space above the profile's plane
    zc0, zc1 = CORNERS[0][0][1], CORNERS[1][0][1]
    fill = X.dbox(X_WALL, tx, 0.0, 3.0, zc0, zc1)
    X.sec(fill, above)
    for (cx, cz), sgn in CORNERS:
        r0 = R_CORNER + LAND
        cone = X.tbm.createCylinderOrCone(k.Dp(cx, 0.0, cz), r0 / 10.0, k.Dp(cx, 3.0, cz), (r0 + 3.0 / m) / 10.0)
        X.sec(cone, X.cyld(cx, cz, R_CORNER + sw, 0.0, 3.0))
        X.sec(cone, X.dbox(cx, cx + 10.0, 0.0, 3.0, cz, cz + sgn * 10.0))
        X.uni(fill, cone)
    # keep the rebate clear (to the rebate floor, d 1.2)
    reb = X.dbox(80.0, X_WALL, -1.0, 1.2, zc0, zc1)
    X.uni(reb, X.dbox(80.0, CORNERS[0][0][0], -1.0, 1.2, zc0 - R_CORNER, zc1 + R_CORNER))
    for (cx, cz), sgn in CORNERS:
        X.uni(reb, X.cyld(cx, cz, R_CORNER, -1.0, 1.2))
    X.dif(fill, reb)
    vadd = X.vol(fill) - X.xv(fill, s)
    X.uni(s, fill)
    v3 = X.vol(s)
    print('lip: added %.4f (fill %.4f, of it already slab %.4f); slab %.3f -> %.3f -> %.3f; lumps %d solid %s' % (
        v3 - v2, X.vol(fill), X.xv(fill, X.tbm.copy(S)), v0, v2, v3, s.lumps.count, s.isSolid))
    k.c['b4_slab'] = s
    # AA-A6
    p = X.tbm.copy(P)
    w0 = X.vol(p)
    for (x, zd, d1) in HOLES:
        c = X.cyld(x, zd, R_HOLE, 8.5, d1)
        print('  hole (%+.1f, %.3f): removed %.4f' % (x, zd, X.xv(c, p)))
        X.dif(p, c)
    k.c['b4_screen'] = p
    print('screen plate %.3f -> %.3f; lumps %d solid %s' % (w0, X.vol(p), p.lumps.count, p.isSolid))
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p46_slab_plate.txt', _main)
