# Block 7 (brief claude/brief-enclosure-audit-fixes-rest-2026-11-25.md): the chin wall (D430), the touch board's bodies, the carrier,
# the clips, the hood, the boxes, built as temporary bodies. Adds and deletes 'TMP_*' bodies for Offset Face; nothing else in the
# document changes. Results in k.c['b7_*']. World mm.
#   'shell'   D430: the chin wall's inner face (the touch board's seat, y 4.2992, x -45.4..45.4, z 6.00..48.04) to y 4.3992 (bed
#             2.4, twelve layers): Offset Face -0.1. AA-A14: the hood's two pins shortened so that they stand 2.0 above the hood's
#             underside round them (the hold: the lift that frees the hood).            -> b7_shell
#   'touch'   the touch board and what is set from it 0.1 toward the screen: TOUCH_PCB, TOUCH_components_env, KO_touch_back, and
#             LEAD_TOUCH's end (the part at y > -1.0).                                               -> b7_tpcb, b7_tcomp, b7_tko, b7_tlead
#   'clip'    AA-A1: the tongue to the board's back as moved (y 2.8: touching as modelled); the hole a slot 3.4 x 4.2 along y (+-0.4)
#             so that the clip is pushed onto the board at the build and its screw tightened. Right = left turned top for bottom
#             about the line along y at x 0, z 38.                                                   -> b7_clipL, b7_clipR
#   'carrier' AA-C6, AA-B1: post tops 0.1 higher (bed 16.0); insert holes to bed 7.8 (8.2 deep). AA-B15: an arrow engraved on
#             the door-side face at the top, 0.4 deep, pointing to the top.                          -> b7_carrier
#   'boxes'   AA-B2: both clip pilots 0.25 deeper (1.25 of wall left to the chamber). AA-A12: the right box's roof edge broken 0.5
#             x 45 deg on its outboard side, and its front outboard upright edge (z 75.5..83) the same; the raised roof's
#             curved outboard side 0.18 inboard (0.30 -> 0.48 to the wall, the left box's figure). AA-B19: the left box's plug-pocket wall: the upper run carried 1.5 further down, the two
#             runs overlapped by 2.0; the added block kept clear of the screw tube's bore.                               -> b7_boxL, b7_boxR
#   'hood'    AA-A14, AA-C16, AA-B18 in the hood's print (top plate's outer face down, n = its normal, 0.20 layers): the top
#             plate's curved edge 0.30 from the wall (Offset Face +0.30 toward it); a pad 0.2 under the top plate over 20.3 of the top foam's
#             21, between the tray's end walls (bed 1.2 -> 1.4: foam 0.5 -> 0.3); the end piece 0.30 from the wall's end (Offset Face); the ear's top face flush
#             (bed 0); the small faces at bed 1.164 and 1.214 to 1.2; the end piece's bottom 5.864 -> 5.8; the foot 17.7 -> 17.6.
#             The top foam envelope and the main foam envelope less the new hood.                   -> b7_hood, b7_foamtop, b7_foam
# Run: runpy.run_path(D + 'p68_b7_build.py')['main'](stage)  -> p68_<stage>.txt
import runpy, math
import adsk.core, adsk.fusion

D = '/Users/danielneocleous/Documents/HA_panel_renders/audit_fixes_v70/'
L = runpy.run_path(D + 'v70_lib.py')
VI = adsk.core.ValueInput


def offset(X, tb, sel, mm, tag):
    """Offset Face on a hidden temporary model copy; sel(face) -> True picks the face. Returns a temporary copy, the copy deleted."""
    b = X.add(X.tbm.copy(tb), 'TMP_' + tag, show=False)
    fs = [f for f in b.faces if sel(f)]
    if not fs:
        b.deleteMe(); raise RuntimeError('%s: no face' % tag)
    print('   %s: offset %d face(s) by %+.4f, %.2f mm2' % (tag, len(fs), mm, sum(f.area * 100 for f in fs)))
    inp = X.root.features.offsetFacesFeatures.createInput(fs, VI.createByReal(mm / 10.0))
    X.root.features.offsetFacesFeatures.add(inp)
    b = X.body('TMP_' + tag); out = X.tbm.copy(b); b.deleteMe()
    return out


def nrm(k, f):
    ok, nv = f.evaluator.getNormalAtPoint(f.pointOnFace); return k.unit(k.wv(nv))


def shell(k, X):
    S = X.tbm.copy(X.body('HOUSING_F_front')); v0 = X.vol(S)

    def chin(f):
        if f.geometry.surfaceType != k.PLN:
            return False
        n = nrm(k, f); p = k.W(f.pointOnFace)
        return n[1] < -0.9999 and abs(p[1] - 4.2992) < 0.002 and abs(f.area * 100 - 3817.43) < 1.0
    S = offset(X, S, chin, -0.1, 'chin')
    print('shell after the chin face: %.3f -> %.3f' % (v0, X.vol(S)))
    hb = X.body('BME_HOOD')
    for r in k.holes_of(hb, rmin=1.15, rmax=1.25):
        A = r['A']; a = r['a']
        if abs(a[2] - 0.989) > 0.01:
            continue
        p1 = tuple(A[i] + 2.0 * a[i] for i in range(3)); p2 = tuple(A[i] + 3.5 * a[i] for i in range(3))
        c = X.cyl(p1, p2, 1.05); vc = X.xv(c, S); X.dif(S, c)
        print('   pin at %s: cut %.4f mm3 beyond 2.0 along its axis from the hood\'s underside' % (A, vc))
    print('shell: %.3f -> %.3f, lumps %d' % (v0, X.vol(S), S.lumps.count))
    k.c['b7_shell'] = S


def touch(k, X):
    for nm, key in (('TOUCH_PCB', 'b7_tpcb'), ('TOUCH_components_env', 'b7_tcomp'), ('KO_touch_back', 'b7_tko')):
        t = X.move(X.tbm.copy(X.body(nm)), 0, 0.1, 0); k.c[key] = t
        print('%s moved 0.1 toward the screen: box %s' % (nm, k.wbb(X, t)))
    ld = X.body('LEAD_TOUCH'); a = X.tbm.copy(ld); b = X.tbm.copy(ld)
    X.sec(a, X.wbox(-60, 60, -1.0, 10, 0, 120)); X.move(a, 0, 0.1, 0)
    X.sec(b, X.wbox(-60, 60, -60, -0.9, 0, 120))
    X.uni(b, a)
    print('LEAD_TOUCH: %.3f -> %.3f, lumps %d, box %s' % (ld.volume * 1000, X.vol(b), b.lumps.count, k.wbb(X, b)))
    k.c['b7_tlead'] = b


def clip(k, X):
    t = X.tbm.copy(X.body('TOUCH_CLIP_L')); v0 = X.vol(t)
    X.uni(t, X.wbox(43.6, 45.0, 1.95, 2.8, 30.0, 46.0))
    for yy in (-7.45, -6.65):
        X.dif(t, X.cyl((40.0, yy, 38.0), (44.0, yy, 38.0), 1.7))
    X.dif(t, X.wbox(40.0, 44.0, -7.45, -6.65, 36.3, 39.7))
    print('TOUCH_CLIP_L: %.3f -> %.3f, lumps %d, faces %d, box %s' % (v0, X.vol(t), t.lumps.count, t.faces.count, k.wbb(X, t)))
    r = X.tbm.copy(t)
    m = adsk.core.Matrix3D.create(); m.setToRotation(math.pi, k.dv((0, 1, 0)), k.Wp(0.0, 0.0, 38.0)); X.tbm.transform(r, m)
    print('TOUCH_CLIP_R (left turned top for bottom about the line along y at x 0, z 38): %.3f, box %s' % (X.vol(r), k.wbb(X, r)))
    old = X.tbm.copy(X.body('TOUCH_CLIP_L')); m2 = adsk.core.Matrix3D.create(); m2.setToRotation(math.pi, k.dv((0, 1, 0)), k.Wp(0.0, 0.0, 38.0))
    X.tbm.transform(old, m2)
    vr = X.body('TOUCH_CLIP_R'); d1 = X.tbm.copy(old); X.dif(d1, X.tbm.copy(vr)); d2 = X.tbm.copy(vr); X.dif(d2, old)
    print('   check: version 75 left turned the same way against version 75 right: %.5f and %.5f mm3 apart' % (X.vol(d1) if d1.faces.count else 0, X.vol(d2) if d2.faces.count else 0))
    k.c['b7_clipL'] = t; k.c['b7_clipR'] = r


def carrier(k, X):
    c = X.tbm.copy(X.body('RESP_CARRIER')); v0 = X.vol(c)
    a = (0.0, 0.978148, 0.207912)
    for r in k.holes_of(X.body('RESP_CARRIER'), rmin=1.9, rmax=2.1):
        A = r['A']
        top = X.tbm.copy(X.body('RESP_CARRIER'))
        X.sec(top, X.cyl(tuple(A[i] - 0.001 * a[i] for i in range(3)), tuple(A[i] + 1.0 * a[i] for i in range(3)), 6.0))
        X.move(top, -0.1 * a[0], -0.1 * a[1], -0.1 * a[2]); X.uni(c, top)
        X.dif(c, X.cyl(tuple(A[i] - 0.2 * a[i] for i in range(3)), tuple(A[i] + 8.1 * a[i] for i in range(3)), 2.0))
        print('   post at %s: top 0.1 higher, hole to 8.1 beyond the old mouth (8.2 from the new top)' % A)
    # the arrow: a triangle on the door-side face (slab frame d 17.2), x -2.5..2.5, Zd -7..-3, pointing to +Zd, 0.4 deep
    tri = None
    for i in range(10):
        zd0 = -7.0 + 0.4 * i; half = 2.5 * (1 - (i + 0.5) / 10.0)
        bx = X.dbox(-half, half, 16.8, 17.3, zd0, zd0 + 0.4)
        tri = bx if tri is None else X.uni(tri, bx)
    print('   arrow: %.3f mm3 of the carrier inside it' % X.xv(tri, c))
    X.dif(c, tri)
    print('RESP_CARRIER: %.3f -> %.3f, lumps %d' % (v0, X.vol(c), c.lumps.count))
    k.c['b7_carrier'] = c


def boxes(k, X):
    # from the hidden _v69 copies: the boxes are unchanged from version 69 to 75 (guard volumes equal), and this keeps the stage repeatable
    L_ = X.tbm.copy(X.body('SPKBOX_L_v69')); R_ = X.tbm.copy(X.body('SPKBOX_R_v69')); vl, vr = X.vol(L_), X.vol(R_)
    X.dif(L_, X.cyl((48.9, -7.05, 38.0), (49.25, -7.05, 38.0), 1.35))
    X.dif(R_, X.cyl((-48.9, -7.05, 38.0), (-49.25, -7.05, 38.0), 1.35))
    print('pilots 0.25 deeper: L %.4f, R %.4f mm3 off' % (vl - X.vol(L_), vr - X.vol(R_)))
    # the breaks below leave the curved outboard face of the raised roof 0.30 from the wall (it runs beside it). Offset Face fails on
    # that face (ASM_LOP_TWK_NO_VERT), so the box is cut instead by the shell's own wall moved 0.48 toward it along +x, over the raised
    # roof's band (z 75.5..83): the box's side then follows the wall 0.48 off in x, the left box's figure (AA-A12's aim)
    cutter = X.tbm.copy(X.body('HOUSING_F_front')); X.sec(cutter, X.wbox(-100, -90, -55, -3.0, 74, 84)); X.move(cutter, 0.48, 0, 0)
    X.sec(cutter, X.wbox(-96, -90, -53, -3.6, 75.5, 83))
    v1 = X.vol(R_); X.dif(R_, cutter)
    print('right box raised roof outboard side kept 0.48 off the wall in x: %.4f mm3 off' % (v1 - X.vol(R_)))
    # right box: break the roof's outboard edge 0.5 x 45: remove -x + z >= 93.22 + 82.0 - 0.5
    n = (-1 / math.sqrt(2), 0.0, 1 / math.sqrt(2)); a2 = (1 / math.sqrt(2), 0.0, 1 / math.sqrt(2))
    p0 = (-92.97, -28.0, 81.75)
    w = X.obox((p0[0] + n[0] * 2.0, p0[1], p0[2] + n[2] * 2.0), (0, 1, 0), a2, 50.0, 6.0, 4.0)
    X.sec(w, X.wbox(-96, -88, -53, -3.6, 76, 83))
    v1 = X.vol(R_); X.dif(R_, w)
    print('right box roof edge broken: %.4f mm3 off' % (v1 - X.vol(R_)))
    # and its front outboard upright edge, where part A's tight point lies (-93.4, -3.8, 78.5): remove -x + y >= 89.27 (0.5 x 45 at
    # the box's most outboard x, -93.47), over z 75.5..83
    n2 = (-1 / math.sqrt(2), 1 / math.sqrt(2), 0.0); b2 = (1 / math.sqrt(2), 1 / math.sqrt(2), 0.0)
    q0 = (-92.97, -3.7, 71.5)
    w2 = X.obox((q0[0] + n2[0] * 2.0, q0[1] + n2[1] * 2.0, q0[2]), (0, 0, 1), b2, 23.0, 6.0, 4.0)
    X.sec(w2, X.wbox(-96, -90, -6, -3.6, 75.5, 83))      # only where the box's outboard side is the curved face beside the shell (z 75.5..82)
    v1 = X.vol(R_); X.dif(R_, w2)
    print('right box front outboard edge broken: %.4f mm3 off' % (v1 - X.vol(R_)))
    # left box: the plug pocket's upper wall run carried down 1.5 (y -36.0 -> -37.5), x 55.65..57.15, z 9.7..20.7; the bore again
    v1 = X.vol(L_)
    add = X.wbox(55.65, 57.15, -37.5, -35.95, 9.7, 20.7)
    X.dif(add, X.cyl((52.75, -52.5, 10.25), (52.75, -18.5, 10.25), 3.1))      # keep the screw tube's bore clear
    print('   added block: %.4f mm3, of which already solid %.4f' % (X.vol(add), X.xv(add, L_)))
    X.uni(L_, add)
    print('left box pocket wall: %+.4f mm3' % (X.vol(L_) - v1))
    print('SPKBOX_L %.3f -> %.3f lumps %d; SPKBOX_R %.3f -> %.3f lumps %d' % (vl, X.vol(L_), L_.lumps.count, vr, X.vol(R_), R_.lumps.count))
    k.c['b7_boxL'] = L_; k.c['b7_boxR'] = R_


def hood(k, X):
    # from the hidden _v69 copy (equal to version 75's hood, 909.833 mm3 at very high accuracy), so the stage can be run again after the put
    H = X.body('BME_HOOD_v69') or X.body('BME_HOOD'); t = X.tbm.copy(H); v0 = X.vol(t)
    n = (0.11394, 0.09756, 0.98869); p0 = (-69.8829, -39.0603, 110.0342)
    u = (0.7593, 0.6497, -0.1517); vv = (-0.6575, 0.7680, 0.0)

    def bed(p):
        return sum((p0[i] - p[i]) * n[i] for i in range(3))

    def plevel(f, b0, sign):
        if f.geometry.surfaceType != k.PLN:
            return False
        m = nrm(k, f); c = sum(m[i] * n[i] for i in range(3))
        return abs(c - sign) < 1e-3 and abs(bed(k.W(f.pointOnFace)) - b0) < 0.003
    # the top plate's curved edge toward the wall: the NURBS face of 33.62 mm2
    t = offset(X, t, lambda f: f.geometry.surfaceType not in (k.PLN, k.CYL) and abs(f.area * 100 - 33.62) < 0.3, 0.30, 'hedge')
    # the end piece's face toward the wall's end (normal ~ -0.751,-0.643,0.15, 15.6 mm2): 0.0217 -> 0.30
    def endp(f):
        if f.geometry.surfaceType != k.PLN:
            return False
        m = nrm(k, f); return abs(f.area * 100 - 15.6) < 0.3 and m[0] < -0.7 and m[1] < -0.6
    t = offset(X, t, endp, -0.2783, 'hend')
    t = offset(X, t, lambda f: plevel(f, -0.0256, 1), -0.0256, 'hear')
    t = offset(X, t, lambda f: plevel(f, 1.2144, 1), 0.0144, 'h12a')
    t = offset(X, t, lambda f: plevel(f, 1.1641, -1), 0.0359, 'h12b')
    t = offset(X, t, lambda f: plevel(f, 5.8644, -1), -0.0644, 'h58')
    t = offset(X, t, lambda f: plevel(f, 17.7, -1), -0.1, 'hfoot')
    # the pad under the top plate over the top foam: bed 1.2 -> 1.4, u -6..5 (to the side plate: the foam lies on the sensor and on the main foam), v -10.05..10.25, cut from the hood moved 0.2 along -n
    n = k.unit(n); dd = sum(u[i] * n[i] for i in range(3)); u = k.unit(tuple(u[i] - dd * n[i] for i in range(3)))
    vv = (n[1] * u[2] - n[2] * u[1], n[2] * u[0] - n[0] * u[2], n[0] * u[1] - n[1] * u[0])
    o = tuple(p0[i] - 1.275 * n[i] for i in range(3))       # pad box bed 1.15..1.40: 0.05 into the plate, so that it joins it
    def at(uu, vq):
        return tuple(o[i] + uu * u[i] + vq * vv[i] for i in range(3))
    box = X.obox(at(-0.5, 0.1), u, vv, 11.0, 20.3, 0.25)      # v -10.05..10.25: 0.45 / 0.25 to the tray's end walls (inner faces v +-10.5), 0.35 each once the screw has drawn the ear 0.10 onto its boss
    T = X.move(X.tbm.copy(t), -0.2 * n[0], -0.2 * n[1], -0.2 * n[2])
    X.sec(box, T)
    print('   pad: %.3f mm3, %d lump(s)' % (X.vol(box), box.lumps.count))
    X.uni(t, box)
    print('BME_HOOD: %.3f -> %.3f mm3, lumps %d, faces %d' % (v0, X.vol(t), t.lumps.count, t.faces.count))
    k.c['b7_hood'] = t
    f = X.tbm.copy(X.body('FOAM_bme_top_env_v69') or X.body('FOAM_bme_top_env')); vf = X.vol(f); X.dif(f, X.tbm.copy(t))
    print('FOAM_bme_top_env: %.3f -> %.3f (squeezed under the pad), lumps %d' % (vf, X.vol(f), f.lumps.count))
    k.c['b7_foamtop'] = f
    # the main foam's envelope reaches the hood's underside beside the sensor (under the top foam): squeezed under the pad the same way
    g = X.tbm.copy(X.body('FOAM_bme_env_v69') or X.body('FOAM_bme_env')); vg = X.vol(g); X.dif(g, X.tbm.copy(t))
    print('FOAM_bme_env: %.3f -> %.3f (squeezed under the pad), lumps %d' % (vg, X.vol(g), g.lumps.count))
    k.c['b7_foam'] = g


def _main(stage):
    k = L['load'](); X = k.K(); k.budget(75)
    print(L['stamp'](), 'before', X.state())
    {'shell': shell, 'touch': touch, 'clip': clip, 'carrier': carrier, 'boxes': boxes, 'hood': hood}[stage](k, X)
    for b in [b for b in X.root.bRepBodies if b.name.startswith('TMP_')]:
        b.deleteMe()
    print(L['stamp'](), 'after', X.state())


def main(stage):
    L['out']('p68_%s.txt' % stage, _main, stage)
