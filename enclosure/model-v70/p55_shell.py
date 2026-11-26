# Block 5: the shell (HOUSING_F_front), built on temporary bodies. CHANGES NOTHING IN THE DOCUMENT except a hidden temporary body
# 'TMP_shell' (Offset Face), deleted again. Result in k.c['b5_shell'] (p57 puts it in). World mm; the shell prints chin down:
# bed at world y +6.80, print height 6.80 - y, 0.20 layers (part C).
#   AA-A7:  the bar's rear face (y -22.5, 426 mm2, normal -y) to y -22.4: 146 layers (bed 29.2); seam 0.20 to the cap's front
#           face (y -22.6). Offset Face -0.1.
#   AA-A19 / AA-C13: the door frame's front face (y -53.5, 1,488.7 mm2, normal +y; its lower ends stop the boxes' backs at
#           y -52.0) at bed 60.3, a half layer: to y -53.6 (bed 60.4), the side that opens the fit. Offset Face -0.1.
#   AA-A18: the right (-x) chin divider stands 0.1 off the left one's mirror (faces x -46.8 / -45.3 against 45.4 / 46.9; the
#           clips 0.30 right, 0.40 left): moved 0.1 outward, to x -46.9 / -45.4. Offset Face on its two side faces.
#   AA-C14: the three fins on each chin divider (the divider's top, z 62.9 to 66.5, x 45.4..46.9 and its mirror, sliced along y
#           into four leaves 0.06 to 0.08 apart, the leaves' tops leaning with the screen): removed down to z 62.8, where the
#           divider is whole, if they carry nothing (their neighbours are read first).
#   AA-A3:  the shell's bottom edge relieved where the four outer driver screw heads pass (heads r 2.85 on axes along y at
#           x +-88.25, z 10.25 and 45.75, y 0 to 1.65): the heads' sweep along z with the plate unit 0.65 behind its place
#           (head y -0.65 to 1.0) is cut from the shell. The corner faces at y 0.5 go to 1.0: the heads clear from 0.65.
#   AA-C4:  a 45 deg chamfer on the back band's bar (x -18.2..18.2, z 165.5..167.05): its bed-side underside leans 14 deg from
#           the print's level; cut along the 45 deg plane through the bar's bed-most edge (z 167.05, y -51.26) down to its lower
#           face (z 165.5), so the bar prints from that edge at 45 deg. Material is only taken from the bar.
# Run: runpy.run_path(D + 'p55_shell.py')['main']()  -> p55_shell.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
HEADS = [(88.25, 10.25), (88.25, 45.75), (-88.25, 10.25), (-88.25, 45.75)]
R_HEAD, B0 = 2.85, 0.65
FINS = [(45.35, 46.95), (-46.95, -45.35)]
BAR_B = (167.05, -51.26)          # the band bar's bed-most edge (z, y), from p54_band.txt


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


def offset(X, b, faces, dist):
    inp = X.root.features.offsetFacesFeatures.createInput(faces, adsk.core.ValueInput.createByReal(dist / 10.0))
    X.root.features.offsetFacesFeatures.add(inp)


def _main():
    k = L['load'](); X = k.K(); k.budget(78)
    print(L['stamp'](), 'before', X.state())
    S = X.body('HOUSING_F_front')
    v0 = X.vol(X.tbm.copy(S))
    # the fins' neighbours, before anything changes
    for (x0, x1) in FINS:
        t = X.wbox(x0, x1, 1.1, 3.95, 62.8, 66.8); X.sec(t, X.tbm.copy(S))
        tb = X.add(t, 'TMP_fin', show=False)
        near = []
        for b in k.current(X, leads=True):
            if b.name in ('HOUSING_F_front',) or b.name.startswith('TMP_'):
                continue
            g = t.boundingBox
            box = adsk.core.BoundingBox3D.create(k.P3(g.minPoint.x - 0.3, g.minPoint.y - 0.3, g.minPoint.z - 0.3), k.P3(g.maxPoint.x + 0.3, g.maxPoint.y + 0.3, g.maxPoint.z + 0.3))
            if box.intersects(b.boundingBox):
                d = X.mm.measureMinimumDistance(tb, b).value * 10
                if d < 3.0:
                    near.append((round(d, 2), b.name))
        print('fins at x %.2f..%.2f: %.3f mm3 in %d lump(s); bodies within 3 of them: %s' % (x0, x1, X.vol(t), t.lumps.count, sorted(near) if near else 'none'))
        tb.deleteMe()
    # Offset Face: bar, frame, the right divider
    tb = X.add(X.tbm.copy(S), 'TMP_shell', show=False)
    bar = find(k, tb, (0, -1, 0), -22.5, 1, 426.1)
    frame = find(k, tb, (0, 1, 0), -53.5, 1, 1488.7)
    print('bar face %d (%s), frame face %d (%s)' % (len(bar), [round(f.area * 100, 1) for f in bar], len(frame), [round(f.area * 100, 1) for f in frame]))
    if len(bar) != 1 or len(frame) != 1:
        tb.deleteMe(); raise RuntimeError('faces')
    offset(X, tb, bar, -0.1)
    tb = X.body('TMP_shell')
    frame = find(k, tb, (0, 1, 0), -53.5, 1, 1488.7)
    offset(X, tb, frame, -0.1)
    tb = X.body('TMP_shell')
    din = find(k, tb, (1, 0, 0), -45.3, 0, 191.9)
    print('right divider inner face %d (%s)' % (len(din), [round(f.area * 100, 1) for f in din]))
    if len(din) != 1:
        tb.deleteMe(); raise RuntimeError('divider inner')
    offset(X, tb, din, -0.1)
    tb = X.body('TMP_shell')
    dout = find(k, tb, (-1, 0, 0), -46.8, 0, 195.0)
    print('right divider outer face %d (%s)' % (len(dout), [round(f.area * 100, 1) for f in dout]))
    if len(dout) != 1:
        tb.deleteMe(); raise RuntimeError('divider outer')
    offset(X, tb, dout, 0.1)
    tb = X.body('TMP_shell')
    s = X.tbm.copy(tb)
    tb.deleteMe()
    v1 = X.vol(s)
    print('after the offsets: %.3f -> %.3f (%+.3f; bar -42.6 and frame -148.9 expected, the divider about 0)' % (v0, v1, v1 - v0))
    # fins
    for (x0, x1) in FINS:
        c = X.wbox(x0, x1, 1.1, 3.95, 62.8, 66.8)
        print('  fins at x %.2f..%.2f: removed %.4f' % (x0, x1, X.xv(c, s)))
        X.dif(s, c)
    # heads' relief
    cut = None
    for (xc, zc) in HEADS:
        c = X.wbox(xc - R_HEAD, xc + R_HEAD, -B0, 1.65 - B0, -60.0, zc)
        X.uni(c, X.cyl((xc, -B0, zc), (xc, 1.65 - B0, zc), R_HEAD))
        cut = c if cut is None else X.uni(cut, c)
    rem = X.tbm.copy(cut); X.sec(rem, X.tbm.copy(s))
    print('heads\' relief: %.4f mm3 in %d lump(s): %s' % (X.vol(rem), rem.lumps.count, X.lumps(rem)))
    X.dif(s, cut)
    # the band bar's chamfer: off the half space (y - yB) - (z - zB) > 0 in the bar's box
    zB, yB = BAR_B
    n = (0.0, math.sqrt(0.5), -math.sqrt(0.5))
    cen = (0.0, yB + n[1] * 2.0, zB + n[2] * 2.0)
    hs = X.obox(cen, (1.0, 0.0, 0.0), (0.0, math.sqrt(0.5), math.sqrt(0.5)), 40.0, 8.0, 4.0)
    X.sec(hs, X.wbox(-18.2, 18.2, -53.2, -50.8, 165.5, 167.3))
    print('band bar chamfer: removed %.4f in %d lump(s): %s' % (X.xv(hs, s), hs.lumps.count, X.lumps(hs)[:4]))
    X.dif(s, hs)
    k.c['b5_shell'] = s
    print('shell: %.3f -> %.3f (%+.3f); lumps %d solid %s faces %d' % (v0, X.vol(s), X.vol(s) - v0, s.lumps.count, s.isSolid, s.faces.count))
    for b in [b for b in X.root.bRepBodies if b.name.startswith('TMP_')]:
        b.deleteMe()
    print(L['stamp'](), 'after', X.state())


def main():
    L['out']('p55_shell.txt', _main)
