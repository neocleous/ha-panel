# Block 5: the shell (HOUSING_F_front), built on temporary bodies, as built. Replaces p55_shell.py (kept with its output): p55
# chamfered the back band's bar with a plane, but the bar is an arc in plan (its bed-most edge is 0.49 nearer the bed at
# x 12 than at x 0), so the plane cut deeper toward its ends. Here the chamfer follows the arc: a cone round an upright axis.
# CHANGES NOTHING IN THE DOCUMENT except a hidden temporary body 'TMP_shell' (Offset Face), deleted again.
# Result in k.c['b5_shell'] (p57 puts it in). World mm; the shell prints chin down: bed at world y +6.80, print height
# 6.80 - y, 0.20 layers (part C).
#   AA-A7:  the bar's rear face (y -22.5, 426 mm2, normal -y) to y -22.4: bed 29.2, 146 layers; seam 0.20 to the cap's front
#           face (y -22.6). Offset Face -0.1.
#   AA-A19 / AA-C13: the door frame's front face (y -53.5, 1,488.7 mm2, normal +y; its lower ends stop the boxes' backs at
#           y -52.0) at bed 60.3, a half layer: to y -53.6 (bed 60.4), the side that opens the fit. Offset Face -0.1.
#   AA-A18: the right (-x) chin divider stood 0.1 off the left one's mirror (faces x -46.8 / -45.3 against 45.4 / 46.9; the clips
#           0.30 right, 0.40 left): moved 0.1 outward, to x -46.9 / -45.4. Offset Face on its two side faces.
#   AA-C14: the three fins on each chin divider (its top, z 62.9 to 66.5, cut along y into four leaves 0.71 to 0.78 thick with
#           gaps of 0.05 to 0.08; nothing within 3 but the screen plate, 0.2 off): removed down to z 62.8, where it is whole.
#   AA-A3:  the shell's bottom edge relieved where the four outer driver screw heads pass (heads r 2.85, axes along y at
#           x +-88.25, z 10.25 and 45.75, y 0 to 1.65): the heads' sweep along z with the plate unit 0.65 behind its place
#           (head y -0.65 to 1.0) cut from the shell: the corner faces at y 0.5 go to 1.0 there.
#   AA-C4:  a 45 deg chamfer on the back band's bar (x -18.0..18.0, z 165.5 to its top): its bed-side underside leans 14 deg off
#           the print's level. Cut by a cone round the arc's upright axis that passes through the bar's bed-most edge and leans
#           45 deg, down to the bar's lower face (z 165.5): the bar prints from its edge at 45 deg. Only the bar is cut.
# Run: runpy.run_path(D + 'p55b_shell.py')['main']()  -> p55b_shell.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
HEADS = [(88.25, 10.25), (88.25, 45.75), (-88.25, 10.25), (-88.25, 45.75)]
R_HEAD, B0 = 2.85, 0.65
FINS = [(45.35, 46.95), (-46.95, -45.35)]
BAR_X = 18.0
BAR_Z0 = 165.5


def find(k, b, n_want, at, axis, area, tol=0.03):
    out = []
    for f in b.faces:
        if f.geometry.surfaceType != 0:
            continue
        ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace)
        n = k.wv(nv)
        if sum(n[i] * n_want[i] for i in range(3)) < 0.9999:
            continue
        p = k.W(f.pointOnFace)
        if abs(p[axis] - at) < tol and abs(f.area * 100 - area) < 0.15 * area:
            out.append(f)
    return out


def offset(X, faces, dist):
    inp = X.root.features.offsetFacesFeatures.createInput(faces, adsk.core.ValueInput.createByReal(dist / 10.0))
    X.root.features.offsetFacesFeatures.add(inp)


def bar_edge(k, X, crop):
    """the bar's top (z) at x 0, and its bed-most y at that top at several x, by needles"""
    s = k.needle_t(X, [crop], (0.0, -52.6, 164.0), (0.0, -52.6, 169.0), 0.01)
    ztop = 164.0 + s[0][1]
    zq = ztop - 0.02
    pts = []
    for x in (0.0, 3.0, 10.0, 12.0, 15.0, 17.5):
        s = k.needle_t(X, [crop], (x, -57.0, zq), (x, -45.0, zq), 0.01)
        pts.append((x, -57.0 + s[0][1]))
    # circle centred on x = 0 through the points (least squares on R and yc: y = yc - sqrt(R^2 - x^2))
    best = None
    y0 = pts[0][1]
    for i in range(2001):
        R = 100.0 + i * 0.1
        yc = y0 + R
        e = sum((yc - math.sqrt(R * R - x * x) - y) ** 2 for x, y in pts)
        if best is None or e < best[0]:
            best = (e, R, yc)
    return ztop, pts, best


def _main():
    k = L['load'](); X = k.K(); k.budget(78)
    print(L['stamp'](), 'before', X.state())
    S = X.body('HOUSING_F_front')
    v0 = X.vol(X.tbm.copy(S))
    crop = X.wbox(-19, 19, -58, -44, 163.5, 171.5); X.sec(crop, X.tbm.copy(S))
    ztop, pts, (e, R, yc) = bar_edge(k, X, crop)
    print('band bar: top z %.3f; bed-most y at its top: %s; arc R %.1f centred y %.2f (rms %.3f)' % (ztop, [(x, round(y, 3)) for x, y in pts], R, yc, math.sqrt(e / len(pts))))
    # Offset Face: bar, frame, the right divider
    tb = X.add(X.tbm.copy(S), 'TMP_shell', show=False)
    bar = find(k, tb, (0, -1, 0), -22.5, 1, 426.1)
    if len(bar) != 1:
        tb.deleteMe(); raise RuntimeError('bar face')
    offset(X, bar, -0.1)
    tb = X.body('TMP_shell')
    frame = find(k, tb, (0, 1, 0), -53.5, 1, 1488.7)
    if len(frame) != 1:
        tb.deleteMe(); raise RuntimeError('frame face')
    offset(X, frame, -0.1)
    tb = X.body('TMP_shell')
    din = find(k, tb, (1, 0, 0), -45.3, 0, 191.9)
    if len(din) != 1:
        tb.deleteMe(); raise RuntimeError('divider inner')
    offset(X, din, -0.1)
    tb = X.body('TMP_shell')
    dout = find(k, tb, (-1, 0, 0), -46.8, 0, 195.0)
    if len(dout) != 1:
        tb.deleteMe(); raise RuntimeError('divider outer')
    offset(X, dout, 0.1)
    tb = X.body('TMP_shell')
    s = X.tbm.copy(tb)
    tb.deleteMe()
    print('offsets done (bar -0.1, frame -0.1, right divider -0.1 / +0.1)')
    for (x0, x1) in FINS:
        c = X.wbox(x0, x1, 1.1, 3.95, 62.8, 66.8)
        print('  fins at x %.2f..%.2f: removed %.4f' % (x0, x1, X.xv(c, s)))
        X.dif(s, c)
    cut = None
    for (xc, zc) in HEADS:
        c = X.wbox(xc - R_HEAD, xc + R_HEAD, -B0, 1.65 - B0, -60.0, zc)
        X.uni(c, X.cyl((xc, -B0, zc), (xc, 1.65 - B0, zc), R_HEAD))
        cut = c if cut is None else X.uni(cut, c)
    rem = X.tbm.copy(cut); X.sec(rem, X.tbm.copy(s))
    print('heads\' relief: %.4f mm3 in %d lump(s): %s' % (X.vol(rem), rem.lumps.count, X.lumps(rem)))
    X.dif(s, cut)
    # the band bar's chamfer: inside the cone rho < R - (z - ztop), within the bar's box
    za, zb = BAR_Z0 - 0.5, ztop + 0.3
    cone = X.cyl((0.0, yc, za), (0.0, yc, zb), R + (ztop - za), R - (zb - ztop))
    X.sec(cone, X.wbox(-BAR_X, BAR_X, -54.0, -49.5, BAR_Z0, zb))
    vc = X.xv(cone, s)
    print('band bar chamfer: removed %.4f' % vc)
    X.dif(s, cone)
    k.c['b5_shell'] = s
    k.c['b5_bar'] = (ztop, R, yc)
    print('shell: %.3f -> %.3f (temporary-body reading; %+.3f); lumps %d solid %s faces %d' % (v0, X.vol(s), X.vol(s) - v0, s.lumps.count, s.isSolid, s.faces.count))
    for b in [b for b in X.root.bRepBodies if b.name.startswith('TMP_')]:
        b.deleteMe()
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p55b_shell.txt', _main)
